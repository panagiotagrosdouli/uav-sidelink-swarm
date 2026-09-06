"""Compare experimental sidelink resource-allocation abstractions.

Algorithms are THIS_WORK system-level abstractions, not normative NR Mode 2.
Reliability/goodput uses the verified 5G-LENA MCS4/5/6 BG1/CBS4096 fixture and
is therefore limited LINK_LEVEL_SIMULATION-derived evidence.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import jain_fairness
from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.sidelink.resource_allocation import (
    greedy_distance_aware_allocation,
    random_allocation,
    weighted_conflict_graph_allocation,
)
from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    dbm_to_w,
    generate_equal_altitude_positions,
    received_power_w,
    thermal_noise_dbm,
)

SWARM_SIZES = [10, 20, 30, 50]
N_RESOURCES = [1, 2, 4, 8]
N_SEEDS = 50
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"


def _curves():
    all_curves = load_bler_curves(BLER_CSV, source="5G-LENA verified Table1 BG1 CBS4096 subset")
    return curves_for_cbs(all_curves, code_block_size=4096, base_graph=1)


def evaluate(seed: int, n_uavs: int, n_resources: int, algorithm: str) -> dict[str, float | int | str]:
    cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a")
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(n_uavs)
    tx_pos = np.array([positions[t] for t, _ in pairs])
    rx_pos = np.array([positions[r] for _, r in pairs])

    if algorithm == "random":
        alloc = random_allocation(len(pairs), n_resources, seed)
    elif algorithm == "greedy":
        alloc = greedy_distance_aware_allocation(tx_pos, rx_pos, n_resources)
    elif algorithm == "graph":
        alloc = weighted_conflict_graph_allocation(tx_pos, rx_pos, n_resources)
    else:
        raise ValueError(algorithm)

    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    curves = _curves()
    sinrs: list[float] = []
    successes: list[float] = []
    goodputs: list[float] = []
    selected_mcs: list[int] = []
    for i, (tx, rx) in enumerate(pairs):
        s_w, _, _ = received_power_w(tx, rx, positions, cfg)
        interference_w = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if j == i or alloc.resources[j] != alloc.resources[i]:
                continue
            p_i, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interference_w += p_i
        sinr_linear = s_w / (noise_w + interference_w)
        sinr_db = 10.0 * np.log10(sinr_linear)
        sinrs.append(float(sinr_db))
        choice = select_max_goodput_mcs(
            sinr_db=float(sinr_db),
            curves=curves,
            bandwidth_mhz=cfg.bandwidth_mhz,
            resource_fraction=1.0 / n_resources,
        )
        if choice is None:
            successes.append(0.0)
            goodputs.append(0.0)
            selected_mcs.append(-1)
        else:
            successes.append(choice.first_tx_success_probability)
            goodputs.append(choice.expected_phy_goodput_mbps)
            selected_mcs.append(choice.mcs_index)

    unique, counts = np.unique(alloc.resources, return_counts=True)
    collisions = int(np.sum(np.maximum(counts - 1, 0)))
    return {
        "seed": seed,
        "n_uavs": n_uavs,
        "n_resources": n_resources,
        "algorithm": algorithm,
        "mean_sinr_db": float(np.mean(sinrs)),
        "median_sinr_db": float(np.median(sinrs)),
        "mean_first_tx_success_probability": float(np.mean(successes)),
        "mean_expected_phy_goodput_mbps": float(np.mean(goodputs)),
        "jain_goodput_fairness": jain_fairness(goodputs),
        "median_selected_mcs": float(np.median([m for m in selected_mcs if m >= 0])) if any(m >= 0 for m in selected_mcs) else -1.0,
        "resource_reuse_excess_links": collisions,
    }


def main() -> None:
    rows = []
    for n in SWARM_SIZES:
        for r in N_RESOURCES:
            for seed in range(N_SEEDS):
                for algorithm in ("random", "greedy", "graph"):
                    rows.append(evaluate(seed, n, r, algorithm))
    raw = pd.DataFrame(rows)
    out = Path("results/resource_allocation")
    figs = Path("figures/resource_allocation")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "raw.csv", index=False)

    summary = raw.groupby(["n_uavs", "n_resources", "algorithm"], as_index=False).agg(
        mean_sinr_db=("mean_sinr_db", "mean"),
        std_sinr_db=("mean_sinr_db", "std"),
        mean_first_tx_success_probability=("mean_first_tx_success_probability", "mean"),
        mean_expected_phy_goodput_mbps=("mean_expected_phy_goodput_mbps", "mean"),
        mean_jain_goodput_fairness=("jain_goodput_fairness", "mean"),
        mean_resource_reuse_excess_links=("resource_reuse_excess_links", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)

    for metric, ylabel, stem in [
        ("mean_sinr_db", "Mean SINR [dB]", "sinr"),
        ("mean_expected_phy_goodput_mbps", "Mean expected PHY goodput [Mbps]", "goodput"),
        ("mean_jain_goodput_fairness", "Mean Jain goodput fairness", "fairness"),
    ]:
        for n in SWARM_SIZES:
            fig, ax = plt.subplots(figsize=(7.2, 4.8))
            subset = summary[summary.n_uavs == n]
            for algorithm, group in subset.groupby("algorithm"):
                ax.plot(group.n_resources, group[metric], marker="o", label=algorithm)
            ax.set_xlabel("Number of abstract orthogonal resources")
            ax.set_ylabel(ylabel)
            ax.set_title(f"Resource allocation comparison — N={n} UAVs")
            ax.grid(True, alpha=0.3)
            ax.legend()
            fig.tight_layout()
            fig.savefig(figs / f"{stem}_resources_n{n}.png", dpi=300)
            fig.savefig(figs / f"{stem}_resources_n{n}.pdf")
            plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

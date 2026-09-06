"""Compare random vs experimental distance-aware resource reuse.

This is a system-level comparison, not a normative NR Mode-1/Mode-2 simulator.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.sidelink.resource_allocation import greedy_distance_aware_allocation, random_allocation
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

SWARM_SIZES = [10, 20, 30, 50]
N_RESOURCES = [1, 2, 4, 8]
N_SEEDS = 50


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
    else:
        raise ValueError(algorithm)

    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    sinrs = []
    outages = []
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
        sinrs.append(sinr_db)
        outages.append(sinr_db < cfg.sinr_threshold_db)

    unique, counts = np.unique(alloc.resources, return_counts=True)
    collisions = int(np.sum(np.maximum(counts - 1, 0)))
    return {
        "seed": seed,
        "n_uavs": n_uavs,
        "n_resources": n_resources,
        "algorithm": algorithm,
        "mean_sinr_db": float(np.mean(sinrs)),
        "median_sinr_db": float(np.median(sinrs)),
        "outage_proxy": float(np.mean(outages)),
        "resource_reuse_excess_links": collisions,
    }


def main() -> None:
    rows = []
    for n in SWARM_SIZES:
        for r in N_RESOURCES:
            for seed in range(N_SEEDS):
                rows.append(evaluate(seed, n, r, "random"))
                rows.append(evaluate(seed, n, r, "greedy"))
    raw = pd.DataFrame(rows)
    out = Path("results/resource_allocation")
    figs = Path("figures/resource_allocation")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "raw.csv", index=False)

    summary = raw.groupby(["n_uavs", "n_resources", "algorithm"], as_index=False).agg(
        mean_sinr_db=("mean_sinr_db", "mean"),
        std_sinr_db=("mean_sinr_db", "std"),
        mean_outage_proxy=("outage_proxy", "mean"),
        mean_resource_reuse_excess_links=("resource_reuse_excess_links", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)

    for n in SWARM_SIZES:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        subset = summary[summary.n_uavs == n]
        for algorithm, group in subset.groupby("algorithm"):
            ax.plot(group.n_resources, group.mean_sinr_db, marker="o", label=algorithm)
        ax.set_xlabel("Number of abstract sidelink resources")
        ax.set_ylabel("Mean SINR [dB]")
        ax.set_title(f"Resource allocation comparison — N={n} UAVs")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(figs / f"sinr_resources_n{n}.png", dpi=300)
        fig.savefig(figs / f"sinr_resources_n{n}.pdf")
        plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

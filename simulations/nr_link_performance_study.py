"""Sourced-BLER NR link-performance density study.

Scope: bundled verified 5G-LENA Table-1 BG1/CBS4096 MCS4/5/6 subset plus the
measurement-derived A2A propagation model. BLER is LINK_LEVEL_SIMULATION;
system outputs are DERIVED, not measured PDR/throughput.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import summarize
from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.swarm_system import SwarmConfig, simulate_snapshot

N_VALUES = [5, 10, 20, 30, 50, 75, 100]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    n_values = [5, 20, 50] if args.smoke else N_VALUES
    seeds = range(3 if args.smoke else args.seeds)

    curves = load_bler_curves(
        "data/reference/5glena_table1_bg1_cbs4096_subset.csv",
        source="5G-LENA verified Table1 BG1 CBS4096 MCS4/5/6 subset",
    )
    available = curves_for_cbs(curves, code_block_size=4096, base_graph=1)

    rows: list[dict[str, float | int]] = []
    for n_uavs in n_values:
        for seed in seeds:
            cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a", carrier_ghz=3.5, bandwidth_mhz=50.0, tx_power_dbm=30.0)
            _, links = simulate_snapshot(cfg)
            for link in links.itertuples(index=False):
                choice = select_max_goodput_mcs(float(link.sinr_db), available, cfg.bandwidth_mhz)
                if choice is None:
                    continue
                rows.append({
                    "n_uavs": n_uavs,
                    "seed": seed,
                    "link_id": int(link.link_id),
                    "sinr_db": float(link.sinr_db),
                    "selected_mcs": choice.mcs_index,
                    "bler": choice.bler,
                    "first_tx_success_probability": choice.first_tx_success_probability,
                    "expected_phy_goodput_mbps": choice.expected_phy_goodput_mbps,
                })

    df = pd.DataFrame(rows)
    out = Path("results/nr_link_performance")
    figs = Path("figures/nr_link_performance")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_link.csv", index=False)

    per_seed = df.groupby(["n_uavs", "seed"], as_index=False).agg(
        mean_sinr_db=("sinr_db", "mean"),
        mean_bler=("bler", "mean"),
        mean_first_tx_success_probability=("first_tx_success_probability", "mean"),
        mean_expected_phy_goodput_mbps=("expected_phy_goodput_mbps", "mean"),
        median_selected_mcs=("selected_mcs", "median"),
    )
    per_seed.to_csv(out / "per_seed.csv", index=False)

    summary_rows = []
    for n, group in per_seed.groupby("n_uavs"):
        row: dict[str, float | int] = {"n_uavs": int(n), "seeds": int(group.seed.nunique())}
        for metric in ["mean_sinr_db", "mean_bler", "mean_first_tx_success_probability", "mean_expected_phy_goodput_mbps", "median_selected_mcs"]:
            for key, value in summarize(group[metric]).items():
                row[f"{metric}_{key}"] = value
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    for metric, ylabel, stem, ylim in [
        ("mean_bler", "Mean BLER", "bler_vs_density", (0.0, 1.0)),
        ("mean_first_tx_success_probability", "Mean first-TX success probability", "success_vs_density", (0.0, 1.0)),
        ("mean_expected_phy_goodput_mbps", "Mean expected PHY goodput [Mbps]", "goodput_vs_density", None),
        ("median_selected_mcs", "Median selected MCS index", "mcs_vs_density", None),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.plot(summary.n_uavs, summary[f"{metric}_mean"], marker="o")
        ax.fill_between(summary.n_uavs, summary[f"{metric}_ci95_low"], summary[f"{metric}_ci95_high"], alpha=0.15)
        ax.set_xlabel("Number of UAVs")
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_title(f"{ylabel} vs swarm size")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(figs / f"{stem}.png", dpi=300)
        fig.savefig(figs / f"{stem}.pdf")
        plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

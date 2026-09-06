"""Diagnose simulated link failures by interference regime.

Failure is defined here by an EXPERIMENTAL policy target on sourced-BLER-derived
first-transmission success probability, not by measured PDR.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.swarm_system import SwarmConfig, simulate_snapshot

N_VALUES = [10, 20, 30, 50, 75, 100]
SUCCESS_TARGET = 0.50  # EXPERIMENTAL policy threshold.
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"


def classify_reason(interference_to_noise: float, dominant_fraction: float) -> str:
    if interference_to_noise < 1.0:
        return "noise_limited"
    if dominant_fraction >= 0.5:
        return "dominant_interferer"
    return "aggregate_interference"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    n_values = [10, 50] if args.smoke else N_VALUES
    seeds = range(3 if args.smoke else args.seeds)
    curves = curves_for_cbs(
        load_bler_curves(BLER_CSV, source="5G-LENA verified Table1 BG1 CBS4096 subset"),
        4096,
        base_graph=1,
    )

    rows = []
    for n in n_values:
        for seed in seeds:
            _, links = simulate_snapshot(SwarmConfig(n_uavs=n, seed=seed))
            for link in links.itertuples(index=False):
                choice = select_max_goodput_mcs(float(link.sinr_db), curves, 50.0)
                success = choice.first_tx_success_probability if choice is not None else 0.0
                failed = success < SUCCESS_TARGET
                rows.append({
                    "n_uavs": n,
                    "seed": seed,
                    "link_id": int(link.link_id),
                    "distance_m": float(link.distance_m),
                    "rx_power_dbm": float(link.rx_power_dbm),
                    "strongest_interferer_dbm": float(link.strongest_interferer_dbm),
                    "interference_dbm": float(link.interference_dbm),
                    "noise_dbm": float(link.noise_dbm),
                    "sinr_db": float(link.sinr_db),
                    "dominant_interferer_fraction": float(link.dominant_interferer_fraction),
                    "interference_to_noise_linear": float(link.interference_to_noise_linear),
                    "first_tx_success_probability": success,
                    "failed": failed,
                    "failure_reason": classify_reason(float(link.interference_to_noise_linear), float(link.dominant_interferer_fraction)) if failed else "success",
                })

    raw = pd.DataFrame(rows)
    out = Path("results/failure_analysis")
    figs = Path("figures/failure_analysis")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "per_link.csv", index=False)

    counts = raw.groupby(["n_uavs", "failure_reason"]).size().rename("count").reset_index()
    totals = raw.groupby("n_uavs").size().rename("total").reset_index()
    summary = counts.merge(totals, on="n_uavs")
    summary["fraction"] = summary["count"] / summary["total"]
    summary["success_target"] = SUCCESS_TARGET
    summary["classification"] = "DERIVED_FAILURE_DIAGNOSTIC"
    summary.to_csv(out / "summary.csv", index=False)

    pivot = summary.pivot(index="n_uavs", columns="failure_reason", values="fraction").fillna(0.0)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    bottom = np.zeros(len(pivot))
    for column in ["noise_limited", "dominant_interferer", "aggregate_interference"]:
        if column not in pivot:
            continue
        values = pivot[column].to_numpy()
        ax.bar(pivot.index.astype(str), values, bottom=bottom, label=column.replace("_", " "))
        bottom += values
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Fraction of all evaluated links")
    ax.set_title("Failure mechanism decomposition")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "failure_reason_vs_density.png", dpi=300)
    fig.savefig(figs / "failure_reason_vs_density.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()

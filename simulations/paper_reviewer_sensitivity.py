"""Reviewer-facing sensitivity experiments for the publication operating envelope.

This module is deliberately separate from the primary operating-envelope grid.
It tests two major modelling choices that can otherwise confound interpretation:

1. resource-allocation policy: random reuse versus THIS_WORK weighted
   conflict-graph allocation under the same N/R/G geometry and link model;
2. transmitter/receiver pairing: deterministic sequential disjoint pairs versus
   nearest-neighbour disjoint pairs under the same N/R/G resource policy.

All outputs remain DERIVED_SYSTEM_LEVEL_METRIC. These are robustness checks, not
additional field measurements and not normative NR Sidelink procedures.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from simulations.paper_operating_envelope import (
    MAIN_ALLOCATOR_MODE,
    MAIN_PAIRING_MODE,
    snapshot,
    summarize_group,
)
from src.sidelink.adaptive_tb import load_preferred_bler_curves

ALLOCATOR_N_VALUES = [10, 50, 100]
ALLOCATOR_RESOURCE_COUNTS = [2, 4, 8]
ALLOCATOR_ADVANTAGES_DB = [0.0, 6.0]
ALLOCATOR_MODES = ["random", "weighted_conflict_graph"]

PAIRING_N_VALUES = [10, 50, 100]
PAIRING_CONFIGS = [(1, 0.0), (8, 6.0)]
PAIRING_MODES = ["sequential", "nearest_neighbor"]

METRICS = [
    "mean_desired_distance_m",
    "mean_sinr_db",
    "mean_first_tx_success",
    "mean_expected_goodput_mbps",
    "jain_goodput_fairness",
    "mean_n_cochannel_interferers",
    "failure_dominant_fraction",
    "failure_aggregate_fraction",
]


def _summarize(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    for keys, group in raw.groupby(group_cols, sort=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        base = dict(zip(group_cols, keys))
        rows.append({**base, **summarize_group(group, METRICS)})
    return pd.DataFrame(rows)


def run_allocator_sensitivity(curves, seeds, out: Path, figs: Path) -> None:
    rows: list[dict] = []
    for n in ALLOCATOR_N_VALUES:
        for r in ALLOCATOR_RESOURCE_COUNTS:
            for g in ALLOCATOR_ADVANTAGES_DB:
                for allocator in ALLOCATOR_MODES:
                    for seed in seeds:
                        metrics = snapshot(
                            seed,
                            n,
                            r,
                            g,
                            curves,
                            pairing_mode=MAIN_PAIRING_MODE,
                            allocator_mode=allocator,
                        )
                        rows.append({
                            "n_uavs": n,
                            "n_resources": r,
                            "directional_relative_advantage_db": g,
                            "seed": seed,
                            **metrics,
                        })

    raw = pd.DataFrame(rows)
    raw.to_csv(out / "allocator_per_seed.csv", index=False)
    summary = _summarize(
        raw,
        ["n_uavs", "n_resources", "directional_relative_advantage_db", "allocator_mode"],
    )
    summary.to_csv(out / "allocator_summary.csv", index=False)

    nmax = max(ALLOCATOR_N_VALUES)
    q = summary[
        (summary.n_uavs == nmax)
        & (summary.directional_relative_advantage_db == 0.0)
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for allocator, group in q.groupby("allocator_mode"):
        group = group.sort_values("n_resources")
        ax.plot(
            group.n_resources,
            group.mean_first_tx_success,
            marker="o",
            label=allocator,
        )
    ax.set_xlabel("Orthogonal frequency resources")
    ax.set_ylabel("Mean first-TX success")
    ax.set_title(f"Allocator sensitivity at N={nmax}, G=0 dB")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "allocator_success_n100.pdf")
    fig.savefig(figs / "allocator_success_n100.png", dpi=300)
    plt.close(fig)


def run_pairing_sensitivity(curves, seeds, out: Path, figs: Path) -> None:
    rows: list[dict] = []
    for n in PAIRING_N_VALUES:
        for r, g in PAIRING_CONFIGS:
            for pairing in PAIRING_MODES:
                for seed in seeds:
                    metrics = snapshot(
                        seed,
                        n,
                        r,
                        g,
                        curves,
                        pairing_mode=pairing,
                        allocator_mode=MAIN_ALLOCATOR_MODE,
                    )
                    rows.append({
                        "n_uavs": n,
                        "n_resources": r,
                        "directional_relative_advantage_db": g,
                        "seed": seed,
                        **metrics,
                    })

    raw = pd.DataFrame(rows)
    raw.to_csv(out / "pairing_per_seed.csv", index=False)
    summary = _summarize(
        raw,
        ["n_uavs", "n_resources", "directional_relative_advantage_db", "pairing_mode"],
    )
    summary.to_csv(out / "pairing_summary.csv", index=False)

    q = summary[
        (summary.n_resources == 1)
        & (summary.directional_relative_advantage_db == 0.0)
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for pairing, group in q.groupby("pairing_mode"):
        group = group.sort_values("n_uavs")
        ax.plot(
            group.n_uavs,
            group.mean_first_tx_success,
            marker="o",
            label=pairing,
        )
    ax.set_xlabel("UAVs")
    ax.set_ylabel("Mean first-TX success")
    ax.set_title("Pairing sensitivity for the shared-resource baseline")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "pairing_success_baseline.pdf")
    fig.savefig(figs / "pairing_success_baseline.png", dpi=300)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--require-full-curves", action="store_true")
    args = parser.parse_args()

    curves, curve_mode = load_preferred_bler_curves()
    if args.require_full_curves and curve_mode != "FULL_5GLENA_V5_LOCAL":
        raise RuntimeError("reviewer sensitivity requires official 5G-LENA v5.0 full Table-1 curves")

    seeds = range(2 if args.smoke else args.seeds)
    out = Path("results/paper_reviewer_sensitivity")
    figs = Path("figures/paper_reviewer_sensitivity")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    run_allocator_sensitivity(curves, seeds, out, figs)
    run_pairing_sensitivity(curves, seeds, out, figs)

    metadata = pd.DataFrame([{
        "curve_mode": curve_mode,
        "allocator_n_values": ",".join(map(str, ALLOCATOR_N_VALUES)),
        "allocator_resource_counts": ",".join(map(str, ALLOCATOR_RESOURCE_COUNTS)),
        "allocator_advantages_db": ",".join(map(str, ALLOCATOR_ADVANTAGES_DB)),
        "allocator_modes": ",".join(ALLOCATOR_MODES),
        "pairing_n_values": ",".join(map(str, PAIRING_N_VALUES)),
        "pairing_configs": ";".join(f"R={r},G={g:g}" for r, g in PAIRING_CONFIGS),
        "pairing_modes": ",".join(PAIRING_MODES),
        "classification": "DERIVED_SYSTEM_LEVEL_REVIEWER_SENSITIVITY",
    }])
    metadata.to_csv(out / "design.csv", index=False)


if __name__ == "__main__":
    main()

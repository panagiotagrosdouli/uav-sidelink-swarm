"""Matched-seed effect-size analysis for selected algorithm comparisons."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.statistical_tests import paired_comparison


def _compare_resource_allocation(rows: list[dict]) -> None:
    path = Path("results/resource_allocation/raw.csv")
    if not path.exists():
        return
    df = pd.read_csv(path)
    for (n, r), group in df.groupby(["n_uavs", "n_resources"]):
        pivot = group.pivot(index="seed", columns="algorithm", values="mean_expected_phy_goodput_mbps")
        if {"random", "greedy"}.issubset(pivot.columns):
            comp = paired_comparison(pivot.random.to_numpy(), pivot.greedy.to_numpy())
            rows.append({"experiment": "resource_allocation", "n_uavs": n, "setting": f"resources={r}", "baseline": "random", "treatment": "greedy", "metric": "mean_expected_phy_goodput_mbps", **comp.__dict__})
        if {"random", "graph"}.issubset(pivot.columns):
            comp = paired_comparison(pivot.random.to_numpy(), pivot.graph.to_numpy())
            rows.append({"experiment": "resource_allocation", "n_uavs": n, "setting": f"resources={r}", "baseline": "random", "treatment": "graph", "metric": "mean_expected_phy_goodput_mbps", **comp.__dict__})


def _compare_ablation(rows: list[dict]) -> None:
    path = Path("results/ablation/per_seed.csv")
    if not path.exists():
        return
    df = pd.read_csv(path)
    baseline_name = "baseline_fixed_mcs4_shared"
    combined_name = "combined_graph4_harq4_directional6"
    for n, group in df.groupby("n_uavs"):
        pivot = group.pivot(index="seed", columns="scenario", values="mean_goodput_mbps")
        if {baseline_name, combined_name}.issubset(pivot.columns):
            comp = paired_comparison(pivot[baseline_name].to_numpy(), pivot[combined_name].to_numpy())
            rows.append({"experiment": "ablation", "n_uavs": n, "setting": "combined_vs_baseline", "baseline": baseline_name, "treatment": combined_name, "metric": "mean_goodput_mbps", **comp.__dict__})


def main() -> None:
    rows: list[dict] = []
    _compare_resource_allocation(rows)
    _compare_ablation(rows)
    out = Path("results/statistics")
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "paired_effects.csv", index=False)
    print(df.to_string(index=False) if len(df) else "No matched result pairs available yet.")


if __name__ == "__main__":
    main()

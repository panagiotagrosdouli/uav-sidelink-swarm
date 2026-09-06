"""Descriptive scaling-law diagnostics for the density experiment.

This script consumes `scaling_geometry_activity_study` outputs. Candidate fits
are descriptive and are not asserted as physical laws solely from R².
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.scaling import fit_linear, fit_logarithmic, fit_power_law


def main() -> None:
    source = Path("results/scaling_geometry_activity/scaling_summary.csv")
    if not source.exists():
        raise FileNotFoundError("run simulations.scaling_geometry_activity_study first")
    summary = pd.read_csv(source)
    rows = []
    for family, group in summary[summary.metric == "mean_sinr_db"].groupby("family"):
        x = group.n_uavs.to_numpy(dtype=float)
        y = group["mean"].to_numpy(dtype=float)
        for fit in [fit_linear(x, y), fit_logarithmic(x, y)]:
            rows.append({
                "family": family,
                "metric": "mean_sinr_db",
                "model": fit.model,
                "coefficients": repr(fit.coefficients),
                "r2": fit.r2,
                "interpretation": "DESCRIPTIVE_FIT_ONLY",
            })
    for family, group in summary[summary.metric == "mean_interference_to_noise_linear"].groupby("family"):
        x = group.n_uavs.to_numpy(dtype=float)
        y = group["mean"].to_numpy(dtype=float)
        if (y > 0).all():
            fit = fit_power_law(x, y)
            rows.append({
                "family": family,
                "metric": "mean_interference_to_noise_linear",
                "model": fit.model,
                "coefficients": repr(fit.coefficients),
                "r2": fit.r2,
                "interpretation": "DESCRIPTIVE_FIT_ONLY",
            })
    out = Path("results/scaling_geometry_activity/scaling_fits.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()

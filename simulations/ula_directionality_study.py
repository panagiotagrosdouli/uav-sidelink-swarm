"""Simple physical ULA array-factor sensitivity experiment.

The experiment uses isotropic elements, uniform weights and half-wavelength
spacing. It is an array-factor study, not full NR MIMO/beam management.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.antenna.ula import ula_power_gain_db

N_ELEMENTS = [1, 2, 4, 8, 16]
ANGLES_DEG = np.linspace(-90.0, 90.0, 361)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    elements = [1, 4, 8] if args.smoke else N_ELEMENTS

    rows = []
    for n in elements:
        gains = ula_power_gain_db(ANGLES_DEG, 0.0, n)
        for angle, gain in zip(ANGLES_DEG, gains):
            rows.append({
                "n_elements": n,
                "steering_angle_deg": 0.0,
                "observation_angle_deg": angle,
                "array_power_gain_db": float(gain),
                "classification": "PHYSICAL_ARRAY_FACTOR_MODEL",
            })
    df = pd.DataFrame(rows)
    out = Path("results/ula_directionality")
    figs = Path("figures/ula_directionality")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "array_pattern.csv", index=False)

    summary = []
    for n, group in df.groupby("n_elements"):
        boresight = float(group.iloc[np.argmin(np.abs(group.observation_angle_deg))].array_power_gain_db)
        outside = group[np.abs(group.observation_angle_deg) >= 20.0]
        summary.append({
            "n_elements": n,
            "boresight_gain_db": boresight,
            "max_gain_outside_20deg_db": float(outside.array_power_gain_db.max()),
            "classification": "PHYSICAL_ARRAY_FACTOR_MODEL",
        })
    pd.DataFrame(summary).to_csv(out / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for n, group in df.groupby("n_elements"):
        ax.plot(group.observation_angle_deg, group.array_power_gain_db, label=f"N={n}")
    ax.set_xlabel("Observation angle from broadside [deg]")
    ax.set_ylabel("Array power gain [dB]")
    ax.set_ylim(-40, None)
    ax.set_title("Uniform linear array factor — broadside steering")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "ula_array_factor.png", dpi=300)
    fig.savefig(figs / "ula_array_factor.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()

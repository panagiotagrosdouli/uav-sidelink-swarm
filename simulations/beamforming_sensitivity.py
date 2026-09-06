"""Beamforming sensitivity study with explicit experimental gain assumptions.

This is NOT a full antenna-array or NR beam-management simulation. Tx/Rx gain
and interference suppression values are controlled EXPERIMENTAL_SWEEP inputs.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

GAIN_CASES_DB = [0.0, 3.0, 6.0, 9.0]
N_UAVS = 30
N_SEEDS = 100


def evaluate(seed: int, gain_db: float) -> dict[str, float]:
    cfg = SwarmConfig(n_uavs=N_UAVS, seed=seed, channel="measured_a2a")
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(N_UAVS)
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))

    # Sensitivity abstraction: desired link receives total directional gain,
    # while interference is unchanged. This isolates desired-signal gain only.
    gain_linear = 10.0 ** (gain_db / 10.0)
    sinrs = []
    for i, (tx, rx) in enumerate(pairs):
        signal_w, _, _ = received_power_w(tx, rx, positions, cfg)
        signal_w *= gain_linear
        interference_w = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if i == j:
                continue
            p_i, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interference_w += p_i
        sinrs.append(10.0 * np.log10(signal_w / (noise_w + interference_w)))
    return {
        "seed": seed,
        "directional_gain_db": gain_db,
        "mean_sinr_db": float(np.mean(sinrs)),
        "outage_proxy": float(np.mean(np.asarray(sinrs) < cfg.sinr_threshold_db)),
    }


def main() -> None:
    rows = [evaluate(seed, gain) for gain in GAIN_CASES_DB for seed in range(N_SEEDS)]
    raw = pd.DataFrame(rows)
    out = Path("results/beamforming_sensitivity")
    figs = Path("figures/beamforming")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "raw.csv", index=False)
    summary = raw.groupby("directional_gain_db", as_index=False).agg(
        mean_sinr_db=("mean_sinr_db", "mean"),
        std_sinr_db=("mean_sinr_db", "std"),
        mean_outage_proxy=("outage_proxy", "mean"),
    )
    summary.to_csv(out / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(summary.directional_gain_db, summary.mean_sinr_db, marker="o")
    ax.set_xlabel("Assumed desired-link directional gain [dB]")
    ax.set_ylabel("Mean SINR [dB]")
    ax.set_title("Beamforming gain sensitivity — N=30 UAVs")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figs / "sinr_vs_directional_gain.png", dpi=300)
    fig.savefig(figs / "sinr_vs_directional_gain.pdf")
    plt.close(fig)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

"""Directional-gain sensitivity with desired gain and interference suppression.

This is NOT a full antenna-array/MIMO/NR beam-management simulation. Gains are
controlled EXPERIMENTAL_SWEEP inputs. BLER/goodput use the verified 5G-LENA
MCS4/5/6 BG1/CBS4096 fixture and remain link-level-simulation derived.
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
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

GAIN_CASES_DB = [0.0, 3.0, 6.0, 9.0]
MODES = ["desired_only", "suppression_only", "combined"]
N_UAVS = 30
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"


def _curves():
    curves = load_bler_curves(BLER_CSV, source="5G-LENA verified Table1 BG1 CBS4096 subset")
    return curves_for_cbs(curves, 4096, base_graph=1)


def evaluate(seed: int, gain_db: float, mode: str, n_uavs: int = N_UAVS) -> dict[str, float | int | str]:
    if mode not in MODES:
        raise ValueError(mode)
    cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a")
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(n_uavs)
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))

    desired_gain_linear = 10.0 ** (gain_db / 10.0) if mode in {"desired_only", "combined"} else 1.0
    suppression_linear = 10.0 ** (gain_db / 10.0) if mode in {"suppression_only", "combined"} else 1.0
    curves = _curves()
    sinrs: list[float] = []
    goodputs: list[float] = []
    successes: list[float] = []
    for i, (tx, rx) in enumerate(pairs):
        signal_w, _, _ = received_power_w(tx, rx, positions, cfg)
        signal_w *= desired_gain_linear
        interference_w = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if i == j:
                continue
            p_i, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interference_w += p_i / suppression_linear
        sinr_db = 10.0 * np.log10(signal_w / (noise_w + interference_w))
        sinrs.append(float(sinr_db))
        choice = select_max_goodput_mcs(float(sinr_db), curves, cfg.bandwidth_mhz)
        if choice is None:
            goodputs.append(0.0)
            successes.append(0.0)
        else:
            goodputs.append(choice.expected_phy_goodput_mbps)
            successes.append(choice.first_tx_success_probability)
    return {
        "seed": seed,
        "n_uavs": n_uavs,
        "mode": mode,
        "gain_or_suppression_db": gain_db,
        "mean_sinr_db": float(np.mean(sinrs)),
        "mean_expected_phy_goodput_mbps": float(np.mean(goodputs)),
        "mean_first_tx_success_probability": float(np.mean(successes)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    seeds = range(3 if args.smoke else args.seeds)
    gains = [0.0, 6.0] if args.smoke else GAIN_CASES_DB

    rows = [evaluate(seed, gain, mode) for mode in MODES for gain in gains for seed in seeds]
    raw = pd.DataFrame(rows)
    out = Path("results/beamforming_sensitivity")
    figs = Path("figures/beamforming")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "raw.csv", index=False)

    summary_rows = []
    for (mode, gain), group in raw.groupby(["mode", "gain_or_suppression_db"]):
        row: dict[str, float | int | str] = {"mode": mode, "gain_or_suppression_db": gain}
        for metric in ["mean_sinr_db", "mean_expected_phy_goodput_mbps", "mean_first_tx_success_probability"]:
            stats = summarize(group[metric])
            for k, v in stats.items():
                row[f"{metric}_{k}"] = v
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    for metric, ylabel, stem in [
        ("mean_sinr_db_mean", "Mean SINR [dB]", "sinr"),
        ("mean_expected_phy_goodput_mbps_mean", "Expected PHY goodput [Mbps]", "goodput"),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for mode, group in summary.groupby("mode"):
            ax.plot(group.gain_or_suppression_db, group[metric], marker="o", label=mode.replace("_", " "))
        ax.set_xlabel("Directional gain / interference suppression [dB]")
        ax.set_ylabel(ylabel)
        ax.set_title("Directional-gain sensitivity — N=30 UAVs")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(figs / f"{stem}_vs_directionality.png", dpi=300)
        fig.savefig(figs / f"{stem}_vs_directionality.pdf")
        plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

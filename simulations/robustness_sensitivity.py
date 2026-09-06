"""Robustness/sensitivity campaign for uncertain system assumptions.

The study separates STANDARD/LITERATURE-backed channel mechanics from explicit
EXPERIMENTAL_SWEEP choices. It does not infer a universal receiver NF, Tx power,
altitude or swarm area.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.channel_models.tr38901_a2a import equal_height_umi_av_shadow_sigma_db
from src.metrics import summarize
from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    dbm_to_w,
    generate_equal_altitude_positions,
    path_loss_for_link,
    thermal_noise_dbm,
)

CHANNELS = ["free_space", "measured_a2a", "tr38901_umi_av_los"]
NOISE_FIGURES_DB = [3.0, 5.0, 7.0, 9.0, 12.0]
TX_POWERS_DBM = [10.0, 20.0, 23.0, 30.0]
AREAS_M = [500.0, 1000.0, 1500.0, 2000.0]
ALTITUDES_M = [30.0, 50.0, 100.0, 150.0, 250.0]
N_UAVS = 30


def _snapshot_metrics(cfg: SwarmConfig, shadow_fading: bool = False) -> dict[str, float | str | int | bool]:
    rng = np.random.default_rng(cfg.seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(cfg.n_uavs)
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    sigma_db = None
    if shadow_fading:
        if cfg.channel != "tr38901_umi_av_los":
            raise ValueError("shadow fading is enabled only for the sourced 3GPP UMi-AV model")
        sigma_db = equal_height_umi_av_shadow_sigma_db(cfg.altitude_m, los=True)

    sinrs = []
    desired_dbm = []
    aggregate_i_dbm = []
    strongest_fraction = []
    for link_id, (tx, rx) in enumerate(pairs):
        distance = max(float(np.linalg.norm(positions[tx] - positions[rx])), 1e-6)
        pl = path_loss_for_link(distance, cfg)
        desired_shadow = rng.normal(0.0, sigma_db) if sigma_db is not None else 0.0
        s_dbm = cfg.tx_power_dbm - pl + desired_shadow
        s_w = float(dbm_to_w(s_dbm))
        interferers = []
        for other_id, (other_tx, _) in enumerate(pairs):
            if other_id == link_id:
                continue
            d_i = max(float(np.linalg.norm(positions[other_tx] - positions[rx])), 1e-6)
            pl_i = path_loss_for_link(d_i, cfg)
            shadow_i = rng.normal(0.0, sigma_db) if sigma_db is not None else 0.0
            interferers.append(float(dbm_to_w(cfg.tx_power_dbm - pl_i + shadow_i)))
        i_w = float(np.sum(interferers)) if interferers else 0.0
        sinrs.append(10.0 * np.log10(s_w / (i_w + noise_w)))
        desired_dbm.append(s_dbm)
        aggregate_i_dbm.append(10.0 * np.log10(i_w) + 30.0 if i_w > 0 else -np.inf)
        strongest_fraction.append(max(interferers, default=0.0) / i_w if i_w > 0 else 0.0)

    finite_i = np.asarray([v for v in aggregate_i_dbm if np.isfinite(v)], dtype=float)
    return {
        "seed": cfg.seed,
        "n_uavs": cfg.n_uavs,
        "channel": cfg.channel,
        "noise_figure_db": cfg.noise_figure_db,
        "tx_power_dbm": cfg.tx_power_dbm,
        "area_xy_m": cfg.area_xy_m,
        "altitude_m": cfg.altitude_m,
        "shadow_fading": shadow_fading,
        "shadow_sigma_db": sigma_db if sigma_db is not None else 0.0,
        "mean_sinr_db": float(np.mean(sinrs)),
        "median_sinr_db": float(np.median(sinrs)),
        "mean_desired_rx_power_dbm": float(np.mean(desired_dbm)),
        "mean_interference_dbm": float(np.mean(finite_i)) if finite_i.size else -np.inf,
        "mean_dominant_interferer_fraction": float(np.mean(strongest_fraction)),
    }


def _summary(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for key, group in raw.groupby(group_cols, sort=True):
        key = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key))
        for metric in ["mean_sinr_db", "mean_desired_rx_power_dbm", "mean_dominant_interferer_fraction"]:
            stats = summarize(group[metric])
            rows.append({**base, "metric": metric, **stats})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    seeds = range(3 if args.smoke else args.seeds)

    out = Path("results/robustness")
    figs = Path("figures/robustness")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    rows = []
    channels = ["measured_a2a", "tr38901_umi_av_los"] if args.smoke else CHANNELS
    for channel in channels:
        for seed in seeds:
            rows.append(_snapshot_metrics(SwarmConfig(N_UAVS, seed, channel=channel)))
    channel_df = pd.DataFrame(rows)
    channel_df.to_csv(out / "channel_per_seed.csv", index=False)
    _summary(channel_df, ["channel"]).to_csv(out / "channel_summary.csv", index=False)

    nf_values = [3.0, 9.0] if args.smoke else NOISE_FIGURES_DB
    nf_rows = [_snapshot_metrics(SwarmConfig(N_UAVS, seed, noise_figure_db=nf)) for nf in nf_values for seed in seeds]
    nf_df = pd.DataFrame(nf_rows)
    nf_df.to_csv(out / "noise_figure_per_seed.csv", index=False)
    _summary(nf_df, ["noise_figure_db"]).to_csv(out / "noise_figure_summary.csv", index=False)

    power_values = [20.0, 30.0] if args.smoke else TX_POWERS_DBM
    power_rows = [_snapshot_metrics(SwarmConfig(N_UAVS, seed, tx_power_dbm=p)) for p in power_values for seed in seeds]
    power_df = pd.DataFrame(power_rows)
    power_df.to_csv(out / "tx_power_per_seed.csv", index=False)
    power_summary = _summary(power_df, ["tx_power_dbm"])
    power_summary.to_csv(out / "tx_power_summary.csv", index=False)

    area_values = [500.0, 1500.0] if args.smoke else AREAS_M
    area_rows = [_snapshot_metrics(SwarmConfig(N_UAVS, seed, area_xy_m=a)) for a in area_values for seed in seeds]
    area_df = pd.DataFrame(area_rows)
    area_df.to_csv(out / "area_per_seed.csv", index=False)
    _summary(area_df, ["area_xy_m"]).to_csv(out / "area_summary.csv", index=False)

    altitude_values = [50.0, 150.0] if args.smoke else ALTITUDES_M
    altitude_rows = [
        _snapshot_metrics(SwarmConfig(N_UAVS, seed, channel="tr38901_umi_av_los", altitude_m=h))
        for h in altitude_values for seed in seeds
    ]
    altitude_df = pd.DataFrame(altitude_rows)
    altitude_df.to_csv(out / "altitude_per_seed.csv", index=False)
    _summary(altitude_df, ["altitude_m"]).to_csv(out / "altitude_summary.csv", index=False)

    shadow_rows = []
    for shadow in (False, True):
        for seed in seeds:
            shadow_rows.append(_snapshot_metrics(SwarmConfig(N_UAVS, seed, channel="tr38901_umi_av_los", altitude_m=100.0), shadow_fading=shadow))
    shadow_df = pd.DataFrame(shadow_rows)
    shadow_df.to_csv(out / "shadow_fading_per_seed.csv", index=False)
    _summary(shadow_df, ["shadow_fading"]).to_csv(out / "shadow_fading_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    p = power_summary[power_summary.metric == "mean_sinr_db"]
    ax.plot(p.tx_power_dbm, p["mean"], marker="o")
    ax.fill_between(p.tx_power_dbm, p.ci95_low, p.ci95_high, alpha=0.15)
    ax.set_xlabel("Transmit power [dBm]")
    ax.set_ylabel("Mean SINR [dB]")
    ax.set_title("Transmit-power sensitivity in a reused-resource swarm")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figs / "tx_power_sinr.png", dpi=300)
    fig.savefig(figs / "tx_power_sinr.pdf")
    plt.close(fig)

    print(power_summary.to_string(index=False))


if __name__ == "__main__":
    main()

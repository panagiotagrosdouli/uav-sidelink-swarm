"""Common system-level UAV swarm simulator with pluggable large-scale channels.

This is not a bit-accurate NR sidelink PHY. It is a reproducible system-level
interference simulator used to compare propagation assumptions while keeping
traffic, geometry and power accounting identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from src.channel_models.free_space import path_loss_db as fspl_path_loss_db
from src.channel_models.measured_a2a import path_loss_db as measured_a2a_path_loss_db
from src.channel_models.tr38901_a2a import umi_av_los_path_loss_db

K_B = 1.380649e-23
T0_K = 290.0

ChannelName = Literal["measured_a2a", "free_space", "tr38901_umi_av_los"]


def dbm_to_w(dbm: float | np.ndarray) -> np.ndarray:
    return 10.0 ** ((np.asarray(dbm, dtype=float) - 30.0) / 10.0)


def w_to_dbm(w: float | np.ndarray) -> np.ndarray:
    arr = np.asarray(w, dtype=float)
    return 10.0 * np.log10(arr) + 30.0


def thermal_noise_dbm(bandwidth_hz: float, noise_figure_db: float) -> float:
    return float(w_to_dbm(K_B * T0_K * bandwidth_hz) + noise_figure_db)


@dataclass(frozen=True)
class SwarmConfig:
    n_uavs: int
    seed: int
    channel: ChannelName = "measured_a2a"
    area_xy_m: float = 1000.0
    altitude_m: float = 100.0
    carrier_ghz: float = 3.5
    bandwidth_mhz: float = 50.0
    tx_power_dbm: float = 30.0
    noise_figure_db: float = 7.0
    sinr_threshold_db: float = 5.0
    activity_probability: float = 1.0


def generate_equal_altitude_positions(cfg: SwarmConfig, rng: np.random.Generator) -> np.ndarray:
    xy = rng.uniform(0.0, cfg.area_xy_m, size=(cfg.n_uavs, 2))
    z = np.full((cfg.n_uavs, 1), cfg.altitude_m)
    return np.hstack([xy, z])


def path_loss_for_link(distance_m: float, cfg: SwarmConfig) -> float:
    if cfg.channel == "measured_a2a":
        return float(measured_a2a_path_loss_db(distance_m))
    if cfg.channel == "free_space":
        return float(fspl_path_loss_db(distance_m, cfg.carrier_ghz * 1e9))
    if cfg.channel == "tr38901_umi_av_los":
        return float(umi_av_los_path_loss_db(distance_m, cfg.altitude_m, cfg.carrier_ghz))
    raise ValueError(f"unknown channel {cfg.channel}")


def received_power_w(tx: int, rx: int, positions: np.ndarray, cfg: SwarmConfig) -> tuple[float, float, float]:
    d = float(np.linalg.norm(positions[tx] - positions[rx]))
    if d <= 0:
        d = 1e-6
    pl_db = path_loss_for_link(d, cfg)
    pr_dbm = cfg.tx_power_dbm - pl_db
    return float(dbm_to_w(pr_dbm)), d, pl_db


def simulate_snapshot(cfg: SwarmConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    if cfg.n_uavs < 2:
        raise ValueError("n_uavs must be at least 2")
    rng = np.random.default_rng(cfg.seed)
    pos = generate_equal_altitude_positions(cfg, rng)
    noise_dbm = thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)
    noise_w = float(dbm_to_w(noise_dbm))

    desired = [(i, (i + 1) % cfg.n_uavs) for i in range(cfg.n_uavs)]
    active = rng.random(cfg.n_uavs) < cfg.activity_probability
    if not np.any(active):
        active[rng.integers(0, cfg.n_uavs)] = True

    rows: list[dict[str, float | int | bool | str]] = []
    for link_id, (tx, rx) in enumerate(desired):
        if not active[link_id]:
            continue
        signal_w, d_m, pl_db = received_power_w(tx, rx, pos, cfg)
        interference_w = 0.0
        n_interferers = 0
        for other_id, (other_tx, _) in enumerate(desired):
            if other_id == link_id or not active[other_id]:
                continue
            p_i_w, _, _ = received_power_w(other_tx, rx, pos, cfg)
            interference_w += p_i_w
            n_interferers += 1

        sir_linear = signal_w / interference_w if interference_w > 0 else np.inf
        sinr_linear = signal_w / (interference_w + noise_w)
        sinr_db = 10.0 * np.log10(sinr_linear)
        rows.append({
            "channel": cfg.channel,
            "seed": cfg.seed,
            "n_uavs": cfg.n_uavs,
            "link_id": link_id,
            "tx": tx,
            "rx": rx,
            "distance_m": d_m,
            "path_loss_db": pl_db,
            "rx_power_dbm": float(w_to_dbm(signal_w)),
            "interference_dbm": float(w_to_dbm(interference_w)) if interference_w > 0 else -np.inf,
            "noise_dbm": noise_dbm,
            "n_interferers": n_interferers,
            "sir_db": 10.0 * np.log10(sir_linear) if np.isfinite(sir_linear) else np.inf,
            "sinr_db": sinr_db,
            "outage_proxy": bool(sinr_db < cfg.sinr_threshold_db),
            "link_success_proxy": bool(sinr_db >= cfg.sinr_threshold_db),
            "shannon_upper_bound_mbps": cfg.bandwidth_mhz * np.log2(1.0 + sinr_linear),
        })

    positions = pd.DataFrame(pos, columns=["x_m", "y_m", "z_m"])
    positions.insert(0, "uav_id", np.arange(cfg.n_uavs))
    return positions, pd.DataFrame(rows)

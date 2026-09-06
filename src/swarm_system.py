"""Common system-level UAV swarm simulator with pluggable large-scale channels.

This is not a bit-accurate NR sidelink PHY. It is a reproducible system-level
interference simulator used to compare propagation, geometry and resource-reuse
assumptions while keeping power accounting explicit.
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
    if bandwidth_hz <= 0.0:
        raise ValueError("bandwidth_hz must be positive")
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


def received_power_w(
    tx: int,
    rx: int,
    positions: np.ndarray,
    cfg: SwarmConfig,
    *,
    extra_gain_db: float = 0.0,
    shadow_fading_db: float = 0.0,
) -> tuple[float, float, float]:
    d = float(np.linalg.norm(positions[tx] - positions[rx]))
    if d <= 0:
        d = 1e-6
    pl_db = path_loss_for_link(d, cfg)
    pr_dbm = cfg.tx_power_dbm - pl_db + float(extra_gain_db) - float(shadow_fading_db)
    return float(dbm_to_w(pr_dbm)), d, pl_db


def build_disjoint_pairs(n_uavs: int) -> list[tuple[int, int]]:
    """Return half-duplex-compatible disjoint Tx->Rx pairs."""
    return [(i, i + 1) for i in range(0, n_uavs - 1, 2)]


def _default_active_mask(cfg: SwarmConfig, rng: np.random.Generator, n_links: int) -> np.ndarray:
    active = rng.random(n_links) < cfg.activity_probability
    # Preserve at least one observation for finite Monte-Carlo summaries. This is
    # a simulator convenience, not a traffic-model claim.
    if n_links and not np.any(active):
        active[rng.integers(0, n_links)] = True
    return active


def simulate_positions(
    cfg: SwarmConfig,
    positions: np.ndarray,
    *,
    resources: np.ndarray | list[int] | None = None,
    active_mask: np.ndarray | list[bool] | None = None,
    desired_gain_db: float = 0.0,
    interference_suppression_db: float = 0.0,
    shadow_fading_std_db: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate one snapshot using explicit positions/resource assignments.

    ``resources`` are abstract orthogonal resource labels. Only co-resource
    transmitters interfere. They do not by themselves imply a particular time
    or frequency bandwidth split.

    ``desired_gain_db`` and ``interference_suppression_db`` are controlled
    DIRECTIONAL_GAIN_SENSITIVITY inputs, not a full MIMO/beam-management model.

    ``shadow_fading_std_db`` is an explicit stochastic input. Callers must only
    use a non-zero value when its provenance is valid for the selected channel.
    """
    if cfg.n_uavs < 2:
        raise ValueError("n_uavs must be at least 2")
    pos = np.asarray(positions, dtype=float)
    if pos.shape != (cfg.n_uavs, 3):
        raise ValueError(f"positions must have shape ({cfg.n_uavs},3)")
    if shadow_fading_std_db < 0.0:
        raise ValueError("shadow_fading_std_db must be non-negative")

    desired = build_disjoint_pairs(cfg.n_uavs)
    n_links = len(desired)
    if resources is None:
        resource_ids = np.zeros(n_links, dtype=int)
    else:
        resource_ids = np.asarray(resources, dtype=int)
        if resource_ids.shape != (n_links,):
            raise ValueError("resources must contain one resource id per disjoint link")
        if np.any(resource_ids < 0):
            raise ValueError("resource ids must be non-negative")

    if active_mask is None:
        active = _default_active_mask(cfg, np.random.default_rng(cfg.seed + 7919), n_links)
    else:
        active = np.asarray(active_mask, dtype=bool)
        if active.shape != (n_links,):
            raise ValueError("active_mask must contain one flag per disjoint link")

    noise_dbm = thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)
    noise_w = float(dbm_to_w(noise_dbm))

    if shadow_fading_std_db > 0.0:
        shadow_rng = np.random.default_rng(cfg.seed + 104729)
        shadow_matrix_db = shadow_rng.normal(
            0.0,
            shadow_fading_std_db,
            size=(cfg.n_uavs, cfg.n_uavs),
        )
    else:
        shadow_matrix_db = np.zeros((cfg.n_uavs, cfg.n_uavs), dtype=float)

    rows: list[dict[str, float | int | bool | str]] = []
    for link_id, (tx, rx) in enumerate(desired):
        if not active[link_id]:
            continue
        signal_w, d_m, pl_db = received_power_w(
            tx,
            rx,
            pos,
            cfg,
            extra_gain_db=desired_gain_db,
            shadow_fading_db=float(shadow_matrix_db[tx, rx]),
        )
        interference_w = 0.0
        strongest_interferer_w = 0.0
        n_interferers = 0
        for other_id, (other_tx, _) in enumerate(desired):
            if other_id == link_id or not active[other_id]:
                continue
            if resource_ids[other_id] != resource_ids[link_id]:
                continue
            p_i_w, _, _ = received_power_w(
                other_tx,
                rx,
                pos,
                cfg,
                extra_gain_db=-interference_suppression_db,
                shadow_fading_db=float(shadow_matrix_db[other_tx, rx]),
            )
            interference_w += p_i_w
            strongest_interferer_w = max(strongest_interferer_w, p_i_w)
            n_interferers += 1

        sir_linear = signal_w / interference_w if interference_w > 0 else np.inf
        sinr_linear = signal_w / (interference_w + noise_w)
        sinr_db = 10.0 * np.log10(sinr_linear)
        if interference_w <= noise_w:
            interference_regime = "noise_limited"
        elif strongest_interferer_w >= 0.5 * interference_w:
            interference_regime = "dominant_interferer"
        else:
            interference_regime = "aggregate_interference"

        rows.append(
            {
                "channel": cfg.channel,
                "seed": cfg.seed,
                "n_uavs": cfg.n_uavs,
                "link_id": link_id,
                "tx": tx,
                "rx": rx,
                "resource_id": int(resource_ids[link_id]),
                "distance_m": d_m,
                "path_loss_db": pl_db,
                "shadow_fading_db": float(shadow_matrix_db[tx, rx]),
                "desired_gain_db": float(desired_gain_db),
                "interference_suppression_db": float(interference_suppression_db),
                "rx_power_dbm": float(w_to_dbm(signal_w)),
                "interference_dbm": (
                    float(w_to_dbm(interference_w)) if interference_w > 0 else -np.inf
                ),
                "strongest_interferer_dbm": (
                    float(w_to_dbm(strongest_interferer_w))
                    if strongest_interferer_w > 0
                    else -np.inf
                ),
                "noise_dbm": noise_dbm,
                "n_interferers": n_interferers,
                "interference_regime": interference_regime,
                "sir_db": 10.0 * np.log10(sir_linear) if np.isfinite(sir_linear) else np.inf,
                "sinr_db": sinr_db,
                "outage_proxy": bool(sinr_db < cfg.sinr_threshold_db),
                "link_success_proxy": bool(sinr_db >= cfg.sinr_threshold_db),
                "shannon_upper_bound_mbps": cfg.bandwidth_mhz * np.log2(1.0 + sinr_linear),
            }
        )

    positions_df = pd.DataFrame(pos, columns=["x_m", "y_m", "z_m"])
    positions_df.insert(0, "uav_id", np.arange(cfg.n_uavs))
    return positions_df, pd.DataFrame(rows)


def simulate_snapshot(cfg: SwarmConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Backward-compatible uniform-random, single-resource snapshot."""
    if cfg.n_uavs < 2:
        raise ValueError("n_uavs must be at least 2")
    rng = np.random.default_rng(cfg.seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    active = _default_active_mask(cfg, rng, len(build_disjoint_pairs(cfg.n_uavs)))
    return simulate_positions(cfg, positions, active_mask=active)

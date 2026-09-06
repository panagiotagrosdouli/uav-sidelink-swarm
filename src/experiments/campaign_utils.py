"""Common helpers for the canonical multi-dimensional experimental campaign."""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.analysis.metrics import jains_fairness
from src.analysis.statistics import summarize
from src.experiments.system_evaluation import annotate_nr_link_metrics
from src.sidelink.link_performance import BlerCurve
from src.sidelink.resource_allocation import (
    graph_conflict_allocation,
    greedy_distance_aware_allocation,
    random_allocation,
)
from src.sidelink.resource_grid import SidelinkResourceGrid
from src.swarm_geometry import GeometryName, generate_positions
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, simulate_positions


def resources_for_algorithm(
    algorithm: str,
    positions: np.ndarray,
    n_resources: int,
    seed: int,
) -> np.ndarray:
    pairs = build_disjoint_pairs(len(positions))
    if n_resources < 1:
        raise ValueError("n_resources must be >= 1")
    if algorithm == "shared":
        return np.zeros(len(pairs), dtype=int)
    tx = np.asarray([positions[t] for t, _ in pairs], dtype=float)
    rx = np.asarray([positions[r] for _, r in pairs], dtype=float)
    if algorithm == "random":
        return random_allocation(len(pairs), n_resources, seed).resources
    if algorithm == "greedy":
        return greedy_distance_aware_allocation(tx, rx, n_resources).resources
    if algorithm == "graph":
        return graph_conflict_allocation(tx, rx, n_resources).resources
    raise ValueError(f"unknown resource algorithm {algorithm}")


def evaluate_snapshot(
    cfg: SwarmConfig,
    curves: dict[tuple[int, int, int], BlerCurve],
    grid: SidelinkResourceGrid,
    *,
    geometry: GeometryName = "uniform",
    positions: np.ndarray | None = None,
    n_resources: int = 1,
    resource_algorithm: str = "shared",
    active_mask: np.ndarray | list[bool] | None = None,
    desired_gain_db: float = 0.0,
    interference_suppression_db: float = 0.0,
    shadow_fading_std_db: float = 0.0,
    mcs_policy: str | int = "adaptive",
    harq_attempts: int = 1,
    feedback_gap_slots: int = 2,
) -> tuple[dict[str, float | int | str], pd.DataFrame, np.ndarray]:
    pos = (
        generate_positions(geometry, cfg.n_uavs, cfg.area_xy_m, cfg.altitude_m, cfg.seed)
        if positions is None
        else np.asarray(positions, dtype=float)
    )
    resources = resources_for_algorithm(resource_algorithm, pos, n_resources, cfg.seed)
    _, raw_links = simulate_positions(
        cfg,
        pos,
        resources=resources,
        active_mask=active_mask,
        desired_gain_db=desired_gain_db,
        interference_suppression_db=interference_suppression_db,
        shadow_fading_std_db=shadow_fading_std_db,
    )
    if raw_links.empty:
        row = {
            "seed": cfg.seed,
            "n_uavs": cfg.n_uavs,
            "area_xy_m": cfg.area_xy_m,
            "spatial_density_uavs_per_km2": cfg.n_uavs / (cfg.area_xy_m**2 / 1e6),
            "geometry": geometry,
            "channel": cfg.channel,
            "activity_probability": cfg.activity_probability,
            "n_resources": n_resources,
            "resource_algorithm": resource_algorithm,
            "active_links": 0,
            "mean_sinr_db": np.nan,
            "median_sinr_db": np.nan,
            "p05_sinr_db": np.nan,
            "mean_tb_bler": np.nan,
            "outage_bler_gt_0p1": np.nan,
            "mean_first_tx_goodput_mbps": 0.0,
            "mean_harq_goodput_mbps": 0.0,
            "mean_harq_latency_ms": np.nan,
            "goodput_fairness": np.nan,
            "mean_interference_w": 0.0,
            "dominant_interferer_fraction": 0.0,
            "aggregate_interference_fraction": 0.0,
            "noise_limited_fraction": 0.0,
        }
        return row, raw_links, pos

    links = annotate_nr_link_metrics(
        raw_links,
        curves,
        grid,
        mcs_policy=mcs_policy,
        harq_attempts=harq_attempts,
        feedback_and_retx_gap_slots=feedback_gap_slots,
    )
    sinr = links.sinr_db.to_numpy(dtype=float)
    bler = links.tb_bler.to_numpy(dtype=float)
    first_goodput = links.first_tx_goodput_mbps.to_numpy(dtype=float)
    harq_goodput = links.harq_goodput_mbps.to_numpy(dtype=float)
    latency = links.harq_latency_ms.to_numpy(dtype=float)
    finite_latency = latency[np.isfinite(latency)]
    interference_dbm = links.interference_dbm.to_numpy(dtype=float)
    interference_w = np.where(
        np.isfinite(interference_dbm),
        dbm_to_w(interference_dbm),
        0.0,
    )
    regimes = links.interference_regime.astype(str)
    row: dict[str, float | int | str] = {
        "seed": cfg.seed,
        "n_uavs": cfg.n_uavs,
        "area_xy_m": cfg.area_xy_m,
        "spatial_density_uavs_per_km2": cfg.n_uavs / (cfg.area_xy_m**2 / 1e6),
        "geometry": geometry,
        "channel": cfg.channel,
        "activity_probability": cfg.activity_probability,
        "n_resources": n_resources,
        "resource_algorithm": resource_algorithm,
        "active_links": len(links),
        "mean_sinr_db": float(np.mean(sinr)),
        "median_sinr_db": float(np.median(sinr)),
        "p05_sinr_db": float(np.percentile(sinr, 5.0)),
        "mean_tb_bler": float(np.nanmean(bler)),
        "outage_bler_gt_0p1": float(np.nanmean(bler > 0.1)),
        "mean_first_tx_goodput_mbps": float(np.nanmean(first_goodput)),
        "mean_harq_goodput_mbps": float(np.nanmean(harq_goodput)),
        "mean_harq_latency_ms": float(np.mean(finite_latency)) if len(finite_latency) else np.nan,
        "goodput_fairness": jains_fairness(np.nan_to_num(harq_goodput, nan=0.0)),
        "mean_interference_w": float(np.mean(interference_w)),
        "dominant_interferer_fraction": float(np.mean(regimes == "dominant_interferer")),
        "aggregate_interference_fraction": float(np.mean(regimes == "aggregate_interference")),
        "noise_limited_fraction": float(np.mean(regimes == "noise_limited")),
    }
    return row, links, pos


def summarize_groups(
    frame: pd.DataFrame,
    group_columns: list[str],
    metric_columns: Iterable[str],
) -> pd.DataFrame:
    """Summarize per-seed metrics with mean/median/std/p05/p95/CI95."""
    rows: list[dict[str, object]] = []
    for key, group in frame.groupby(group_columns, dropna=False, sort=True):
        keys = key if isinstance(key, tuple) else (key,)
        row: dict[str, object] = dict(zip(group_columns, keys))
        for metric in metric_columns:
            if metric not in group.columns:
                continue
            values = pd.to_numeric(group[metric], errors="coerce").to_numpy(dtype=float)
            finite = values[np.isfinite(values)]
            if len(finite) == 0:
                for suffix in ("mean", "median", "std", "p05", "p95", "ci95_low", "ci95_high"):
                    row[f"{metric}_{suffix}"] = np.nan
                continue
            stats = summarize(finite)
            for name, value in stats.items():
                if name == "n":
                    row[f"{metric}_n"] = value
                else:
                    row[f"{metric}_{name}"] = value
        rows.append(row)
    return pd.DataFrame(rows)

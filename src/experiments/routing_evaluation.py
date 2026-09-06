"""Connectivity/routing evaluation on isolated candidate links.

This module intentionally separates route-graph analysis from simultaneous
co-channel scheduling. Every candidate edge is evaluated as an isolated link
(no mutual interference), then routing composes those edge metrics. Therefore
outputs are CONNECTIVITY_ABSTRACTION / DERIVED_NETWORK_METRIC, not a scheduled
multi-hop NR network simulation.
"""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from src.experiments.system_evaluation import annotate_nr_link_metrics
from src.networking.routing import (
    build_graph,
    minimum_hop_path,
    path_metrics,
    quality_aware_path,
    reliability_aware_path,
)
from src.sidelink.link_performance import BlerCurve
from src.sidelink.resource_grid import SidelinkResourceGrid
from src.swarm_system import SwarmConfig, dbm_to_w, received_power_w, thermal_noise_dbm


def pairwise_isolated_links(
    cfg: SwarmConfig,
    positions: np.ndarray,
    curves: dict[tuple[int, int, int], BlerCurve],
    grid: SidelinkResourceGrid,
    *,
    harq_attempts: int = 1,
    feedback_and_retx_gap_slots: int = 2,
) -> pd.DataFrame:
    pos = np.asarray(positions, dtype=float)
    if pos.shape != (cfg.n_uavs, 3):
        raise ValueError("positions shape does not match cfg.n_uavs")
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    rows: list[dict[str, object]] = []
    for i in range(cfg.n_uavs):
        for j in range(i + 1, cfg.n_uavs):
            signal_w, distance_m, path_loss_db = received_power_w(i, j, pos, cfg)
            snr_linear = signal_w / noise_w
            rows.append(
                {
                    "tx": i,
                    "rx": j,
                    "distance_m": distance_m,
                    "path_loss_db": path_loss_db,
                    "sinr_db": 10.0 * np.log10(snr_linear),
                    "interference_model": "isolated_link_connectivity_abstraction",
                }
            )
    links = annotate_nr_link_metrics(
        pd.DataFrame(rows),
        curves,
        grid,
        mcs_policy="adaptive",
        harq_attempts=harq_attempts,
        feedback_and_retx_gap_slots=feedback_and_retx_gap_slots,
    )
    links["success_probability"] = links["harq_success_probability"]
    links["latency_ms"] = links["harq_latency_ms"]
    return links


def evaluate_source_target_routes(
    links: pd.DataFrame,
    source: int,
    target: int,
    *,
    minimum_success_probability: float = 0.9,
) -> pd.DataFrame:
    """Compare direct/min-hop/quality/reliability-aware routes."""
    graph = build_graph(
        links,
        minimum_sinr_db=-100.0,
        minimum_success_probability=minimum_success_probability,
    )
    route_functions = {
        "minimum_hop": minimum_hop_path,
        "quality_aware": quality_aware_path,
        "reliability_aware": reliability_aware_path,
    }
    rows: list[dict[str, object]] = []

    direct = links[((links.tx == source) & (links.rx == target)) | ((links.tx == target) & (links.rx == source))]
    if len(direct):
        d = direct.iloc[0]
        rows.append(
            {
                "method": "direct",
                "route_exists": bool(float(d.success_probability) >= minimum_success_probability),
                "hop_count": 1,
                "bottleneck_sinr_db": float(d.sinr_db),
                "route_success_probability": float(d.success_probability),
                "route_latency_ms": float(d.latency_ms),
                "path": f"{source}-{target}",
            }
        )

    for name, fn in route_functions.items():
        try:
            path = fn(graph, source, target)
            metrics = path_metrics(graph, path)
            rows.append(
                {
                    "method": name,
                    "route_exists": True,
                    **metrics,
                    "path": "-".join(str(x) for x in path),
                }
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            rows.append(
                {
                    "method": name,
                    "route_exists": False,
                    "hop_count": np.nan,
                    "bottleneck_sinr_db": np.nan,
                    "route_success_probability": 0.0,
                    "route_latency_ms": np.nan,
                    "path": "",
                }
            )
    return pd.DataFrame(rows)

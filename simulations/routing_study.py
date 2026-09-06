"""Graph-level multi-hop routing study using measurement-derived A2A path loss.

Link quality is computed as interference-free SNR for topology construction.
Routing results are therefore a connectivity abstraction, not a full NR network
routing protocol or end-to-end latency model.
"""
from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from src.networking.routing import build_graph, minimum_hop_path, path_bottleneck_sinr_db, quality_aware_path
from src.swarm_system import SwarmConfig, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

N_UAVS = 30
N_SEEDS = 100
MINIMUM_SINR_DB = 5.0


def all_pair_links(cfg: SwarmConfig, positions: np.ndarray) -> pd.DataFrame:
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    rows = []
    for i in range(cfg.n_uavs):
        for j in range(i + 1, cfg.n_uavs):
            signal_w, distance_m, path_loss_db = received_power_w(i, j, positions, cfg)
            snr_db = 10.0 * np.log10(signal_w / noise_w)
            rows.append({"tx": i, "rx": j, "distance_m": distance_m, "path_loss_db": path_loss_db, "sinr_db": snr_db})
    return pd.DataFrame(rows)


def main() -> None:
    rows = []
    for seed in range(N_SEEDS):
        cfg = SwarmConfig(n_uavs=N_UAVS, seed=seed, channel="measured_a2a")
        rng = np.random.default_rng(seed)
        positions = generate_equal_altitude_positions(cfg, rng)
        links = all_pair_links(cfg, positions)
        graph = build_graph(links, MINIMUM_SINR_DB)
        source, target = 0, N_UAVS - 1
        connected = nx.has_path(graph, source, target) if source in graph and target in graph else False
        row = {"seed": seed, "connected": connected, "graph_edges": graph.number_of_edges()}
        if connected:
            hop_path = minimum_hop_path(graph, source, target)
            quality_path = quality_aware_path(graph, source, target)
            row.update({
                "minimum_hop_count": len(hop_path) - 1,
                "minimum_hop_bottleneck_sinr_db": path_bottleneck_sinr_db(graph, hop_path),
                "quality_path_hop_count": len(quality_path) - 1,
                "quality_path_bottleneck_sinr_db": path_bottleneck_sinr_db(graph, quality_path),
            })
        rows.append(row)

    df = pd.DataFrame(rows)
    out = Path("results/routing")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_seed.csv", index=False)
    summary = pd.DataFrame([{
        "n_uavs": N_UAVS,
        "seeds": N_SEEDS,
        "minimum_link_snr_db": MINIMUM_SINR_DB,
        "source_target_connectivity_probability": float(df.connected.mean()),
        "mean_graph_edges": float(df.graph_edges.mean()),
        "mean_minimum_hops_when_connected": float(df.loc[df.connected, "minimum_hop_count"].mean()),
        "mean_quality_path_hops_when_connected": float(df.loc[df.connected, "quality_path_hop_count"].mean()),
    }])
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

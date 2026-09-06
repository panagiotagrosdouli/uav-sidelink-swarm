"""Cross-layer synthetic mobility experiment.

Evaluates constant-velocity, formation-preserving, random-waypoint and
leader-follower traces. Mobility is SYNTHETIC. RF/link/routing metrics are
system-level derived quantities using the measurement-derived channel and the
bundled limited 5G-LENA BLER fixture.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.mobility.synthetic import (
    constant_velocity_trace,
    formation_translation_trace,
    generate_positions,
    leader_follower_trace,
    random_waypoint_trace,
)
from src.networking.routing import build_graph, reliability_aware_path
from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, received_power_w, thermal_noise_dbm

MODES = ["constant_velocity", "formation_translation", "random_waypoint", "leader_follower"]
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"
ROUTE_SUCCESS_TARGET = 0.50  # EXPERIMENTAL policy target.


def _trace(mode: str, initial: np.ndarray, cfg: SwarmConfig, seed: int, duration: float, sample: float):
    rng = np.random.default_rng(seed + 1000)
    if mode == "constant_velocity":
        direction = rng.uniform(-1.0, 1.0, size=(cfg.n_uavs, 2))
        norm = np.linalg.norm(direction, axis=1)
        norm[norm == 0] = 1.0
        velocities = np.column_stack([3.0 * direction / norm[:, None], np.zeros(cfg.n_uavs)])
        return constant_velocity_trace(initial, velocities, duration, sample)
    if mode == "formation_translation":
        return formation_translation_trace(initial, (3.0, 1.0, 0.0), duration, sample)
    if mode == "random_waypoint":
        return random_waypoint_trace(initial, cfg.area_xy_m, 3.0, duration, sample, seed + 2000)
    if mode == "leader_follower":
        return leader_follower_trace(initial, (3.0, 1.0, 0.0), duration, sample)
    raise ValueError(mode)


def _direct_link_metrics(positions: np.ndarray, cfg: SwarmConfig, curves) -> list[dict[str, float | int]]:
    pairs = build_disjoint_pairs(cfg.n_uavs)
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    rows = []
    for i, (tx, rx) in enumerate(pairs):
        signal_w, distance, _ = received_power_w(tx, rx, positions, cfg)
        interference = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if i == j:
                continue
            p_i, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interference += p_i
        sinr_db = float(10.0 * np.log10(signal_w / (noise_w + interference)))
        choice = select_max_goodput_mcs(sinr_db, curves, cfg.bandwidth_mhz)
        rows.append({
            "link_id": i,
            "distance_m": distance,
            "sinr_db": sinr_db,
            "selected_mcs": choice.mcs_index if choice else -1,
            "bler": choice.bler if choice else 1.0,
            "success_probability": choice.first_tx_success_probability if choice else 0.0,
            "expected_goodput_mbps": choice.expected_phy_goodput_mbps if choice else 0.0,
        })
    return rows


def _route_signature(positions: np.ndarray, cfg: SwarmConfig, curves) -> tuple[str, bool]:
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    rows = []
    for i in range(cfg.n_uavs):
        for j in range(i + 1, cfg.n_uavs):
            signal_w, _, _ = received_power_w(i, j, positions, cfg)
            snr_db = float(10.0 * np.log10(signal_w / noise_w))
            choice = select_max_goodput_mcs(snr_db, curves, cfg.bandwidth_mhz)
            success = choice.first_tx_success_probability if choice else 0.0
            if success >= ROUTE_SUCCESS_TARGET:
                rows.append({"tx": i, "rx": j, "sinr_db": snr_db, "success_probability": success})
    graph = build_graph(pd.DataFrame(rows, columns=["tx", "rx", "sinr_db", "success_probability"]), minimum_sinr_db=-100.0)
    source, target = 0, cfg.n_uavs - 1
    if source not in graph or target not in graph or not nx.has_path(graph, source, target):
        return "unavailable", False
    path = reliability_aware_path(graph, source, target)
    return "-".join(str(x) for x in path), True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=20)
    args = parser.parse_args()
    seeds = range(2 if args.smoke else args.seeds)
    duration = 5.0 if args.smoke else 30.0
    sample = 1.0
    n_uavs = 10 if args.smoke else 20
    all_curves = load_bler_curves(BLER_CSV, source="5G-LENA verified MCS4/5/6 subset")
    curves = curves_for_cbs(all_curves, 4096, base_graph=1)

    rows = []
    route_rows = []
    for mode in MODES:
        for seed in seeds:
            cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, area_xy_m=1000.0)
            rng = np.random.default_rng(seed)
            geometry = "leader_follower" if mode == "leader_follower" else "uniform"
            initial = generate_positions(n_uavs, cfg.area_xy_m, cfg.altitude_m, rng, geometry=geometry)
            trace = _trace(mode, initial, cfg, seed, duration, sample)
            previous_route = None
            route_changes = 0
            for k, t in enumerate(trace.time_s):
                positions = trace.positions_m[k]
                direct = _direct_link_metrics(positions, cfg, curves)
                signature, connected = _route_signature(positions, cfg, curves)
                if previous_route is not None and signature != previous_route:
                    route_changes += 1
                previous_route = signature
                route_rows.append({"mode": mode, "seed": seed, "time_s": t, "route_signature": signature, "connected": connected, "route_changes_so_far": route_changes})
                for link in direct:
                    rows.append({"mode": mode, "seed": seed, "time_s": t, **link, "mobility_classification": "SYNTHETIC_MOBILITY"})

    direct_df = pd.DataFrame(rows)
    routes_df = pd.DataFrame(route_rows)
    out = Path("results/synthetic_mobility")
    figs = Path("figures/synthetic_mobility")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    direct_df.to_csv(out / "direct_links_time_series.csv", index=False)
    routes_df.to_csv(out / "route_time_series.csv", index=False)

    summary = direct_df.groupby("mode", as_index=False).agg(
        mean_distance_m=("distance_m", "mean"),
        mean_sinr_db=("sinr_db", "mean"),
        mean_bler=("bler", "mean"),
        mean_goodput_mbps=("expected_goodput_mbps", "mean"),
    )
    route_summary = routes_df.groupby("mode", as_index=False).agg(
        connectivity_fraction=("connected", "mean"),
        mean_final_route_changes=("route_changes_so_far", "max"),
    )
    summary = summary.merge(route_summary, on="mode")
    summary.to_csv(out / "summary.csv", index=False)

    example_seed = 0
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ex = direct_df[(direct_df.seed == example_seed) & (direct_df.link_id == 0)]
    for mode, group in ex.groupby("mode"):
        ax.plot(group.time_s, group.sinr_db, label=mode.replace("_", " "))
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Link-0 SINR [dB]")
    ax.set_title("Synthetic mobility: example link SINR evolution")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "sinr_vs_time.png", dpi=300)
    fig.savefig(figs / "sinr_vs_time.pdf")
    plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

"""Additional canonical studies required by the master experimental program.

Produces per-link MCS-density distributions, failure decomposition,
communication-energy tradeoffs and representative spatial topology maps.
All RF/network outputs are DERIVED system-level quantities.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.analysis.metrics import energy_per_delivered_bit_j
from src.experiments.campaign_utils import evaluate_snapshot
from src.experiments.routing_evaluation import pairwise_isolated_links
from src.networking.routing import build_graph, reliability_aware_path
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.swarm_geometry import generate_positions
from src.swarm_system import SwarmConfig


def run(curves_path: str | Path, output_dir: str | Path, figure_dir: str | Path, smoke: bool = False) -> None:
    curves = load_bler_curves(curves_path, source="5G-LENA Table-1 processed BLER curves")
    grid = thesis_profile_50mhz_30khz()
    out, figs = Path(output_dir), Path(figure_dir)
    out.mkdir(parents=True, exist_ok=True); figs.mkdir(parents=True, exist_ok=True)
    seeds = range(3 if smoke else 100)
    n_values = [5, 20, 50] if smoke else [5, 10, 20, 30, 50, 75, 100]

    # MCS distribution versus density + per-link failure decomposition.
    mcs_rows: list[dict[str, object]] = []
    failure_rows: list[dict[str, object]] = []
    for n in n_values:
        for seed in seeds:
            cfg = SwarmConfig(n_uavs=n, seed=seed, channel="measured_a2a", activity_probability=1.0)
            _, links, _ = evaluate_snapshot(cfg, curves, grid)
            for r in links.to_dict(orient="records"):
                mcs_rows.append({"n_uavs": n, "seed": seed, "link_id": r["link_id"], "sinr_db": r["sinr_db"], "selected_mcs": r["selected_mcs"], "tb_bler": r["tb_bler"], "tbs_bits": r["tbs_bits"], "goodput_mbps": r["harq_goodput_mbps"]})
                if np.isfinite(float(r["tb_bler"])) and float(r["tb_bler"]) > 0.1:
                    failure_rows.append({
                        "n_uavs": n, "seed": seed, "link_id": r["link_id"], "distance_m": r["distance_m"],
                        "rx_power_dbm": r["rx_power_dbm"], "strongest_interferer_dbm": r["strongest_interferer_dbm"],
                        "aggregate_interference_dbm": r["interference_dbm"], "noise_dbm": r["noise_dbm"],
                        "n_interferers": r["n_interferers"], "interference_regime": r["interference_regime"],
                        "resource_id": r["resource_id"], "sinr_db": r["sinr_db"], "selected_mcs": r["selected_mcs"],
                        "tb_bler": r["tb_bler"], "goodput_mbps": r["harq_goodput_mbps"],
                        "classification": "DERIVED_FAILURE_ANALYSIS",
                    })
    mcs_df = pd.DataFrame(mcs_rows); fail_df = pd.DataFrame(failure_rows)
    mcs_df.to_csv(out / "mcs_density_per_link.csv", index=False)
    fail_df.to_csv(out / "failure_decomposition_per_link.csv", index=False)
    if not mcs_df.empty:
        mcs_summary = mcs_df.groupby("n_uavs", as_index=False).agg(mean_selected_mcs=("selected_mcs", "mean"), median_selected_mcs=("selected_mcs", "median"), p05_selected_mcs=("selected_mcs", lambda x: np.nanpercentile(x, 5)), p95_selected_mcs=("selected_mcs", lambda x: np.nanpercentile(x, 95)))
        mcs_summary.to_csv(out / "mcs_density_summary.csv", index=False)
        fig, ax = plt.subplots(figsize=(7.2, 4.8)); ax.plot(mcs_summary.n_uavs, mcs_summary.mean_selected_mcs, marker="o"); ax.fill_between(mcs_summary.n_uavs, mcs_summary.p05_selected_mcs, mcs_summary.p95_selected_mcs, alpha=0.2); ax.set_xlabel("Number of UAVs"); ax.set_ylabel("Selected MCS index"); ax.set_title("Adaptive MCS versus swarm density"); ax.grid(True, alpha=0.3); fig.tight_layout(); fig.savefig(figs / "fig06_selected_mcs_density.png", dpi=300); fig.savefig(figs / "fig06_selected_mcs_density.pdf"); plt.close(fig)

    # Communication energy abstraction: transmit power x ideal Chase attempts.
    energy_rows: list[dict[str, object]] = []
    for tx_dbm in ([20.0, 30.0] if smoke else [20.0, 25.0, 30.0]):
        for attempts in ([1, 3] if smoke else [1, 2, 3, 4]):
            for seed in seeds:
                cfg = SwarmConfig(n_uavs=30, seed=seed, channel="measured_a2a", tx_power_dbm=tx_dbm, activity_probability=1.0)
                _, links, _ = evaluate_snapshot(cfg, curves, grid, harq_attempts=attempts)
                for r in links.to_dict(orient="records"):
                    delivered = float(r["tbs_bits"]) * float(r["harq_success_probability"]) if np.isfinite(float(r["tbs_bits"])) else 0.0
                    ebit = energy_per_delivered_bit_j(tx_dbm, grid.slot_duration_ms, float(r["expected_attempts"]), delivered)
                    energy_rows.append({"tx_power_dbm": tx_dbm, "harq_attempts_max": attempts, "seed": seed, "link_id": r["link_id"], "expected_attempts": r["expected_attempts"], "harq_success_probability": r["harq_success_probability"], "energy_per_delivered_bit_j": ebit, "classification": "DERIVED_COMMUNICATION_ENERGY_NOT_UAV_BATTERY"})
    energy_df = pd.DataFrame(energy_rows); energy_df.to_csv(out / "communication_energy_per_link.csv", index=False)
    finite_energy = energy_df[np.isfinite(energy_df.energy_per_delivered_bit_j)].copy()
    energy_summary = finite_energy.groupby(["tx_power_dbm", "harq_attempts_max"], as_index=False).agg(median_energy_per_bit_j=("energy_per_delivered_bit_j", "median"), mean_success_probability=("harq_success_probability", "mean"), mean_attempts=("expected_attempts", "mean"))
    energy_summary.to_csv(out / "communication_energy_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for tx, g in energy_summary.groupby("tx_power_dbm"):
        ax.plot(g.harq_attempts_max, g.median_energy_per_bit_j, marker="o", label=f"{tx:g} dBm")
    ax.set_xlabel("Maximum HARQ attempts"); ax.set_ylabel("Median Tx energy / delivered bit [J/bit]"); ax.set_title("Communication-energy tradeoff (not UAV battery model)"); ax.set_yscale("log"); ax.grid(True, alpha=0.3); ax.legend(); fig.tight_layout(); fig.savefig(figs / "fig14_energy_tradeoff.png", dpi=300); fig.savefig(figs / "fig14_energy_tradeoff.pdf"); plt.close(fig)

    # Representative spatial resource/SINR map.
    n, seed = 50, 0
    cfg = SwarmConfig(n_uavs=n, seed=seed, channel="measured_a2a", activity_probability=1.0)
    positions = generate_positions("uniform", n, cfg.area_xy_m, cfg.altitude_m, seed)
    _, topo_links, _ = evaluate_snapshot(cfg, curves, grid, positions=positions, n_resources=4, resource_algorithm="graph")
    topo_links.to_csv(out / "representative_topology_links.csv", index=False)
    pd.DataFrame(positions, columns=["x_m", "y_m", "z_m"]).assign(uav_id=np.arange(n)).to_csv(out / "representative_topology_positions.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.0, 6.2)); ax.scatter(positions[:, 0], positions[:, 1], s=18)
    for r in topo_links.itertuples(index=False):
        ax.plot([positions[r.tx,0], positions[r.rx,0]], [positions[r.tx,1], positions[r.rx,1]], alpha=0.45)
        mx=(positions[r.tx,0]+positions[r.rx,0])/2; my=(positions[r.tx,1]+positions[r.rx,1])/2; ax.text(mx,my,f"R{int(r.resource_id)}\n{r.sinr_db:.1f}dB",fontsize=5)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_title("Representative resource/SINR topology (N=50, graph allocator)"); ax.set_aspect("equal", adjustable="box"); ax.grid(True, alpha=0.2); fig.tight_layout(); fig.savefig(figs / "fig15_resource_sinr_topology.png", dpi=300); fig.savefig(figs / "fig15_resource_sinr_topology.pdf"); plt.close(fig)

    # Representative reliability-aware routing topology on isolated candidate links.
    route_links = pairwise_isolated_links(cfg, positions, curves, grid, harq_attempts=2)
    graph = build_graph(route_links, minimum_sinr_db=-100.0, minimum_success_probability=0.9)
    try:
        path = reliability_aware_path(graph, 0, n-1)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        path = []
    pd.DataFrame({"path_node": path}).to_csv(out / "representative_reliability_route.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.0, 6.2)); ax.scatter(positions[:,0], positions[:,1], s=18); ax.scatter([positions[0,0],positions[-1,0]],[positions[0,1],positions[-1,1]],s=45)
    if len(path) >= 2:
        for u,v in zip(path[:-1],path[1:]): ax.plot([positions[u,0],positions[v,0]],[positions[u,1],positions[v,1]], linewidth=2)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_title("Reliability-aware isolated-link route abstraction"); ax.set_aspect("equal", adjustable="box"); ax.grid(True, alpha=0.2); fig.tight_layout(); fig.savefig(figs / "fig16_routing_topology.png", dpi=300); fig.savefig(figs / "fig16_routing_topology.pdf"); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curves", default="data/generated/5glena_v5_table1_full.csv")
    parser.add_argument("--output-dir", default="results/final_campaign")
    parser.add_argument("--figure-dir", default="figures/final_campaign")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(); run(args.curves, args.output_dir, args.figure_dir, args.smoke)


if __name__ == "__main__":
    main()

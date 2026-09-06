"""Spatial diagnostic maps for selected synthetic swarm scenarios.

Maps are generated from simulation/model outputs, not hand-drawn. The received-
power field is a single-transmitter measurement-derived-model field; the link
resource map uses THIS_WORK weighted conflict-graph allocation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.channel_models.measured_a2a import path_loss_db
from src.sidelink.resource_allocation import weighted_conflict_graph_allocation
from src.swarm_system import SwarmConfig, build_disjoint_pairs, generate_equal_altitude_positions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--n-uavs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    n = 10 if args.smoke else args.n_uavs
    cfg = SwarmConfig(n_uavs=n, seed=args.seed)
    rng = np.random.default_rng(args.seed)
    positions = generate_equal_altitude_positions(cfg, rng)

    out = Path("results/spatial_diagnostics")
    figs = Path("figures/spatial_diagnostics")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    # Single-source model-derived received-power field at the swarm altitude.
    resolution = 25 if args.smoke else 80
    axis = np.linspace(0.0, cfg.area_xy_m, resolution)
    xx, yy = np.meshgrid(axis, axis)
    source = positions[0]
    distances = np.sqrt((xx - source[0]) ** 2 + (yy - source[1]) ** 2)
    distances = np.maximum(distances, 1.0)
    rx_power = cfg.tx_power_dbm - path_loss_db(distances)
    pd.DataFrame({
        "x_m": xx.ravel(),
        "y_m": yy.ravel(),
        "rx_power_dbm": rx_power.ravel(),
        "classification": "DERIVED_FROM_MEASUREMENT_FIT",
    }).to_csv(out / "source0_rx_power_field.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    mesh = ax.pcolormesh(xx, yy, rx_power, shading="auto")
    fig.colorbar(mesh, ax=ax, label="Model-derived received power [dBm]")
    ax.scatter(positions[:, 0], positions[:, 1], s=18, label="UAVs")
    ax.scatter([source[0]], [source[1]], s=60, marker="*", label="Source UAV 0")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Measurement-derived A2A received-power field")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "received_power_map.png", dpi=300)
    fig.savefig(figs / "received_power_map.pdf")
    plt.close(fig)

    # Preferred abstract resource and communication-pair geometry.
    pairs = build_disjoint_pairs(n)
    tx_pos = np.array([positions[t] for t, _ in pairs])
    rx_pos = np.array([positions[r] for _, r in pairs])
    allocation = weighted_conflict_graph_allocation(tx_pos, rx_pos, n_resources=4)
    resource_rows = []
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.scatter(positions[:, 0], positions[:, 1], s=20)
    for link_id, ((tx, rx), resource) in enumerate(zip(pairs, allocation.resources)):
        ax.plot(
            [positions[tx, 0], positions[rx, 0]],
            [positions[tx, 1], positions[rx, 1]],
            marker="o",
            label=f"resource {resource}" if link_id == np.where(allocation.resources == resource)[0][0] else None,
        )
        resource_rows.append({"link_id": link_id, "tx": tx, "rx": rx, "resource": int(resource)})
    pd.DataFrame(resource_rows).to_csv(out / "link_resources.csv", index=False)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("THIS_WORK weighted conflict-graph resource assignment")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "resource_connectivity_map.png", dpi=300)
    fig.savefig(figs / "resource_connectivity_map.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()

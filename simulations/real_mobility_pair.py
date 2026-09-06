"""Apply the measurement-derived A2A RF model to a real AMOVFLY flight pair.

The trajectory is measured; RF quantities are model-derived/simulated.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.channel_models.measured_a2a import path_loss_db
from src.mobility.amovfly import load_ready_csv, parse_takeoff_time, synchronize_pair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uav1-file", required=True)
    parser.add_argument("--uav1-time", required=True, help="YYYY/MM/DD HH:MM from Multi-Uav_infosheet.csv")
    parser.add_argument("--uav2-file", required=True)
    parser.add_argument("--uav2-time", required=True)
    parser.add_argument("--tx-power-dbm", type=float, default=30.0)
    parser.add_argument("--sample-period", type=float, default=0.2)
    parser.add_argument("--output-dir", default="results/real_mobility_pair")
    args = parser.parse_args()

    t1 = load_ready_csv(args.uav1_file)
    t2 = load_ready_csv(args.uav2_file)
    aligned = synchronize_pair(
        t1,
        parse_takeoff_time(args.uav1_time),
        t2,
        parse_takeoff_time(args.uav2_time),
        sample_period_s=args.sample_period,
    )
    aligned["path_loss_db"] = path_loss_db(aligned.a2a_distance_m.to_numpy())
    aligned["rx_power_dbm"] = args.tx_power_dbm - aligned.path_loss_db
    aligned["rf_classification"] = "SIMULATION_USING_MEASUREMENT_DERIVED_CHANNEL"

    out = Path(args.output_dir)
    fig_dir = Path("figures/mobility")
    out.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(out / "aligned_pair_rf_model.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(aligned.elapsed_overlap_s, aligned.a2a_distance_m)
    ax.set_xlabel("Overlapping flight time [s]")
    ax.set_ylabel("UAV-to-UAV distance [m]")
    ax.set_title("Measured AMOVFLY mobility: UAV separation over time")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "real_pair_distance_vs_time.png", dpi=300)
    fig.savefig(fig_dir / "real_pair_distance_vs_time.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(aligned.elapsed_overlap_s, aligned.rx_power_dbm)
    ax.set_xlabel("Overlapping flight time [s]")
    ax.set_ylabel("Model-derived received power [dBm]")
    ax.set_title("RF model applied to measured UAV trajectories")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "real_pair_rx_power_vs_time.png", dpi=300)
    fig.savefig(fig_dir / "real_pair_rx_power_vs_time.pdf")
    plt.close(fig)

    print(aligned[["a2a_distance_m", "path_loss_db", "rx_power_dbm"]].describe().to_string())


if __name__ == "__main__":
    main()

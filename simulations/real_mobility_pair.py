"""Apply RF/link models to a real AMOVFLY simultaneous-flight pair.

Mobility is MEASURED_DATASET. Common-frame synchronization is
DERIVED_FROM_MEASURED_DATASET. Path loss/SINR/BLER/MCS/goodput are simulated or
derived and must never be labelled measured RF performance.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.channel_models.measured_a2a import path_loss_db
from src.mobility.amovfly import (
    common_origin_from_trajectories,
    load_ready_csv,
    parse_takeoff_time,
    synchronize_pair,
    trajectory_to_common_enu,
)
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.sidelink.tb_link_model import estimate_tb_bler
from src.swarm_system import dbm_to_w, thermal_noise_dbm


def _add_link_adaptation(aligned: pd.DataFrame, bler_csv: str, source: str) -> pd.DataFrame:
    curves = load_bler_curves(bler_csv, source=source)
    available_mcs = sorted({mcs for (mcs, _, _) in curves})
    grid = thesis_profile_50mhz_30khz()
    rows = []
    for sinr_db in aligned.sinr_db.to_numpy(dtype=float):
        choices = []
        for mcs in available_mcs:
            tbs = grid.tbs_bits(mcs)
            try:
                estimate = estimate_tb_bler(curves, mcs, tbs, float(sinr_db))
            except ValueError:
                continue
            expected_bits = tbs * estimate.first_tx_success_probability
            goodput_mbps = expected_bits / (grid.slot_duration_ms * 1000.0)
            choices.append((goodput_mbps, mcs, estimate, tbs))
        if not choices:
            rows.append((np.nan, np.nan, np.nan, np.nan, np.nan))
            continue
        goodput, mcs, estimate, tbs = max(choices, key=lambda x: (x[0], -x[1]))
        rows.append((mcs, tbs, estimate.transport_block_bler, estimate.first_tx_success_probability, goodput))
    out = aligned.copy()
    out[["selected_mcs", "tbs_bits", "tb_bler", "first_tx_success_probability", "expected_goodput_mbps"]] = pd.DataFrame(rows, index=out.index)
    out["link_performance_classification"] = "SIMULATION_USING_MEASURED_MOBILITY_AND_LINK_LEVEL_BLER"
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uav1-file", required=True)
    parser.add_argument("--uav1-time", required=True, help="YYYY/MM/DD HH:MM from Multi-Uav_infosheet.csv")
    parser.add_argument("--uav2-file", required=True)
    parser.add_argument("--uav2-time", required=True)
    parser.add_argument("--tx-power-dbm", type=float, default=30.0)
    parser.add_argument("--noise-figure-db", type=float, default=7.0, help="EXPERIMENTAL_ASSUMPTION unless separately sourced")
    parser.add_argument("--sample-period", type=float, default=0.2)
    parser.add_argument("--bler-csv", help="optional processed 5G-LENA Table-1 CSV")
    parser.add_argument("--bler-source", default="5G-LENA Table-1 processed local source")
    parser.add_argument("--output-dir", default="results/real_mobility_pair")
    args = parser.parse_args()

    # Prefer global geodetic telemetry and transform BOTH UAVs into one common ENU frame.
    t1_global = load_ready_csv(args.uav1_file, prefer_global=True)
    t2_global = load_ready_csv(args.uav2_file, prefer_global=True)
    origin = common_origin_from_trajectories(t1_global, t2_global)
    t1 = trajectory_to_common_enu(t1_global, origin)
    t2 = trajectory_to_common_enu(t2_global, origin)

    aligned = synchronize_pair(
        t1,
        parse_takeoff_time(args.uav1_time),
        t2,
        parse_takeoff_time(args.uav2_time),
        sample_period_s=args.sample_period,
    )
    aligned["path_loss_db"] = path_loss_db(aligned.a2a_distance_m.to_numpy())
    aligned["rx_power_dbm"] = args.tx_power_dbm - aligned.path_loss_db
    noise_dbm = thermal_noise_dbm(50e6, args.noise_figure_db)
    aligned["noise_dbm"] = noise_dbm
    aligned["sinr_db"] = 10.0 * np.log10(dbm_to_w(aligned.rx_power_dbm.to_numpy()) / float(dbm_to_w(noise_dbm)))
    aligned["rf_classification"] = "SIMULATION_USING_MEASURED_MOBILITY"
    aligned["noise_figure_classification"] = "EXPERIMENTAL_ASSUMPTION"

    if args.bler_csv:
        aligned = _add_link_adaptation(aligned, args.bler_csv, args.bler_source)

    out = Path(args.output_dir)
    fig_dir = Path("figures/mobility")
    out.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(out / "aligned_pair_rf_model.csv", index=False)
    pd.DataFrame([{
        "origin_lon_deg": origin[0],
        "origin_lat_deg": origin[1],
        "origin_altitude_m": origin[2],
        "coordinate_frame": "COMMON_ENU_WGS84",
        "mobility_classification": "MEASURED_DATASET",
        "rf_classification": "SIMULATION_USING_MEASURED_MOBILITY",
    }]).to_csv(out / "provenance.csv", index=False)

    plots = [
        ("a2a_distance_m", "UAV-to-UAV distance [m]", "Measured AMOVFLY mobility: UAV separation", "real_pair_distance_vs_time"),
        ("sinr_db", "Noise-limited simulated SINR [dB]", "Simulated RF model on measured UAV mobility", "real_pair_sinr_vs_time"),
    ]
    if "expected_goodput_mbps" in aligned:
        plots.extend([
            ("selected_mcs", "Selected MCS index", "Adaptive MCS on measured UAV mobility", "real_pair_mcs_vs_time"),
            ("expected_goodput_mbps", "Expected PHY goodput [Mbps]", "BLER-derived goodput on measured UAV mobility", "real_pair_goodput_vs_time"),
        ])
    for column, ylabel, title, stem in plots:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.plot(aligned.elapsed_overlap_s, aligned[column])
        ax.set_xlabel("Overlapping flight time [s]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(fig_dir / f"{stem}.png", dpi=300)
        fig.savefig(fig_dir / f"{stem}.pdf")
        plt.close(fig)

    columns = ["a2a_distance_m", "path_loss_db", "rx_power_dbm", "sinr_db"]
    if "expected_goodput_mbps" in aligned:
        columns += ["selected_mcs", "tb_bler", "expected_goodput_mbps"]
    print(aligned[columns].describe().to_string())


if __name__ == "__main__":
    main()

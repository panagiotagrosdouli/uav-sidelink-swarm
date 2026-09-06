"""Run one pinned public AMOVFLY simultaneous-pair experiment.

The AMOVFLY CSVs are downloaded transiently and are NOT redistributed by this
repository. Original telemetry is MEASURED_DATASET. Synchronization/common-frame
coordinates are DERIVED_FROM_MEASURED_DATASET. All RF/link metrics are
SIMULATION_USING_MEASURED_MOBILITY.
"""
from __future__ import annotations

import argparse
import tempfile
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.mobility.amovfly import load_ready_csv, parse_takeoff_time, synchronize_pair
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.sidelink.tb_link_model import select_tbs_aware_mcs
from src.swarm_system import SwarmConfig, dbm_to_w, path_loss_for_link, thermal_noise_dbm, w_to_dbm

AMOVFLY_COMMIT = "67069ed00ddbebd62b71aa9bb1272415e9b15ff8"
PAIR = {
    "uav1_name": "UavY_P0A10S6_1",
    "uav1_takeoff": "2024/11/21 13:50",
    "uav1_path": "FAFS/FAFS/UavY_P0A10S6_1.csv",
    "uav2_name": "UavR_P0A40VarS8_1",
    "uav2_takeoff": "2024/11/21 13:46",
    "uav2_path": "FAVS/FAVS/UavR_P0A40VarS8_1.csv",
}
RAW_BASE = f"https://raw.githubusercontent.com/YujiaoHu/AMOVFLY-Dataset/{AMOVFLY_COMMIT}"


def _download(path: str, destination: Path) -> None:
    url = f"{RAW_BASE}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "uav-sidelink-swarm-research"})
    with urllib.request.urlopen(req, timeout=90) as response:
        destination.write_bytes(response.read())


def run(curves_csv: str | Path, output_dir: str | Path, figure_dir: str | Path) -> pd.DataFrame:
    curves = load_bler_curves(curves_csv, source="5G-LENA v5.0 pinned Table-1 processed data")
    grid = thesis_profile_50mhz_30khz()
    cfg = SwarmConfig(
        n_uavs=2,
        seed=0,
        channel="measured_a2a",
        carrier_ghz=3.5,
        bandwidth_mhz=50.0,
        tx_power_dbm=30.0,
        noise_figure_db=7.0,  # EXPERIMENTAL_ASSUMPTION, not from AMOVFLY.
    )

    with tempfile.TemporaryDirectory(prefix="amovfly-") as tmp:
        tmp_path = Path(tmp)
        p1, p2 = tmp_path / "uav1.csv", tmp_path / "uav2.csv"
        _download(PAIR["uav1_path"], p1)
        _download(PAIR["uav2_path"], p2)
        t1 = load_ready_csv(p1, PAIR["uav1_name"])
        t2 = load_ready_csv(p2, PAIR["uav2_name"])
        sync = synchronize_pair(
            t1,
            parse_takeoff_time(PAIR["uav1_takeoff"]),
            t2,
            parse_takeoff_time(PAIR["uav2_takeoff"]),
            sample_period_s=0.2,
            coordinate_mode="auto",
        )

    noise_w = float(dbm_to_w(thermal_noise_dbm(50e6, cfg.noise_figure_db)))
    rows: list[dict[str, object]] = []
    for r in sync.itertuples(index=False):
        distance = max(float(r.a2a_distance_m), 1.0)
        path_loss_db = path_loss_for_link(distance, cfg)
        rx_dbm = cfg.tx_power_dbm - path_loss_db
        snr_linear = float(dbm_to_w(rx_dbm)) / noise_w
        sinr_db = 10.0 * np.log10(snr_linear)
        choice = select_tbs_aware_mcs(curves, sinr_db, grid)
        rows.append({
            "elapsed_overlap_s": float(r.elapsed_overlap_s),
            "a2a_distance_m": distance,
            "relative_speed_mps": float(r.relative_speed_mps),
            "path_loss_db": path_loss_db,
            "rx_power_dbm": rx_dbm,
            "sinr_db": sinr_db,
            "selected_mcs": choice.mcs_index if choice else np.nan,
            "tb_bler": choice.transport_block_bler if choice else 1.0,
            "first_tx_success_probability": choice.first_tx_success_probability if choice else 0.0,
            "tbs_bits": choice.tbs_bits if choice else np.nan,
            "expected_first_tx_goodput_mbps": choice.expected_first_tx_goodput_mbps if choice else 0.0,
            "coordinate_source": r.coordinate_source,
            "mobility_classification": "DERIVED_FROM_MEASURED_DATASET",
            "rf_classification": "SIMULATION_USING_MEASURED_MOBILITY",
        })
    result = pd.DataFrame(rows)
    out = Path(output_dir)
    figs = Path(figure_dir)
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "amovfly_pair_timeseries.csv", index=False)
    pd.DataFrame([{**PAIR, "dataset_commit": AMOVFLY_COMMIT, "raw_data_redistributed": False}]).to_csv(
        out / "amovfly_pair_provenance.csv", index=False
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.elapsed_overlap_s, result.a2a_distance_m)
    ax.set_xlabel("Overlap time [s]")
    ax.set_ylabel("A2A distance [m]")
    ax.set_title("AMOVFLY measured mobility — synchronized A2A separation")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figs / "fig11a_real_mobility_distance.png", dpi=300)
    fig.savefig(figs / "fig11a_real_mobility_distance.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.elapsed_overlap_s, result.sinr_db, label="model-derived SINR")
    ax.set_xlabel("Overlap time [s]")
    ax.set_ylabel("SINR [dB]")
    ax.set_title("AMOVFLY mobility + Erdemir A2A model")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "fig11b_real_mobility_sinr.png", dpi=300)
    fig.savefig(figs / "fig11b_real_mobility_sinr.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(result.elapsed_overlap_s, result.expected_first_tx_goodput_mbps)
    ax.set_xlabel("Overlap time [s]")
    ax.set_ylabel("Expected first-TX PHY goodput [Mbit/s]")
    ax.set_title("AMOVFLY mobility — adaptive-MCS model-derived goodput")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figs / "fig11c_real_mobility_goodput.png", dpi=300)
    fig.savefig(figs / "fig11c_real_mobility_goodput.pdf")
    plt.close(fig)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curves", default="data/generated/5glena_v5_table1_full.csv")
    parser.add_argument("--output-dir", default="results/final_campaign/real_mobility")
    parser.add_argument("--figure-dir", default="figures/final_campaign")
    args = parser.parse_args()
    result = run(args.curves, args.output_dir, args.figure_dir)
    print(result[["a2a_distance_m", "sinr_db", "tb_bler", "expected_first_tx_goodput_mbps"]].describe())


if __name__ == "__main__":
    main()

"""DEPRECATED compatibility wrapper around :mod:`src.swarm_system`.

The original prototype used a separate 5.9 GHz / 20 MHz / 23 dBm baseline and a
ring topology, which conflicted with the measurement-grounded 3.5 GHz research
pipeline. It is retained only so old commands fail gracefully into the common
simulator. New experiments must use ``src.swarm_system`` directly.
"""
from __future__ import annotations

import argparse
import warnings
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.swarm_system import SwarmConfig, simulate_snapshot


@dataclass(frozen=True)
class Config:
    seed: int = 42
    n_uavs: int = 20
    area_xy_m: float = 1000.0
    altitude_m: float = 100.0
    carrier_ghz: float = 3.5
    bandwidth_mhz: float = 50.0
    tx_power_dbm: float = 30.0
    noise_figure_db: float = 7.0
    sinr_threshold_db: float = 5.0
    activity_probability: float = 0.35


def simulate(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    warnings.warn(
        "src.sinr_sim is deprecated; use src.swarm_system instead",
        DeprecationWarning,
        stacklevel=2,
    )
    swarm_cfg = SwarmConfig(
        seed=cfg.seed,
        n_uavs=cfg.n_uavs,
        area_xy_m=cfg.area_xy_m,
        altitude_m=cfg.altitude_m,
        carrier_ghz=cfg.carrier_ghz,
        bandwidth_mhz=cfg.bandwidth_mhz,
        tx_power_dbm=cfg.tx_power_dbm,
        noise_figure_db=cfg.noise_figure_db,
        sinr_threshold_db=cfg.sinr_threshold_db,
        activity_probability=cfg.activity_probability,
        channel="measured_a2a",
    )
    positions, links = simulate_snapshot(swarm_cfg)
    if not links.empty:
        links = links.copy()
        links["success"] = links["link_success_proxy"]
        links["pathloss_db"] = links["path_loss_db"]
    return positions, links


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-uavs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--activity", type=float, default=0.35)
    parser.add_argument("--output-dir", default="results/legacy_sinr_wrapper")
    args = parser.parse_args()
    cfg = Config(n_uavs=args.n_uavs, seed=args.seed, activity_probability=args.activity)
    positions, links = simulate(cfg)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    positions.to_csv(out / "positions.csv", index=False)
    links.to_csv(out / "links.csv", index=False)
    print("DEPRECATED wrapper: canonical experiments use src.swarm_system")
    print(f"Results: {out}")


if __name__ == "__main__":
    main()

"""Interference-aware UAV sidelink system-level simulator.

Scientific scope
----------------
This is a transparent system-level baseline, not a bit-accurate NR sidelink PHY.
Geometry is synthetic. RF quantities are calculated from explicit assumptions.
The channel function is intentionally modular so a scenario-specific 3GPP aerial
UE channel can replace the free-space sanity-check model without changing the
interference/scheduling logic.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

C = 299_792_458.0
K_B = 1.380649e-23
T0 = 290.0


def dbm_to_w(dbm: np.ndarray | float) -> np.ndarray | float:
    return 10.0 ** ((np.asarray(dbm) - 30.0) / 10.0)


def w_to_dbm(w: np.ndarray | float) -> np.ndarray | float:
    return 10.0 * np.log10(np.asarray(w)) + 30.0


def fspl_db(distance_m: np.ndarray, carrier_hz: float) -> np.ndarray:
    """Free-space path loss used only as a LOS sanity-check baseline."""
    d = np.maximum(distance_m, 1e-3)
    wavelength = C / carrier_hz
    return 20.0 * np.log10(4.0 * np.pi * d / wavelength)


def noise_power_dbm(bandwidth_hz: float, noise_figure_db: float) -> float:
    thermal_w = K_B * T0 * bandwidth_hz
    return float(w_to_dbm(thermal_w) + noise_figure_db)


@dataclass(frozen=True)
class Config:
    seed: int = 42
    n_uavs: int = 20
    area_xy_m: float = 500.0
    altitude_min_m: float = 60.0
    altitude_max_m: float = 120.0
    carrier_hz: float = 5.9e9
    bandwidth_hz: float = 20e6
    tx_power_dbm: float = 23.0
    noise_figure_db: float = 7.0
    sinr_threshold_db: float = 5.0
    activity_probability: float = 0.35


def generate_positions(cfg: Config, rng: np.random.Generator) -> np.ndarray:
    xy = rng.uniform(0.0, cfg.area_xy_m, size=(cfg.n_uavs, 2))
    z = rng.uniform(cfg.altitude_min_m, cfg.altitude_max_m, size=(cfg.n_uavs, 1))
    return np.hstack([xy, z])


def received_power_w(tx: int, rx: int, positions: np.ndarray, cfg: Config) -> tuple[float, float, float]:
    distance = float(np.linalg.norm(positions[tx] - positions[rx]))
    loss_db = float(fspl_db(np.array(distance), cfg.carrier_hz))
    pr_dbm = cfg.tx_power_dbm - loss_db
    return float(dbm_to_w(pr_dbm)), distance, loss_db


def simulate(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    pos = generate_positions(cfg, rng)
    noise_dbm = noise_power_dbm(cfg.bandwidth_hz, cfg.noise_figure_db)
    noise_w = float(dbm_to_w(noise_dbm))

    # Directed desired links i -> (i+1) mod N form a simple reproducible ring.
    desired = [(i, (i + 1) % cfg.n_uavs) for i in range(cfg.n_uavs)]
    active = rng.random(cfg.n_uavs) < cfg.activity_probability
    if not np.any(active):
        active[rng.integers(0, cfg.n_uavs)] = True

    rows = []
    for link_id, (tx, rx) in enumerate(desired):
        if not active[link_id]:
            continue

        signal_w, distance_m, pathloss_db = received_power_w(tx, rx, pos, cfg)
        interference_w = 0.0
        n_interferers = 0

        # Same-resource co-channel assumption: every other active transmitter
        # contributes interference at this receiver.
        for other_id, (other_tx, _) in enumerate(desired):
            if other_id == link_id or not active[other_id]:
                continue
            p_i_w, _, _ = received_power_w(other_tx, rx, pos, cfg)
            interference_w += p_i_w
            n_interferers += 1

        sinr_linear = signal_w / (noise_w + interference_w)
        sinr_db = 10.0 * np.log10(sinr_linear)
        spectral_efficiency = np.log2(1.0 + sinr_linear)
        throughput_mbps = cfg.bandwidth_hz * spectral_efficiency / 1e6

        rows.append({
            "link_id": link_id,
            "tx": tx,
            "rx": rx,
            "distance_m": distance_m,
            "pathloss_db": pathloss_db,
            "rx_power_dbm": float(w_to_dbm(signal_w)),
            "interference_dbm": float(w_to_dbm(interference_w)) if interference_w > 0 else -np.inf,
            "noise_dbm": noise_dbm,
            "n_interferers": n_interferers,
            "sinr_db": sinr_db,
            "success": bool(sinr_db >= cfg.sinr_threshold_db),
            "shannon_upper_bound_mbps": throughput_mbps,
        })

    positions = pd.DataFrame(pos, columns=["x_m", "y_m", "z_m"])
    positions.insert(0, "uav_id", np.arange(cfg.n_uavs))
    return positions, pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-uavs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--activity", type=float, default=0.35)
    parser.add_argument("--output-dir", default="results/sinr_baseline")
    args = parser.parse_args()

    cfg = Config(n_uavs=args.n_uavs, seed=args.seed, activity_probability=args.activity)
    positions, links = simulate(cfg)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    positions.to_csv(out / "positions.csv", index=False)
    links.to_csv(out / "links.csv", index=False)

    print(f"Active links: {len(links)}")
    if len(links):
        print(f"Mean SINR: {links.sinr_db.mean():.2f} dB")
        print(f"PDR proxy (SINR threshold): {links.success.mean():.3f}")
        print(f"Mean Shannon upper bound: {links.shannon_upper_bound_mbps.mean():.2f} Mbps")
    print(f"Results: {out}")


if __name__ == "__main__":
    main()

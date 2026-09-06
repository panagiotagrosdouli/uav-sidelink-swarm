"""Reproduce a published 3.5 GHz UAV air-to-air path-loss experiment.

This script uses only parameters reported by Erdemir et al. (2023) for the
measurement campaign and fitted A2A log-distance model. It does NOT synthesize
SINR, PDR, traffic load, interference, or receiver noise-figure assumptions.

Source:
U. Erdemir et al., "Measurement-based Channel Characterization for A2A and A2G
Wireless Drone Communication Systems", 2023, arXiv:2306.08474.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CENTER_FREQUENCY_GHZ = 3.5
BANDWIDTH_MHZ = 50.0
TX_POWER_DBM = 30.0
ALTITUDE_M = 100.0
INITIAL_DISTANCE_M = 85.0
TRAJECTORY_LENGTH_M = 1000.0
TX_SPEED_MPS = 3.0
MEASUREMENT_PERIOD_S = 0.1
REFERENCE_DISTANCE_M = 1.0
PATH_LOSS_EXPONENT = 2.166
PL0_DB = 34.650


def measured_fit_path_loss_db(distance_m: np.ndarray) -> np.ndarray:
    """Measurement-derived A2A log-distance fit reported in the paper."""
    d = np.maximum(np.asarray(distance_m, dtype=float), REFERENCE_DISTANCE_M)
    return PL0_DB + 10.0 * PATH_LOSS_EXPONENT * np.log10(d / REFERENCE_DISTANCE_M)


def reproduce_route() -> pd.DataFrame:
    """Generate points along the reported 1-km straight A2A measurement route.

    The paper reports an initial separation of 85 m, a stationary RX UAV, and a
    TX UAV flying a 1 km straight trajectory at 3 m/s, both at 100 m altitude.
    We therefore parameterize link distance along a collinear route beginning
    at 85 m. The absolute geographic coordinates are not claimed to be known.
    """
    duration_s = TRAJECTORY_LENGTH_M / TX_SPEED_MPS
    t = np.arange(0.0, duration_s + MEASUREMENT_PERIOD_S, MEASUREMENT_PERIOD_S)
    travelled_m = np.minimum(TX_SPEED_MPS * t, TRAJECTORY_LENGTH_M)
    distance_m = INITIAL_DISTANCE_M + travelled_m
    path_loss_db = measured_fit_path_loss_db(distance_m)
    received_power_dbm = TX_POWER_DBM - path_loss_db

    return pd.DataFrame(
        {
            "time_s": t,
            "tx_travelled_m": travelled_m,
            "a2a_distance_m": distance_m,
            "altitude_tx_m": ALTITUDE_M,
            "altitude_rx_m": ALTITUDE_M,
            "path_loss_fit_db": path_loss_db,
            "rx_power_from_fit_dbm": received_power_dbm,
        }
    )


def main() -> None:
    out_dir = Path("results/measured_a2a_35ghz")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = reproduce_route()
    output = out_dir / "published_fit_reproduction.csv"
    df.to_csv(output, index=False)

    print("Published measurement-based A2A baseline")
    print(f"Carrier: {CENTER_FREQUENCY_GHZ:.1f} GHz")
    print(f"Bandwidth: {BANDWIDTH_MHZ:.0f} MHz")
    print(f"TX power: {TX_POWER_DBM:.0f} dBm")
    print(f"Altitude: {ALTITUDE_M:.0f} m for both UAVs")
    print(f"Path-loss fit: PL(d) = {PL0_DB:.3f} + 10*{PATH_LOSS_EXPONENT:.3f}*log10(d/1m)")
    print(f"Rows: {len(df)}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()

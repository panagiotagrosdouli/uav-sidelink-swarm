"""Evaluate the measurement-derived 3.5 GHz UAV air-to-air path-loss fit.

Primary peer-reviewed source:
U. Erdemir et al., "Measurement-based Channel Characterization for A2A and A2G
Wireless Drone Communication Systems," IEEE VTC 2023-Spring,
doi:10.1109/VTC2023-Spring57618.2023.10199853.

The paper reports campaign geometry and a fitted A2A large-scale path-loss model,
but the exact relative route geometry/raw GPS samples are not distributed here.
Therefore this script evaluates the sourced fit on an explicit DISTANCE SWEEP;
it does not reconstruct A2A distance as initial_distance + travelled_distance.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.channel_models.measured_a2a import (
    PATH_LOSS_EXPONENT,
    PL0_DB,
    REFERENCE_DISTANCE_M,
    path_loss_db,
)

CENTER_FREQUENCY_GHZ = 3.5
BANDWIDTH_MHZ = 50.0
TX_POWER_DBM = 30.0
ALTITUDE_M = 100.0
INITIAL_REPORTED_DISTANCE_M = 85.0
REPORTED_TRAJECTORY_LENGTH_M = 1000.0
TX_SPEED_MPS = 3.0
MEASUREMENT_PERIOD_S = 0.1


def evaluate_distance_sweep(min_distance_m: float = 1.0, max_distance_m: float = 1200.0, n_points: int = 1200) -> pd.DataFrame:
    """Evaluate the fitted path-loss equation on an explicit experimental sweep."""
    if min_distance_m <= 0 or max_distance_m <= min_distance_m or n_points < 2:
        raise ValueError("invalid distance sweep")
    distance_m = np.linspace(min_distance_m, max_distance_m, n_points)
    model_path_loss_db = path_loss_db(distance_m)
    received_power_dbm = TX_POWER_DBM - model_path_loss_db
    return pd.DataFrame({
        "a2a_distance_m": distance_m,
        "altitude_tx_m": ALTITUDE_M,
        "altitude_rx_m": ALTITUDE_M,
        "path_loss_model_db": model_path_loss_db,
        "rx_power_model_dbm": received_power_dbm,
        "distance_axis_classification": "EXPERIMENTAL_SWEEP",
        "rf_value_classification": "DERIVED_FROM_MEASUREMENT_FIT",
    })


def reproduce_route() -> pd.DataFrame:
    """Backward-compatible alias; no route geometry is reconstructed."""
    return evaluate_distance_sweep()


def main() -> None:
    out_dir = Path("results/measured_a2a_35ghz")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = evaluate_distance_sweep()
    output = out_dir / "measurement_fit_distance_sweep.csv"
    df.to_csv(output, index=False)

    print("Measurement-derived A2A path-loss fit — explicit distance sweep")
    print(f"Carrier: {CENTER_FREQUENCY_GHZ:.1f} GHz")
    print(f"Bandwidth: {BANDWIDTH_MHZ:.0f} MHz")
    print(f"TX power: {TX_POWER_DBM:.0f} dBm")
    print(f"Reported campaign altitude: {ALTITUDE_M:.0f} m for both UAVs")
    print(f"Reported initial separation: {INITIAL_REPORTED_DISTANCE_M:.0f} m (metadata only)")
    print(f"Reported TX trajectory length: {REPORTED_TRAJECTORY_LENGTH_M:.0f} m (metadata only)")
    print(
        f"Fit: PL(d) = {PL0_DB:.3f} + 10*{PATH_LOSS_EXPONENT:.3f}*"
        f"log10(d/{REFERENCE_DISTANCE_M:.0f}m)"
    )
    print("Distance axis: EXPERIMENTAL_SWEEP; RF values: DERIVED_FROM_MEASUREMENT_FIT")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()

"""Reproduce the measurement-derived 3.5 GHz UAV air-to-air path-loss fit.

Primary peer-reviewed source:
U. Erdemir et al., "Measurement-based Channel Characterization for A2A and A2G
Wireless Drone Communication Systems," IEEE VTC 2023-Spring,
doi:10.1109/VTC2023-Spring57618.2023.10199853.

This script uses reported campaign geometry and the fitted A2A large-scale
path-loss model. It does NOT claim that the generated route samples are the raw
measurement dataset, and it does not invent SINR, PDR, traffic load,
interference, or receiver noise-figure values.
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
INITIAL_DISTANCE_M = 85.0
TRAJECTORY_LENGTH_M = 1000.0
TX_SPEED_MPS = 3.0
MEASUREMENT_PERIOD_S = 0.1


def reproduce_route() -> pd.DataFrame:
    """Parameterize the reported straight A2A route for model evaluation.

    The paper reports a stationary RX UAV, a TX UAV starting 85 m away and
    flying a 1 km straight trajectory at 3 m/s, with both UAVs at 100 m.
    Without the original GPS sample file, this script uses travelled distance
    along that reported straight route as a reconstruction variable. Therefore
    the resulting rows are DERIVED model samples, not raw measured samples.
    """
    duration_s = TRAJECTORY_LENGTH_M / TX_SPEED_MPS
    t = np.arange(0.0, duration_s + MEASUREMENT_PERIOD_S, MEASUREMENT_PERIOD_S)
    travelled_m = np.minimum(TX_SPEED_MPS * t, TRAJECTORY_LENGTH_M)
    distance_m = INITIAL_DISTANCE_M + travelled_m
    model_path_loss_db = path_loss_db(distance_m)
    received_power_dbm = TX_POWER_DBM - model_path_loss_db

    return pd.DataFrame(
        {
            "time_s": t,
            "tx_travelled_m": travelled_m,
            "a2a_distance_m": distance_m,
            "altitude_tx_m": ALTITUDE_M,
            "altitude_rx_m": ALTITUDE_M,
            "path_loss_model_db": model_path_loss_db,
            "rx_power_model_dbm": received_power_dbm,
            "data_classification": "DERIVED_FROM_MEASUREMENT_FIT",
        }
    )


def main() -> None:
    out_dir = Path("results/measured_a2a_35ghz")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = reproduce_route()
    output = out_dir / "measurement_fit_reproduction.csv"
    df.to_csv(output, index=False)

    print("Measurement-derived A2A path-loss fit reproduction")
    print(f"Carrier: {CENTER_FREQUENCY_GHZ:.1f} GHz")
    print(f"Bandwidth: {BANDWIDTH_MHZ:.0f} MHz")
    print(f"TX power: {TX_POWER_DBM:.0f} dBm")
    print(f"Altitude: {ALTITUDE_M:.0f} m for both UAVs")
    print(
        f"Fit: PL(d) = {PL0_DB:.3f} + 10*{PATH_LOSS_EXPONENT:.3f}*"
        f"log10(d/{REFERENCE_DISTANCE_M:.0f}m)"
    )
    print("Output classification: DERIVED_FROM_MEASUREMENT_FIT (not raw measurements)")
    print(f"Rows: {len(df)}")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()

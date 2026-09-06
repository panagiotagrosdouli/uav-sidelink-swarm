"""Load and synchronize real AMOVFLY UAV telemetry trajectories.

AMOVFLY is used only as a mobility/telemetry source. Applying propagation or
sidelink models to these positions produces simulated RF quantities, not RF
measurements.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("time", "gps_x", "gps_y", "gps_z")


@dataclass(frozen=True)
class Trajectory:
    uav_name: str
    data: pd.DataFrame
    source: str = "AMOVFLY"
    classification: str = "MEASURED_DATASET"


def load_ready_csv(path: str | Path, uav_name: str | None = None) -> Trajectory:
    """Load one AMOVFLY ready-data CSV into a normalized local trajectory."""
    path = Path(path)
    df = pd.read_csv(path)
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:") or str(c) == ""]
    if unnamed:
        df = df.drop(columns=unnamed)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing AMOVFLY columns: {missing}")

    out = df.loc[:, REQUIRED_COLUMNS].rename(
        columns={"time": "time_s", "gps_x": "x_m", "gps_y": "y_m", "gps_z": "z_m"}
    )
    out = out.apply(pd.to_numeric, errors="coerce").dropna().sort_values("time_s")
    out = out.drop_duplicates(subset="time_s", keep="first").reset_index(drop=True)
    if out.empty:
        raise ValueError("trajectory contains no valid samples")
    name = uav_name or path.stem
    return Trajectory(uav_name=name, data=out)


def parse_takeoff_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y/%m/%d %H:%M")


def synchronize_pair(
    first: Trajectory,
    first_takeoff: datetime,
    second: Trajectory,
    second_takeoff: datetime,
    sample_period_s: float = 0.2,
) -> pd.DataFrame:
    """Synchronize two measured trajectories on a common absolute-time axis.

    Linear interpolation is a DERIVED_FROM_MEASURED_DATASET operation. Samples
    are emitted only over the time interval where both flights overlap.
    """
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be positive")

    a = first.data.copy()
    b = second.data.copy()
    a["absolute_s"] = first_takeoff.timestamp() + a.time_s
    b["absolute_s"] = second_takeoff.timestamp() + b.time_s

    start = max(float(a.absolute_s.min()), float(b.absolute_s.min()))
    end = min(float(a.absolute_s.max()), float(b.absolute_s.max()))
    if end <= start:
        raise ValueError("trajectories do not overlap in time")

    grid = np.arange(start, end + 0.5 * sample_period_s, sample_period_s)

    def interp(df: pd.DataFrame, column: str) -> np.ndarray:
        return np.interp(grid, df.absolute_s.to_numpy(), df[column].to_numpy())

    out = pd.DataFrame({
        "absolute_time_s": grid,
        "elapsed_overlap_s": grid - start,
        "uav1_x_m": interp(a, "x_m"),
        "uav1_y_m": interp(a, "y_m"),
        "uav1_z_m": interp(a, "z_m"),
        "uav2_x_m": interp(b, "x_m"),
        "uav2_y_m": interp(b, "y_m"),
        "uav2_z_m": interp(b, "z_m"),
    })
    dx = out.uav1_x_m - out.uav2_x_m
    dy = out.uav1_y_m - out.uav2_y_m
    dz = out.uav1_z_m - out.uav2_z_m
    out["a2a_distance_m"] = np.sqrt(dx * dx + dy * dy + dz * dz)
    out["classification"] = "DERIVED_FROM_MEASURED_DATASET"
    return out

"""Load and synchronize real AMOVFLY UAV telemetry trajectories.

AMOVFLY is used only as a mobility/telemetry source. Applying propagation or
sidelink models to these positions produces simulated RF quantities, not RF
measurements.

When global latitude/longitude/altitude are available for both UAVs, pair
synchronization converts them to one common WGS-84 ECEF/ENU frame before A2A
distances are calculated. Local gps_x/gps_y/gps_z are used only as an explicit
fallback because their origins must not silently be assumed identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from src.mobility.geodesy import geodetic_to_enu

TIME_COLUMN = "time"
LOCAL_COLUMNS = ("gps_x", "gps_y", "gps_z")
GLOBAL_COLUMNS = ("gps_lat", "gps_lon", "altitude")
CoordinateMode = Literal["auto", "global_enu", "local_assumed_common"]


@dataclass(frozen=True)
class Trajectory:
    uav_name: str
    data: pd.DataFrame
    source: str = "AMOVFLY"
    classification: str = "MEASURED_DATASET"

    @property
    def has_global_coordinates(self) -> bool:
        return {"latitude_deg", "longitude_deg", "altitude_m"}.issubset(self.data.columns)

    @property
    def has_local_coordinates(self) -> bool:
        return {"x_m", "y_m", "z_m"}.issubset(self.data.columns)


def load_ready_csv(path: str | Path, uav_name: str | None = None) -> Trajectory:
    """Load an AMOVFLY ready-data CSV while preserving local and global coordinates."""
    path = Path(path)
    df = pd.read_csv(path)
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:") or str(c) == ""]
    if unnamed:
        df = df.drop(columns=unnamed)
    if TIME_COLUMN not in df.columns:
        raise ValueError("missing AMOVFLY time column")
    has_local = set(LOCAL_COLUMNS).issubset(df.columns)
    has_global = set(GLOBAL_COLUMNS).issubset(df.columns)
    if not has_local and not has_global:
        raise ValueError(
            "trajectory needs either gps_x/gps_y/gps_z or gps_lat/gps_lon/altitude"
        )

    selected = [TIME_COLUMN]
    if has_local:
        selected.extend(LOCAL_COLUMNS)
    if has_global:
        selected.extend(GLOBAL_COLUMNS)
    # Preserve reported ground-speed/velocity fields when present for validation.
    for optional in ("gps_speed", "gps_vx", "gps_vy", "gps_vz"):
        if optional in df.columns:
            selected.append(optional)

    out = df.loc[:, selected].copy()
    rename = {
        "time": "time_s",
        "gps_x": "x_m",
        "gps_y": "y_m",
        "gps_z": "z_m",
        "gps_lat": "latitude_deg",
        "gps_lon": "longitude_deg",
        "altitude": "altitude_m",
        "gps_speed": "reported_speed_mps",
        "gps_vx": "reported_vx_mps",
        "gps_vy": "reported_vy_mps",
        "gps_vz": "reported_vz_mps",
    }
    out = out.rename(columns=rename)
    out = out.apply(pd.to_numeric, errors="coerce")
    out = out.dropna(subset=["time_s"]).sort_values("time_s")
    # Rows need one complete coordinate representation.
    if has_global:
        global_ok = out[["latitude_deg", "longitude_deg", "altitude_m"]].notna().all(axis=1)
    else:
        global_ok = pd.Series(False, index=out.index)
    if has_local:
        local_ok = out[["x_m", "y_m", "z_m"]].notna().all(axis=1)
    else:
        local_ok = pd.Series(False, index=out.index)
    out = out[global_ok | local_ok]
    out = out.drop_duplicates(subset="time_s", keep="first").reset_index(drop=True)
    if out.empty:
        raise ValueError("trajectory contains no valid coordinate samples")
    name = uav_name or path.stem
    return Trajectory(uav_name=name, data=out)


def parse_takeoff_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y/%m/%d %H:%M")


def _common_frame_pair(
    first: Trajectory,
    second: Trajectory,
    mode: CoordinateMode,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    use_global = mode == "global_enu" or (
        mode == "auto" and first.has_global_coordinates and second.has_global_coordinates
    )
    if use_global:
        if not first.has_global_coordinates or not second.has_global_coordinates:
            raise ValueError("global_enu requires global coordinates for both trajectories")
        # One shared reference is sufficient; ENU remains a metric local frame while
        # both input tracks are transformed from the same WGS-84 Earth frame.
        ref = first.data.iloc[0]
        ref_lat = float(ref.latitude_deg)
        ref_lon = float(ref.longitude_deg)
        ref_alt = float(ref.altitude_m)

        def transformed(traj: Trajectory) -> pd.DataFrame:
            df = traj.data.copy()
            enu = geodetic_to_enu(
                df.latitude_deg.to_numpy(),
                df.longitude_deg.to_numpy(),
                df.altitude_m.to_numpy(),
                ref_lat,
                ref_lon,
                ref_alt,
            )
            df["x_m"], df["y_m"], df["z_m"] = enu[:, 0], enu[:, 1], enu[:, 2]
            return df

        return transformed(first), transformed(second), "WGS84_ECEF_TO_COMMON_ENU"

    if mode not in ("auto", "local_assumed_common"):
        raise ValueError(f"unknown coordinate mode {mode}")
    if not first.has_local_coordinates or not second.has_local_coordinates:
        raise ValueError("local fallback requires local coordinates for both trajectories")
    return first.data.copy(), second.data.copy(), "LOCAL_FRAME_ASSUMED_COMMON"


def synchronize_pair(
    first: Trajectory,
    first_takeoff: datetime,
    second: Trajectory,
    second_takeoff: datetime,
    sample_period_s: float = 0.2,
    coordinate_mode: CoordinateMode = "auto",
) -> pd.DataFrame:
    """Synchronize two measured trajectories on a common absolute-time axis.

    Linear interpolation and coordinate transformation are
    DERIVED_FROM_MEASURED_DATASET operations. Samples are emitted only over the
    interval where both flights overlap.
    """
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be positive")

    a, b, coordinate_source = _common_frame_pair(first, second, coordinate_mode)
    a["absolute_s"] = first_takeoff.timestamp() + a.time_s
    b["absolute_s"] = second_takeoff.timestamp() + b.time_s

    start = max(float(a.absolute_s.min()), float(b.absolute_s.min()))
    end = min(float(a.absolute_s.max()), float(b.absolute_s.max()))
    if end <= start:
        raise ValueError("trajectories do not overlap in time")

    grid = np.arange(start, end + 0.5 * sample_period_s, sample_period_s)

    def interp(df: pd.DataFrame, column: str) -> np.ndarray:
        return np.interp(grid, df.absolute_s.to_numpy(), df[column].to_numpy())

    out = pd.DataFrame(
        {
            "absolute_time_s": grid,
            "elapsed_overlap_s": grid - start,
            "uav1_x_m": interp(a, "x_m"),
            "uav1_y_m": interp(a, "y_m"),
            "uav1_z_m": interp(a, "z_m"),
            "uav2_x_m": interp(b, "x_m"),
            "uav2_y_m": interp(b, "y_m"),
            "uav2_z_m": interp(b, "z_m"),
        }
    )
    dx = out.uav1_x_m - out.uav2_x_m
    dy = out.uav1_y_m - out.uav2_y_m
    dz = out.uav1_z_m - out.uav2_z_m
    out["a2a_distance_m"] = np.sqrt(dx * dx + dy * dy + dz * dz)

    if len(out) >= 2:
        dt = float(sample_period_s)
        rel = np.column_stack([dx.to_numpy(), dy.to_numpy(), dz.to_numpy()])
        drel_dt = np.gradient(rel, dt, axis=0)
        out["relative_speed_mps"] = np.linalg.norm(drel_dt, axis=1)
    else:
        out["relative_speed_mps"] = 0.0
    out["coordinate_source"] = coordinate_source
    out["classification"] = "DERIVED_FROM_MEASURED_DATASET"
    return out

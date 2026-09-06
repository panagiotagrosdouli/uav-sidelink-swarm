"""Load and synchronize real AMOVFLY UAV telemetry trajectories.

AMOVFLY is used only as a mobility/telemetry source. Applying propagation or
sidelink models to these positions produces simulated RF quantities, not RF
measurements.

Important: per-UAV local gps_x/gps_y/gps_z origins must not be assumed equal
across aircraft. When longitude/latitude/altitude are available, cross-UAV A2A
separation should use the common WGS84 -> ECEF -> local ENU path implemented
here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

LOCAL_REQUIRED_COLUMNS = ("time", "gps_x", "gps_y", "gps_z")
GLOBAL_REQUIRED_COLUMNS = ("time", "gps_lon", "gps_lat", "altitude")

WGS84_A_M = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)


@dataclass(frozen=True)
class Trajectory:
    uav_name: str
    data: pd.DataFrame
    source: str = "AMOVFLY"
    classification: str = "MEASURED_DATASET"
    coordinate_frame: str = "LOCAL_UNKNOWN_ORIGIN"


def _clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:") or str(c) == ""]
    return df.drop(columns=unnamed) if unnamed else df


def load_ready_csv(
    path: str | Path,
    uav_name: str | None = None,
    prefer_global: bool = True,
) -> Trajectory:
    """Load one AMOVFLY ready-data CSV.

    If global GPS columns exist and ``prefer_global`` is true, retain
    lon/lat/altitude so multiple UAVs can be transformed into one common frame.
    Otherwise retain the historical local xyz columns for single-UAV/local use.
    """
    path = Path(path)
    df = _clean_frame(pd.read_csv(path))
    name = uav_name or path.stem

    if prefer_global and all(c in df.columns for c in GLOBAL_REQUIRED_COLUMNS):
        out = df.loc[:, GLOBAL_REQUIRED_COLUMNS].rename(
            columns={
                "time": "time_s",
                "gps_lon": "lon_deg",
                "gps_lat": "lat_deg",
                "altitude": "altitude_m",
            }
        )
        out = out.apply(pd.to_numeric, errors="coerce").dropna().sort_values("time_s")
        out = out.drop_duplicates(subset="time_s", keep="first").reset_index(drop=True)
        if out.empty:
            raise ValueError("trajectory contains no valid global samples")
        return Trajectory(name, out, coordinate_frame="WGS84_GEODETIC")

    missing = [c for c in LOCAL_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing AMOVFLY columns: {missing}")
    out = df.loc[:, LOCAL_REQUIRED_COLUMNS].rename(
        columns={"time": "time_s", "gps_x": "x_m", "gps_y": "y_m", "gps_z": "z_m"}
    )
    out = out.apply(pd.to_numeric, errors="coerce").dropna().sort_values("time_s")
    out = out.drop_duplicates(subset="time_s", keep="first").reset_index(drop=True)
    if out.empty:
        raise ValueError("trajectory contains no valid samples")
    return Trajectory(name, out, coordinate_frame="LOCAL_UNKNOWN_ORIGIN")


def parse_takeoff_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y/%m/%d %H:%M")


def geodetic_to_ecef(lon_deg: np.ndarray, lat_deg: np.ndarray, altitude_m: np.ndarray) -> np.ndarray:
    """Convert WGS84 geodetic coordinates to ECEF meters."""
    lon = np.deg2rad(np.asarray(lon_deg, dtype=float))
    lat = np.deg2rad(np.asarray(lat_deg, dtype=float))
    h = np.asarray(altitude_m, dtype=float)
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    n = WGS84_A_M / np.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    x = (n + h) * cos_lat * np.cos(lon)
    y = (n + h) * cos_lat * np.sin(lon)
    z = (n * (1.0 - WGS84_E2) + h) * sin_lat
    return np.column_stack([x, y, z])


def ecef_to_enu(ecef_m: np.ndarray, origin_lon_deg: float, origin_lat_deg: float, origin_altitude_m: float) -> np.ndarray:
    """Convert ECEF coordinates to a local ENU frame around one WGS84 origin."""
    ecef = np.asarray(ecef_m, dtype=float)
    if ecef.ndim != 2 or ecef.shape[1] != 3:
        raise ValueError("ecef_m must have shape [n,3]")
    origin = geodetic_to_ecef(
        np.array([origin_lon_deg]), np.array([origin_lat_deg]), np.array([origin_altitude_m])
    )[0]
    d = ecef - origin
    lon = np.deg2rad(origin_lon_deg)
    lat = np.deg2rad(origin_lat_deg)
    rotation = np.array([
        [-np.sin(lon), np.cos(lon), 0.0],
        [-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)],
        [np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)],
    ])
    return d @ rotation.T


def trajectory_to_common_enu(trajectory: Trajectory, origin: tuple[float, float, float]) -> Trajectory:
    """Transform a WGS84 trajectory into one explicitly shared ENU frame."""
    if trajectory.coordinate_frame != "WGS84_GEODETIC":
        raise ValueError("trajectory must contain WGS84 geodetic coordinates")
    df = trajectory.data
    ecef = geodetic_to_ecef(df.lon_deg.to_numpy(), df.lat_deg.to_numpy(), df.altitude_m.to_numpy())
    enu = ecef_to_enu(ecef, *origin)
    out = pd.DataFrame({
        "time_s": df.time_s.to_numpy(dtype=float),
        "x_m": enu[:, 0],
        "y_m": enu[:, 1],
        "z_m": enu[:, 2],
    })
    return Trajectory(
        trajectory.uav_name,
        out,
        source=trajectory.source,
        classification="DERIVED_FROM_MEASURED_DATASET",
        coordinate_frame="COMMON_ENU_WGS84",
    )


def common_origin_from_trajectories(*trajectories: Trajectory) -> tuple[float, float, float]:
    """Choose a deterministic common origin from the first sample of all flights."""
    if not trajectories:
        raise ValueError("at least one trajectory is required")
    if any(t.coordinate_frame != "WGS84_GEODETIC" for t in trajectories):
        raise ValueError("all trajectories must be WGS84_GEODETIC")
    lon = np.mean([float(t.data.lon_deg.iloc[0]) for t in trajectories])
    lat = np.mean([float(t.data.lat_deg.iloc[0]) for t in trajectories])
    alt = np.mean([float(t.data.altitude_m.iloc[0]) for t in trajectories])
    return float(lon), float(lat), float(alt)


def synchronize_pair(
    first: Trajectory,
    first_takeoff: datetime,
    second: Trajectory,
    second_takeoff: datetime,
    sample_period_s: float = 0.2,
) -> pd.DataFrame:
    """Synchronize two trajectories already expressed in one common Cartesian frame."""
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be positive")
    required = {"time_s", "x_m", "y_m", "z_m"}
    if not required.issubset(first.data.columns) or not required.issubset(second.data.columns):
        raise ValueError("synchronize_pair requires Cartesian trajectories; convert global GPS to common ENU first")
    if first.coordinate_frame != second.coordinate_frame:
        raise ValueError("trajectory coordinate frames do not match")
    if first.coordinate_frame == "LOCAL_UNKNOWN_ORIGIN":
        raise ValueError("cross-UAV distance is unsafe for LOCAL_UNKNOWN_ORIGIN; use global GPS common ENU")

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
    out["coordinate_frame"] = first.coordinate_frame
    return out

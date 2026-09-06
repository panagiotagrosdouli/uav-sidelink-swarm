"""Load and synchronize real AMOVFLY UAV telemetry trajectories.

AMOVFLY is used only as a mobility/telemetry source. Applying propagation or
sidelink models to these positions produces simulated RF quantities, not RF
measurements.

AMOVFLY documents ``gps_x/gps_y`` as position relative to each UAV's takeoff
point, ``gps_z`` as altitude above ground, and ``real_lat/real_long`` as the
actual global trajectory. For multi-UAV analysis, ``auto`` therefore uses
WGS-84 latitude/longitude to derive one common horizontal ENU frame and the
measured AGL ``gps_z`` as vertical coordinate. Direct subtraction of local
``gps_x/gps_y`` remains an explicit fallback only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from src.mobility.geodesy import geodetic_to_enu

CoordinateMode = Literal["auto", "global_horizontal_agl", "local_assumed_common"]


@dataclass(frozen=True)
class Trajectory:
    uav_name: str
    data: pd.DataFrame
    source: str = "AMOVFLY"
    classification: str = "MEASURED_DATASET"

    @property
    def has_global_horizontal_agl(self) -> bool:
        return {"latitude_deg", "longitude_deg", "z_m"}.issubset(self.data.columns)

    @property
    def has_local_coordinates(self) -> bool:
        return {"x_m", "y_m", "z_m"}.issubset(self.data.columns)


def load_ready_csv(path: str | Path, uav_name: str | None = None) -> Trajectory:
    """Load one documented AMOVFLY ready-data CSV."""
    path = Path(path)
    df = pd.read_csv(path)
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:") or str(c) == ""]
    if unnamed:
        df = df.drop(columns=unnamed)
    if "time" not in df.columns:
        raise ValueError("missing AMOVFLY time column")

    has_local = {"gps_x", "gps_y", "gps_z"}.issubset(df.columns)
    # Current public ready-data schema uses real_lat/real_long. Older aliases are
    # accepted only to keep the loader robust to dataset revisions.
    if {"real_lat", "real_long"}.issubset(df.columns):
        lat_col, lon_col = "real_lat", "real_long"
    elif {"gps_lat", "gps_lon"}.issubset(df.columns):
        lat_col, lon_col = "gps_lat", "gps_lon"
    else:
        lat_col = lon_col = None
    has_global_horizontal = lat_col is not None and "gps_z" in df.columns
    if not has_local and not has_global_horizontal:
        raise ValueError("trajectory needs AMOVFLY local coordinates or real_lat/real_long + gps_z")

    selected = ["time"]
    if has_local:
        selected.extend(["gps_x", "gps_y", "gps_z"])
    elif "gps_z" in df.columns:
        selected.append("gps_z")
    if has_global_horizontal:
        selected.extend([lat_col, lon_col])
    for optional in ("gps_speed", "gps_vx", "gps_vy", "gps_vz", "v_x", "v_y", "v_z"):
        if optional in df.columns and optional not in selected:
            selected.append(optional)

    out = df.loc[:, selected].copy()
    rename = {
        "time": "time_s",
        "gps_x": "x_m",
        "gps_y": "y_m",
        "gps_z": "z_m",
        "real_lat": "latitude_deg",
        "real_long": "longitude_deg",
        "gps_lat": "latitude_deg",
        "gps_lon": "longitude_deg",
        "gps_speed": "reported_speed_mps",
        "gps_vx": "reported_vx_mps",
        "gps_vy": "reported_vy_mps",
        "gps_vz": "reported_vz_mps",
        "v_x": "reported_vx_mps",
        "v_y": "reported_vy_mps",
        "v_z": "reported_vz_mps",
    }
    out = out.rename(columns=rename)
    out = out.loc[:, ~out.columns.duplicated()].apply(pd.to_numeric, errors="coerce")
    out = out.dropna(subset=["time_s"]).sort_values("time_s")
    coordinate_columns = [c for c in ("x_m", "y_m", "z_m", "latitude_deg", "longitude_deg") if c in out]
    out = out.dropna(subset=coordinate_columns if coordinate_columns else ["time_s"])
    out = out.drop_duplicates(subset="time_s", keep="first").reset_index(drop=True)
    if out.empty:
        raise ValueError("trajectory contains no valid coordinate samples")
    return Trajectory(uav_name=uav_name or path.stem, data=out)


def parse_takeoff_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y/%m/%d %H:%M")


def _common_frame_pair(
    first: Trajectory,
    second: Trajectory,
    mode: CoordinateMode,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    use_global = mode == "global_horizontal_agl" or (
        mode == "auto" and first.has_global_horizontal_agl and second.has_global_horizontal_agl
    )
    if use_global:
        if not first.has_global_horizontal_agl or not second.has_global_horizontal_agl:
            raise ValueError("global_horizontal_agl requires latitude/longitude/gps_z for both UAVs")
        ref = first.data.iloc[0]
        ref_lat, ref_lon = float(ref.latitude_deg), float(ref.longitude_deg)

        def transformed(traj: Trajectory) -> pd.DataFrame:
            df = traj.data.copy()
            # Set ellipsoidal altitude to zero for all samples so ENU x/y derive
            # solely from global horizontal coordinates. The dataset's measured
            # AGL gps_z is then retained separately as the vertical coordinate.
            zeros = np.zeros(len(df), dtype=float)
            enu = geodetic_to_enu(
                df.latitude_deg.to_numpy(),
                df.longitude_deg.to_numpy(),
                zeros,
                ref_lat,
                ref_lon,
                0.0,
            )
            df["x_m"], df["y_m"] = enu[:, 0], enu[:, 1]
            return df

        return (
            transformed(first),
            transformed(second),
            "WGS84_COMMON_HORIZONTAL_ENU_PLUS_MEASURED_AGL_Z",
        )

    if mode not in ("auto", "local_assumed_common"):
        raise ValueError(f"unknown coordinate mode {mode}")
    if not first.has_local_coordinates or not second.has_local_coordinates:
        raise ValueError("local fallback requires local coordinates for both trajectories")
    return first.data.copy(), second.data.copy(), "LOCAL_XY_FRAME_ASSUMED_COMMON"


def synchronize_pair(
    first: Trajectory,
    first_takeoff: datetime,
    second: Trajectory,
    second_takeoff: datetime,
    sample_period_s: float = 0.2,
    coordinate_mode: CoordinateMode = "auto",
) -> pd.DataFrame:
    """Synchronize two measured trajectories over their common time interval."""
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

    out = pd.DataFrame({
        "absolute_time_s": grid,
        "elapsed_overlap_s": grid - start,
        "uav1_x_m": interp(a, "x_m"), "uav1_y_m": interp(a, "y_m"), "uav1_z_m": interp(a, "z_m"),
        "uav2_x_m": interp(b, "x_m"), "uav2_y_m": interp(b, "y_m"), "uav2_z_m": interp(b, "z_m"),
    })
    dx, dy, dz = out.uav1_x_m - out.uav2_x_m, out.uav1_y_m - out.uav2_y_m, out.uav1_z_m - out.uav2_z_m
    out["a2a_distance_m"] = np.sqrt(dx * dx + dy * dy + dz * dz)
    if len(out) >= 2:
        rel = np.column_stack([dx.to_numpy(), dy.to_numpy(), dz.to_numpy()])
        out["relative_speed_mps"] = np.linalg.norm(np.gradient(rel, sample_period_s, axis=0), axis=1)
    else:
        out["relative_speed_mps"] = 0.0
    out["coordinate_source"] = coordinate_source
    out["classification"] = "DERIVED_FROM_MEASURED_DATASET"
    return out

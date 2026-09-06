from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from src.mobility.amovfly import (
    Trajectory,
    common_origin_from_trajectories,
    geodetic_to_ecef,
    synchronize_pair,
    trajectory_to_common_enu,
)


def _trajectory(name: str, offset: float = 0.0, frame: str = "COMMON_ENU_WGS84") -> Trajectory:
    return Trajectory(
        name,
        pd.DataFrame({
            "time_s": [0.0, 1.0, 2.0],
            "x_m": [offset, offset + 1.0, offset + 2.0],
            "y_m": [0.0, 0.0, 0.0],
            "z_m": [10.0, 10.0, 10.0],
        }),
        coordinate_frame=frame,
    )


def test_synchronize_pair_distance():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A", 0.0)
    b = _trajectory("B", 3.0)
    out = synchronize_pair(a, t0, b, t0, sample_period_s=1.0)
    assert np.allclose(out.a2a_distance_m, 3.0)
    assert set(out.classification) == {"DERIVED_FROM_MEASURED_DATASET"}
    assert set(out.coordinate_frame) == {"COMMON_ENU_WGS84"}


def test_takeoff_offset_reduces_overlap():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A")
    b = _trajectory("B")
    out = synchronize_pair(a, t0, b, t0 + timedelta(seconds=1), sample_period_s=1.0)
    assert out.elapsed_overlap_s.iloc[-1] <= 1.0 + 1e-12


def test_local_unknown_origin_is_rejected_for_cross_uav_distance():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A", frame="LOCAL_UNKNOWN_ORIGIN")
    b = _trajectory("B", frame="LOCAL_UNKNOWN_ORIGIN")
    with pytest.raises(ValueError, match="LOCAL_UNKNOWN_ORIGIN"):
        synchronize_pair(a, t0, b, t0)


def test_wgs84_equator_origin_ecef_anchor():
    ecef = geodetic_to_ecef(np.array([0.0]), np.array([0.0]), np.array([0.0]))
    assert np.allclose(ecef[0], [6378137.0, 0.0, 0.0], atol=1e-6)


def test_two_global_trajectories_share_common_enu():
    base = pd.DataFrame({
        "time_s": [0.0, 1.0],
        "lon_deg": [23.70, 23.70],
        "lat_deg": [37.98, 37.98],
        "altitude_m": [100.0, 100.0],
    })
    shifted = base.copy()
    shifted["lon_deg"] += 1e-4
    a = Trajectory("A", base, coordinate_frame="WGS84_GEODETIC")
    b = Trajectory("B", shifted, coordinate_frame="WGS84_GEODETIC")
    origin = common_origin_from_trajectories(a, b)
    ae = trajectory_to_common_enu(a, origin)
    be = trajectory_to_common_enu(b, origin)
    distance = np.linalg.norm(ae.data[["x_m", "y_m", "z_m"]].iloc[0].to_numpy() - be.data[["x_m", "y_m", "z_m"]].iloc[0].to_numpy())
    assert 5.0 < distance < 15.0

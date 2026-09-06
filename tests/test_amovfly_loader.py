from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.mobility.amovfly import Trajectory, synchronize_pair
from src.mobility.geodesy import geodetic_to_ecef, geodetic_to_enu


def _trajectory(name: str, offset: float = 0.0) -> Trajectory:
    return Trajectory(
        name,
        pd.DataFrame(
            {
                "time_s": [0.0, 1.0, 2.0],
                "x_m": [offset, offset + 1.0, offset + 2.0],
                "y_m": [0.0, 0.0, 0.0],
                "z_m": [10.0, 10.0, 10.0],
            }
        ),
    )


def test_synchronize_pair_distance():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A", 0.0)
    b = _trajectory("B", 3.0)
    out = synchronize_pair(a, t0, b, t0, sample_period_s=1.0)
    assert np.allclose(out.a2a_distance_m, 3.0)
    assert set(out.classification) == {"DERIVED_FROM_MEASURED_DATASET"}
    assert set(out.coordinate_source) == {"LOCAL_FRAME_ASSUMED_COMMON"}


def test_takeoff_offset_reduces_overlap():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A")
    b = _trajectory("B")
    out = synchronize_pair(a, t0, b, t0 + timedelta(seconds=1), sample_period_s=1.0)
    assert out.elapsed_overlap_s.iloc[-1] <= 1.0 + 1e-12


def test_wgs84_reference_maps_to_enu_origin():
    enu = geodetic_to_enu(40.0, 23.0, 100.0, 40.0, 23.0, 100.0)
    assert np.linalg.norm(enu) < 1e-6
    ecef = geodetic_to_ecef(40.0, 23.0, 100.0)
    assert ecef.shape == (3,)
    assert np.linalg.norm(ecef) > 6.3e6


def test_wgs84_north_shift_is_about_111m_per_millidegree():
    enu = geodetic_to_enu(40.001, 23.0, 100.0, 40.0, 23.0, 100.0)
    assert 110.5 < float(enu[1]) < 111.6
    assert abs(float(enu[0])) < 0.1


def test_auto_mode_prefers_global_coordinates_over_incompatible_local_origins():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    common_global = {
        "latitude_deg": [40.0, 40.0, 40.0],
        "longitude_deg": [23.0, 23.0, 23.0],
        "altitude_m": [100.0, 100.0, 100.0],
    }
    a = Trajectory(
        "A",
        pd.DataFrame(
            {
                "time_s": [0.0, 1.0, 2.0],
                "x_m": [0.0, 1.0, 2.0],
                "y_m": [0.0, 0.0, 0.0],
                "z_m": [0.0, 0.0, 0.0],
                **common_global,
            }
        ),
    )
    b = Trajectory(
        "B",
        pd.DataFrame(
            {
                "time_s": [0.0, 1.0, 2.0],
                "x_m": [1000.0, 1001.0, 1002.0],
                "y_m": [0.0, 0.0, 0.0],
                "z_m": [0.0, 0.0, 0.0],
                **common_global,
            }
        ),
    )
    auto = synchronize_pair(a, t0, b, t0, sample_period_s=1.0)
    local = synchronize_pair(
        a,
        t0,
        b,
        t0,
        sample_period_s=1.0,
        coordinate_mode="local_assumed_common",
    )
    assert np.allclose(auto.a2a_distance_m, 0.0, atol=1e-6)
    assert np.allclose(local.a2a_distance_m, 1000.0)
    assert set(auto.coordinate_source) == {"WGS84_ECEF_TO_COMMON_ENU"}

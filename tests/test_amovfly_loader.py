from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.mobility.amovfly import Trajectory, synchronize_pair


def _trajectory(name: str, offset: float = 0.0) -> Trajectory:
    return Trajectory(
        name,
        pd.DataFrame({
            "time_s": [0.0, 1.0, 2.0],
            "x_m": [offset, offset + 1.0, offset + 2.0],
            "y_m": [0.0, 0.0, 0.0],
            "z_m": [10.0, 10.0, 10.0],
        }),
    )


def test_synchronize_pair_distance():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A", 0.0)
    b = _trajectory("B", 3.0)
    out = synchronize_pair(a, t0, b, t0, sample_period_s=1.0)
    assert np.allclose(out.a2a_distance_m, 3.0)
    assert set(out.classification) == {"DERIVED_FROM_MEASURED_DATASET"}


def test_takeoff_offset_reduces_overlap():
    t0 = datetime(2024, 1, 1, 12, 0, 0)
    a = _trajectory("A")
    b = _trajectory("B")
    out = synchronize_pair(a, t0, b, t0 + timedelta(seconds=1), sample_period_s=1.0)
    assert out.elapsed_overlap_s.iloc[-1] <= 1.0 + 1e-12

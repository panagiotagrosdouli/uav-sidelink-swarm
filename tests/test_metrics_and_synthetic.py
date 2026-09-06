import numpy as np

from src.metrics import jain_fairness, summarize
from src.mobility.synthetic import (
    constant_velocity_trace,
    generate_positions,
    leader_follower_trace,
    random_waypoint_trace,
)


def test_jain_fairness_equal_and_unfair():
    assert np.isclose(jain_fairness([1.0, 1.0, 1.0]), 1.0)
    assert jain_fairness([1.0, 0.0, 0.0]) < 0.5


def test_summary_contains_ci_and_percentiles():
    s = summarize([1, 2, 3, 4, 5])
    assert s["n"] == 5
    assert s["p05"] <= s["median"] <= s["p95"]
    assert s["ci95_low"] < s["mean"] < s["ci95_high"]


def test_all_geometries_shape_and_altitude():
    rng = np.random.default_rng(7)
    for geometry in ["uniform", "grid", "circle", "clustered", "leader_follower"]:
        p = generate_positions(10, 1000.0, 100.0, rng, geometry=geometry)
        assert p.shape == (10, 3)
        assert np.allclose(p[:, 2], 100.0)
        assert np.all((p[:, :2] >= 0.0) & (p[:, :2] <= 1000.0))


def test_constant_velocity_trace():
    p0 = np.array([[0.0, 0.0, 100.0], [10.0, 0.0, 100.0]])
    v = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    trace = constant_velocity_trace(p0, v, duration_s=2.0, sample_period_s=1.0)
    assert trace.positions_m.shape == (3, 2, 3)
    assert np.allclose(trace.positions_m[-1, :, 0], [2.0, 12.0])


def test_random_waypoint_stays_inside_area_and_altitude():
    p0 = np.array([[10.0, 20.0, 100.0], [40.0, 50.0, 100.0]])
    trace = random_waypoint_trace(p0, 100.0, 5.0, 10.0, 1.0, seed=4)
    assert np.all((trace.positions_m[:, :, :2] >= 0.0) & (trace.positions_m[:, :, :2] <= 100.0))
    assert np.allclose(trace.positions_m[:, :, 2], 100.0)


def test_leader_follower_preserves_finite_trace():
    p0 = np.array([[0.0, 0.0, 100.0], [10.0, 0.0, 100.0], [0.0, 10.0, 100.0]])
    trace = leader_follower_trace(p0, (1.0, 0.0, 0.0), 5.0, 1.0)
    assert trace.positions_m.shape == (6, 3, 3)
    assert np.all(np.isfinite(trace.positions_m))
    assert trace.positions_m[-1, 0, 0] > trace.positions_m[0, 0, 0]

import numpy as np

from src.analysis.metrics import communication_energy_j, energy_per_delivered_bit_j, jains_fairness
from src.analysis.statistics import paired_difference, summarize
from src.swarm_geometry import generate_positions


def test_summary_has_expected_central_statistics():
    out = summarize([1.0, 2.0, 3.0, 4.0, 5.0])
    assert out["n"] == 5
    assert np.isclose(out["mean"], 3.0)
    assert np.isclose(out["median"], 3.0)
    assert out["ci95_low"] < 3.0 < out["ci95_high"]


def test_paired_difference_uses_second_minus_first():
    out = paired_difference([1.0, 2.0, 3.0], [2.0, 3.0, 4.0])
    assert np.isclose(out["mean"], 1.0)


def test_jain_fairness_bounds_and_equal_case():
    assert np.isclose(jains_fairness([1.0, 1.0, 1.0]), 1.0)
    unequal = jains_fairness([1.0, 0.0, 0.0])
    assert 0.0 < unequal < 1.0


def test_communication_energy_reference():
    # 30 dBm = 1 W; 0.5 ms transmission => 0.5 mJ.
    assert np.isclose(communication_energy_j(30.0, 0.5), 5e-4)
    assert np.isclose(energy_per_delivered_bit_j(30.0, 0.5, 1.0, 1000), 5e-7)


def test_all_synthetic_geometries_have_expected_shape_and_altitude():
    for name in ("uniform", "grid", "circle", "clustered", "leader_follower"):
        p = generate_positions(name, 17, 1000.0, 100.0, seed=7)
        assert p.shape == (17, 3)
        assert np.allclose(p[:, 2], 100.0)
        assert np.all((p[:, :2] >= 0.0) & (p[:, :2] <= 1000.0))


def test_seeded_uniform_geometry_is_reproducible():
    a = generate_positions("uniform", 10, 1000.0, 100.0, seed=11)
    b = generate_positions("uniform", 10, 1000.0, 100.0, seed=11)
    assert np.array_equal(a, b)

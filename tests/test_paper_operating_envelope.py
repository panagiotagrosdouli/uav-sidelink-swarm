import numpy as np

from simulations.paper_operating_envelope import (
    allocate_resources,
    build_pairs,
    grid_for_prbs,
    occupied_bandwidth_hz,
    prb_partition,
)


def test_prb_partition_is_exact_and_balanced():
    for resources in (1, 2, 4, 8):
        parts = prb_partition(resources)
        assert len(parts) == resources
        assert sum(parts) == 133
        assert max(parts) - min(parts) <= 1


def test_grid_tracks_partition_prb_count():
    parts = prb_partition(4)
    assert parts == [34, 33, 33, 33]
    assert grid_for_prbs(parts[0]).n_prb == 34
    assert grid_for_prbs(parts[-1]).n_prb == 33


def test_occupied_bandwidth_uses_allocated_prb_subcarriers():
    assert occupied_bandwidth_hz(133, 30) == 47_880_000.0
    assert occupied_bandwidth_hz(1, 30) == 360_000.0


def test_pairing_modes_are_explicit_and_disjoint():
    positions = np.array([
        [0.0, 0.0, 100.0],
        [1.0, 0.0, 100.0],
        [100.0, 0.0, 100.0],
        [101.0, 0.0, 100.0],
    ])
    sequential = build_pairs(positions, "sequential")
    nearest = build_pairs(positions, "nearest_neighbor")
    assert sequential == [(0, 1), (2, 3)]
    assert nearest == [(0, 1), (2, 3)]


def test_random_allocator_is_seed_deterministic():
    tx = np.array([[0.0, 0.0, 100.0], [10.0, 0.0, 100.0], [20.0, 0.0, 100.0]])
    rx = tx + np.array([1.0, 1.0, 0.0])
    a = allocate_resources(tx, rx, 2, "random", seed=7)
    b = allocate_resources(tx, rx, 2, "random", seed=7)
    assert np.array_equal(a, b)
    assert set(a).issubset({0, 1})

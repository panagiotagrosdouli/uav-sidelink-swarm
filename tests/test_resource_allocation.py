import numpy as np

from src.sidelink.resource_allocation import (
    greedy_distance_aware_allocation,
    pair_conflict_weights,
    random_allocation,
    weighted_conflict_graph_allocation,
)


def test_random_allocation_is_reproducible():
    a = random_allocation(10, 3, 42).resources
    b = random_allocation(10, 3, 42).resources
    assert np.array_equal(a, b)


def test_greedy_allocation_returns_valid_resources():
    tx = np.array([[0, 0, 0], [10, 0, 0], [20, 0, 0]], dtype=float)
    rx = np.array([[1, 0, 0], [11, 0, 0], [21, 0, 0]], dtype=float)
    out = greedy_distance_aware_allocation(tx, rx, 2).resources
    assert len(out) == 3
    assert np.all((out >= 0) & (out < 2))


def test_conflict_weights_are_symmetric_and_zero_diagonal():
    tx = np.array([[0, 0, 0], [10, 0, 0], [20, 0, 0]], dtype=float)
    rx = np.array([[1, 0, 0], [11, 0, 0], [21, 0, 0]], dtype=float)
    w = pair_conflict_weights(tx, rx)
    assert np.allclose(w, w.T)
    assert np.allclose(np.diag(w), 0.0)
    assert np.all(w >= 0.0)


def test_weighted_conflict_graph_allocation_valid_and_deterministic():
    tx = np.array([[0, 0, 0], [10, 0, 0], [20, 0, 0], [30, 0, 0]], dtype=float)
    rx = tx + np.array([1.0, 0.0, 0.0])
    a = weighted_conflict_graph_allocation(tx, rx, 2).resources
    b = weighted_conflict_graph_allocation(tx, rx, 2).resources
    assert np.array_equal(a, b)
    assert np.all((a >= 0) & (a < 2))

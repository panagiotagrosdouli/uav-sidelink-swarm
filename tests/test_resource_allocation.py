import numpy as np

from src.sidelink.resource_allocation import (
    graph_conflict_allocation,
    greedy_distance_aware_allocation,
    random_allocation,
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


def test_graph_conflict_allocation_is_valid_and_deterministic():
    tx = np.array([[0, 0, 0], [10, 0, 0], [20, 0, 0], [30, 0, 0]], dtype=float)
    rx = np.array([[1, 0, 0], [11, 0, 0], [21, 0, 0], [31, 0, 0]], dtype=float)
    a = graph_conflict_allocation(tx, rx, 2)
    b = graph_conflict_allocation(tx, rx, 2)
    assert a.algorithm == "graph_conflict_weighted"
    assert np.array_equal(a.resources, b.resources)
    assert np.all((a.resources >= 0) & (a.resources < 2))

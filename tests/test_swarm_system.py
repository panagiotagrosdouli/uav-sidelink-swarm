import numpy as np

from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    build_nearest_disjoint_pairs,
    dbm_to_w,
    simulate_snapshot,
    thermal_noise_dbm,
)


def test_dbm_to_w_reference():
    assert np.isclose(float(dbm_to_w(0.0)), 1e-3)


def test_disjoint_pairs_are_half_duplex():
    pairs = build_disjoint_pairs(7)
    assert pairs == [(0, 1), (2, 3), (4, 5)]
    nodes = [x for pair in pairs for x in pair]
    assert len(nodes) == len(set(nodes))


def test_nearest_disjoint_pairs_are_local_and_half_duplex():
    positions = np.array([
        [0.0, 0.0, 100.0],
        [1.0, 0.0, 100.0],
        [100.0, 0.0, 100.0],
        [102.0, 0.0, 100.0],
        [300.0, 0.0, 100.0],
    ])
    pairs = build_nearest_disjoint_pairs(positions)
    assert pairs == [(0, 1), (2, 3)]
    nodes = [node for pair in pairs for node in pair]
    assert len(nodes) == len(set(nodes))


def test_nearest_pairing_snapshot_is_reproducible():
    cfg = SwarmConfig(n_uavs=20, seed=7, pairing="nearest_neighbor", activity_probability=1.0)
    p1, l1 = simulate_snapshot(cfg)
    p2, l2 = simulate_snapshot(cfg)
    assert p1.equals(p2)
    assert l1.equals(l2)
    assert set(l1.pairing) == {"nearest_neighbor"}


def test_snapshot_has_no_receiver_as_simultaneous_transmitter():
    cfg = SwarmConfig(n_uavs=10, seed=1, activity_probability=1.0)
    _, links = simulate_snapshot(cfg)
    txs = set(links.tx.tolist())
    rxs = set(links.rx.tolist())
    assert txs.isdisjoint(rxs)


def test_noise_is_finite():
    assert np.isfinite(thermal_noise_dbm(50e6, 7.0))


def test_snapshot_is_reproducible():
    cfg = SwarmConfig(n_uavs=10, seed=42, activity_probability=1.0)
    p1, l1 = simulate_snapshot(cfg)
    p2, l2 = simulate_snapshot(cfg)
    assert p1.equals(p2)
    assert l1.equals(l2)

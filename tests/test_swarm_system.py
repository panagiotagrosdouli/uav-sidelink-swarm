import numpy as np

from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    dbm_to_w,
    simulate_positions,
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


def test_orthogonal_resources_remove_cochannel_interference():
    cfg = SwarmConfig(n_uavs=4, seed=1, activity_probability=1.0)
    positions = np.array(
        [[0.0, 0.0, 100.0], [10.0, 0.0, 100.0], [0.0, 10.0, 100.0], [10.0, 10.0, 100.0]]
    )
    active = np.array([True, True])
    _, shared = simulate_positions(cfg, positions, resources=[0, 0], active_mask=active)
    _, separate = simulate_positions(cfg, positions, resources=[0, 1], active_mask=active)
    assert np.all(shared.n_interferers.to_numpy() == 1)
    assert np.all(separate.n_interferers.to_numpy() == 0)
    assert np.all(separate.sinr_db.to_numpy() > shared.sinr_db.to_numpy())


def test_directional_terms_have_expected_sign():
    cfg = SwarmConfig(n_uavs=4, seed=2, activity_probability=1.0)
    positions = np.array(
        [[0.0, 0.0, 100.0], [50.0, 0.0, 100.0], [0.0, 50.0, 100.0], [50.0, 50.0, 100.0]]
    )
    active = [True, True]
    _, baseline = simulate_positions(cfg, positions, active_mask=active)
    _, improved = simulate_positions(
        cfg,
        positions,
        active_mask=active,
        desired_gain_db=3.0,
        interference_suppression_db=3.0,
    )
    assert np.all(improved.rx_power_dbm.to_numpy() > baseline.rx_power_dbm.to_numpy())
    assert np.all(improved.interference_dbm.to_numpy() < baseline.interference_dbm.to_numpy())
    assert np.all(improved.sinr_db.to_numpy() > baseline.sinr_db.to_numpy())

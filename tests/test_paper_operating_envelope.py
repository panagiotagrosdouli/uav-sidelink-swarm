from simulations.paper_operating_envelope import grid_for_prbs, prb_partition


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


def test_exact_prb_occupied_bandwidth_matches_ofdm_definition():
    from simulations.paper_robustness import exact_prb_occupied_bandwidth_hz

    assert exact_prb_occupied_bandwidth_hz(133, 30) == 47_880_000.0
    assert exact_prb_occupied_bandwidth_hz(1, 30) == 360_000.0


def test_reviewer_pairing_and_allocator_helpers_are_deterministic():
    import numpy as np
    from simulations.paper_robustness import choose_pairs, choose_resources

    positions = np.array([
        [0.0, 0.0, 100.0],
        [1.0, 0.0, 100.0],
        [10.0, 0.0, 100.0],
        [11.0, 0.0, 100.0],
    ])
    pairs = choose_pairs("nearest_neighbor", positions, 4)
    assert pairs == [(0, 1), (2, 3)]

    tx = np.array([positions[t] for t, _ in pairs])
    rx = np.array([positions[r] for _, r in pairs])
    a = choose_resources("random", tx, rx, 2, seed=7)
    b = choose_resources("random", tx, rx, 2, seed=7)
    assert np.array_equal(a, b)

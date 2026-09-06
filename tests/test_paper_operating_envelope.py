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

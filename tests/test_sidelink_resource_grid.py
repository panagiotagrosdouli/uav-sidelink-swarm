import pytest

from src.sidelink.resource_grid import SidelinkResourceGrid, thesis_profile_50mhz_30khz


def test_thesis_profile_resource_accounting():
    grid = thesis_profile_50mhz_30khz()
    assert grid.n_prb == 133
    assert grid.slot_duration_ms == pytest.approx(0.5)
    assert grid.raw_pssch_re_per_prb == 132
    assert grid.usable_re_per_prb == 108
    assert grid.pssch_dmrs_overhead_fraction == pytest.approx(24 / 132)


def test_overhead_reduces_tbs():
    ideal = SidelinkResourceGrid(n_pscch_symbols=0, n_guard_symbols=0, n_pssch_symbols=14, dmrs_re_per_prb=0)
    realistic_study = thesis_profile_50mhz_30khz()
    assert realistic_study.tbs_bits(6) < ideal.tbs_bits(6)


def test_invalid_symbol_budget_rejected():
    with pytest.raises(ValueError):
        SidelinkResourceGrid(n_pscch_symbols=3, n_guard_symbols=2, n_pssch_symbols=10)

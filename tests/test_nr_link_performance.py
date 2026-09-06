import math
from pathlib import Path

from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.sidelink.link_performance import BlerCurve, first_tx_success_probability
from src.sidelink.nr_mcs import get_mcs


def test_standard_mcs_table_anchor_values():
    assert get_mcs(0).modulation_order == 2
    assert get_mcs(0).target_code_rate_x1024 == 120
    assert math.isclose(get_mcs(0).spectral_efficiency, 0.2344)
    assert get_mcs(28).modulation_order == 6
    assert get_mcs(28).target_code_rate_x1024 == 948
    assert math.isclose(get_mcs(28).spectral_efficiency, 5.5547)


def test_bler_interpolation_and_success_probability():
    curve = BlerCurve(
        mcs_index=4,
        code_block_size=4096,
        base_graph=1,
        sinr_db=(1.73, 1.965, 2.2),
        bler=(0.4936275, 0.0659, 0.0018),
        source="5G-LENA",
    )
    assert math.isclose(float(curve.bler_at(1.965)), 0.0659)
    assert math.isclose(float(first_tx_success_probability(curve, 1.965)), 0.9341)
    assert 0.0659 < float(curve.bler_at(1.9)) < 0.4936275


def test_verified_fixture_loads_and_adapts():
    path = Path("data/reference/5glena_table1_bg1_cbs4096_subset.csv")
    curves = load_bler_curves(path, source="5G-LENA nr-eesm-t1.cc")
    selected = curves_for_cbs(curves, 4096, 1)
    assert [c.mcs_index for c in selected] == [4, 5, 6]
    choice = select_max_goodput_mcs(3.0, selected, bandwidth_mhz=50.0)
    assert choice is not None
    assert choice.mcs_index in {4, 5, 6}
    assert 0.0 <= choice.bler <= 1.0

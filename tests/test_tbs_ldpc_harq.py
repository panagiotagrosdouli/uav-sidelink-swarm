import math

from src.sidelink.harq import ideal_chase_combined_sinr_db, slot_duration_ms
from src.sidelink.ldpc import code_block_segmentation, select_base_graph
from src.sidelink.nr_tbs import data_re_per_prb, tbs_from_n_info


def test_small_tbs_quantization_is_standard_table_value():
    assert tbs_from_n_info(1000.0, 0.5) == 1032


def test_data_re_per_prb_cap():
    assert data_re_per_prb(14, 0, 0) == 156


def test_ldpc_base_graph_rules():
    assert select_base_graph(292, 0.9) == 2
    assert select_base_graph(3000, 0.5) == 2
    assert select_base_graph(5000, 0.5) == 1
    assert select_base_graph(10000, 0.2) == 2


def test_ldpc_segmentation_adds_cb_crc_when_needed():
    seg = code_block_segmentation(20000, 0.5)
    assert seg["base_graph"] == 1
    assert seg["code_blocks"] >= 3
    assert seg["code_block_crc_bits"] == 24


def test_nr_mu1_slot_duration():
    assert slot_duration_ms(1) == 0.5


def test_two_equal_chase_observations_gain_three_db():
    combined = ideal_chase_combined_sinr_db([0.0, 0.0])
    assert math.isclose(combined[0], 0.0, abs_tol=1e-12)
    assert math.isclose(combined[1], 10.0 * math.log10(2.0), rel_tol=1e-12)

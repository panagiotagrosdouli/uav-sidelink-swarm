from src.sidelink.adaptive_tb import load_preferred_bler_curves, select_tbs_aware_mcs


def test_select_tbs_aware_mcs_preserves_curve_source():
    curves, mode = load_preferred_bler_curves()
    choice = select_tbs_aware_mcs(0.0, curves)
    assert choice is not None
    assert choice.curve_source
    assert choice.success_probability >= 0.0
    assert choice.success_probability <= 1.0
    assert mode in {"FULL_5GLENA_V5_LOCAL", "BUNDLED_VERIFIED_SUBSET"}

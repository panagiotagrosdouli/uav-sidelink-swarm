from src.sidelink.adaptive_tb import load_preferred_bler_curves
from src.sidelink.tb_link_model import closest_curve


def _brute_force(curves, mcs_index, base_graph, requested_cbs_bits):
    candidates = [
        curve for (mcs, bg, _), curve in curves.items()
        if mcs == mcs_index and bg == base_graph
    ]
    if not candidates:
        raise ValueError
    return min(
        candidates,
        key=lambda c: (abs(c.code_block_size - requested_cbs_bits), c.code_block_size),
    )


def test_indexed_lookup_matches_brute_force_reference():
    curves, _ = load_preferred_bler_curves()
    combinations = sorted({(mcs, bg) for mcs, bg, _ in curves})
    for mcs, bg in combinations[:12]:
        cbs_values = sorted(cbs for cmcs, cbg, cbs in curves if cmcs == mcs and cbg == bg)
        requests = [cbs_values[0], cbs_values[-1], (cbs_values[0] + cbs_values[-1]) // 2]
        for requested in requests:
            assert closest_curve(curves, mcs, bg, requested) is _brute_force(curves, mcs, bg, requested)


def test_indexed_lookup_is_stable_across_repeated_calls():
    curves, _ = load_preferred_bler_curves()
    mcs, bg, cbs = next(iter(curves))
    first = closest_curve(curves, mcs, bg, cbs)
    second = closest_curve(curves, mcs, bg, cbs)
    assert first is second

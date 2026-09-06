"""Transport-block-aware mapping from sourced code-block BLER curves.

The BLER curves come from link-level simulation. 3GPP supplies TBS/LDPC rules,
not these numerical BLER curves. TB error probability below assumes independent
code-block decoding events, so it is a DERIVED system-level approximation.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.sidelink.ldpc import code_block_segmentation
from src.sidelink.link_performance import BlerCurve
from src.sidelink.nr_mcs import get_mcs
from src.sidelink.resource_grid import SidelinkResourceGrid


@dataclass(frozen=True)
class TbLinkEstimate:
    mcs_index: int
    tbs_bits: int
    base_graph: int
    code_blocks: int
    requested_cbs_bits: int
    curve_cbs_bits: int
    code_block_bler: float
    transport_block_bler: float

    @property
    def first_tx_success_probability(self) -> float:
        return 1.0 - self.transport_block_bler


@dataclass(frozen=True)
class TbMcsChoice:
    """THIS_WORK_LINK_ADAPTATION choice for one SINR/resource-grid point."""

    mcs_index: int
    tbs_bits: int
    base_graph: int
    requested_cbs_bits: int
    curve_cbs_bits: int
    transport_block_bler: float
    first_tx_success_probability: float
    expected_delivered_bits_per_slot: float
    expected_first_tx_goodput_mbps: float


def closest_curve(
    curves: dict[tuple[int, int, int], BlerCurve],
    mcs_index: int,
    base_graph: int,
    requested_cbs_bits: int,
) -> BlerCurve:
    candidates = [
        curve
        for (mcs, bg, _), curve in curves.items()
        if mcs == mcs_index and bg == base_graph
    ]
    if not candidates:
        raise ValueError(f"no sourced curve for MCS={mcs_index}, BG={base_graph}")
    return min(candidates, key=lambda c: (abs(c.code_block_size - requested_cbs_bits), c.code_block_size))


def estimate_tb_bler(
    curves: dict[tuple[int, int, int], BlerCurve],
    mcs_index: int,
    tbs_bits: int,
    sinr_db: float,
) -> TbLinkEstimate:
    mcs = get_mcs(mcs_index)
    seg = code_block_segmentation(tbs_bits, mcs.target_code_rate)
    requested_cbs = seg["nominal_code_block_size"]
    curve = closest_curve(curves, mcs_index, seg["base_graph"], requested_cbs)
    cb_bler = float(curve.bler_at(sinr_db))
    c = seg["code_blocks"]
    # Explicit system-level approximation: code-block decoding events are
    # treated as independent to obtain transport-block error probability.
    tb_bler = 1.0 - (1.0 - cb_bler) ** c
    return TbLinkEstimate(
        mcs_index=mcs_index,
        tbs_bits=tbs_bits,
        base_graph=seg["base_graph"],
        code_blocks=c,
        requested_cbs_bits=requested_cbs,
        curve_cbs_bits=curve.code_block_size,
        code_block_bler=cb_bler,
        transport_block_bler=tb_bler,
    )


def select_tbs_aware_mcs(
    curves: dict[tuple[int, int, int], BlerCurve],
    sinr_db: float,
    grid: SidelinkResourceGrid,
    *,
    candidate_mcs: list[int] | tuple[int, ...] | None = None,
    max_transport_block_bler: float | None = None,
) -> TbMcsChoice | None:
    """Choose the sourced MCS with maximum expected first-TX delivered bits.

    This is THIS_WORK_LINK_ADAPTATION. It is not a normative 3GPP AMC algorithm.
    A BLER constraint, when supplied, is an EXPERIMENTAL policy target.
    """
    if max_transport_block_bler is not None and not 0.0 <= max_transport_block_bler <= 1.0:
        raise ValueError("max_transport_block_bler must lie in [0,1]")
    available = sorted({mcs for mcs, _, _ in curves})
    requested = available if candidate_mcs is None else sorted(set(candidate_mcs))
    choices: list[TbMcsChoice] = []
    for mcs_index in requested:
        if mcs_index not in available:
            continue
        tbs_bits = grid.tbs_bits(mcs_index)
        try:
            estimate = estimate_tb_bler(curves, mcs_index, tbs_bits, sinr_db)
        except ValueError:
            # The upstream table can be sparse for a base graph/MCS pair.
            continue
        if (
            max_transport_block_bler is not None
            and estimate.transport_block_bler > max_transport_block_bler
        ):
            continue
        success = estimate.first_tx_success_probability
        delivered_bits = tbs_bits * success
        goodput_mbps = delivered_bits / (grid.slot_duration_ms * 1000.0)
        choices.append(
            TbMcsChoice(
                mcs_index=mcs_index,
                tbs_bits=tbs_bits,
                base_graph=estimate.base_graph,
                requested_cbs_bits=estimate.requested_cbs_bits,
                curve_cbs_bits=estimate.curve_cbs_bits,
                transport_block_bler=estimate.transport_block_bler,
                first_tx_success_probability=success,
                expected_delivered_bits_per_slot=delivered_bits,
                expected_first_tx_goodput_mbps=goodput_mbps,
            )
        )
    if not choices:
        return None
    return max(
        choices,
        key=lambda c: (c.expected_delivered_bits_per_slot, -c.transport_block_bler, -c.mcs_index),
    )

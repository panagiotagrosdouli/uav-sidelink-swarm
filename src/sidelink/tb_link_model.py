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


# `closest_curve` is called very frequently by TBS-aware link adaptation.  The
# full 5G-LENA Table-1 dictionary is immutable during an experiment, so indexing
# it once by (MCS, base graph) avoids repeatedly scanning every sourced curve.
# The cache stores the original dictionary object alongside the index to guard
# against Python object-id reuse; curve-selection semantics and tie-breaking are
# otherwise unchanged.
_CURVE_INDEX_CACHE: dict[
    int,
    tuple[
        dict[tuple[int, int, int], BlerCurve],
        dict[tuple[int, int], tuple[BlerCurve, ...]],
    ],
] = {}


def _curve_index(
    curves: dict[tuple[int, int, int], BlerCurve],
) -> dict[tuple[int, int], tuple[BlerCurve, ...]]:
    cache_key = id(curves)
    cached = _CURVE_INDEX_CACHE.get(cache_key)
    if cached is not None and cached[0] is curves:
        return cached[1]

    grouped: dict[tuple[int, int], list[BlerCurve]] = {}
    for (mcs, bg, _), curve in curves.items():
        grouped.setdefault((int(mcs), int(bg)), []).append(curve)
    index = {
        key: tuple(sorted(group, key=lambda curve: curve.code_block_size))
        for key, group in grouped.items()
    }
    _CURVE_INDEX_CACHE[cache_key] = (curves, index)
    return index


def closest_curve(
    curves: dict[tuple[int, int, int], BlerCurve],
    mcs_index: int,
    base_graph: int,
    requested_cbs_bits: int,
) -> BlerCurve:
    candidates = _curve_index(curves).get((int(mcs_index), int(base_graph)), ())
    if not candidates:
        raise ValueError(f"no sourced curve for MCS={mcs_index}, BG={base_graph}")
    # Exact historical semantics: minimize absolute CBS error; on an equal
    # distance choose the smaller sourced CBS.
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

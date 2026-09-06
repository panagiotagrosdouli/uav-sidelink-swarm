"""TBS-aware system-level link adaptation over sourced BLER curve dictionaries."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import SidelinkResourceGrid, thesis_profile_50mhz_30khz
from src.sidelink.tb_link_model import estimate_tb_bler

FULL_BLER_PATH = Path("data/generated/5glena_v5_table1_bler.csv")
FIXTURE_BLER_PATH = Path("data/reference/5glena_table1_bg1_cbs4096_subset.csv")


@dataclass(frozen=True)
class TbLinkChoice:
    mcs_index: int
    tbs_bits: int
    base_graph: int
    requested_cbs_bits: int
    curve_cbs_bits: int
    tb_bler: float
    success_probability: float
    expected_goodput_mbps: float
    curve_source: str


def load_preferred_bler_curves():
    """Prefer locally generated official v5.0 data, otherwise verified fixture."""
    if FULL_BLER_PATH.exists():
        return load_bler_curves(FULL_BLER_PATH, source="official 5G-LENA v5.0 processed local Table-1 dataset"), "FULL_5GLENA_V5_LOCAL"
    return load_bler_curves(FIXTURE_BLER_PATH, source="verified 5G-LENA Table1 BG1 CBS4096 MCS4/5/6 subset"), "BUNDLED_VERIFIED_SUBSET"


def select_tbs_aware_mcs(
    sinr_db: float,
    curves,
    grid: SidelinkResourceGrid | None = None,
    candidate_mcs: list[int] | tuple[int, ...] | None = None,
) -> TbLinkChoice | None:
    """Choose available MCS maximizing first-TX expected delivered bits/slot.

    This is THIS_WORK link adaptation, not normative 3GPP AMC. CBS/base graph are
    determined from the standards-based TBS/LDPC path, then mapped to the closest
    sourced curve for the same MCS/BG by `estimate_tb_bler`.
    """
    grid = grid or thesis_profile_50mhz_30khz()
    available = sorted({int(key[0]) for key in curves})
    if candidate_mcs is not None:
        allowed = set(int(m) for m in candidate_mcs)
        available = [m for m in available if m in allowed]
    choices: list[TbLinkChoice] = []
    for mcs in available:
        try:
            tbs = grid.tbs_bits(mcs)
            estimate = estimate_tb_bler(curves, mcs, tbs, float(sinr_db))
        except (ValueError, KeyError):
            continue
        success = estimate.first_tx_success_probability
        goodput = (tbs * success / grid.slot_duration_ms) / 1000.0
        source_curve = curves[(mcs, estimate.base_graph, estimate.curve_cbs_bits)]
        choices.append(TbLinkChoice(
            mcs_index=mcs,
            tbs_bits=tbs,
            base_graph=estimate.base_graph,
            requested_cbs_bits=estimate.requested_cbs_bits,
            curve_cbs_bits=estimate.curve_cbs_bits,
            tb_bler=estimate.transport_block_bler,
            success_probability=success,
            expected_goodput_mbps=goodput,
            curve_source=source_curve.source,
        ))
    return max(choices, key=lambda x: (x.expected_goodput_mbps, -x.mcs_index)) if choices else None

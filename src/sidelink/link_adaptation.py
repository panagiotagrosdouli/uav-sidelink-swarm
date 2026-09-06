"""Simple system-level MCS selection over available sourced BLER curves."""
from __future__ import annotations

from dataclasses import dataclass

from src.sidelink.link_performance import BlerCurve, spectral_goodput_mbps


@dataclass(frozen=True)
class LinkChoice:
    mcs_index: int
    bler: float
    first_tx_success_probability: float
    expected_phy_goodput_mbps: float


def select_max_goodput_mcs(
    sinr_db: float,
    curves: list[BlerCurve],
    bandwidth_mhz: float,
    max_bler: float | None = None,
) -> LinkChoice | None:
    """Choose the available sourced curve with highest expected PHY goodput.

    `max_bler`, when supplied, is an EXPERIMENTAL policy constraint and must not
    be called a 3GPP-required BLER target unless separately sourced.
    """
    if not curves:
        return None
    candidates: list[LinkChoice] = []
    for curve in curves:
        bler = float(curve.bler_at(sinr_db))
        if max_bler is not None and bler > max_bler:
            continue
        goodput = float(spectral_goodput_mbps(curve, sinr_db, bandwidth_mhz))
        candidates.append(
            LinkChoice(
                mcs_index=curve.mcs_index,
                bler=bler,
                first_tx_success_probability=1.0 - bler,
                expected_phy_goodput_mbps=goodput,
            )
        )
    if not candidates:
        return None
    return max(candidates, key=lambda x: x.expected_phy_goodput_mbps)

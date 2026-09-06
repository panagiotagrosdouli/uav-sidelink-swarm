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
    resource_fraction: float = 1.0,
) -> LinkChoice | None:
    """Choose the available sourced curve with highest expected PHY goodput.

    This is THIS_WORK link adaptation, not normative 3GPP AMC. `max_bler`, when
    supplied, is an EXPERIMENTAL policy constraint. `resource_fraction` accounts
    for an explicitly modeled orthogonal resource share and defaults to one for
    backward compatibility.
    """
    if not curves:
        return None
    if not 0.0 < resource_fraction <= 1.0:
        raise ValueError("resource_fraction must be in (0,1]")
    candidates: list[LinkChoice] = []
    for curve in curves:
        bler = float(curve.bler_at(sinr_db))
        if max_bler is not None and bler > max_bler:
            continue
        goodput = float(
            spectral_goodput_mbps(
                curve,
                sinr_db,
                bandwidth_mhz,
                resource_fraction=resource_fraction,
            )
        )
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
    return max(candidates, key=lambda x: (x.expected_phy_goodput_mbps, -x.mcs_index))

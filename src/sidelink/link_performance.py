"""Link-performance primitives for sourced SINR->BLER curves.

BLER curves are NOT 3GPP-standard measurements. They must carry provenance from
a link-level simulator/measurement source (e.g. 5G-LENA EESM tables). This
module only provides interpolation and derived probability/goodput metrics.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.sidelink.nr_mcs import get_mcs


@dataclass(frozen=True)
class BlerCurve:
    mcs_index: int
    code_block_size: int
    base_graph: int
    sinr_db: tuple[float, ...]
    bler: tuple[float, ...]
    source: str
    source_classification: str = "LINK_LEVEL_SIMULATION"

    def __post_init__(self) -> None:
        if len(self.sinr_db) != len(self.bler) or len(self.sinr_db) < 2:
            raise ValueError("SINR and BLER arrays must have equal length >= 2")
        if any(b < 0.0 or b > 1.0 for b in self.bler):
            raise ValueError("BLER values must lie in [0, 1]")
        if any(b <= a for a, b in zip(self.sinr_db, self.sinr_db[1:])):
            raise ValueError("SINR points must be strictly increasing")

    def bler_at(self, sinr_db: float | np.ndarray) -> np.ndarray:
        """Piecewise-linear interpolation, clamped to edge BLER values."""
        x = np.asarray(sinr_db, dtype=float)
        return np.interp(x, self.sinr_db, self.bler, left=self.bler[0], right=self.bler[-1])


def first_tx_success_probability(curve: BlerCurve, sinr_db: float | np.ndarray) -> np.ndarray:
    """Derived first-transmission success probability = 1 - BLER."""
    return 1.0 - curve.bler_at(sinr_db)


def spectral_goodput_mbps(
    curve: BlerCurve,
    sinr_db: float | np.ndarray,
    bandwidth_mhz: float,
    resource_fraction: float = 1.0,
) -> np.ndarray:
    """Idealized PHY goodput from sourced MCS SE and sourced BLER.

    This is still a DERIVED system-level metric: it does not include PSCCH/DMRS,
    guard bands, MAC/RLC/IP overhead, retransmission timing or scheduler losses.
    """
    if bandwidth_mhz <= 0:
        raise ValueError("bandwidth_mhz must be positive")
    if not 0.0 < resource_fraction <= 1.0:
        raise ValueError("resource_fraction must be in (0, 1]")
    se = get_mcs(curve.mcs_index).spectral_efficiency
    success = first_tx_success_probability(curve, sinr_db)
    return bandwidth_mhz * se * resource_fraction * success


def independent_attempt_success_probability(bler: float, attempts: int) -> float:
    """Simple independent-attempt approximation; NOT HARQ combining.

    Kept only for sensitivity analysis. Do not label this as NR HARQ performance.
    """
    if not 0.0 <= bler <= 1.0:
        raise ValueError("bler must be in [0, 1]")
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    return 1.0 - bler**attempts

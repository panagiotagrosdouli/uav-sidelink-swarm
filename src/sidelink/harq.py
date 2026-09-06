"""HARQ abstractions for system-level sensitivity studies.

5G-LENA v5.0 supports EESM HARQ-CC and HARQ-IR history processing. This Python
module does NOT duplicate that complete implementation. It provides an ideal
Chase-Combining abstraction: repeated observations of the same coded packet are
combined by summing linear SINR. This is DERIVED/IDEALIZED, not a 3GPP timing
rule and not measured UAV HARQ performance.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from src.sidelink.tb_link_model import estimate_tb_bler
from src.sidelink.link_performance import BlerCurve


@dataclass(frozen=True)
class HarqEstimate:
    attempts_max: int
    combined_sinr_db: tuple[float, ...]
    bler_after_attempt: tuple[float, ...]
    success_by_final_attempt: float
    expected_attempts_consumed: float
    expected_latency_ms: float
    expected_delivered_goodput_mbps: float


def slot_duration_ms(numerology_mu: int) -> float:
    """NR normal-CP slot duration: 1 ms / 2^mu (TS 38.211 numerology)."""
    if numerology_mu not in (0, 1, 2, 3, 4):
        raise ValueError("numerology_mu must be in 0..4")
    return 1.0 / (2**numerology_mu)


def ideal_chase_combined_sinr_db(per_attempt_sinr_db: list[float] | tuple[float, ...]) -> tuple[float, ...]:
    if not per_attempt_sinr_db:
        raise ValueError("at least one SINR value is required")
    total = 0.0
    out: list[float] = []
    for x_db in per_attempt_sinr_db:
        total += 10.0 ** (float(x_db) / 10.0)
        out.append(10.0 * math.log10(total))
    return tuple(out)


def estimate_ideal_chase_harq(
    curves: dict[tuple[int, int, int], BlerCurve],
    mcs_index: int,
    tbs_bits: int,
    per_attempt_sinr_db: list[float] | tuple[float, ...],
    numerology_mu: int,
    feedback_and_retx_gap_slots: int,
) -> HarqEstimate:
    """Estimate reliability/latency with ideal CC and explicit scheduling gap.

    `feedback_and_retx_gap_slots` is an EXPERIMENTAL/CONFIGURATION input. Exact
    PSFCH and retransmission timing depends on the sidelink resource-pool and
    scheduling configuration; this function deliberately does not hard-code it.
    """
    if feedback_and_retx_gap_slots < 0:
        raise ValueError("feedback_and_retx_gap_slots must be non-negative")
    combined = ideal_chase_combined_sinr_db(per_attempt_sinr_db)
    blers = tuple(
        estimate_tb_bler(curves, mcs_index, tbs_bits, sinr).transport_block_bler
        for sinr in combined
    )
    # Expected number of transmissions consumed: P(reach attempt k).
    expected_attempts = 1.0
    for prior_bler in blers[:-1]:
        expected_attempts += prior_bler

    slot_ms = slot_duration_ms(numerology_mu)
    # One transmission slot per attempt plus feedback/re-tx gap before attempts >1.
    expected_gap_count = max(0.0, expected_attempts - 1.0)
    latency_ms = expected_attempts * slot_ms + expected_gap_count * feedback_and_retx_gap_slots * slot_ms
    success = 1.0 - blers[-1]
    goodput_mbps = (tbs_bits * success / latency_ms) / 1000.0
    return HarqEstimate(
        attempts_max=len(per_attempt_sinr_db),
        combined_sinr_db=combined,
        bler_after_attempt=blers,
        success_by_final_attempt=success,
        expected_attempts_consumed=expected_attempts,
        expected_latency_ms=latency_ms,
        expected_delivered_goodput_mbps=goodput_mbps,
    )

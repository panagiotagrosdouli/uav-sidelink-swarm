"""Unified PHY/link metrics for system-level UAV swarm experiments.

This module keeps system geometry/interference separate from NR link abstraction.
BLER values come from sourced 5G-LENA curves; TBS/MCS/LDPC mechanics are
standard-derived; final reliability/goodput/latency remain DERIVED system-level
metrics.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.sidelink.harq import estimate_ideal_chase_harq
from src.sidelink.link_performance import BlerCurve
from src.sidelink.resource_grid import SidelinkResourceGrid
from src.sidelink.tb_link_model import estimate_tb_bler, select_tbs_aware_mcs


def annotate_nr_link_metrics(
    links: pd.DataFrame,
    curves: dict[tuple[int, int, int], BlerCurve],
    grid: SidelinkResourceGrid,
    *,
    mcs_policy: str | int = "adaptive",
    harq_attempts: int = 1,
    feedback_and_retx_gap_slots: int = 2,
    max_transport_block_bler: float | None = None,
) -> pd.DataFrame:
    """Attach TBS/BLER/goodput/HARQ metrics to a link table.

    ``mcs_policy='adaptive'`` uses THIS_WORK_LINK_ADAPTATION. Supplying an int
    evaluates a fixed MCS. HARQ attempts above one use the ideal Chase Combining
    abstraction already documented by the project.
    """
    if "sinr_db" not in links.columns:
        raise ValueError("links must contain sinr_db")
    if harq_attempts < 1:
        raise ValueError("harq_attempts must be >= 1")
    if feedback_and_retx_gap_slots < 0:
        raise ValueError("feedback_and_retx_gap_slots must be non-negative")

    rows: list[dict[str, object]] = []
    for record in links.to_dict(orient="records"):
        sinr_db = float(record["sinr_db"])
        if mcs_policy == "adaptive":
            choice = select_tbs_aware_mcs(
                curves,
                sinr_db,
                grid,
                max_transport_block_bler=max_transport_block_bler,
            )
            if choice is None:
                rows.append(
                    {
                        **record,
                        "selected_mcs": np.nan,
                        "tbs_bits": np.nan,
                        "tb_bler": 1.0,
                        "first_tx_success_probability": 0.0,
                        "first_tx_goodput_mbps": 0.0,
                        "harq_success_probability": 0.0,
                        "expected_attempts": float(harq_attempts),
                        "harq_latency_ms": np.nan,
                        "harq_goodput_mbps": 0.0,
                        "link_model_status": "no_supported_curve",
                    }
                )
                continue
            mcs = choice.mcs_index
            tbs = choice.tbs_bits
            first_bler = choice.transport_block_bler
            first_success = choice.first_tx_success_probability
            first_goodput = choice.expected_first_tx_goodput_mbps
        elif isinstance(mcs_policy, int):
            mcs = int(mcs_policy)
            tbs = grid.tbs_bits(mcs)
            try:
                estimate = estimate_tb_bler(curves, mcs, tbs, sinr_db)
            except ValueError:
                rows.append(
                    {
                        **record,
                        "selected_mcs": mcs,
                        "tbs_bits": tbs,
                        "tb_bler": np.nan,
                        "first_tx_success_probability": np.nan,
                        "first_tx_goodput_mbps": np.nan,
                        "harq_success_probability": np.nan,
                        "expected_attempts": np.nan,
                        "harq_latency_ms": np.nan,
                        "harq_goodput_mbps": np.nan,
                        "link_model_status": "fixed_mcs_curve_unavailable",
                    }
                )
                continue
            first_bler = estimate.transport_block_bler
            first_success = estimate.first_tx_success_probability
            first_goodput = tbs * first_success / (grid.slot_duration_ms * 1000.0)
        else:
            raise ValueError("mcs_policy must be 'adaptive' or an integer MCS index")

        if harq_attempts == 1:
            harq_success = first_success
            expected_attempts = 1.0
            harq_latency = grid.slot_duration_ms
            harq_goodput = first_goodput
        else:
            harq = estimate_ideal_chase_harq(
                curves,
                mcs,
                tbs,
                [sinr_db] * harq_attempts,
                numerology_mu=1,
                feedback_and_retx_gap_slots=feedback_and_retx_gap_slots,
            )
            harq_success = harq.success_by_final_attempt
            expected_attempts = harq.expected_attempts_consumed
            harq_latency = harq.expected_latency_ms
            harq_goodput = harq.expected_delivered_goodput_mbps

        rows.append(
            {
                **record,
                "selected_mcs": mcs,
                "tbs_bits": tbs,
                "tb_bler": first_bler,
                "first_tx_success_probability": first_success,
                "first_tx_goodput_mbps": first_goodput,
                "harq_success_probability": harq_success,
                "expected_attempts": expected_attempts,
                "harq_latency_ms": harq_latency,
                "harq_goodput_mbps": harq_goodput,
                "link_model_status": "ok",
            }
        )
    return pd.DataFrame(rows)


def aggregate_link_metrics(
    links: pd.DataFrame,
    columns: Iterable[str] = (
        "sinr_db",
        "tb_bler",
        "first_tx_success_probability",
        "first_tx_goodput_mbps",
        "harq_success_probability",
        "expected_attempts",
        "harq_latency_ms",
        "harq_goodput_mbps",
    ),
) -> dict[str, float]:
    """Return finite per-snapshot means without changing metric provenance."""
    out: dict[str, float] = {}
    for column in columns:
        if column not in links.columns:
            continue
        values = pd.to_numeric(links[column], errors="coerce").to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        out[f"mean_{column}"] = float(np.mean(finite)) if len(finite) else float("nan")
        out[f"median_{column}"] = float(np.median(finite)) if len(finite) else float("nan")
    out["evaluated_links"] = float(len(links))
    return out

"""TBS/CBS-aware reliability and ideal Chase-HARQ latency study.

Standard anchors:
- 50 MHz / 30 kHz SCS -> 133 PRBs (3GPP TS 38.104 Table 5.3.2-1)
- mu=1 -> 0.5 ms slot duration (3GPP NR numerology)
- TBS/LDPC rules from TS 38.214 / TS 38.212

BLER source:
- verified 5G-LENA Table-1 BG1/CBS4096 subset (MCS 4/5/6)

Important: PSSCH DM-RS/PSCCH overhead and HARQ feedback/retransmission gaps depend
on sidelink configuration. This experiment uses an explicit idealized data-grid
profile and sweeps the gap; those inputs are not field measurements.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.sidelink.bler_io import load_bler_curves
from src.sidelink.harq import estimate_ideal_chase_harq
from src.sidelink.nr_mcs import get_mcs
from src.sidelink.nr_tbs import n_info_bits, tbs_from_n_info
from src.sidelink.tb_link_model import estimate_tb_bler
from src.swarm_system import SwarmConfig, simulate_snapshot

N_PRB = 133
NUMEROLOGY_MU = 1
N_SYMBOLS = 12
# Kept explicit instead of pretending one sidelink DM-RS/PSCCH layout is universal.
DMRS_RE_PER_PRB = 0
OTHER_OVERHEAD_RE_PER_PRB = 0
MCS_CANDIDATES = (4, 5, 6)
MAX_ATTEMPTS = 4
GAP_SLOT_SWEEP = (1, 2, 4, 8)


def choose_mcs(curves, sinr_db: float) -> tuple[int, int, float]:
    """Choose MCS by maximum first-transmission delivered bits per slot."""
    best = None
    for mcs_index in MCS_CANDIDATES:
        mcs = get_mcs(mcs_index)
        ninfo = n_info_bits(
            mcs_index=mcs_index,
            n_prb=N_PRB,
            n_symbols=N_SYMBOLS,
            dmrs_re_per_prb=DMRS_RE_PER_PRB,
            other_overhead_re_per_prb=OTHER_OVERHEAD_RE_PER_PRB,
        )
        tbs = tbs_from_n_info(ninfo, mcs.target_code_rate)
        try:
            est = estimate_tb_bler(curves, mcs_index, tbs, sinr_db)
        except ValueError:
            continue
        expected_bits = tbs * est.first_tx_success_probability
        candidate = (expected_bits, mcs_index, tbs, est.transport_block_bler)
        if best is None or candidate > best:
            best = candidate
    if best is None:
        raise ValueError("no sourced BLER curve available for candidate MCS values")
    _, mcs_index, tbs, bler = best
    return mcs_index, tbs, bler


def main() -> None:
    curves = load_bler_curves(
        "data/reference/5glena_table1_bg1_cbs4096_subset.csv",
        source="5G-LENA nr-eesm-t1.cc; verified Table1 BG1 CBS4096 subset",
    )
    rows: list[dict[str, float | int]] = []
    for n_uavs in [5, 10, 20, 30, 50]:
        for seed in range(100):
            cfg = SwarmConfig(
                n_uavs=n_uavs,
                seed=seed,
                channel="measured_a2a",
                carrier_ghz=3.5,
                bandwidth_mhz=50.0,
                tx_power_dbm=30.0,
            )
            _, links = simulate_snapshot(cfg)
            for link in links.itertuples(index=False):
                sinr = float(link.sinr_db)
                try:
                    mcs_index, tbs, first_bler = choose_mcs(curves, sinr)
                except ValueError:
                    continue
                first = estimate_tb_bler(curves, mcs_index, tbs, sinr)
                for gap_slots in GAP_SLOT_SWEEP:
                    harq = estimate_ideal_chase_harq(
                        curves=curves,
                        mcs_index=mcs_index,
                        tbs_bits=tbs,
                        per_attempt_sinr_db=[sinr] * MAX_ATTEMPTS,
                        numerology_mu=NUMEROLOGY_MU,
                        feedback_and_retx_gap_slots=gap_slots,
                    )
                    rows.append({
                        "n_uavs": n_uavs,
                        "seed": seed,
                        "link_id": int(link.link_id),
                        "sinr_db": sinr,
                        "selected_mcs": mcs_index,
                        "tbs_bits": tbs,
                        "base_graph": first.base_graph,
                        "code_blocks": first.code_blocks,
                        "requested_cbs_bits": first.requested_cbs_bits,
                        "curve_cbs_bits": first.curve_cbs_bits,
                        "first_tx_tb_bler": first_bler,
                        "harq_max_attempts": MAX_ATTEMPTS,
                        "feedback_retx_gap_slots": gap_slots,
                        "success_by_final_attempt": harq.success_by_final_attempt,
                        "expected_attempts": harq.expected_attempts_consumed,
                        "expected_latency_ms": harq.expected_latency_ms,
                        "expected_delivered_goodput_mbps": harq.expected_delivered_goodput_mbps,
                    })

    df = pd.DataFrame(rows)
    out = Path("results/harq_tbs_latency")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_link.csv", index=False)
    summary = df.groupby(["n_uavs", "feedback_retx_gap_slots"]).agg(
        mean_sinr_db=("sinr_db", "mean"),
        mean_first_tx_tb_bler=("first_tx_tb_bler", "mean"),
        mean_success_by_final_attempt=("success_by_final_attempt", "mean"),
        mean_expected_attempts=("expected_attempts", "mean"),
        mean_expected_latency_ms=("expected_latency_ms", "mean"),
        mean_expected_delivered_goodput_mbps=("expected_delivered_goodput_mbps", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

"""TBS/CBS-aware reliability and ideal Chase-HARQ latency study.

STANDARD anchors: 50 MHz / 30 kHz -> 133 PRBs, mu=1 -> 0.5 ms slot, TBS/LDPC
from TS 38.214/38.212. The concrete PSCCH/PSSCH/DM-RS layout comes from the
explicit thesis study profile and remains EXPERIMENTAL_CONFIGURATION. HARQ is an
ideal Chase-Combining abstraction; feedback gaps are EXPERIMENTAL_SWEEP.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.metrics import summarize
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.harq import estimate_ideal_chase_harq
from src.sidelink.nr_mcs import get_mcs
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.sidelink.tb_link_model import estimate_tb_bler
from src.swarm_system import SwarmConfig, simulate_snapshot

MCS_CANDIDATES = (4, 5, 6)
MAX_ATTEMPTS = 4
GAP_SLOT_SWEEP = (1, 2, 4, 8)
N_VALUES = [5, 10, 20, 30, 50, 75, 100]


def choose_mcs(curves, sinr_db: float) -> tuple[int, int, float]:
    grid = thesis_profile_50mhz_30khz()
    best = None
    for mcs_index in MCS_CANDIDATES:
        tbs = grid.tbs_bits(mcs_index)
        try:
            est = estimate_tb_bler(curves, mcs_index, tbs, sinr_db)
        except ValueError:
            continue
        expected_bits = tbs * est.first_tx_success_probability
        candidate = (expected_bits, -mcs_index, mcs_index, tbs, est.transport_block_bler)
        if best is None or candidate > best:
            best = candidate
    if best is None:
        raise ValueError("no sourced BLER curve available for candidate MCS values")
    _, _, mcs_index, tbs, bler = best
    return mcs_index, tbs, bler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    n_values = [5, 20, 50] if args.smoke else N_VALUES
    seeds = range(3 if args.smoke else args.seeds)
    gaps = (1, 4) if args.smoke else GAP_SLOT_SWEEP

    curves = load_bler_curves(
        "data/reference/5glena_table1_bg1_cbs4096_subset.csv",
        source="5G-LENA verified Table1 BG1 CBS4096 MCS4/5/6 subset",
    )
    rows: list[dict[str, float | int | str]] = []
    for n_uavs in n_values:
        for seed in seeds:
            cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a", carrier_ghz=3.5, bandwidth_mhz=50.0, tx_power_dbm=30.0)
            _, links = simulate_snapshot(cfg)
            for link in links.itertuples(index=False):
                sinr = float(link.sinr_db)
                try:
                    mcs_index, tbs, first_bler = choose_mcs(curves, sinr)
                except ValueError:
                    continue
                first = estimate_tb_bler(curves, mcs_index, tbs, sinr)
                for gap_slots in gaps:
                    harq = estimate_ideal_chase_harq(
                        curves=curves,
                        mcs_index=mcs_index,
                        tbs_bits=tbs,
                        per_attempt_sinr_db=[sinr] * MAX_ATTEMPTS,
                        numerology_mu=1,
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
                        "resource_grid_classification": "EXPERIMENTAL_CONFIGURATION",
                        "harq_classification": "DERIVED_SYSTEM_LEVEL_HARQ_ABSTRACTION",
                    })

    df = pd.DataFrame(rows)
    out = Path("results/harq_tbs_latency")
    figs = Path("figures/harq_tbs_latency")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_link.csv", index=False)

    per_seed = df.groupby(["n_uavs", "feedback_retx_gap_slots", "seed"], as_index=False).agg(
        mean_first_tx_tb_bler=("first_tx_tb_bler", "mean"),
        mean_success_by_final_attempt=("success_by_final_attempt", "mean"),
        mean_expected_attempts=("expected_attempts", "mean"),
        mean_expected_latency_ms=("expected_latency_ms", "mean"),
        mean_expected_delivered_goodput_mbps=("expected_delivered_goodput_mbps", "mean"),
    )
    per_seed.to_csv(out / "per_seed.csv", index=False)

    summary_rows = []
    for (n, gap), group in per_seed.groupby(["n_uavs", "feedback_retx_gap_slots"]):
        row = {"n_uavs": int(n), "feedback_retx_gap_slots": int(gap), "seeds": int(group.seed.nunique())}
        for metric in ["mean_first_tx_tb_bler", "mean_success_by_final_attempt", "mean_expected_attempts", "mean_expected_latency_ms", "mean_expected_delivered_goodput_mbps"]:
            for key, value in summarize(group[metric]).items():
                row[f"{metric}_{key}"] = value
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    for metric, ylabel, stem, ylim in [
        ("mean_success_by_final_attempt", "Mean success by final HARQ attempt", "success_vs_density", (0.0, 1.0)),
        ("mean_expected_latency_ms", "Mean modeled HARQ delivery latency [ms]", "latency_vs_density", None),
        ("mean_expected_delivered_goodput_mbps", "Mean HARQ delivered goodput [Mbps]", "goodput_vs_density", None),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for gap, group in summary.groupby("feedback_retx_gap_slots"):
            ax.plot(group.n_uavs, group[f"{metric}_mean"], marker="o", label=f"gap={gap} slots")
        ax.set_xlabel("Number of UAVs")
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_title(ylabel + " vs swarm size")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(figs / f"{stem}.png", dpi=300)
        fig.savefig(figs / f"{stem}.pdf")
        plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

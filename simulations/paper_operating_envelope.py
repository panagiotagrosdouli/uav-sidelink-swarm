"""Publication experiment: density x resources x directionality operating envelope.

Scientific semantics
--------------------
* RF/network outputs are DERIVED_SYSTEM_LEVEL_METRIC.
* Resource count and directional relative advantage are EXPERIMENTAL_SWEEP.
* The conflict-graph allocator is THIS_WORK, not normative NR Sidelink Mode 1/2.
* 133 FR1 PRBs are partitioned exactly across R orthogonal frequency resources.
  Each link uses the PRB count of its assigned resource, so resource separation
  changes co-channel interference, occupied noise bandwidth, TBS and LDPC/CBS.
* Directional relative advantage G is split as +G/2 dB desired gain and -G/2 dB
  co-channel interference gain. It is a sensitivity abstraction, not full MIMO.
* Numerical SINR->BLER curves are LINK_LEVEL_SIMULATION data from 5G-LENA.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import jain_fairness, mean_ci95
from src.sidelink.adaptive_tb import load_preferred_bler_curves, select_tbs_aware_mcs
from src.sidelink.resource_allocation import weighted_conflict_graph_allocation
from src.sidelink.resource_grid import SidelinkResourceGrid, thesis_profile_50mhz_30khz
from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    dbm_to_w,
    generate_equal_altitude_positions,
    received_power_w,
    thermal_noise_dbm,
)

N_VALUES = [5, 10, 20, 30, 50, 75, 100]
RESOURCE_COUNTS = [1, 2, 4, 8]
ADVANTAGES_DB = [0.0, 3.0, 6.0, 9.0]
SUCCESS_TARGET = 0.10
GOODPUT_TARGET_MBPS = 1.0
FAILURE_SUCCESS_POLICY = 0.50
TOTAL_PRB = 133


def prb_partition(n_resources: int) -> list[int]:
    """Balanced exact partition whose entries sum to the 133-PRB profile."""
    if n_resources < 1 or n_resources > TOTAL_PRB:
        raise ValueError("n_resources must be in [1, 133]")
    base, remainder = divmod(TOTAL_PRB, n_resources)
    return [base + (1 if i < remainder else 0) for i in range(n_resources)]


def grid_for_prbs(n_prb: int) -> SidelinkResourceGrid:
    base = thesis_profile_50mhz_30khz()
    return SidelinkResourceGrid(
        n_prb=n_prb,
        n_slot_symbols=base.n_slot_symbols,
        n_pscch_symbols=base.n_pscch_symbols,
        n_guard_symbols=base.n_guard_symbols,
        n_pssch_symbols=base.n_pssch_symbols,
        dmrs_re_per_prb=base.dmrs_re_per_prb,
        other_overhead_re_per_prb=base.other_overhead_re_per_prb,
        scs_khz=base.scs_khz,
    )


def snapshot(seed: int, n_uavs: int, n_resources: int, advantage_db: float, curves) -> dict[str, float | int]:
    cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a")
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(n_uavs)
    tx_pos = np.array([positions[t] for t, _ in pairs])
    rx_pos = np.array([positions[r] for _, r in pairs])
    resources = (
        np.zeros(len(pairs), dtype=int)
        if n_resources == 1
        else weighted_conflict_graph_allocation(tx_pos, rx_pos, n_resources).resources
    )
    partition = prb_partition(n_resources)
    desired_gain = 10.0 ** ((advantage_db / 2.0) / 10.0)
    interference_gain = 10.0 ** ((-advantage_db / 2.0) / 10.0)

    sinrs: list[float] = []
    successes: list[float] = []
    goodputs: list[float] = []
    dominant_fractions: list[float] = []
    n_interferers: list[int] = []
    failure_labels: list[str] = []
    unsupported = 0

    for i, (tx, rx) in enumerate(pairs):
        resource_id = int(resources[i])
        n_prb = partition[resource_id]
        grid = grid_for_prbs(n_prb)
        occupied_bandwidth_hz = cfg.bandwidth_mhz * 1e6 * (n_prb / TOTAL_PRB)
        noise_w = float(dbm_to_w(thermal_noise_dbm(occupied_bandwidth_hz, cfg.noise_figure_db)))

        signal_w, _, _ = received_power_w(tx, rx, positions, cfg)
        signal_w *= desired_gain
        interferers: list[float] = []
        for j, (other_tx, _) in enumerate(pairs):
            if j == i or int(resources[j]) != resource_id:
                continue
            p_w, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interferers.append(float(p_w * interference_gain))
        interference_w = float(sum(interferers))
        sinr_db = float(10.0 * np.log10(signal_w / (noise_w + interference_w)))
        choice = select_tbs_aware_mcs(sinr_db, curves, grid=grid)

        if choice is None:
            unsupported += 1
            success = 0.0
            goodput = 0.0
        else:
            success = float(choice.success_probability)
            goodput = float(choice.expected_goodput_mbps)

        dominant_fraction = float(max(interferers) / interference_w) if interference_w > 0.0 else 0.0
        if success < FAILURE_SUCCESS_POLICY:
            if interference_w / noise_w < 1.0:
                failure_labels.append("noise_limited")
            elif dominant_fraction >= 0.5:
                failure_labels.append("dominant_interferer")
            else:
                failure_labels.append("aggregate_interference")

        sinrs.append(sinr_db)
        successes.append(success)
        goodputs.append(goodput)
        dominant_fractions.append(dominant_fraction)
        n_interferers.append(len(interferers))

    failed = max(len(failure_labels), 1)
    return {
        "mean_sinr_db": float(np.mean(sinrs)),
        "mean_first_tx_success": float(np.mean(successes)),
        "mean_expected_goodput_mbps": float(np.mean(goodputs)),
        "jain_goodput_fairness": jain_fairness(goodputs),
        "mean_dominant_interferer_fraction": float(np.mean(dominant_fractions)),
        "mean_n_cochannel_interferers": float(np.mean(n_interferers)),
        "failed_link_fraction": float(len(failure_labels) / len(pairs)),
        "failure_dominant_fraction": float(failure_labels.count("dominant_interferer") / failed) if failure_labels else 0.0,
        "failure_aggregate_fraction": float(failure_labels.count("aggregate_interference") / failed) if failure_labels else 0.0,
        "failure_noise_fraction": float(failure_labels.count("noise_limited") / failed) if failure_labels else 0.0,
        "unsupported_link_fraction": float(unsupported / len(pairs)),
    }


def summarize_group(group: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for column in columns:
        mean, lo, hi = mean_ci95(group[column])
        out[column] = mean
        out[f"{column}_ci95_low"] = lo
        out[f"{column}_ci95_high"] = hi
    return out


def save_heatmap(summary: pd.DataFrame, gain_db: float, metric: str, label: str, stem: str, figs: Path) -> None:
    q = summary[summary.directional_relative_advantage_db == gain_db]
    pivot = q.pivot(index="n_uavs", columns="n_resources", values=metric).sort_index()
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    im = ax.imshow(pivot.values, aspect="auto", origin="lower")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_xlabel("Orthogonal frequency resources (exact 133-PRB partition)")
    ax.set_ylabel("UAVs")
    ax.set_title(f"{label}, directional relative advantage {gain_db:g} dB")
    fig.colorbar(im, ax=ax, label=label)
    fig.tight_layout()
    fig.savefig(figs / f"{stem}_g{int(gain_db)}.pdf")
    fig.savefig(figs / f"{stem}_g{int(gain_db)}.png", dpi=300)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--require-full-curves", action="store_true")
    args = parser.parse_args()

    curves, curve_mode = load_preferred_bler_curves()
    if args.require_full_curves and curve_mode != "FULL_5GLENA_V5_LOCAL":
        raise RuntimeError("publication campaign requires locally prepared official 5G-LENA v5.0 full Table-1 curves")

    # The bundled fixture is intentionally limited; smoke validates the supported R=1 path.
    ns = [5, 20] if args.smoke else N_VALUES
    rs = [1] if args.smoke else RESOURCE_COUNTS
    gs = [0.0, 6.0] if args.smoke else ADVANTAGES_DB
    seeds = range(2 if args.smoke else args.seeds)

    out = Path("results/paper_operating_envelope")
    figs = Path("figures/paper_operating_envelope")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for n in ns:
        for r in rs:
            for g in gs:
                for seed in seeds:
                    metrics = snapshot(seed, n, r, g, curves)
                    rows.append({
                        "n_uavs": n,
                        "n_resources": r,
                        "prb_partition": "+".join(str(x) for x in prb_partition(r)),
                        "directional_relative_advantage_db": g,
                        "desired_gain_db": g / 2.0,
                        "cochannel_interference_gain_db": -g / 2.0,
                        "seed": seed,
                        "curve_mode": curve_mode,
                        **metrics,
                    })

    raw = pd.DataFrame(rows)
    raw.to_csv(out / "per_seed.csv", index=False)
    if not args.smoke and float(raw.unsupported_link_fraction.max()) > 0.0:
        raise RuntimeError("full publication grid contains links without a sourced same-MCS/base-graph BLER curve")

    metric_columns = [
        "mean_sinr_db",
        "mean_first_tx_success",
        "mean_expected_goodput_mbps",
        "jain_goodput_fairness",
        "mean_dominant_interferer_fraction",
        "mean_n_cochannel_interferers",
        "failed_link_fraction",
        "failure_dominant_fraction",
        "failure_aggregate_fraction",
        "failure_noise_fraction",
        "unsupported_link_fraction",
    ]
    summary_rows: list[dict] = []
    for keys, group in raw.groupby(["n_uavs", "n_resources", "directional_relative_advantage_db"]):
        n, r, g = keys
        summary_rows.append({
            "n_uavs": int(n),
            "n_resources": int(r),
            "prb_partition": "+".join(str(x) for x in prb_partition(int(r))),
            "directional_relative_advantage_db": float(g),
            **summarize_group(group, metric_columns),
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    envelope_rows: list[dict] = []
    for (r, g), group in summary.groupby(["n_resources", "directional_relative_advantage_db"]):
        qualifying = group[
            (group.mean_first_tx_success >= SUCCESS_TARGET)
            & (group.mean_expected_goodput_mbps >= GOODPUT_TARGET_MBPS)
        ]
        envelope_rows.append({
            "n_resources": int(r),
            "prb_partition": "+".join(str(x) for x in prb_partition(int(r))),
            "directional_relative_advantage_db": float(g),
            "success_target": SUCCESS_TARGET,
            "goodput_target_mbps": GOODPUT_TARGET_MBPS,
            "max_evaluated_n_meeting_both_targets": int(qualifying.n_uavs.max()) if len(qualifying) else 0,
            "classification": "DERIVED_SYSTEM_LEVEL_METRIC_FROM_EXPERIMENTAL_POLICY_TARGETS",
        })
    envelope = pd.DataFrame(envelope_rows)
    envelope.to_csv(out / "operating_envelope.csv", index=False)

    if not args.smoke:
        for g in gs:
            save_heatmap(summary, g, "mean_first_tx_success", "Mean first-TX success", "success_heatmap", figs)
            save_heatmap(summary, g, "mean_expected_goodput_mbps", "Mean expected goodput [Mbps]", "goodput_heatmap", figs)

        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for g, group in envelope.groupby("directional_relative_advantage_db"):
            group = group.sort_values("n_resources")
            ax.plot(group.n_resources, group.max_evaluated_n_meeting_both_targets, marker="o", label=f"G={g:g} dB")
        ax.set_xlabel("Orthogonal frequency resources")
        ax.set_ylabel("Max evaluated N meeting both policy targets")
        ax.set_title(f"Operating envelope: success >= {SUCCESS_TARGET:.2f}, goodput >= {GOODPUT_TARGET_MBPS:.1f} Mbps")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(figs / "operating_envelope.pdf")
        fig.savefig(figs / "operating_envelope.png", dpi=300)
        plt.close(fig)

        selected = summary[
            ((summary.n_resources == 1) & (summary.directional_relative_advantage_db == 0.0))
            | ((summary.n_resources == 8) & (summary.directional_relative_advantage_db == 6.0))
        ].copy()
        selected["configuration"] = np.where(
            selected.n_resources == 1, "baseline R=1,G=0", "mitigated R=8,G=6"
        )
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for label, group in selected.groupby("configuration"):
            group = group.sort_values("n_uavs")
            ax.plot(group.n_uavs, group.failure_aggregate_fraction, marker="o", label=f"aggregate — {label}")
            ax.plot(group.n_uavs, group.failure_dominant_fraction, marker="x", linestyle="--", label=f"dominant — {label}")
        ax.set_xlabel("UAVs")
        ax.set_ylabel("Fraction among policy-failed links")
        ax.set_ylim(0.0, 1.0)
        ax.set_title("Failure-regime composition")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(figs / "failure_regime_comparison.pdf")
        fig.savefig(figs / "failure_regime_comparison.png", dpi=300)
        plt.close(fig)

    print(f"BLER curve mode: {curve_mode}")
    print(envelope.to_string(index=False))


if __name__ == "__main__":
    main()

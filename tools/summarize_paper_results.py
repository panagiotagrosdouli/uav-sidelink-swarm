"""Generate publication statistics and cautious key findings.

Reads the primary operating-envelope campaign and the reviewer-sensitivity
campaign. All statistics are DERIVED_SYSTEM_LEVEL_METRIC and matched by the same
deterministic geometry seed.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.statistical_tests import paired_comparison

BASE = Path("results/paper_operating_envelope")
SENSITIVITY = Path("results/paper_reviewer_sensitivity")

BASELINE = (1, 0.0)
COMPARISONS = [(8, 0.0), (1, 6.0), (2, 6.0), (4, 6.0), (8, 6.0), (1, 9.0)]
PRIMARY_METRICS = ["mean_first_tx_success", "mean_expected_goodput_mbps"]


def _primary_scenario(df: pd.DataFrame, n: int, resource: int, gain: float) -> pd.DataFrame:
    return df[
        (df.n_uavs == n)
        & (df.n_resources == resource)
        & (df.directional_relative_advantage_db == gain)
    ].sort_values("seed")


def _effect_row(comp, **metadata) -> dict:
    return {
        **metadata,
        "classification": "DERIVED_SYSTEM_LEVEL_METRIC_MATCHED_SEED_COMPARISON",
        **comp.__dict__,
    }


def summarize_primary_effects(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for n in sorted(raw.n_uavs.unique()):
        base = _primary_scenario(raw, int(n), *BASELINE)
        for resource, gain in COMPARISONS:
            treatment = _primary_scenario(raw, int(n), resource, gain)
            if len(base) != len(treatment) or not len(base):
                continue
            for metric in PRIMARY_METRICS:
                comp = paired_comparison(base[metric].to_numpy(), treatment[metric].to_numpy())
                rows.append(_effect_row(
                    comp,
                    n_uavs=int(n),
                    baseline_resources=BASELINE[0],
                    baseline_directional_relative_advantage_db=BASELINE[1],
                    treatment_resources=resource,
                    treatment_directional_relative_advantage_db=gain,
                    metric=metric,
                ))
    return pd.DataFrame(rows)


def summarize_allocator_effects(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    metrics = ["mean_sinr_db", "mean_first_tx_success", "mean_expected_goodput_mbps"]
    for (n, resource, gain), group in raw.groupby(
        ["n_uavs", "n_resources", "directional_relative_advantage_db"],
        sort=True,
    ):
        baseline = group[group.allocator_mode == "random"].sort_values("seed")
        treatment = group[group.allocator_mode == "weighted_conflict_graph"].sort_values("seed")
        if len(baseline) != len(treatment) or not len(baseline):
            continue
        if not baseline.seed.reset_index(drop=True).equals(treatment.seed.reset_index(drop=True)):
            raise RuntimeError("allocator comparison does not have matched deterministic seeds")
        for metric in metrics:
            comp = paired_comparison(baseline[metric].to_numpy(), treatment[metric].to_numpy())
            rows.append(_effect_row(
                comp,
                n_uavs=int(n),
                n_resources=int(resource),
                directional_relative_advantage_db=float(gain),
                baseline_allocator="random",
                treatment_allocator="weighted_conflict_graph",
                metric=metric,
            ))
    return pd.DataFrame(rows)


def summarize_pairing_effects(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    metrics = [
        "mean_desired_distance_m",
        "mean_sinr_db",
        "mean_first_tx_success",
        "mean_expected_goodput_mbps",
    ]
    for (n, resource, gain), group in raw.groupby(
        ["n_uavs", "n_resources", "directional_relative_advantage_db"],
        sort=True,
    ):
        baseline = group[group.pairing_mode == "sequential"].sort_values("seed")
        treatment = group[group.pairing_mode == "nearest_neighbor"].sort_values("seed")
        if len(baseline) != len(treatment) or not len(baseline):
            continue
        if not baseline.seed.reset_index(drop=True).equals(treatment.seed.reset_index(drop=True)):
            raise RuntimeError("pairing comparison does not have matched deterministic seeds")
        for metric in metrics:
            comp = paired_comparison(baseline[metric].to_numpy(), treatment[metric].to_numpy())
            rows.append(_effect_row(
                comp,
                n_uavs=int(n),
                n_resources=int(resource),
                directional_relative_advantage_db=float(gain),
                baseline_pairing="sequential",
                treatment_pairing="nearest_neighbor",
                metric=metric,
            ))
    return pd.DataFrame(rows)


def main() -> None:
    raw = pd.read_csv(BASE / "per_seed.csv")
    summary = pd.read_csv(BASE / "summary.csv")
    envelope = pd.read_csv(BASE / "operating_envelope.csv")

    effects = summarize_primary_effects(raw)
    effects.to_csv(BASE / "paired_effects.csv", index=False)

    allocator_raw = pd.read_csv(SENSITIVITY / "allocator_per_seed.csv")
    allocator_effects = summarize_allocator_effects(allocator_raw)
    allocator_effects.to_csv(SENSITIVITY / "allocator_paired_effects.csv", index=False)

    pairing_raw = pd.read_csv(SENSITIVITY / "pairing_per_seed.csv")
    pairing_effects = summarize_pairing_effects(pairing_raw)
    pairing_effects.to_csv(SENSITIVITY / "pairing_paired_effects.csv", index=False)

    lines = [
        "# Publication key findings\n\n",
        "Generated from committed matched-seed simulation tables. Metrics are simulated/derived, not measured swarm RF.\n\n",
    ]

    max_n = int(summary.n_uavs.max())
    nmax = summary[summary.n_uavs == max_n]
    baseline = nmax[
        (nmax.n_resources == 1)
        & (nmax.directional_relative_advantage_db == 0.0)
    ].iloc[0]
    mitigated = nmax[
        (nmax.n_resources == 8)
        & (nmax.directional_relative_advantage_db == 6.0)
    ].iloc[0]

    lines.append(
        f"- At N={max_n}, baseline R=1,G=0 gives mean SINR {baseline.mean_sinr_db:.2f} dB, "
        f"first-TX success {baseline.mean_first_tx_success:.3f}, and expected goodput "
        f"{baseline.mean_expected_goodput_mbps:.3f} Mbps.\n"
    )
    lines.append(
        f"- At N={max_n}, R=8,G=6 gives mean SINR {mitigated.mean_sinr_db:.2f} dB, "
        f"first-TX success {mitigated.mean_first_tx_success:.3f}, and expected goodput "
        f"{mitigated.mean_expected_goodput_mbps:.3f} Mbps. G is an experimental relative "
        "desired/interference advantage, not a full MIMO implementation.\n"
    )

    env_base = envelope[
        (envelope.n_resources == 1)
        & (envelope.directional_relative_advantage_db == 0.0)
    ].iloc[0]
    env_r8 = envelope[
        (envelope.n_resources == 8)
        & (envelope.directional_relative_advantage_db == 0.0)
    ].iloc[0]
    env_r2g6 = envelope[
        (envelope.n_resources == 2)
        & (envelope.directional_relative_advantage_db == 6.0)
    ].iloc[0]
    lines.append(
        f"- Under the explicit experimental policy success >= {env_base.success_target:.2f} and "
        f"goodput >= {env_base.goodput_target_mbps:.1f} Mbps, the largest evaluated N is "
        f"{int(env_base.max_evaluated_n_meeting_both_targets)} for R=1,G=0, "
        f"{int(env_r8.max_evaluated_n_meeting_both_targets)} for R=8,G=0, and "
        f"{int(env_r2g6.max_evaluated_n_meeting_both_targets)} for R=2,G=6. These are evaluated "
        "operating-envelope points, not universal swarm capacity limits.\n"
    )

    selected = effects[
        (effects.n_uavs == max_n)
        & (effects.treatment_resources == 8)
        & (effects.treatment_directional_relative_advantage_db == 6.0)
    ]
    for _, row in selected.iterrows():
        lines.append(
            f"- Matched-seed R=8,G=6 vs baseline at N={max_n}, metric {row.metric}: "
            f"mean difference {row.mean_difference:.4g}, Student-t 95% CI "
            f"[{row.ci95_low:.4g}, {row.ci95_high:.4g}], bootstrap 95% CI "
            f"[{row.bootstrap_ci95_low:.4g}, {row.bootstrap_ci95_high:.4g}], "
            f"Cohen dz={row.cohen_dz:.2f}, Wilcoxon p={row.wilcoxon_pvalue:.3g}.\n"
        )

    allocator_nmax = allocator_effects[
        (allocator_effects.n_uavs == max_n)
        & (allocator_effects.directional_relative_advantage_db == 0.0)
        & (allocator_effects.metric == "mean_first_tx_success")
    ]
    for _, row in allocator_nmax.iterrows():
        lines.append(
            f"- At N={max_n}, R={int(row.n_resources)}, G=0, weighted conflict-graph allocation "
            f"changes first-TX success relative to matched-seed random allocation by "
            f"{row.mean_difference:+.4f} (bootstrap 95% CI "
            f"[{row.bootstrap_ci95_low:.4f}, {row.bootstrap_ci95_high:.4f}]).\n"
        )

    pairing_nmax = pairing_effects[
        (pairing_effects.n_uavs == max_n)
        & (pairing_effects.n_resources == 1)
        & (pairing_effects.directional_relative_advantage_db == 0.0)
        & (pairing_effects.metric.isin(["mean_desired_distance_m", "mean_first_tx_success"]))
    ]
    for _, row in pairing_nmax.iterrows():
        lines.append(
            f"- At N={max_n}, shared-resource baseline, nearest-neighbour pairing changes "
            f"{row.metric} relative to sequential pairing by {row.mean_difference:+.4g} "
            f"(bootstrap 95% CI [{row.bootstrap_ci95_low:.4g}, {row.bootstrap_ci95_high:.4g}]).\n"
        )

    (BASE / "paper_key_findings.md").write_text("".join(lines), encoding="utf-8")
    print(effects.to_string(index=False))
    print(allocator_effects.to_string(index=False))
    print(pairing_effects.to_string(index=False))


if __name__ == "__main__":
    main()

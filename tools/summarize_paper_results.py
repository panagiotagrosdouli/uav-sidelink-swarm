"""Generate matched-seed publication statistics and cautious key findings.

Reads the completed paper operating-envelope per-seed/summary tables. All output
statistics remain DERIVED_SYSTEM_LEVEL_METRIC and comparisons are matched by seed.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.statistical_tests import paired_comparison

BASE = Path("results/paper_operating_envelope")
BASELINE = (1, 0.0)
COMPARISONS = [(8, 0.0), (1, 6.0), (2, 6.0), (4, 6.0), (8, 6.0), (1, 9.0)]
METRICS = ["mean_first_tx_success", "mean_expected_goodput_mbps"]


def _scenario(df: pd.DataFrame, n: int, resource: int, gain: float) -> pd.DataFrame:
    return df[
        (df.n_uavs == n)
        & (df.n_resources == resource)
        & (df.directional_relative_advantage_db == gain)
    ].sort_values("seed")


def main() -> None:
    raw = pd.read_csv(BASE / "per_seed.csv")
    summary = pd.read_csv(BASE / "summary.csv")
    envelope = pd.read_csv(BASE / "operating_envelope.csv")
    rows: list[dict] = []
    for n in sorted(raw.n_uavs.unique()):
        base = _scenario(raw, int(n), *BASELINE)
        for resource, gain in COMPARISONS:
            treatment = _scenario(raw, int(n), resource, gain)
            if len(base) != len(treatment) or not len(base):
                continue
            for metric in METRICS:
                comp = paired_comparison(base[metric].to_numpy(), treatment[metric].to_numpy())
                rows.append({
                    "n_uavs": int(n),
                    "baseline_resources": BASELINE[0],
                    "baseline_directional_relative_advantage_db": BASELINE[1],
                    "treatment_resources": resource,
                    "treatment_directional_relative_advantage_db": gain,
                    "metric": metric,
                    "classification": "DERIVED_SYSTEM_LEVEL_METRIC_MATCHED_SEED_COMPARISON",
                    **comp.__dict__,
                })
    effects = pd.DataFrame(rows)
    effects.to_csv(BASE / "paired_effects.csv", index=False)

    lines = [
        "# Publication key findings\n\n",
        "Generated from the committed 100-seed publication tables. Metrics are simulated/derived, not measured swarm RF.\n\n",
    ]
    max_n = int(summary.n_uavs.max())
    nmax = summary[summary.n_uavs == max_n]
    baseline = nmax[(nmax.n_resources == 1) & (nmax.directional_relative_advantage_db == 0.0)].iloc[0]
    mitigated = nmax[(nmax.n_resources == 8) & (nmax.directional_relative_advantage_db == 6.0)].iloc[0]
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
    env_base = envelope[(envelope.n_resources == 1) & (envelope.directional_relative_advantage_db == 0.0)].iloc[0]
    env_r8 = envelope[(envelope.n_resources == 8) & (envelope.directional_relative_advantage_db == 0.0)].iloc[0]
    env_r2g6 = envelope[(envelope.n_resources == 2) & (envelope.directional_relative_advantage_db == 6.0)].iloc[0]
    lines.append(
        f"- Under the explicit experimental policy success >= {env_base.success_target:.2f} and "
        f"goodput >= {env_base.goodput_target_mbps:.1f} Mbps, the largest evaluated N is "
        f"{int(env_base.max_evaluated_n_meeting_both_targets)} for R=1,G=0, "
        f"{int(env_r8.max_evaluated_n_meeting_both_targets)} for R=8,G=0, and "
        f"{int(env_r2g6.max_evaluated_n_meeting_both_targets)} for R=2,G=6. These are evaluated "
        "operating-envelope points, not universal swarm capacity limits.\n"
    )
    e = effects[
        (effects.n_uavs == max_n)
        & (effects.treatment_resources == 8)
        & (effects.treatment_directional_relative_advantage_db == 6.0)
    ]
    for _, row in e.iterrows():
        lines.append(
            f"- Matched-seed R=8,G=6 vs baseline at N={max_n}, metric `{row.metric}`: "
            f"mean difference {row.mean_difference:.4g}, 95% CI [{row.ci95_low:.4g}, {row.ci95_high:.4g}], "
            f"Cohen dz={row.cohen_dz:.2f}, paired-t p={row.paired_t_pvalue:.3g}.\n"
        )
    (BASE / "paper_key_findings.md").write_text("".join(lines), encoding="utf-8")
    print(effects.to_string(index=False))


if __name__ == "__main__":
    main()

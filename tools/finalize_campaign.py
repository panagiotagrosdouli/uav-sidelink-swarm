"""Collate canonical experimental outputs into final_campaign directories.

Run the full registered thesis pipeline first, then call this finalizer. It copies
stable figure names, collates summary tables, writes a manifest, performs
range/sanity audits and generates cautious key findings only from existing data.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RESULT_OUT = Path("results/final_campaign")
FIG_OUT = Path("figures/final_campaign")

FIGURE_MAP = {
    "fig01_channel_models": "figures/pathloss/pathloss_comparison.pdf",
    "fig02_sinr_density": "figures/density/mean_sinr_vs_swarm_size.pdf",
    "fig03_sinr_cdf": "figures/density/sinr_cdf.pdf",
    "fig04_bler_density": "figures/nr_link_performance/bler_vs_density.pdf",
    "fig05_goodput_density": "figures/nr_link_performance/goodput_vs_density.pdf",
    "fig06_latency_density": "figures/harq_tbs_latency/latency_vs_density.pdf",
    "fig07_resource_allocation": "figures/resource_allocation/goodput_resources_n50.pdf",
    "fig08_routing": "figures/routing/direct_vs_multihop_reliability.pdf",
    "fig09_beamforming": "figures/beamforming/goodput_vs_directionality.pdf",
    "fig10_harq": "figures/harq_tbs_latency/success_vs_density.pdf",
    "fig11_real_mobility": "figures/mobility/real_pair_sinr_vs_time.pdf",
    "fig12_ablation": "figures/ablation/goodput_ablation.pdf",
    "fig13_scaling": "figures/scaling_geometry_activity/fixed_area_vs_fixed_density.pdf",
    "fig14_activity": "figures/scaling_geometry_activity/activity_factor_sinr.pdf",
    "fig15_failures": "figures/failure_analysis/failure_reason_vs_density.pdf",
    "fig16_ula": "figures/ula_directionality/ula_array_factor.pdf",
    "fig17_traffic": "figures/traffic_load/delivery_vs_density.pdf",
}

SUMMARY_SOURCES = {
    "density": "results/density_measurement_based/summary.csv",
    "nr_link_performance": "results/nr_link_performance/summary.csv",
    "harq": "results/harq_tbs_latency/summary.csv",
    "overhead": "results/sidelink_overhead/summary.csv",
    "resource_allocation": "results/resource_allocation/summary.csv",
    "routing": "results/routing/summary.csv",
    "directionality": "results/beamforming_sensitivity/summary.csv",
    "scaling": "results/scaling_geometry_activity/scaling_summary.csv",
    "activity": "results/scaling_geometry_activity/activity_summary.csv",
    "robustness_channel": "results/robustness/channel_summary.csv",
    "traffic": "results/traffic_load/summary.csv",
    "ablation": "results/ablation/summary.csv",
    "failure": "results/failure_analysis/summary.csv",
    "ula": "results/ula_directionality/summary.csv",
}

PROBABILITY_TOKENS = (
    "bler", "success_probability", "delivery_ratio", "fairness",
    "connectivity_probability", "fraction", "outage_proxy",
)
COUNT_NAMES = {"n", "count", "counts", "samples", "seeds"}


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _copy_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def _is_count_column(column: str) -> bool:
    name = column.lower()
    return (
        name in COUNT_NAMES
        or name.endswith("_n")
        or name.endswith("_count")
        or name.endswith("_counts")
        or name.endswith("_samples")
        or name.endswith("_seeds")
    )


def _audit_dataframe(name: str, df: pd.DataFrame) -> list[dict[str, str]]:
    """Audit numeric summary columns without confusing sample counts with metrics."""
    checks: list[dict[str, str]] = []
    for column in df.columns:
        numeric = pd.to_numeric(df[column], errors="coerce")
        if numeric.notna().sum() == 0:
            continue
        values = numeric.dropna().to_numpy(dtype=float)
        status = "pass"
        note = ""
        lower_name = column.lower()

        if _is_count_column(column):
            if np.any(values < -1e-12):
                status, note = "fail", "negative sample/count value"
            elif np.any(np.abs(values - np.rint(values)) > 1e-9):
                status, note = "fail", "non-integer sample/count value"
        else:
            if any(token in lower_name for token in PROBABILITY_TOKENS):
                if np.any((values < -1e-12) | (values > 1.0 + 1e-12)):
                    status, note = "fail", "probability/fraction outside [0,1]"
            if "latency" in lower_name and np.any(values < -1e-12):
                status, note = "fail", "negative latency"
            if "tbs" in lower_name and "bits" in lower_name and np.any(values <= 0):
                status, note = "fail", "non-positive TBS"

        checks.append({"dataset": name, "column": column, "status": status, "note": note})
    return checks


def _parameter_provenance(config: dict) -> pd.DataFrame:
    b = config["baseline"]
    r = config["nr_resource_profile"]
    return pd.DataFrame([
        ["carrier frequency", b["carrier_ghz"], "GHz", "LITERATURE", "Erdemir et al. VTC 2023 A2A campaign"],
        ["bandwidth", b["bandwidth_mhz"], "MHz", "LITERATURE", "Erdemir et al. VTC 2023 A2A campaign"],
        ["baseline TX power", b["tx_power_dbm"], "dBm", "LITERATURE", "Erdemir campaign value; not universal UAV power"],
        ["baseline altitude", b["altitude_m"], "m", "LITERATURE", "Erdemir A2A campaign"],
        ["baseline area side", b["area_xy_m"], "m", "SYNTHETIC", "final campaign configuration"],
        ["receiver noise figure", b["noise_figure_db"], "dB", "EXPERIMENTAL_ASSUMPTION", "sensitivity-tested"],
        ["PRBs", r["n_prb"], "PRB", "STANDARD", "50 MHz / 30 kHz FR1 profile"],
        ["SCS", r["scs_khz"], "kHz", "STANDARD", "NR numerology"],
        ["PSCCH symbols", r["n_pscch_symbols"], "symbols", "EXPERIMENTAL_CONFIGURATION", "thesis study profile"],
        ["PSSCH symbols", r["n_pssch_symbols"], "symbols", "EXPERIMENTAL_CONFIGURATION", "thesis study profile"],
        ["DM-RS overhead", r["dmrs_re_per_prb"], "RE/PRB", "EXPERIMENTAL_CONFIGURATION", "thesis study profile"],
    ], columns=["parameter", "value", "unit", "classification", "source_or_note"])


def _scenario_definitions(config: dict) -> pd.DataFrame:
    rows = []
    for n in config["campaign"]["swarm_sizes"]:
        rows.append({
            "scenario": "canonical_density",
            "n_uavs": n,
            "area_xy_m": config["baseline"]["area_xy_m"],
            "height_m": config["baseline"]["altitude_m"],
            "channel": config["baseline"]["channel"],
            "resources": 1,
            "traffic": "full-activity link snapshot",
            "seeds": config["campaign"]["seeds"],
        })
    return pd.DataFrame(rows)


def _write_key_findings(datasets: dict[str, pd.DataFrame], missing: list[str]) -> None:
    lines = [
        "# Evidence-backed key findings\n\n",
        "This file is generated from final-campaign result tables. Values are simulation/derived unless explicitly stated otherwise.\n\n",
    ]
    scaling = datasets.get("scaling")
    required = {"metric", "family", "n_uavs", "mean", "ci95_low", "ci95_high"}
    if scaling is not None and required.issubset(scaling.columns):
        sinr = scaling[scaling.metric == "mean_sinr_db"]
        for family in ["fixed_area", "fixed_density"]:
            group = sinr[sinr.family == family].sort_values("n_uavs")
            if len(group) >= 2:
                first, last = group.iloc[0], group.iloc[-1]
                lines.append(
                    f"- **Scaling ({family})**: mean SINR changes from {first['mean']:.2f} dB at N={int(first.n_uavs)} "
                    f"to {last['mean']:.2f} dB at N={int(last.n_uavs)}; final-point 95% CI "
                    f"[{last.ci95_low:.2f}, {last.ci95_high:.2f}] dB.\n"
                )
    ablation = datasets.get("ablation")
    if ablation is not None and "mean_goodput_mbps_mean" in ablation:
        max_n = int(ablation.n_uavs.max())
        group = ablation[ablation.n_uavs == max_n]
        if len(group):
            best = group.loc[group.mean_goodput_mbps_mean.idxmax()]
            lines.append(
                f"- **Ablation at N={max_n}**: highest mean modeled goodput among evaluated mechanisms is "
                f"`{best.scenario}` at {best.mean_goodput_mbps_mean:.3f} Mbps. This is system-level modeled goodput, not measured throughput.\n"
            )
    resource = datasets.get("resource_allocation")
    if resource is not None and "mean_expected_phy_goodput_mbps" in resource:
        max_n = int(resource.n_uavs.max())
        group = resource[resource.n_uavs == max_n]
        if len(group):
            best = group.loc[group.mean_expected_phy_goodput_mbps.idxmax()]
            lines.append(
                f"- **Resource allocation at N={max_n}**: highest mean derived PHY goodput in the evaluated grid occurs for "
                f"`{best.algorithm}` with {int(best.n_resources)} resources ({best.mean_expected_phy_goodput_mbps:.3f} Mbps).\n"
            )
    if missing:
        lines.append("\n## External/missing evidence\n")
        lines.extend(f"- {item}\n" for item in missing)
    (RESULT_OUT / "key_findings.md").write_text("".join(lines), encoding="utf-8")


def main() -> int:
    config_path = Path("config/final_campaign.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    RESULT_OUT.mkdir(parents=True, exist_ok=True)
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, RESULT_OUT / "final_campaign.yaml")

    datasets: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    audit: list[dict[str, str]] = []
    for name, source_str in SUMMARY_SOURCES.items():
        source = Path(source_str)
        if source.exists():
            df = pd.read_csv(source)
            datasets[name] = df
            df.to_csv(RESULT_OUT / f"{name}_summary.csv", index=False)
            audit.extend(_audit_dataframe(name, df))
        else:
            missing.append(f"Missing summary `{source}`")

    figure_status = []
    for stem, source_str in FIGURE_MAP.items():
        source = Path(source_str)
        copied = _copy_if_exists(source, FIG_OUT / f"{stem}.pdf")
        png_source = source.with_suffix(".png")
        if png_source.exists():
            _copy_if_exists(png_source, FIG_OUT / f"{stem}.png")
        figure_status.append({"figure": stem, "source": source_str, "present": copied})
        if stem == "fig11_real_mobility" and not copied:
            missing.append("Real AMOVFLY canonical figure is unavailable because raw external telemetry is not vendored; run real_mobility_pair with user-supplied AMOVFLY files.")

    bler_manifest = Path("data/generated/5glena_v5_table1_bler_manifest.json")
    if bler_manifest.exists():
        shutil.copy2(bler_manifest, RESULT_OUT / "5glena_v5_table1_bler_manifest.json")

    _parameter_provenance(config).to_csv(RESULT_OUT / "parameter_provenance.csv", index=False)
    _scenario_definitions(config).to_csv(RESULT_OUT / "scenario_definitions.csv", index=False)
    pd.DataFrame(audit).to_csv(RESULT_OUT / "scientific_audit.csv", index=False)
    pd.DataFrame(figure_status).to_csv(RESULT_OUT / "figure_manifest.csv", index=False)
    _write_key_findings(datasets, missing)

    failures = [row for row in audit if row["status"] == "fail"]
    manifest = {
        "campaign": config["campaign"]["name"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(),
        "python": sys.version,
        "platform": platform.platform(),
        "config": str(config_path),
        "summaries_present": sorted(datasets),
        "missing_external_or_optional": missing,
        "scientific_audit_failures": failures,
        "canonical_results_dir": str(RESULT_OUT),
        "canonical_figures_dir": str(FIG_OUT),
        "non_claims": config["non_claims"],
    }
    (RESULT_OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

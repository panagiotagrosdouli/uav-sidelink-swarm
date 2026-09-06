"""Canonical multi-dimensional UAV NR-sidelink experimental campaign.

This runner produces the final *experimental evidence base*, not thesis prose.
It preserves provenance across measurement-derived propagation, STANDARD NR
mechanics, 5G-LENA LINK_LEVEL_SIMULATION BLER data and explicit experimental
assumptions/sweeps.

Full mode uses the configured 100 deterministic seeds. ``--smoke`` uses the
small verified BLER fixture and reduced scenarios for CI. Full mode expects or
fetches the pinned 5G-LENA v5.0 processed table.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy import stats

from src.analysis.metrics import communication_energy_j
from src.channel_models.free_space import path_loss_db as fspl_path_loss_db
from src.channel_models.measured_a2a import path_loss_db as measured_path_loss_db
from src.channel_models.tr38901_a2a import (
    equal_height_umi_av_shadow_sigma_db,
    umi_av_los_path_loss_db,
)
from src.experiments.campaign_utils import evaluate_snapshot, summarize_groups
from src.experiments.routing_evaluation import evaluate_source_target_routes, pairwise_isolated_links
from src.mobility.synthetic import random_waypoint_tracks
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.swarm_geometry import generate_positions
from src.swarm_system import SwarmConfig, build_disjoint_pairs
from src.traffic import TrafficProfile, sample_slot_activity
from src.antenna.array_factor import ula_array_gain_db

METRICS = [
    "mean_sinr_db",
    "p05_sinr_db",
    "mean_tb_bler",
    "outage_bler_gt_0p1",
    "mean_first_tx_goodput_mbps",
    "mean_harq_goodput_mbps",
    "mean_harq_latency_ms",
    "goodput_fairness",
    "mean_interference_w",
]


def _config(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _ensure_curves(curves_path: Path, smoke: bool, fetch_full: bool) -> Path:
    if smoke:
        return Path("data/reference/5glena_table1_bg1_cbs4096_subset.csv")
    if curves_path.exists():
        return curves_path
    if not fetch_full:
        raise FileNotFoundError(
            f"full campaign requires {curves_path}; rerun with --fetch-full-bler"
        )
    subprocess.run(
        ["python", "-m", "tools.fetch_5glena_v5_bler", str(curves_path)],
        check=True,
    )
    return curves_path


def _seed_range(cfg: dict, smoke: bool) -> range:
    return range(int(cfg["smoke_seeds"] if smoke else cfg["full_seeds"]))


def _n_values(cfg: dict, smoke: bool) -> list[int]:
    values = [int(x) for x in cfg["swarm_sizes"]]
    return [5, 20, 50] if smoke else values


def _save(frame: pd.DataFrame, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out / f"{name}.csv", index=False)


def _lineplot(
    frame: pd.DataFrame,
    x: str,
    y: str,
    group: str | None,
    xlabel: str,
    ylabel: str,
    title: str,
    path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    if group is None:
        g = frame.sort_values(x)
        ax.plot(g[x], g[y], marker="o")
    else:
        for label, g in frame.groupby(group, sort=True):
            g = g.sort_values(x)
            ax.plot(g[x], g[y], marker="o", label=str(label))
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=300)
    fig.savefig(path.with_suffix(".pdf"))
    plt.close(fig)


def run_channel_models(cfg: dict, out: Path, figs: Path) -> pd.DataFrame:
    distances = np.geomspace(10.0, 2000.0, 160)
    rows = []
    for d in distances:
        fspl = float(fspl_path_loss_db(d, cfg["carrier_ghz"] * 1e9))
        measured = float(measured_path_loss_db(d))
        tr = float(umi_av_los_path_loss_db(d, cfg["altitude_baseline_m"], cfg["carrier_ghz"]))
        rows.append({
            "distance_m": d,
            "free_space_db": fspl,
            "measurement_derived_db": measured,
            "tr38901_umi_av_los_db": tr,
            "measured_minus_fspl_db": measured - fspl,
            "tr38901_minus_fspl_db": tr - fspl,
        })
    df = pd.DataFrame(rows)
    _save(df, out, "channel_models")
    long = df.melt("distance_m", ["free_space_db", "measurement_derived_db", "tr38901_umi_av_los_db"], "model", "path_loss_db")
    _lineplot(long, "distance_m", "path_loss_db", "model", "Distance [m]", "Path loss [dB]", "A2A propagation-model comparison", figs / "fig01_channel_models")
    return df


def run_density_scaling(cfg: dict, curves, grid, seeds: range, n_values: list[int], out: Path, figs: Path) -> pd.DataFrame:
    rows = []
    rho = float(cfg["reference_spatial_density_uavs_per_km2"])
    for family in ("fixed_area", "fixed_density"):
        for n in n_values:
            area = float(cfg["fixed_area_xy_m"]) if family == "fixed_area" else math.sqrt(n / rho * 1e6)
            for seed in seeds:
                scfg = SwarmConfig(n, seed, channel="measured_a2a", area_xy_m=area, altitude_m=cfg["altitude_baseline_m"], carrier_ghz=cfg["carrier_ghz"], bandwidth_mhz=cfg["bandwidth_mhz"], tx_power_dbm=cfg["tx_power_baseline_dbm"], noise_figure_db=cfg["noise_figure_baseline_db"], activity_probability=1.0)
                row, _, _ = evaluate_snapshot(scfg, curves, grid, n_resources=1, resource_algorithm="shared")
                row["scaling_family"] = family
                rows.append(row)
    raw = pd.DataFrame(rows)
    summary = summarize_groups(raw, ["scaling_family", "n_uavs"], METRICS)
    _save(raw, out, "density_scaling_per_seed")
    _save(summary, out, "density_scaling_summary")
    _lineplot(summary, "n_uavs", "mean_sinr_db_mean", "scaling_family", "Number of UAVs", "Mean SINR [dB]", "Fixed area vs fixed spatial density", figs / "fig02_sinr_density")
    _lineplot(summary, "n_uavs", "mean_tb_bler_mean", "scaling_family", "Number of UAVs", "Mean TB BLER", "Reliability scaling", figs / "fig04_bler_density")
    _lineplot(summary, "n_uavs", "mean_harq_goodput_mbps_mean", "scaling_family", "Number of UAVs", "Mean PHY goodput [Mbit/s]", "Goodput scaling", figs / "fig05_goodput_density")
    return raw


def run_density_cdf(raw: pd.DataFrame, curves, grid, cfg: dict, seeds: range, out: Path, figs: Path, smoke: bool) -> pd.DataFrame:
    rows = []
    selected_n = [5, 20, 50] if smoke else [5, 20, 50, 100]
    for n in selected_n:
        for seed in seeds:
            scfg = SwarmConfig(n, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"], tx_power_dbm=cfg["tx_power_baseline_dbm"], activity_probability=1.0)
            _, links, _ = evaluate_snapshot(scfg, curves, grid)
            for value in links.sinr_db.to_numpy(dtype=float):
                rows.append({"n_uavs": n, "sinr_db": value})
    df = pd.DataFrame(rows)
    _save(df, out, "sinr_cdf_source")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for n, g in df.groupby("n_uavs"):
        x = np.sort(g.sinr_db.to_numpy())
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(x, y, label=f"N={n}")
    ax.set_xlabel("SINR [dB]"); ax.set_ylabel("Empirical CDF"); ax.set_title("SINR distribution vs swarm density"); ax.grid(True, alpha=0.3); ax.legend(); fig.tight_layout()
    fig.savefig((figs / "fig03_sinr_cdf").with_suffix(".png"), dpi=300); fig.savefig((figs / "fig03_sinr_cdf").with_suffix(".pdf")); plt.close(fig)
    return df


def run_geometry(cfg: dict, curves, grid, seeds: range, out: Path) -> pd.DataFrame:
    rows = []
    for geometry in cfg["geometry_types"]:
        for seed in seeds:
            scfg = SwarmConfig(30, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
            row, _, _ = evaluate_snapshot(scfg, curves, grid, geometry=geometry)
            rows.append(row)
    raw = pd.DataFrame(rows); _save(raw, out, "geometry_per_seed"); _save(summarize_groups(raw, ["geometry"], METRICS), out, "geometry_summary"); return raw


def run_resources_activity(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path, smoke: bool) -> pd.DataFrame:
    resources = [1, 4] if smoke else cfg["resource_counts"]
    activities = [0.25, 1.0] if smoke else cfg["activity_probabilities"]
    algorithms = ["random", "greedy", "graph"]
    rows = []
    for r in resources:
        for p in activities:
            for alg in algorithms:
                for seed in seeds:
                    scfg = SwarmConfig(50, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], activity_probability=p, noise_figure_db=cfg["noise_figure_baseline_db"])
                    row, _, _ = evaluate_snapshot(scfg, curves, grid, n_resources=r, resource_algorithm=alg)
                    rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["n_resources", "activity_probability", "resource_algorithm"], METRICS)
    _save(raw, out, "resource_activity_per_seed"); _save(summary, out, "resource_activity_summary")
    subset = summary[summary.activity_probability == max(activities)]
    _lineplot(subset, "n_resources", "mean_sinr_db_mean", "resource_algorithm", "Abstract orthogonal resources", "Mean SINR [dB]", "Resource allocation under full activity", figs / "fig07_resource_allocation")
    return raw


def run_mcs_comparison(cfg: dict, curves, grid, seeds: range, out: Path) -> pd.DataFrame:
    rows = []
    policies: list[str | int] = ["adaptive", *[int(x) for x in cfg["fixed_mcs_comparison"]]]
    for policy in policies:
        for seed in seeds:
            scfg = SwarmConfig(30, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
            row, _, _ = evaluate_snapshot(scfg, curves, grid, mcs_policy=policy)
            row["mcs_policy"] = str(policy)
            rows.append(row)
    raw = pd.DataFrame(rows); _save(raw, out, "mcs_policy_per_seed"); _save(summarize_groups(raw, ["mcs_policy"], METRICS), out, "mcs_policy_summary"); return raw


def run_harq(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path, smoke: bool) -> pd.DataFrame:
    attempts = [1, 2, 4] if smoke else cfg["harq_attempts_sweep"]
    gaps = [2] if smoke else cfg["harq_feedback_gap_slots"]
    rows = []
    for a in attempts:
        for gap in gaps:
            for seed in seeds:
                scfg = SwarmConfig(30, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
                row, _, _ = evaluate_snapshot(scfg, curves, grid, harq_attempts=int(a), feedback_gap_slots=int(gap))
                row.update({"harq_attempts_max": a, "feedback_gap_slots": gap})
                rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["harq_attempts_max", "feedback_gap_slots"], METRICS)
    _save(raw, out, "harq_per_seed"); _save(summary, out, "harq_summary")
    _lineplot(summary[summary.feedback_gap_slots == gaps[0]], "harq_attempts_max", "mean_harq_latency_ms_mean", None, "Maximum HARQ attempts", "Mean modeled delivery latency [ms]", "Ideal Chase HARQ latency sensitivity", figs / "fig10_harq")
    return raw


def run_directionality(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path, smoke: bool) -> pd.DataFrame:
    gains = [0.0, 6.0] if smoke else cfg["directional_gain_db"]
    modes = ["desired", "suppression", "both"]
    rows = []
    for gain in gains:
        for mode in modes:
            for seed in seeds:
                scfg = SwarmConfig(50, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
                row, _, _ = evaluate_snapshot(scfg, curves, grid, desired_gain_db=gain if mode in ("desired", "both") else 0.0, interference_suppression_db=gain if mode in ("suppression", "both") else 0.0)
                row.update({"directionality_mode": mode, "directional_gain_db": gain})
                rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["directionality_mode", "directional_gain_db"], METRICS)
    _save(raw, out, "directionality_per_seed"); _save(summary, out, "directionality_summary")
    _lineplot(summary, "directional_gain_db", "mean_sinr_db_mean", "directionality_mode", "Directional gain/suppression [dB]", "Mean SINR [dB]", "Directionality sensitivity", figs / "fig09_beamforming")
    return raw


def run_channel_uncertainty(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path) -> pd.DataFrame:
    rows = []
    for channel in cfg["channel_models"]:
        for seed in seeds:
            scfg = SwarmConfig(30, seed, channel=channel, area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
            row, _, _ = evaluate_snapshot(scfg, curves, grid)
            rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["channel"], METRICS)
    _save(raw, out, "channel_uncertainty_per_seed"); _save(summary, out, "channel_uncertainty_summary")
    _lineplot(summary.assign(model_index=np.arange(len(summary))), "model_index", "mean_sinr_db_mean", "channel", "Model index", "Mean SINR [dB]", "System sensitivity to propagation model", figs / "fig18_channel_uncertainty")
    return raw


def run_robustness(cfg: dict, curves, grid, seeds: range, out: Path) -> pd.DataFrame:
    rows = []
    for nf in cfg["noise_figure_db_sweep"]:
        for seed in seeds:
            scfg = SwarmConfig(30, seed, channel="measured_a2a", noise_figure_db=nf, area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
            row, _, _ = evaluate_snapshot(scfg, curves, grid); row.update({"robustness_parameter": "noise_figure_db", "robustness_value": nf}); rows.append(row)
    for tx in cfg["tx_power_dbm_sweep"]:
        for seed in seeds:
            scfg = SwarmConfig(30, seed, channel="measured_a2a", tx_power_dbm=tx, noise_figure_db=cfg["noise_figure_baseline_db"], area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
            row, _, _ = evaluate_snapshot(scfg, curves, grid); row.update({"robustness_parameter": "tx_power_dbm", "robustness_value": tx}); rows.append(row)
    for h in cfg["altitude_m_sweep"]:
        sigma = equal_height_umi_av_shadow_sigma_db(float(h), los=True)
        for shadow in (0.0, sigma):
            for seed in seeds:
                scfg = SwarmConfig(30, seed, channel="tr38901_umi_av_los", altitude_m=h, area_xy_m=cfg["fixed_area_xy_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
                row, _, _ = evaluate_snapshot(scfg, curves, grid, shadow_fading_std_db=shadow)
                row.update({"robustness_parameter": "altitude_shadow", "robustness_value": h, "shadow_sigma_db": shadow}); rows.append(row)
    raw = pd.DataFrame(rows); _save(raw, out, "robustness_per_seed"); _save(summarize_groups(raw, ["robustness_parameter", "robustness_value", "shadow_sigma_db"], METRICS), out, "robustness_summary"); return raw


def run_traffic(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path) -> pd.DataFrame:
    rows = []
    for profile_data in cfg["traffic_profiles"]:
        profile = TrafficProfile(**profile_data)
        p = profile.slot_activity_probability(grid.slot_duration_ms)
        for seed in seeds:
            scfg = SwarmConfig(50, seed, channel="measured_a2a", activity_probability=1.0, area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
            n_links = len(build_disjoint_pairs(50))
            mask = sample_slot_activity(n_links, p, seed)
            row, _, _ = evaluate_snapshot(scfg, curves, grid, active_mask=mask)
            row.update({"traffic_profile": profile.name, "packet_size_bytes": profile.packet_size_bytes, "packet_rate_hz": profile.packet_rate_hz, "offered_load_per_link_mbps": profile.offered_load_mbps, "slot_activity_probability": p})
            rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["traffic_profile", "packet_rate_hz", "slot_activity_probability"], METRICS)
    _save(raw, out, "traffic_per_seed"); _save(summary, out, "traffic_summary")
    _lineplot(summary, "packet_rate_hz", "mean_sinr_db_mean", "traffic_profile", "Packet generation rate [Hz/link]", "Mean SINR [dB]", "Traffic-load/activity sensitivity", figs / "fig19_activity_factor")
    return raw


def run_routing(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path, smoke: bool) -> pd.DataFrame:
    rows = []
    n_values = [10, 20] if smoke else [10, 20, 30, 50]
    for n in n_values:
        for seed in seeds:
            scfg = SwarmConfig(n, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"], noise_figure_db=cfg["noise_figure_baseline_db"])
            pos = generate_positions("uniform", n, scfg.area_xy_m, scfg.altitude_m, seed)
            links = pairwise_isolated_links(scfg, pos, curves, grid, harq_attempts=2)
            routes = evaluate_source_target_routes(links, 0, n - 1, minimum_success_probability=0.9)
            for r in routes.to_dict(orient="records"):
                rows.append({"n_uavs": n, "seed": seed, **r})
    raw = pd.DataFrame(rows); _save(raw, out, "routing_per_seed")
    summary = raw.groupby(["n_uavs", "method"], as_index=False).agg(connectivity_probability=("route_exists", "mean"), mean_route_success_probability=("route_success_probability", "mean"), mean_hop_count=("hop_count", "mean"), mean_route_latency_ms=("route_latency_ms", "mean"))
    _save(summary, out, "routing_summary")
    _lineplot(summary, "n_uavs", "connectivity_probability", "method", "Number of UAVs", "Route-existence probability", "Routing connectivity abstraction", figs / "fig08_routing")
    return raw


def run_synthetic_mobility(cfg: dict, curves, grid, out: Path) -> pd.DataFrame:
    n = 20; times = np.arange(0.0, 20.0, 1.0); seed = 42
    p0 = generate_positions("uniform", n, cfg["fixed_area_xy_m"], cfg["altitude_baseline_m"], seed)
    tracks = random_waypoint_tracks(p0, times, cfg["fixed_area_xy_m"], 10.0, seed)
    rows = []
    for k, positions in enumerate(tracks):
        scfg = SwarmConfig(n, seed + k, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
        row, links, _ = evaluate_snapshot(scfg, curves, grid, positions=positions)
        row["time_s"] = times[k]
        row["successful_links_bler_le_0p1"] = int(np.sum(links.tb_bler <= 0.1)) if len(links) else 0
        rows.append(row)
    df = pd.DataFrame(rows); _save(df, out, "synthetic_mobility_timeseries"); return df


def run_ula(out: Path) -> pd.DataFrame:
    angles = np.linspace(-90.0, 90.0, 361); rows = []
    for n in (2, 4, 8, 16):
        gains = ula_array_gain_db(n, 0.0, angles)
        for angle, gain in zip(angles, gains):
            rows.append({"n_elements": n, "angle_deg": angle, "array_gain_db": float(gain), "classification": "PHYSICAL_ARRAY_FACTOR_ABSTRACTION"})
    df = pd.DataFrame(rows); _save(df, out, "ula_array_factor"); return df


def run_ablation(cfg: dict, curves, grid, seeds: range, out: Path, figs: Path) -> pd.DataFrame:
    stages = [
        ("baseline", 1, "shared", 0.0, 0.0, 1),
        ("adaptive_mcs", 1, "shared", 0.0, 0.0, 1),
        ("four_resources", 4, "random", 0.0, 0.0, 1),
        ("interference_aware", 4, "graph", 0.0, 0.0, 1),
        ("plus_harq", 4, "graph", 0.0, 0.0, 3),
        ("plus_directionality", 4, "graph", 6.0, 6.0, 3),
    ]
    rows = []
    for stage, nr, alg, dg, sup, harq in stages:
        for seed in seeds:
            scfg = SwarmConfig(50, seed, channel="measured_a2a", area_xy_m=cfg["fixed_area_xy_m"], altitude_m=cfg["altitude_baseline_m"])
            # baseline uses fixed MCS4 where supported; later stages use adaptive.
            policy = 4 if stage == "baseline" else "adaptive"
            row, _, _ = evaluate_snapshot(scfg, curves, grid, n_resources=nr, resource_algorithm=alg, desired_gain_db=dg, interference_suppression_db=sup, harq_attempts=harq, mcs_policy=policy)
            row["ablation_stage"] = stage; rows.append(row)
    raw = pd.DataFrame(rows); summary = summarize_groups(raw, ["ablation_stage"], METRICS)
    order = {name: i for i, (name, *_rest) in enumerate(stages)}; summary["stage_order"] = summary.ablation_stage.map(order); summary = summary.sort_values("stage_order")
    _save(raw, out, "ablation_per_seed"); _save(summary, out, "ablation_summary")
    _lineplot(summary, "stage_order", "mean_harq_goodput_mbps_mean", "ablation_stage", "Ablation stage index", "Mean delivered PHY goodput [Mbit/s]", "Incremental system-level mechanisms", figs / "fig12_ablation")
    return raw


def failure_analysis(frames: list[pd.DataFrame], out: Path) -> pd.DataFrame:
    candidates = [f for f in frames if "mean_tb_bler" in f.columns]
    combined = pd.concat(candidates, ignore_index=True, sort=False) if candidates else pd.DataFrame()
    if combined.empty:
        return combined
    failed = combined[pd.to_numeric(combined.mean_tb_bler, errors="coerce") > 0.1].copy()
    _save(failed, out, "failure_scenarios_bler_gt_0p1")
    return failed


def scaling_fit(density_raw: pd.DataFrame, out: Path) -> pd.DataFrame:
    fixed = density_raw[density_raw.scaling_family == "fixed_area"].groupby("n_uavs", as_index=False).mean(numeric_only=True)
    x = fixed.n_uavs.to_numpy(dtype=float); y = fixed.mean_sinr_db.to_numpy(dtype=float); rows = []
    models = {
        "linear_N": np.column_stack([np.ones_like(x), x]),
        "log_N": np.column_stack([np.ones_like(x), np.log(x)]),
        "power_basis": np.column_stack([np.ones_like(x), np.log(x)]),
    }
    for name, design in models.items():
        beta, *_ = np.linalg.lstsq(design, y, rcond=None); pred = design @ beta
        ss_res = float(np.sum((y - pred) ** 2)); ss_tot = float(np.sum((y - np.mean(y)) ** 2)); r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
        rows.append({"candidate_form": name, "intercept": beta[0], "slope": beta[1], "r_squared": r2, "classification": "EXPLORATORY_SCALING_FIT_NOT_PHYSICAL_LAW"})
    df = pd.DataFrame(rows).sort_values("r_squared", ascending=False); _save(df, out, "scaling_fit_candidates"); return df


def write_findings(out: Path, summaries: dict[str, pd.DataFrame]) -> None:
    lines = ["# Evidence-backed experimental observations", "", "Generated automatically from the canonical campaign. These are research-log observations, not thesis prose.", ""]
    density = summaries.get("density")
    if density is not None and not density.empty:
        fixed = density[density.scaling_family == "fixed_area"].sort_values("n_uavs")
        if len(fixed) >= 2:
            a, b = fixed.iloc[0], fixed.iloc[-1]
            lines += [f"- Fixed-area mean SINR changed from {a.mean_sinr_db_mean:.3f} dB at N={int(a.n_uavs)} to {b.mean_sinr_db_mean:.3f} dB at N={int(b.n_uavs)}. Classification: DERIVED system-level simulation.", ""]
    resource = summaries.get("resource")
    if resource is not None and not resource.empty:
        best = resource.sort_values("mean_harq_goodput_mbps_mean", ascending=False).iloc[0]
        lines += [f"- Highest mean goodput within the tested resource/activity/allocator grid was {best.mean_harq_goodput_mbps_mean:.3f} Mbit/s for R={int(best.n_resources)}, activity={best.activity_probability:.2f}, algorithm={best.resource_algorithm}. This is THIS_WORK/system-level, not normative Mode 2.", ""]
    lines += ["## Persistent limitations", "", "- No bit-accurate NR Sidelink PHY.", "- No measured swarm RF PDR/interference/latency.", "- HARQ uses ideal Chase Combining, not complete IR/CC history processing.", "- Resource labels are abstract orthogonal resources, not a normative Mode-2 scheduler.", "- Routing is a connectivity abstraction evaluated on isolated candidate links."]
    (out / "key_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/final_campaign.yaml")
    parser.add_argument("--curves", default="data/generated/5glena_v5_table1_full.csv")
    parser.add_argument("--fetch-full-bler", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output-dir", default="results/final_campaign")
    parser.add_argument("--figure-dir", default="figures/final_campaign")
    args = parser.parse_args()

    cfg = _config(args.config); out = Path(args.output_dir); figs = Path(args.figure_dir); out.mkdir(parents=True, exist_ok=True); figs.mkdir(parents=True, exist_ok=True)
    curves_path = _ensure_curves(Path(args.curves), args.smoke, args.fetch_full_bler)
    curves = load_bler_curves(curves_path, source="5G-LENA Table-1 processed BLER curves")
    grid = thesis_profile_50mhz_30khz(); seeds = _seed_range(cfg, args.smoke); n_values = _n_values(cfg, args.smoke)
    Path(out / "campaign_config_snapshot.yaml").write_text(Path(args.config).read_text(encoding="utf-8"), encoding="utf-8")

    run_channel_models(cfg, out, figs)
    density_raw = run_density_scaling(cfg, curves, grid, seeds, n_values, out, figs)
    run_density_cdf(density_raw, curves, grid, cfg, seeds, out, figs, args.smoke)
    geometry = run_geometry(cfg, curves, grid, seeds, out)
    resource = run_resources_activity(cfg, curves, grid, seeds, out, figs, args.smoke)
    mcs = run_mcs_comparison(cfg, curves, grid, seeds, out)
    harq = run_harq(cfg, curves, grid, seeds, out, figs, args.smoke)
    directionality = run_directionality(cfg, curves, grid, seeds, out, figs, args.smoke)
    channel = run_channel_uncertainty(cfg, curves, grid, seeds, out, figs)
    robustness = run_robustness(cfg, curves, grid, seeds, out)
    traffic = run_traffic(cfg, curves, grid, seeds, out, figs)
    routing = run_routing(cfg, curves, grid, seeds, out, figs, args.smoke)
    mobility = run_synthetic_mobility(cfg, curves, grid, out)
    ula = run_ula(out)
    ablation = run_ablation(cfg, curves, grid, seeds, out, figs)
    failure_analysis([density_raw, geometry, resource, mcs, harq, directionality, channel, robustness, traffic, ablation], out)
    scaling_fit(density_raw, out)

    density_summary = pd.read_csv(out / "density_scaling_summary.csv")
    resource_summary = pd.read_csv(out / "resource_activity_summary.csv")
    write_findings(out, {"density": density_summary, "resource": resource_summary})

    manifest = {
        "campaign": cfg["campaign_name"],
        "mode": "smoke" if args.smoke else "full",
        "seed_count": len(seeds),
        "curves_path": str(curves_path),
        "curve_count": len(curves),
        "scientific_classification": cfg["classification"],
        "real_mobility": "run separately with simulations.real_mobility_amovfly_public when network access is available",
        "important_nonclaims": ["not bit-accurate NR PHY", "not measured swarm RF", "not normative Mode 2", "HARQ is ideal Chase abstraction"],
    }
    try:
        manifest["git_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        manifest["git_sha"] = "unknown"
    (out / "final_campaign_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Final campaign ({manifest['mode']}) complete: {out}")


if __name__ == "__main__":
    main()

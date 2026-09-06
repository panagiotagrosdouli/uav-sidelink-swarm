"""Density, spatial-scaling, geometry and activity-factor experiments.

All geometries/activity choices are SYNTHETIC or EXPERIMENTAL_SWEEP. The channel
is measurement-derived by default; RF outputs are system-level simulations.

The fixed-area vs fixed-density comparison uses nearest-neighbor disjoint link
pairing in both families. This keeps the desired communication relation local as
the simulated region grows, so the experiment can distinguish UAV count from
spatial density. The nearest-neighbor pairing is a THIS_WORK topology abstraction,
not a normative NR procedure.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import summarize
from src.swarm_system import SwarmConfig, simulate_snapshot

N_VALUES = [5, 10, 20, 30, 50, 75, 100]
GEOMETRIES = ["uniform", "grid", "circle", "clustered", "leader_follower"]
ACTIVITY = [0.10, 0.25, 0.50, 0.75, 1.00]
BASE_AREA_SIDE_M = 1000.0
BASE_DENSITY_UAV_PER_M2 = 20.0 / (BASE_AREA_SIDE_M**2)
SCALING_PAIRING = "nearest_neighbor"


def _seed_metrics(cfg: SwarmConfig) -> dict[str, float | int | str]:
    _, links = simulate_snapshot(cfg)
    finite_sir = links.sir_db.replace([np.inf, -np.inf], np.nan).dropna()
    return {
        "seed": cfg.seed,
        "n_uavs": cfg.n_uavs,
        "geometry": cfg.geometry,
        "pairing": cfg.pairing,
        "area_xy_m": cfg.area_xy_m,
        "spatial_density_uav_per_km2": cfg.n_uavs / ((cfg.area_xy_m / 1000.0) ** 2),
        "activity_probability": cfg.activity_probability,
        "mean_link_distance_m": float(links.distance_m.mean()),
        "mean_sinr_db": float(links.sinr_db.mean()),
        "median_sinr_db": float(links.sinr_db.median()),
        "mean_sir_db": float(finite_sir.mean()) if len(finite_sir) else np.inf,
        "mean_interference_to_noise_linear": float(links.interference_to_noise_linear.mean()),
        "mean_dominant_interferer_fraction": float(links.dominant_interferer_fraction.mean()),
        "mean_n_interferers": float(links.n_interferers.mean()),
        "legacy_outage_proxy": float(links.outage_proxy.mean()),
        "n_active_links": int(len(links)),
    }


def _summarize(raw: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for key, group in raw.groupby(group_cols, sort=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key_tuple))
        for metric in [
            "mean_link_distance_m",
            "mean_sinr_db",
            "mean_interference_to_noise_linear",
            "mean_dominant_interferer_fraction",
            "mean_n_interferers",
            "legacy_outage_proxy",
        ]:
            stats = summarize(group[metric])
            rows.append({**base, "metric": metric, **stats})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="small deterministic CI run")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    seeds = range(3 if args.smoke else args.seeds)
    n_values = [5, 20, 50] if args.smoke else N_VALUES

    out = Path("results/scaling_geometry_activity")
    figs = Path("figures/scaling_geometry_activity")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    # Family 1: fixed area, increasing N. Desired links use the same local
    # nearest-neighbor policy as the fixed-density family.
    fixed_area = []
    for n in n_values:
        for seed in seeds:
            fixed_area.append(_seed_metrics(SwarmConfig(
                n_uavs=n,
                seed=seed,
                area_xy_m=BASE_AREA_SIDE_M,
                pairing=SCALING_PAIRING,
            )))
    fixed_area_df = pd.DataFrame(fixed_area)
    fixed_area_df["family"] = "fixed_area"

    # Family 2: fixed spatial density, increasing N and area. Local pairing
    # prevents desired-link distance from scaling with total region size.
    fixed_density = []
    for n in n_values:
        area_side = float(np.sqrt(n / BASE_DENSITY_UAV_PER_M2))
        for seed in seeds:
            fixed_density.append(_seed_metrics(SwarmConfig(
                n_uavs=n,
                seed=seed,
                area_xy_m=area_side,
                pairing=SCALING_PAIRING,
            )))
    fixed_density_df = pd.DataFrame(fixed_density)
    fixed_density_df["family"] = "fixed_density"

    scaling_raw = pd.concat([fixed_area_df, fixed_density_df], ignore_index=True)
    scaling_raw.to_csv(out / "scaling_per_seed.csv", index=False)
    scaling_summary = _summarize(scaling_raw, ["family", "n_uavs"])
    scaling_summary.to_csv(out / "scaling_summary.csv", index=False)

    # Family 3: geometry at one representative density/size. Keep the canonical
    # sequential pairing so this remains comparable to earlier geometry results.
    geometry_rows = []
    geometry_n = 30 if not args.smoke else 20
    for geometry in GEOMETRIES:
        for seed in seeds:
            geometry_rows.append(_seed_metrics(SwarmConfig(n_uavs=geometry_n, seed=seed, geometry=geometry)))
    geometry_df = pd.DataFrame(geometry_rows)
    geometry_df.to_csv(out / "geometry_per_seed.csv", index=False)
    geometry_summary = _summarize(geometry_df, ["geometry"])
    geometry_summary.to_csv(out / "geometry_summary.csv", index=False)

    # Family 4: activity factor vs density, retaining the canonical sequential
    # link definition so only activity changes relative to the main baseline.
    activity_rows = []
    activity_values = [0.25, 1.0] if args.smoke else ACTIVITY
    activity_n = [20, 50] if args.smoke else [10, 20, 30, 50, 75, 100]
    for n in activity_n:
        for p in activity_values:
            for seed in seeds:
                activity_rows.append(_seed_metrics(SwarmConfig(n_uavs=n, seed=seed, activity_probability=p)))
    activity_df = pd.DataFrame(activity_rows)
    activity_df.to_csv(out / "activity_per_seed.csv", index=False)
    activity_summary = _summarize(activity_df, ["n_uavs", "activity_probability"])
    activity_summary.to_csv(out / "activity_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    sinr = scaling_summary[scaling_summary.metric == "mean_sinr_db"]
    for family, group in sinr.groupby("family"):
        ax.plot(group.n_uavs, group["mean"], marker="o", label=family.replace("_", " "))
        ax.fill_between(group.n_uavs, group.ci95_low, group.ci95_high, alpha=0.15)
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean link SINR [dB]")
    ax.set_title("Fixed area vs fixed spatial density — local link pairing")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "fixed_area_vs_fixed_density.png", dpi=300)
    fig.savefig(figs / "fixed_area_vs_fixed_density.pdf")
    plt.close(fig)

    # Diagnostic figure: verify that desired-link spacing behaves differently in
    # the two experiment families rather than scaling with the whole region.
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    distance = scaling_summary[scaling_summary.metric == "mean_link_distance_m"]
    for family, group in distance.groupby("family"):
        ax.plot(group.n_uavs, group["mean"], marker="o", label=family.replace("_", " "))
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean desired-link distance [m]")
    ax.set_title("Desired-link spacing under local pairing")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "link_distance_fixed_area_vs_density.png", dpi=300)
    fig.savefig(figs / "link_distance_fixed_area_vs_density.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    act = activity_summary[activity_summary.metric == "mean_sinr_db"]
    for p, group in act.groupby("activity_probability"):
        ax.plot(group.n_uavs, group["mean"], marker="o", label=f"p={p:g}")
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean link SINR [dB]")
    ax.set_title("Density × transmitter activity")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "activity_factor_sinr.png", dpi=300)
    fig.savefig(figs / "activity_factor_sinr.pdf")
    plt.close(fig)

    print(scaling_summary.to_string(index=False))


if __name__ == "__main__":
    main()

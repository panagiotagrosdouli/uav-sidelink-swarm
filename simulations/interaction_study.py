"""Selected multi-factor interactions without brute-force combinatorial sweeps.

Experiments:
1) swarm size × channel model;
2) resource allocation × desired-link directional gain.
All system outputs are simulated/derived. Gain/resource choices are experimental.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import summarize
from src.sidelink.resource_allocation import weighted_conflict_graph_allocation
from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    dbm_to_w,
    generate_equal_altitude_positions,
    received_power_w,
    simulate_snapshot,
    thermal_noise_dbm,
)

CHANNELS = ["free_space", "measured_a2a", "tr38901_umi_av_los"]
N_VALUES = [10, 20, 30, 50, 75, 100]
GAINS_DB = [0.0, 3.0, 6.0, 9.0]
RESOURCE_COUNTS = [1, 4]


def _resource_gain_snapshot(seed: int, n_uavs: int, n_resources: int, gain_db: float) -> float:
    cfg = SwarmConfig(n_uavs=n_uavs, seed=seed)
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = build_disjoint_pairs(n_uavs)
    tx = np.array([positions[t] for t, _ in pairs])
    rx = np.array([positions[r] for _, r in pairs])
    resources = np.zeros(len(pairs), dtype=int) if n_resources == 1 else weighted_conflict_graph_allocation(tx, rx, n_resources).resources
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    gain_linear = 10.0 ** (gain_db / 10.0)
    sinrs = []
    for i, (link_tx, link_rx) in enumerate(pairs):
        signal, _, _ = received_power_w(link_tx, link_rx, positions, cfg)
        signal *= gain_linear
        interference = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if i == j or resources[i] != resources[j]:
                continue
            p_i, _, _ = received_power_w(other_tx, link_rx, positions, cfg)
            interference += p_i
        sinrs.append(10.0 * np.log10(signal / (noise_w + interference)))
    return float(np.mean(sinrs))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    seeds = range(2 if args.smoke else args.seeds)
    n_values = [10, 50] if args.smoke else N_VALUES

    out = Path("results/interactions")
    figs = Path("figures/interactions")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    channel_rows = []
    for n in n_values:
        for channel in CHANNELS:
            for seed in seeds:
                _, links = simulate_snapshot(SwarmConfig(n_uavs=n, seed=seed, channel=channel))
                channel_rows.append({"n_uavs": n, "channel": channel, "seed": seed, "mean_sinr_db": float(links.sinr_db.mean())})
    channel_df = pd.DataFrame(channel_rows)
    channel_df.to_csv(out / "density_channel_per_seed.csv", index=False)

    summary_rows = []
    for (n, channel), group in channel_df.groupby(["n_uavs", "channel"]):
        summary_rows.append({"n_uavs": n, "channel": channel, **summarize(group.mean_sinr_db)})
    channel_summary = pd.DataFrame(summary_rows)
    channel_summary.to_csv(out / "density_channel_summary.csv", index=False)

    gain_values = [0.0, 6.0] if args.smoke else GAINS_DB
    rg_rows = []
    for n in n_values:
        for resources in RESOURCE_COUNTS:
            for gain in gain_values:
                for seed in seeds:
                    rg_rows.append({
                        "n_uavs": n,
                        "n_resources": resources,
                        "desired_gain_db": gain,
                        "seed": seed,
                        "mean_sinr_db": _resource_gain_snapshot(seed, n, resources, gain),
                    })
    rg_df = pd.DataFrame(rg_rows)
    rg_df.to_csv(out / "resource_directionality_per_seed.csv", index=False)
    rg_summary = rg_df.groupby(["n_uavs", "n_resources", "desired_gain_db"], as_index=False).mean(numeric_only=True)
    rg_summary.to_csv(out / "resource_directionality_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for channel, group in channel_summary.groupby("channel"):
        ax.plot(group.n_uavs, group["mean"], marker="o", label=channel)
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean SINR [dB]")
    ax.set_title("Swarm size × propagation model")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "density_channel.png", dpi=300)
    fig.savefig(figs / "density_channel.pdf")
    plt.close(fig)

    print(channel_summary.to_string(index=False))


if __name__ == "__main__":
    main()

"""Monte Carlo density study using the measurement-derived A2A path-loss model."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.swarm_system import SwarmConfig, simulate_snapshot

SWARM_SIZES = [5, 10, 20, 30, 50]
N_SEEDS = 100


def percentile_5(x: pd.Series) -> float:
    return float(np.percentile(x, 5))


def percentile_95(x: pd.Series) -> float:
    return float(np.percentile(x, 95))


def main() -> None:
    all_links = []
    for n in SWARM_SIZES:
        for seed in range(N_SEEDS):
            cfg = SwarmConfig(n_uavs=n, seed=seed, channel="measured_a2a")
            _, links = simulate_snapshot(cfg)
            all_links.append(links)

    raw = pd.concat(all_links, ignore_index=True)
    results_dir = Path("results/density_measurement_based")
    figures_dir = Path("figures/density")
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(results_dir / "raw_links.csv", index=False)

    per_seed = raw.groupby(["n_uavs", "seed"], as_index=False).agg(
        mean_sinr_db=("sinr_db", "mean"),
        median_sinr_db=("sinr_db", "median"),
        outage_proxy=("outage_proxy", "mean"),
        link_success_proxy=("link_success_proxy", "mean"),
        mean_shannon_upper_bound_mbps=("shannon_upper_bound_mbps", "mean"),
    )
    per_seed.to_csv(results_dir / "per_seed.csv", index=False)

    summary = per_seed.groupby("n_uavs", as_index=False).agg(
        mean_sinr_db=("mean_sinr_db", "mean"),
        median_sinr_db=("mean_sinr_db", "median"),
        std_sinr_db=("mean_sinr_db", "std"),
        p05_sinr_db=("mean_sinr_db", percentile_5),
        p95_sinr_db=("mean_sinr_db", percentile_95),
        mean_outage_proxy=("outage_proxy", "mean"),
        mean_link_success_proxy=("link_success_proxy", "mean"),
        mean_shannon_upper_bound_mbps=("mean_shannon_upper_bound_mbps", "mean"),
    )
    # 95% CI for the Monte-Carlo mean of per-seed SINR.
    counts = per_seed.groupby("n_uavs").size().reindex(summary.n_uavs).to_numpy()
    summary["sinr_ci95_halfwidth_db"] = 1.96 * summary.std_sinr_db / np.sqrt(counts)
    summary.to_csv(results_dir / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(summary.n_uavs, summary.mean_sinr_db, yerr=summary.sinr_ci95_halfwidth_db, marker="o", capsize=4)
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean SINR [dB]")
    ax.set_title("Swarm density vs mean SINR — measurement-derived A2A channel")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figures_dir / "mean_sinr_vs_swarm_size.png", dpi=300)
    fig.savefig(figures_dir / "mean_sinr_vs_swarm_size.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(summary.n_uavs, summary.mean_outage_proxy, marker="o")
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Outage proxy probability")
    ax.set_ylim(0, 1)
    ax.set_title("Swarm density vs outage proxy")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figures_dir / "outage_proxy_vs_swarm_size.png", dpi=300)
    fig.savefig(figures_dir / "outage_proxy_vs_swarm_size.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for n in [5, 20, 50]:
        values = np.sort(raw.loc[raw.n_uavs == n, "sinr_db"].to_numpy())
        cdf = np.arange(1, len(values) + 1) / len(values)
        ax.plot(values, cdf, label=f"N={n}")
    ax.set_xlabel("SINR [dB]")
    ax.set_ylabel("Empirical CDF")
    ax.set_title("SINR distribution vs swarm size")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "sinr_cdf.png", dpi=300)
    fig.savefig(figures_dir / "sinr_cdf.pdf")
    plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

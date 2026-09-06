"""Sweep swarm size and export SINR/PDR summary statistics."""
from pathlib import Path

import pandas as pd

from src.sinr_sim import Config, simulate


def main() -> None:
    rows = []
    for n in [5, 10, 20, 30, 50]:
        for seed in range(20):
            cfg = Config(n_uavs=n, seed=seed, activity_probability=0.35)
            _, links = simulate(cfg)
            if links.empty:
                continue
            rows.append({
                "n_uavs": n,
                "seed": seed,
                "active_links": len(links),
                "mean_sinr_db": links.sinr_db.mean(),
                "median_sinr_db": links.sinr_db.median(),
                "pdr_proxy": links.success.mean(),
                "mean_shannon_upper_bound_mbps": links.shannon_upper_bound_mbps.mean(),
            })

    out = Path("results/density_sweep")
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "per_seed.csv", index=False)
    summary = df.groupby("n_uavs").agg(
        mean_sinr_db=("mean_sinr_db", "mean"),
        std_sinr_db=("mean_sinr_db", "std"),
        mean_pdr_proxy=("pdr_proxy", "mean"),
        std_pdr_proxy=("pdr_proxy", "std"),
        mean_shannon_upper_bound_mbps=("mean_shannon_upper_bound_mbps", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

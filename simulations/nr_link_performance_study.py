"""Replace the fixed SINR-threshold proxy with sourced BLER curves where available.

Scope: 5G-LENA Table-1 BG1/CBS4096 verified subset (MCS 4/5/6) plus the
measurement-derived A2A propagation model. The resulting BLER, first-TX success
probability and expected PHY goodput are DERIVED system-level quantities.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.swarm_system import SwarmConfig, simulate_snapshot


def main() -> None:
    curves = load_bler_curves(
        "data/reference/5glena_table1_bg1_cbs4096_subset.csv",
        source="5G-LENA nr-eesm-t1.cc; Table1 BG1 CBS4096 subset",
    )
    available = curves_for_cbs(curves, code_block_size=4096, base_graph=1)

    rows: list[dict[str, float | int]] = []
    for n_uavs in [5, 10, 20, 30, 50]:
        for seed in range(100):
            cfg = SwarmConfig(
                n_uavs=n_uavs,
                seed=seed,
                channel="measured_a2a",
                carrier_ghz=3.5,
                bandwidth_mhz=50.0,
                tx_power_dbm=30.0,
            )
            _, links = simulate_snapshot(cfg)
            for link in links.itertuples(index=False):
                choice = select_max_goodput_mcs(
                    sinr_db=float(link.sinr_db),
                    curves=available,
                    bandwidth_mhz=cfg.bandwidth_mhz,
                )
                if choice is None:
                    continue
                rows.append({
                    "n_uavs": n_uavs,
                    "seed": seed,
                    "link_id": int(link.link_id),
                    "sinr_db": float(link.sinr_db),
                    "selected_mcs": choice.mcs_index,
                    "bler": choice.bler,
                    "first_tx_success_probability": choice.first_tx_success_probability,
                    "expected_phy_goodput_mbps": choice.expected_phy_goodput_mbps,
                })

    df = pd.DataFrame(rows)
    out = Path("results/nr_link_performance")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "per_link.csv", index=False)

    summary = df.groupby("n_uavs").agg(
        mean_sinr_db=("sinr_db", "mean"),
        mean_bler=("bler", "mean"),
        mean_first_tx_success_probability=("first_tx_success_probability", "mean"),
        mean_expected_phy_goodput_mbps=("expected_phy_goodput_mbps", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

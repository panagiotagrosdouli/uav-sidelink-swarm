"""Packet traffic-load sensitivity under full-buffer-derived link service.

Traffic rates and packet size are EXPERIMENTAL_SWEEP choices, not measured UAV
application traffic. Per-link service success is derived from a full-activity
swarm snapshot using the bundled verified 5G-LENA MCS4/5/6 fixture. Queueing is
a slotted system-level abstraction, not NR MAC/RLC.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.metrics import jain_fairness, summarize
from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.swarm_system import SwarmConfig, simulate_snapshot
from src.traffic import simulate_slotted_queue

TRAFFIC_SCENARIOS = {
    "low": 50.0,
    "medium": 500.0,
    "high": 1500.0,
}
PACKET_SIZE_BYTES = 256  # EXPERIMENTAL_CONFIGURATION; payload size is not sourced.
N_VALUES = [10, 30, 50]
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"


def _curves():
    curves = load_bler_curves(BLER_CSV, source="5G-LENA verified Table1 BG1 CBS4096 subset")
    return curves_for_cbs(curves, 4096, base_graph=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--slots", type=int, default=20000)
    args = parser.parse_args()
    seeds = range(2 if args.smoke else args.seeds)
    n_slots = 1000 if args.smoke else args.slots
    n_values = [10, 30] if args.smoke else N_VALUES
    traffic = {"low": 50.0, "high": 1500.0} if args.smoke else TRAFFIC_SCENARIOS
    curves = _curves()
    slot_ms = thesis_profile_50mhz_30khz().slot_duration_ms

    rows = []
    for n in n_values:
        for seed in seeds:
            cfg = SwarmConfig(n_uavs=n, seed=seed, activity_probability=1.0)
            _, links = simulate_snapshot(cfg)
            success_probabilities = []
            for link in links.itertuples(index=False):
                choice = select_max_goodput_mcs(float(link.sinr_db), curves, cfg.bandwidth_mhz)
                success_probabilities.append(choice.first_tx_success_probability if choice is not None else 0.0)
            for scenario, rate in traffic.items():
                link_delivery = []
                link_latency = []
                link_utilization = []
                link_queue = []
                for link_id, success in enumerate(success_probabilities):
                    q = simulate_slotted_queue(
                        arrival_rate_pps=rate,
                        slot_duration_ms=slot_ms,
                        success_probability=success,
                        n_slots=n_slots,
                        seed=seed * 10000 + link_id,
                    )
                    link_delivery.append(q.delivery_ratio)
                    if np.isfinite(q.mean_latency_ms):
                        link_latency.append(q.mean_latency_ms)
                    link_utilization.append(q.utilization)
                    link_queue.append(q.mean_queue_length)
                rows.append({
                    "seed": seed,
                    "n_uavs": n,
                    "traffic_scenario": scenario,
                    "arrival_rate_pps_per_link": rate,
                    "packet_size_bytes": PACKET_SIZE_BYTES,
                    "slot_duration_ms": slot_ms,
                    "mean_delivery_ratio": float(np.mean(link_delivery)),
                    "mean_latency_ms": float(np.mean(link_latency)) if link_latency else np.nan,
                    "mean_queue_length_packets": float(np.mean(link_queue)),
                    "mean_utilization": float(np.mean(link_utilization)),
                    "jain_delivery_fairness": jain_fairness(link_delivery),
                    "traffic_classification": "EXPERIMENTAL_SWEEP",
                    "service_classification": "LINK_LEVEL_SIMULATION_DERIVED_FULL_ACTIVITY",
                })

    raw = pd.DataFrame(rows)
    out = Path("results/traffic_load")
    figs = Path("figures/traffic_load")
    out.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / "per_seed.csv", index=False)

    summary_rows = []
    for (n, scenario, rate), group in raw.groupby(["n_uavs", "traffic_scenario", "arrival_rate_pps_per_link"]):
        row = {"n_uavs": n, "traffic_scenario": scenario, "arrival_rate_pps_per_link": rate}
        for metric in ["mean_delivery_ratio", "mean_latency_ms", "mean_queue_length_packets", "mean_utilization", "jain_delivery_fairness"]:
            values = group[metric].dropna()
            if len(values):
                for key, value in summarize(values).items():
                    row[f"{metric}_{key}"] = value
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for scenario, group in summary.groupby("traffic_scenario"):
        ax.plot(group.n_uavs, group.mean_delivery_ratio_mean, marker="o", label=scenario)
    ax.set_xlabel("Number of UAVs")
    ax.set_ylabel("Mean packet delivery ratio (simulated)")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Experimental traffic load under full-activity interference service")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figs / "delivery_vs_density.png", dpi=300)
    fig.savefig(figs / "delivery_vs_density.pdf")
    plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

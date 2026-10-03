"""Reviewer-facing robustness experiments for the UAV sidelink paper.

These experiments do not overwrite the frozen publication operating-envelope
campaign. They test whether the headline qualitative conclusions are sensitive
to pairing, resource-allocation, noise-bandwidth accounting, and link-adaptation
abstractions.

Scientific classifications
--------------------------
* All RF/network outputs are DERIVED_SYSTEM_LEVEL_METRIC.
* Pairing choice, allocator choice, noise-bandwidth accounting and fixed-MCS
  checks are ROBUSTNESS / EXPERIMENTAL_CONFIGURATION dimensions.
* The conflict-graph allocator is THIS_WORK, not normative NR Sidelink Mode 1/2.
* Random allocation is a no-coordination baseline.
* Nearest-neighbour pairing is a geometry-derived topology sensitivity, not a
  standardized sidelink association rule.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from simulations.paper_operating_envelope import (
    ADVANTAGES_DB,
    TOTAL_PRB,
    grid_for_prbs,
    prb_partition,
)
from src.metrics import jain_fairness, mean_ci95
from src.sidelink.adaptive_tb import load_preferred_bler_curves, select_tbs_aware_mcs
from src.sidelink.resource_allocation import random_allocation, weighted_conflict_graph_allocation
from src.swarm_system import (
    SwarmConfig,
    build_disjoint_pairs,
    build_nearest_disjoint_pairs,
    dbm_to_w,
    generate_equal_altitude_positions,
    received_power_w,
    thermal_noise_dbm,
)

ROBUST_N = [20, 50, 100]
ROBUST_R = [1, 4, 8]
ROBUST_G = [0.0, 6.0]
PAIRINGS = ["sequential", "nearest_neighbor"]
ALLOCATORS = ["conflict_graph", "random"]
LINK_ADAPTATION = ["adaptive", "fixed_mcs4"]


def exact_prb_occupied_bandwidth_hz(n_prb: int, scs_khz: int = 30) -> float:
    """Occupied OFDM bandwidth represented by allocated PRBs.

    One PRB spans 12 subcarriers. This excludes channel guard bands and is used
    only in the robustness experiment so the frozen publication run remains
    byte-for-byte interpretable under its original nominal-channel-share noise
    convention.
    """
    if n_prb < 1:
        raise ValueError("n_prb must be positive")
    return float(n_prb * 12 * scs_khz * 1e3)


def choose_pairs(pairing: str, positions: np.ndarray, n_uavs: int):
    if pairing == "sequential":
        return build_disjoint_pairs(n_uavs)
    if pairing == "nearest_neighbor":
        return build_nearest_disjoint_pairs(positions)
    raise ValueError(f"unknown pairing: {pairing}")


def choose_resources(
    allocator: str,
    tx_pos: np.ndarray,
    rx_pos: np.ndarray,
    n_resources: int,
    seed: int,
) -> np.ndarray:
    if n_resources == 1:
        return np.zeros(len(tx_pos), dtype=int)
    if allocator == "conflict_graph":
        return weighted_conflict_graph_allocation(tx_pos, rx_pos, n_resources).resources
    if allocator == "random":
        return random_allocation(len(tx_pos), n_resources, seed).resources
    raise ValueError(f"unknown allocator: {allocator}")


def snapshot(
    seed: int,
    n_uavs: int,
    n_resources: int,
    advantage_db: float,
    pairing: str,
    allocator: str,
    link_adaptation: str,
    curves,
) -> dict[str, float]:
    cfg = SwarmConfig(n_uavs=n_uavs, seed=seed, channel="measured_a2a")
    rng = np.random.default_rng(seed)
    positions = generate_equal_altitude_positions(cfg, rng)
    pairs = choose_pairs(pairing, positions, n_uavs)
    tx_pos = np.array([positions[t] for t, _ in pairs])
    rx_pos = np.array([positions[r] for _, r in pairs])
    resources = choose_resources(allocator, tx_pos, rx_pos, n_resources, seed)
    partition = prb_partition(n_resources)
    desired_gain = 10.0 ** ((advantage_db / 2.0) / 10.0)
    interference_gain = 10.0 ** ((-advantage_db / 2.0) / 10.0)

    sinrs, successes, goodputs, desired_distances = [], [], [], []
    unsupported = 0

    for i, (tx, rx) in enumerate(pairs):
        resource_id = int(resources[i])
        n_prb = partition[resource_id]
        grid = grid_for_prbs(n_prb)
        occupied_bandwidth_hz = exact_prb_occupied_bandwidth_hz(n_prb, grid.scs_khz)
        noise_w = float(dbm_to_w(thermal_noise_dbm(occupied_bandwidth_hz, cfg.noise_figure_db)))

        signal_w, distance_m, _ = received_power_w(tx, rx, positions, cfg)
        signal_w *= desired_gain
        interference_w = 0.0
        for j, (other_tx, _) in enumerate(pairs):
            if j == i or int(resources[j]) != resource_id:
                continue
            p_w, _, _ = received_power_w(other_tx, rx, positions, cfg)
            interference_w += float(p_w * interference_gain)

        sinr_db = float(10.0 * np.log10(signal_w / (noise_w + interference_w)))
        candidate_mcs = None if link_adaptation == "adaptive" else [4]
        choice = select_tbs_aware_mcs(sinr_db, curves, grid=grid, candidate_mcs=candidate_mcs)
        if choice is None:
            unsupported += 1
            success = 0.0
            goodput = 0.0
        else:
            success = float(choice.success_probability)
            goodput = float(choice.expected_goodput_mbps)

        sinrs.append(sinr_db)
        successes.append(success)
        goodputs.append(goodput)
        desired_distances.append(distance_m)

    return {
        "mean_sinr_db": float(np.mean(sinrs)),
        "mean_first_tx_success": float(np.mean(successes)),
        "mean_expected_goodput_mbps": float(np.mean(goodputs)),
        "jain_goodput_fairness": jain_fairness(goodputs),
        "mean_desired_link_distance_m": float(np.mean(desired_distances)),
        "unsupported_link_fraction": float(unsupported / len(pairs)),
    }


def summarize(group: pd.DataFrame) -> dict[str, float]:
    out = {}
    for col in [
        "mean_sinr_db",
        "mean_first_tx_success",
        "mean_expected_goodput_mbps",
        "jain_goodput_fairness",
        "mean_desired_link_distance_m",
        "unsupported_link_fraction",
    ]:
        mean, lo, hi = mean_ci95(group[col])
        out[col] = mean
        out[f"{col}_ci95_low"] = lo
        out[f"{col}_ci95_high"] = hi
    return out


def main() -> None:
    curves, curve_mode = load_preferred_bler_curves()
    if curve_mode != "FULL_5GLENA_V5_LOCAL":
        raise RuntimeError("reviewer robustness campaign requires official 5G-LENA v5.0 full curves")

    out = Path("results/paper_robustness")
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    seeds = range(100)
    for n in ROBUST_N:
        for r in ROBUST_R:
            for g in ROBUST_G:
                for pairing in PAIRINGS:
                    for allocator in ALLOCATORS:
                        if r == 1 and allocator == "random":
                            continue
                        for link_adaptation in LINK_ADAPTATION:
                            for seed in seeds:
                                metrics = snapshot(
                                    seed, n, r, g, pairing, allocator, link_adaptation, curves
                                )
                                rows.append({
                                    "n_uavs": n,
                                    "n_resources": r,
                                    "prb_partition": "+".join(str(x) for x in prb_partition(r)),
                                    "directional_relative_advantage_db": g,
                                    "pairing": pairing,
                                    "allocator": allocator,
                                    "link_adaptation": link_adaptation,
                                    "noise_bandwidth_mode": "exact_prb_occupied_bandwidth",
                                    "seed": seed,
                                    "curve_mode": curve_mode,
                                    **metrics,
                                })

    raw = pd.DataFrame(rows)
    raw.to_csv(out / "per_seed.csv", index=False)

    summary_rows = []
    keys = [
        "n_uavs",
        "n_resources",
        "directional_relative_advantage_db",
        "pairing",
        "allocator",
        "link_adaptation",
        "noise_bandwidth_mode",
    ]
    for key_values, group in raw.groupby(keys):
        row = dict(zip(keys, key_values))
        row.update(summarize(group))
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "summary.csv", index=False)

    manifest = {
        "classification": "DERIVED_SYSTEM_LEVEL_ROBUSTNESS_CAMPAIGN",
        "seeds": 100,
        "swarm_sizes": ROBUST_N,
        "resource_counts": ROBUST_R,
        "directional_relative_advantage_db": ROBUST_G,
        "pairings": PAIRINGS,
        "allocators": ALLOCATORS,
        "link_adaptation": LINK_ADAPTATION,
        "noise_bandwidth_mode": "exact PRB occupied bandwidth = N_PRB * 12 * SCS",
        "purpose": (
            "Reviewer-facing sensitivity checks; does not replace the frozen "
            "paper-operating-envelope evidence."
        ),
    }
    import json
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

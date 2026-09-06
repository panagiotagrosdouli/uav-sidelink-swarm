"""Graph-level direct vs multi-hop routing study.

Topology uses interference-free SNR and the verified 5G-LENA MCS4/5/6 fixture.
Thus route reliability is LINK_LEVEL_SIMULATION-derived and assumes independent
per-hop decoding. Nominal route latency is the sum of one configured slot per
hop; it excludes scheduling, queueing and full network-stack delay.

The source/target pair is selected as the farthest pair in each realization.
This avoids the previous index-based endpoint choice, which frequently made the
routing experiment a trivial one-hop sanity check. The graph additionally uses
an experimental maximum hop range so that multi-hop behavior is actually
observable. Neither policy is normative 3GPP routing behavior.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.metrics import summarize
from src.networking.routing import (
    build_graph,
    minimum_hop_path,
    path_bottleneck_sinr_db,
    path_latency_ms,
    path_success_probability,
    quality_aware_path,
    reliability_aware_path,
)
from src.sidelink.bler_io import curves_for_cbs, load_bler_curves
from src.sidelink.link_adaptation import select_max_goodput_mcs
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.swarm_system import SwarmConfig, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

N_VALUES = [10, 20, 30, 50, 75, 100]
MIN_SUCCESS_PROBABILITY = 0.50  # EXPERIMENTAL policy target, not a 3GPP mandate.
MAX_ROUTING_HOP_DISTANCE_M = 350.0  # EXPERIMENTAL topology policy, not a 3GPP mandate.
BLER_CSV = "data/reference/5glena_table1_bg1_cbs4096_subset.csv"


def _curves():
    all_curves = load_bler_curves(BLER_CSV, source="5G-LENA verified Table1 BG1 CBS4096 subset")
    return curves_for_cbs(all_curves, code_block_size=4096, base_graph=1)


def all_pair_links(cfg: SwarmConfig, positions: np.ndarray) -> pd.DataFrame:
    noise_w = float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz * 1e6, cfg.noise_figure_db)))
    slot_ms = thesis_profile_50mhz_30khz().slot_duration_ms
    curves = _curves()
    rows = []
    for i in range(cfg.n_uavs):
        for j in range(i + 1, cfg.n_uavs):
            signal_w, distance_m, path_loss_db = received_power_w(i, j, positions, cfg)
            snr_db = 10.0 * np.log10(signal_w / noise_w)
            choice = select_max_goodput_mcs(float(snr_db), curves, cfg.bandwidth_mhz)
            if choice is None:
                success, mcs, goodput = 0.0, -1, 0.0
            else:
                success, mcs, goodput = choice.first_tx_success_probability, choice.mcs_index, choice.expected_phy_goodput_mbps
            rows.append({
                "tx": i, "rx": j, "distance_m": distance_m, "path_loss_db": path_loss_db,
                "sinr_db": snr_db, "success_probability": success, "selected_mcs": mcs,
                "expected_phy_goodput_mbps": goodput, "latency_ms": slot_ms,
            })
    return pd.DataFrame(rows)


def _farthest_pair(positions: np.ndarray) -> tuple[int, int, float]:
    best = (-1.0, 0, 1)
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            d = float(np.linalg.norm(positions[i] - positions[j]))
            if d > best[0]: best = (d, i, j)
    return best[1], best[2], best[0]


def _path_metrics(graph: nx.Graph, path: list[int]) -> dict[str, float | int]:
    return {"hops": len(path)-1, "bottleneck_sinr_db": path_bottleneck_sinr_db(graph,path),
            "route_success_probability": path_success_probability(graph,path),
            "nominal_phy_latency_ms": path_latency_ms(graph,path)}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--smoke",action="store_true"); parser.add_argument("--seeds",type=int,default=100); args=parser.parse_args()
    seeds=range(3 if args.smoke else args.seeds); n_values=[10,30] if args.smoke else N_VALUES
    rows=[]
    for n_uavs in n_values:
        for seed in seeds:
            cfg=SwarmConfig(n_uavs=n_uavs,seed=seed,channel="measured_a2a")
            positions=generate_equal_altitude_positions(cfg,np.random.default_rng(seed)); links=all_pair_links(cfg,positions)
            source,target,endpoint_distance=_farthest_pair(positions)
            viable=links[(links.success_probability>=MIN_SUCCESS_PROBABILITY)&(links.distance_m<=MAX_ROUTING_HOP_DISTANCE_M)].copy()
            graph=build_graph(viable,minimum_sinr_db=-100.0)
            connected=source in graph and target in graph and nx.has_path(graph,source,target)
            direct=links[((links.tx==source)&(links.rx==target))|((links.tx==target)&(links.rx==source))].iloc[0]
            base={"seed":seed,"n_uavs":n_uavs,"source":source,"target":target,"endpoint_distance_m":endpoint_distance,
                  "connected":connected,"graph_edges":graph.number_of_edges(),"maximum_routing_hop_distance_m":MAX_ROUTING_HOP_DISTANCE_M,
                  "direct_success_probability":float(direct.success_probability),"direct_sinr_db":float(direct.sinr_db),
                  "direct_nominal_phy_latency_ms":thesis_profile_50mhz_30khz().slot_duration_ms}
            if connected:
                paths={"minhop":minimum_hop_path(graph,source,target),"quality":quality_aware_path(graph,source,target),"reliability":reliability_aware_path(graph,source,target)}
                for name,path in paths.items():
                    for key,value in _path_metrics(graph,path).items(): base[f"{name}_{key}"]=value
            rows.append(base)
    df=pd.DataFrame(rows); out=Path("results/routing"); figs=Path("figures/routing"); out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); df.to_csv(out/"per_seed.csv",index=False)
    summary_rows=[]
    for n,group in df.groupby("n_uavs"):
        row={"n_uavs":n,"seeds":len(group),"minimum_link_success_probability":MIN_SUCCESS_PROBABILITY,"maximum_routing_hop_distance_m":MAX_ROUTING_HOP_DISTANCE_M,
             "connectivity_probability":float(group.connected.mean()),"mean_graph_edges":float(group.graph_edges.mean()),"mean_endpoint_distance_m":float(group.endpoint_distance_m.mean())}
        for metric in ["direct_success_probability","direct_sinr_db"]:
            for k,v in summarize(group[metric]).items(): row[f"{metric}_{k}"]=v
        for prefix in ["minhop","quality","reliability"]:
            for metric in ["hops","bottleneck_sinr_db","route_success_probability","nominal_phy_latency_ms"]:
                col=f"{prefix}_{metric}"
                if col in group and group[col].notna().any(): row[f"{col}_mean"]=float(group[col].mean()); row[f"{col}_median"]=float(group[col].median())
        summary_rows.append(row)
    summary=pd.DataFrame(summary_rows); summary.to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.plot(summary.n_uavs,summary.connectivity_probability,marker="o"); ax.set_xlabel("Number of UAVs"); ax.set_ylabel("Farthest-pair route availability probability"); ax.set_ylim(0,1.05); ax.set_title("Multi-hop route availability vs swarm size"); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(figs/"connectivity_vs_density.png",dpi=300); fig.savefig(figs/"connectivity_vs_density.pdf"); plt.close(fig)
    if "reliability_route_success_probability_mean" in summary:
        fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.plot(summary.n_uavs,summary.direct_success_probability_mean,marker="o",label="direct farthest pair"); ax.plot(summary.n_uavs,summary.reliability_route_success_probability_mean,marker="o",label="reliability-aware multi-hop"); ax.set_xlabel("Number of UAVs"); ax.set_ylabel("Derived first-TX success probability"); ax.set_ylim(0,1.05); ax.set_title("Direct vs multi-hop reliability abstraction"); ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(figs/"direct_vs_multihop_reliability.png",dpi=300); fig.savefig(figs/"direct_vs_multihop_reliability.pdf"); plt.close(fig)
    print(summary.to_string(index=False))

if __name__=="__main__": main()

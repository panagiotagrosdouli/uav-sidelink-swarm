"""Incremental cross-layer ablation for the experimental UAV sidelink system.

Resource allocation and link adaptation are THIS_WORK; HARQ is ideal Chase
Combining; directionality is an explicit sensitivity abstraction. TBS/LDPC are
standards-based and BLER is from the bundled limited 5G-LENA fixture.

Four-resource cases partition the 133-PRB carrier as 34/33/33/33 PRBs instead
of silently discarding one PRB. The directional6 scenario applies +3 dB desired
link gain and -3 dB co-channel interference gain, for a 6 dB desired/interferer
relative advantage. This avoids the previous ambiguity where a parameter named
"directional6" was implemented as +6 dB desired gain only.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.energy import energy_per_delivered_bit_joule
from src.metrics import jain_fairness, summarize
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.harq import estimate_ideal_chase_harq
from src.sidelink.resource_allocation import weighted_conflict_graph_allocation
from src.sidelink.resource_grid import SidelinkResourceGrid
from src.sidelink.tb_link_model import estimate_tb_bler
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm
MCS_CANDIDATES=[4,5,6]
SCENARIOS=["baseline_fixed_mcs4_shared","adaptive_mcs_shared","adaptive_graph4","adaptive_harq4_shared","adaptive_directional6_shared","combined_graph4_harq4_directional6"]
N_VALUES=[10,20,30,50,75,100]
BLER_CSV="data/reference/5glena_table1_bg1_cbs4096_subset.csv"

def _choose_mcs(curves,sinr_db,grid,fixed_mcs=None):
    candidates=[fixed_mcs] if fixed_mcs is not None else MCS_CANDIDATES; choices=[]
    for mcs in candidates:
        tbs=grid.tbs_bits(mcs)
        try: estimate=estimate_tb_bler(curves,mcs,tbs,sinr_db)
        except ValueError: continue
        choices.append((tbs*estimate.first_tx_success_probability,mcs,tbs,estimate))
    return max(choices,key=lambda x:(x[0],-x[1])) if choices else None

def _evaluate(seed,n_uavs,scenario,curves):
    cfg=SwarmConfig(n_uavs=n_uavs,seed=seed); positions=generate_equal_altitude_positions(cfg,np.random.default_rng(seed)); pairs=build_disjoint_pairs(n_uavs)
    tx_pos=np.array([positions[t] for t,_ in pairs]); rx_pos=np.array([positions[r] for _,r in pairs])
    n_resources=4 if "graph4" in scenario else 1
    allocation=weighted_conflict_graph_allocation(tx_pos,rx_pos,4).resources if n_resources==4 else np.zeros(len(pairs),dtype=int)
    # Exact 133-PRB partition: resource 0 receives the remainder PRB.
    prb_by_resource=[34,33,33,33] if n_resources==4 else [133]
    desired_gain_db=3.0 if "directional6" in scenario else 0.0
    interference_gain_db=-3.0 if "directional6" in scenario else 0.0
    desired_gain_linear=10**(desired_gain_db/10); interference_gain_linear=10**(interference_gain_db/10)
    use_harq="harq4" in scenario; fixed_mcs=4 if scenario=="baseline_fixed_mcs4_shared" else None
    noise_w=float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz*1e6,cfg.noise_figure_db)))
    successes=[]; goodputs=[]; latencies=[]; energies=[]; sinrs=[]; selected=[]
    for i,(tx,rx) in enumerate(pairs):
        resource=int(allocation[i]); grid=SidelinkResourceGrid(n_prb=prb_by_resource[resource])
        signal_w,_,_=received_power_w(tx,rx,positions,cfg); signal_w*=desired_gain_linear
        interference_w=0.0
        for j,(other_tx,_) in enumerate(pairs):
            if i==j or allocation[j]!=resource: continue
            p_i,_,_=received_power_w(other_tx,rx,positions,cfg); interference_w+=p_i*interference_gain_linear
        sinr_db=float(10*np.log10(signal_w/(noise_w+interference_w))); sinrs.append(sinr_db); choice=_choose_mcs(curves,sinr_db,grid,fixed_mcs)
        if choice is None:
            successes.append(0.0); goodputs.append(0.0); latencies.append(grid.slot_duration_ms); energies.append(float("inf")); selected.append(-1); continue
        _,mcs,tbs,estimate=choice; selected.append(mcs)
        if use_harq:
            harq=estimate_ideal_chase_harq(curves,mcs_index=mcs,tbs_bits=tbs,per_attempt_sinr_db=[sinr_db]*4,numerology_mu=1,feedback_and_retx_gap_slots=2)
            success=harq.success_by_final_attempt; latency_ms=harq.expected_latency_ms; goodput=harq.expected_delivered_goodput_mbps; attempts=harq.expected_attempts_consumed
        else:
            success=estimate.first_tx_success_probability; latency_ms=grid.slot_duration_ms; goodput=(tbs*success/latency_ms)/1000; attempts=1.0
        successes.append(success); goodputs.append(goodput); latencies.append(latency_ms)
        energies.append(energy_per_delivered_bit_joule(cfg.tx_power_dbm,grid.slot_duration_ms/1000,delivered_bits=tbs*success,attempts=attempts))
    finite=[e for e in energies if np.isfinite(e)]
    return {"seed":seed,"n_uavs":n_uavs,"scenario":scenario,"mean_sinr_db":float(np.mean(sinrs)),"mean_success_probability":float(np.mean(successes)),"mean_goodput_mbps":float(np.mean(goodputs)),"median_goodput_mbps":float(np.median(goodputs)),"jain_goodput_fairness":jain_fairness(goodputs),"mean_latency_ms":float(np.mean(latencies)),"mean_energy_per_delivered_bit_j":float(np.mean(finite)) if finite else np.inf,"median_selected_mcs":float(np.median([m for m in selected if m>=0])) if any(m>=0 for m in selected) else -1.0,"directional_desired_gain_db":desired_gain_db,"directional_interference_gain_db":interference_gain_db}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true"); p.add_argument("--seeds",type=int,default=100); a=p.parse_args(); seeds=range(2 if a.smoke else a.seeds); ns=[10,30] if a.smoke else N_VALUES; scenarios=[SCENARIOS[0],SCENARIOS[1],SCENARIOS[-1]] if a.smoke else SCENARIOS; curves=load_bler_curves(BLER_CSV,source="5G-LENA verified Table1 subset")
    raw=pd.DataFrame([_evaluate(s,n,x,curves) for n in ns for x in scenarios for s in seeds]); out=Path("results/ablation"); figs=Path("figures/ablation"); out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); raw.to_csv(out/"per_seed.csv",index=False)
    rows=[]
    for (n,scenario),g in raw.groupby(["n_uavs","scenario"]):
        row={"n_uavs":n,"scenario":scenario}
        for metric in ["mean_success_probability","mean_goodput_mbps","jain_goodput_fairness","mean_latency_ms","mean_energy_per_delivered_bit_j"]:
            finite=g[metric].replace([np.inf,-np.inf],np.nan).dropna()
            if len(finite):
                for k,v in summarize(finite).items(): row[f"{metric}_{k}"]=v
        rows.append(row)
    summary=pd.DataFrame(rows); summary.to_csv(out/"summary.csv",index=False)
    for metric,ylabel,stem in [("mean_goodput_mbps_mean","Mean delivered PHY goodput [Mbps]","goodput"),("mean_success_probability_mean","Mean success probability","reliability"),("mean_latency_ms_mean","Mean modeled delivery latency [ms]","latency")]:
        fig,ax=plt.subplots(figsize=(8.2,5.2))
        for scenario,g in summary.groupby("scenario"): ax.plot(g.n_uavs,g[metric],marker="o",label=scenario.replace("_"," "))
        ax.set_xlabel("Number of UAVs"); ax.set_ylabel(ylabel); ax.set_title("Cross-layer ablation"); ax.grid(True,alpha=.3); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(figs/f"{stem}_ablation.png",dpi=300); fig.savefig(figs/f"{stem}_ablation.pdf"); plt.close(fig)
    print(summary.to_string(index=False))
if __name__=="__main__": main()

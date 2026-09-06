"""Cross-layer ablation using only BLER-fixture-supported shared-resource cases.

Resource-allocation comparisons remain in resource_allocation_study. We do not
fabricate BLER for smaller TBS/code-block regimes caused by PRB partitioning.
Link adaptation is THIS_WORK; HARQ is ideal Chase Combining; directionality is
an experimental sensitivity abstraction.
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
from src.sidelink.resource_grid import SidelinkResourceGrid
from src.sidelink.tb_link_model import estimate_tb_bler
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm
MCS_CANDIDATES=[4,5,6]
SCENARIOS=["baseline_fixed_mcs4_shared","adaptive_mcs_shared","adaptive_harq4_shared","adaptive_directional6_shared","adaptive_harq4_directional6_shared"]
N_VALUES=[10,20,30,50,75,100]
BLER_CSV="data/reference/5glena_table1_bg1_cbs4096_subset.csv"
def _choose_mcs(curves,sinr_db,grid,fixed_mcs=None):
    choices=[]
    for mcs in ([fixed_mcs] if fixed_mcs is not None else MCS_CANDIDATES):
        tbs=grid.tbs_bits(mcs)
        try: estimate=estimate_tb_bler(curves,mcs,tbs,sinr_db)
        except ValueError: continue
        choices.append((tbs*estimate.first_tx_success_probability,mcs,tbs,estimate))
    return max(choices,key=lambda x:(x[0],-x[1])) if choices else None
def _evaluate(seed,n_uavs,scenario,curves):
    cfg=SwarmConfig(n_uavs=n_uavs,seed=seed); positions=generate_equal_altitude_positions(cfg,np.random.default_rng(seed)); pairs=build_disjoint_pairs(n_uavs); grid=SidelinkResourceGrid(n_prb=133)
    dg=3.0 if "directional6" in scenario else 0.0; ig=-3.0 if "directional6" in scenario else 0.0; dlin=10**(dg/10); ilin=10**(ig/10); use_harq="harq4" in scenario; fixed=4 if scenario=="baseline_fixed_mcs4_shared" else None
    noise=float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz*1e6,cfg.noise_figure_db))); successes=[]; goodputs=[]; latencies=[]; energies=[]; sinrs=[]; selected=[]
    for i,(tx,rx) in enumerate(pairs):
        signal,_,_=received_power_w(tx,rx,positions,cfg); signal*=dlin; interference=0.0
        for j,(other_tx,_) in enumerate(pairs):
            if i!=j:
                p,_,_=received_power_w(other_tx,rx,positions,cfg); interference+=p*ilin
        sinr=float(10*np.log10(signal/(noise+interference))); sinrs.append(sinr); choice=_choose_mcs(curves,sinr,grid,fixed)
        if choice is None: successes.append(0.0); goodputs.append(0.0); latencies.append(grid.slot_duration_ms); energies.append(float("inf")); selected.append(-1); continue
        _,mcs,tbs,est=choice; selected.append(mcs)
        if use_harq:
            h=estimate_ideal_chase_harq(curves,mcs_index=mcs,tbs_bits=tbs,per_attempt_sinr_db=[sinr]*4,numerology_mu=1,feedback_and_retx_gap_slots=2); success=h.success_by_final_attempt; latency=h.expected_latency_ms; goodput=h.expected_delivered_goodput_mbps; attempts=h.expected_attempts_consumed
        else: success=est.first_tx_success_probability; latency=grid.slot_duration_ms; goodput=(tbs*success/latency)/1000; attempts=1.0
        successes.append(success); goodputs.append(goodput); latencies.append(latency); energies.append(energy_per_delivered_bit_joule(cfg.tx_power_dbm,grid.slot_duration_ms/1000,delivered_bits=tbs*success,attempts=attempts))
    finite=[x for x in energies if np.isfinite(x)]
    return {"seed":seed,"n_uavs":n_uavs,"scenario":scenario,"mean_sinr_db":float(np.mean(sinrs)),"mean_success_probability":float(np.mean(successes)),"mean_goodput_mbps":float(np.mean(goodputs)),"median_goodput_mbps":float(np.median(goodputs)),"jain_goodput_fairness":jain_fairness(goodputs),"mean_latency_ms":float(np.mean(latencies)),"mean_energy_per_delivered_bit_j":float(np.mean(finite)) if finite else np.inf,"median_selected_mcs":float(np.median([m for m in selected if m>=0])) if any(m>=0 for m in selected) else -1.0,"directional_desired_gain_db":dg,"directional_interference_gain_db":ig}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true"); p.add_argument("--seeds",type=int,default=100); a=p.parse_args(); seeds=range(2 if a.smoke else a.seeds); ns=[10,30] if a.smoke else N_VALUES; scenarios=[SCENARIOS[0],SCENARIOS[1],SCENARIOS[-1]] if a.smoke else SCENARIOS; curves=load_bler_curves(BLER_CSV,source="5G-LENA verified Table1 subset")
    raw=pd.DataFrame([_evaluate(s,n,x,curves) for n in ns for x in scenarios for s in seeds]); out=Path("results/ablation"); figs=Path("figures/ablation"); out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); raw.to_csv(out/"per_seed.csv",index=False); rows=[]
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
        ax.set_xlabel("Number of UAVs"); ax.set_ylabel(ylabel); ax.set_title("Cross-layer ablation — fixture-supported cases"); ax.grid(True,alpha=.3); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(figs/f"{stem}_ablation.png",dpi=300); fig.savefig(figs/f"{stem}_ablation.pdf"); plt.close(fig)
    print(summary.to_string(index=False))
if __name__=="__main__": main()

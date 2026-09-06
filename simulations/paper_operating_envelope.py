"""Paper experiment: density x resources x directionality operating envelope.

All RF/network outputs are DERIVED_SYSTEM_LEVEL_METRIC. Resource counts and
spatial gain/suppression values are EXPERIMENTAL_SWEEP choices. Allocations are
THIS_WORK abstractions, not normative NR Sidelink Mode 1/2 scheduling.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.sidelink.adaptive_tb import load_preferred_bler_curves, select_tbs_aware_mcs
from src.sidelink.resource_allocation import weighted_conflict_graph_allocation
from src.swarm_system import SwarmConfig, build_disjoint_pairs, dbm_to_w, generate_equal_altitude_positions, received_power_w, thermal_noise_dbm

N_VALUES=[5,10,20,30,50,75,100]; RESOURCE_COUNTS=[1,2,4,8]; ADVANTAGES_DB=[0.0,3.0,6.0,9.0]
SUCCESS_TARGET=0.10; GOODPUT_TARGET_MBPS=1.0

def snapshot(seed,n_uavs,n_resources,advantage_db,curves):
    cfg=SwarmConfig(n_uavs=n_uavs,seed=seed); rng=np.random.default_rng(seed); pos=generate_equal_altitude_positions(cfg,rng); pairs=build_disjoint_pairs(n_uavs)
    tx=np.array([pos[t] for t,_ in pairs]); rx=np.array([pos[r] for _,r in pairs]); resources=np.zeros(len(pairs),dtype=int) if n_resources==1 else weighted_conflict_graph_allocation(tx,rx,n_resources).resources
    noise=float(dbm_to_w(thermal_noise_dbm(cfg.bandwidth_mhz*1e6,cfg.noise_figure_db))); desired_gain=10**((advantage_db/2)/10); interference_gain=10**((-advantage_db/2)/10)
    sinrs=[]; successes=[]; goodputs=[]
    for i,(t,r) in enumerate(pairs):
        signal,_,_=received_power_w(t,r,pos,cfg); signal*=desired_gain; interf=0.0
        for j,(ot,_) in enumerate(pairs):
            if j==i or resources[j]!=resources[i]: continue
            p,_,_=received_power_w(ot,r,pos,cfg); interf+=p*interference_gain
        sinr=10*np.log10(signal/(noise+interf)); choice=select_tbs_aware_mcs(sinr,curves)
        sinrs.append(sinr); successes.append(choice.success_probability if choice else np.nan); goodputs.append(choice.expected_goodput_mbps if choice else np.nan)
    return float(np.mean(sinrs)),float(np.nanmean(successes)),float(np.nanmean(goodputs))

def ci95(x):
    a=np.asarray(x,float); m=float(np.mean(a)); h=1.96*float(np.std(a,ddof=1))/np.sqrt(len(a)) if len(a)>1 else 0.0; return m,m-h,m+h

def main():
    p=argparse.ArgumentParser(); p.add_argument('--smoke',action='store_true'); p.add_argument('--seeds',type=int,default=100); a=p.parse_args(); curves,curve_mode=load_preferred_bler_curves()
    ns=[5,20] if a.smoke else N_VALUES; rs=[1,4] if a.smoke else RESOURCE_COUNTS; gs=[0.0,6.0] if a.smoke else ADVANTAGES_DB; seeds=range(2 if a.smoke else a.seeds)
    out=Path('results/paper_operating_envelope'); figs=Path('figures/paper_operating_envelope'); out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); rows=[]
    for n in ns:
      for r in rs:
       for g in gs:
        for seed in seeds:
         sinr,succ,gp=snapshot(seed,n,r,g,curves); rows.append({'n_uavs':n,'n_resources':r,'directional_relative_advantage_db':g,'seed':seed,'mean_sinr_db':sinr,'mean_first_tx_success':succ,'mean_expected_goodput_mbps':gp,'curve_mode':curve_mode})
    raw=pd.DataFrame(rows); raw.to_csv(out/'per_seed.csv',index=False); summary=[]
    for keys,q in raw.groupby(['n_uavs','n_resources','directional_relative_advantage_db']):
      row=dict(zip(['n_uavs','n_resources','directional_relative_advantage_db'],keys))
      for col in ['mean_sinr_db','mean_first_tx_success','mean_expected_goodput_mbps']:
       m,lo,hi=ci95(q[col]); row[col]=m; row[col+'_ci95_low']=lo; row[col+'_ci95_high']=hi
      summary.append(row)
    s=pd.DataFrame(summary); s.to_csv(out/'summary.csv',index=False); env=[]
    for (r,g),q in s.groupby(['n_resources','directional_relative_advantage_db']):
      ok=q[(q.mean_first_tx_success>=SUCCESS_TARGET)&(q.mean_expected_goodput_mbps>=GOODPUT_TARGET_MBPS)]
      env.append({'n_resources':r,'directional_relative_advantage_db':g,'success_target':SUCCESS_TARGET,'goodput_target_mbps':GOODPUT_TARGET_MBPS,'max_evaluated_n_meeting_both_targets':int(ok.n_uavs.max()) if len(ok) else 0,'classification':'DERIVED_SYSTEM_LEVEL_METRIC_FROM_EXPERIMENTAL_POLICY_TARGETS'})
    e=pd.DataFrame(env); e.to_csv(out/'operating_envelope.csv',index=False)
    if not a.smoke:
      for g in gs:
       q=s[s.directional_relative_advantage_db==g]; pivot=q.pivot(index='n_uavs',columns='n_resources',values='mean_first_tx_success'); fig,ax=plt.subplots(figsize=(6.8,4.8)); im=ax.imshow(pivot.values,aspect='auto',origin='lower'); ax.set_xticks(range(len(pivot.columns)),pivot.columns); ax.set_yticks(range(len(pivot.index)),pivot.index); ax.set_xlabel('Abstract orthogonal resources'); ax.set_ylabel('UAVs'); ax.set_title(f'First-TX success, directional advantage {g:g} dB'); fig.colorbar(im,ax=ax,label='Mean first-TX success'); fig.tight_layout(); fig.savefig(figs/f'success_heatmap_g{int(g)}.pdf'); fig.savefig(figs/f'success_heatmap_g{int(g)}.png',dpi=300); plt.close(fig)
    print(e.to_string(index=False))
if __name__=='__main__': main()

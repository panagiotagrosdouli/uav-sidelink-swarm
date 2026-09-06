"""Collate canonical outputs, audit them, and generate current-run evidence metadata."""
from __future__ import annotations
import json, platform, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, yaml
RESULT_OUT=Path("results/final_campaign"); FIG_OUT=Path("figures/final_campaign")
FIGURE_MAP={"fig01_channel_models":"figures/pathloss/pathloss_comparison.pdf","fig02_sinr_density":"figures/density/mean_sinr_vs_swarm_size.pdf","fig03_sinr_cdf":"figures/density/sinr_cdf.pdf","fig04_bler_density":"figures/nr_link_performance/bler_vs_density.pdf","fig05_goodput_density":"figures/nr_link_performance/goodput_vs_density.pdf","fig06_latency_density":"figures/harq_tbs_latency/latency_vs_density.pdf","fig07_resource_allocation":"figures/resource_allocation/goodput_resources_n50.pdf","fig08_routing":"figures/routing/direct_vs_multihop_reliability.pdf","fig09_beamforming":"figures/beamforming/goodput_vs_directionality.pdf","fig10_harq":"figures/harq_tbs_latency/success_vs_density.pdf","fig11_real_mobility":"figures/mobility/real_pair_distance_vs_time.pdf","fig12_ablation":"figures/ablation/goodput_ablation.pdf","fig13_scaling":"figures/scaling_geometry_activity/fixed_area_vs_fixed_density.pdf","fig14_activity":"figures/scaling_geometry_activity/activity_factor_sinr.pdf","fig15_failures":"figures/failure_analysis/failure_reason_vs_density.pdf","fig16_ula":"figures/ula_directionality/ula_array_factor.pdf","fig17_traffic":"figures/traffic_load/delivery_vs_density.pdf"}
SUMMARY_SOURCES={"density":"results/density_measurement_based/summary.csv","nr_link_performance":"results/nr_link_performance/summary.csv","harq":"results/harq_tbs_latency/summary.csv","overhead":"results/sidelink_overhead/summary.csv","resource_allocation":"results/resource_allocation/summary.csv","routing":"results/routing/summary.csv","directionality":"results/beamforming_sensitivity/summary.csv","scaling":"results/scaling_geometry_activity/scaling_summary.csv","activity":"results/scaling_geometry_activity/activity_summary.csv","robustness_channel":"results/robustness/channel_summary.csv","traffic":"results/traffic_load/summary.csv","ablation":"results/ablation/summary.csv","failure":"results/failure_analysis/summary.csv","ula":"results/ula_directionality/summary.csv","real_mobility":"results/real_mobility_pair/summary.csv"}
PROBABILITY_TOKENS=("bler","success_probability","delivery_ratio","fairness","connectivity_probability","fraction","outage_proxy"); COUNT_NAMES={"n","count","counts","samples","seeds"}
def _git_sha():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception:return "unknown"
def _copy(src,dst):
    if not src.exists():return False
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); return True
def _is_count(c):
    n=c.lower(); return n in COUNT_NAMES or n.endswith(("_n","_count","_counts","_samples","_seeds"))
def _audit(name,df):
    checks=[]
    for c in df.columns:
        num=pd.to_numeric(df[c],errors="coerce")
        if not num.notna().sum():continue
        v=num.dropna().to_numpy(float); status="pass"; note=""; low=c.lower()
        if _is_count(c):
            if np.any(v < -1e-12):status,note="fail","negative sample/count value"
            elif np.any(np.abs(v-np.rint(v))>1e-9):status,note="fail","non-integer sample/count value"
        else:
            if any(t in low for t in PROBABILITY_TOKENS) and np.any((v < -1e-12)|(v > 1+1e-12)):status,note="fail","probability/fraction outside [0,1]"
            if "latency" in low and np.any(v < -1e-12):status,note="fail","negative latency"
            if "tbs" in low and "bits" in low and np.any(v<=0):status,note="fail","non-positive TBS"
        checks.append({"dataset":name,"column":c,"status":status,"note":note})
    return checks
def _parameter_provenance(cfg):
    b=cfg["baseline"]; r=cfg["nr_resource_profile"]
    return pd.DataFrame([["carrier frequency",b["carrier_ghz"],"GHz","LITERATURE","Erdemir et al. VTC 2023 A2A campaign"],["bandwidth",b["bandwidth_mhz"],"MHz","LITERATURE","Erdemir et al. VTC 2023 A2A campaign"],["baseline TX power",b["tx_power_dbm"],"dBm","LITERATURE","Erdemir campaign value; not universal UAV power"],["baseline altitude",b["altitude_m"],"m","LITERATURE","Erdemir A2A campaign"],["baseline area side",b["area_xy_m"],"m","SYNTHETIC","final campaign configuration"],["receiver noise figure",b["noise_figure_db"],"dB","EXPERIMENTAL_ASSUMPTION","sensitivity-tested"],["PRBs",r["n_prb"],"PRB","STANDARD","50 MHz / 30 kHz FR1 profile"],["SCS",r["scs_khz"],"kHz","STANDARD","NR numerology"],["PSCCH symbols",r["n_pscch_symbols"],"symbols","EXPERIMENTAL_CONFIGURATION","thesis study profile"],["PSSCH symbols",r["n_pssch_symbols"],"symbols","EXPERIMENTAL_CONFIGURATION","thesis study profile"],["DM-RS overhead",r["dmrs_re_per_prb"],"RE/PRB","EXPERIMENTAL_CONFIGURATION","thesis study profile"]],columns=["parameter","value","unit","classification","source_or_note"])
def _scenario_definitions(cfg):
    return pd.DataFrame([{"scenario":"canonical_density","n_uavs":n,"area_xy_m":cfg["baseline"]["area_xy_m"],"height_m":cfg["baseline"]["altitude_m"],"channel":cfg["baseline"]["channel"],"resources":1,"traffic":"full-activity link snapshot","seeds":cfg["campaign"]["seeds"]} for n in cfg["campaign"]["swarm_sizes"]])
def _key_findings(ds,missing):
    lines=["# Evidence-backed key findings\n\n","Generated from this run's final-campaign tables. Values are simulation/derived unless explicitly stated otherwise.\n\n"]
    s=ds.get("scaling")
    if s is not None and {"metric","family","n_uavs","mean","ci95_low","ci95_high"}.issubset(s.columns):
        for fam in ("fixed_area","fixed_density"):
            g=s[(s.metric=="mean_sinr_db")&(s.family==fam)].sort_values("n_uavs")
            if len(g)>=2:
                a,b=g.iloc[0],g.iloc[-1]; lines.append(f"- **Scaling ({fam})**: mean SINR {a['mean']:.2f} dB at N={int(a.n_uavs)} to {b['mean']:.2f} dB at N={int(b.n_uavs)}; final 95% CI [{b.ci95_low:.2f}, {b.ci95_high:.2f}] dB.\n")
    a=ds.get("ablation")
    if a is not None and "mean_goodput_mbps_mean" in a:
        n=int(a.n_uavs.max()); g=a[a.n_uavs==n]; best=g.loc[g.mean_goodput_mbps_mean.idxmax()]; lines.append(f"- **Ablation at N={n}**: best evaluated fixture-supported mechanism is `{best.scenario}` at {best.mean_goodput_mbps_mean:.3f} Mbps modeled goodput.\n")
    r=ds.get("resource_allocation")
    if r is not None and "mean_expected_phy_goodput_mbps" in r:
        n=int(r.n_uavs.max()); g=r[r.n_uavs==n]; best=g.loc[g.mean_expected_phy_goodput_mbps.idxmax()]; lines.append(f"- **Resource allocation at N={n}**: `{best.algorithm}`/{int(best.n_resources)} resources gives {best.mean_expected_phy_goodput_mbps:.3f} Mbps mean derived PHY goodput in the evaluated grid.\n")
    m=ds.get("real_mobility")
    if m is not None and len(m):
        x=m.iloc[0]; lines.append(f"- **AMOVFLY pair**: {int(x.samples)} synchronized telemetry samples over {x.overlap_duration_s:.1f} s; derived horizontal separation {x.horizontal_separation_min_m:.2f}–{x.horizontal_separation_max_m:.2f} m (mean {x.horizontal_separation_mean_m:.2f} m). Mobility evidence, not measured RF.\n")
    if missing:lines.extend(["\n## Missing evidence\n"]+[f"- {x}\n" for x in missing])
    (RESULT_OUT/"key_findings.md").write_text("".join(lines),encoding="utf-8")
def main():
    cfgp=Path("config/final_campaign.yaml"); cfg=yaml.safe_load(cfgp.read_text()); RESULT_OUT.mkdir(parents=True,exist_ok=True); FIG_OUT.mkdir(parents=True,exist_ok=True); shutil.copy2(cfgp,RESULT_OUT/"final_campaign.yaml"); ds={}; missing=[]; audit=[]
    for name,p in SUMMARY_SOURCES.items():
        src=Path(p)
        if src.exists(): df=pd.read_csv(src); ds[name]=df; df.to_csv(RESULT_OUT/f"{name}_summary.csv",index=False); audit.extend(_audit(name,df))
        else:missing.append(f"Missing summary `{src}`")
    figs=[]
    for stem,p in FIGURE_MAP.items():
        src=Path(p); present=_copy(src,FIG_OUT/f"{stem}.pdf"); png=src.with_suffix(".png"); _copy(png,FIG_OUT/f"{stem}.png") if png.exists() else None; figs.append({"figure":stem,"source":p,"present":present})
        if not present:missing.append(f"Missing canonical figure `{stem}` from `{p}`")
    bm=Path("data/generated/5glena_v5_table1_bler_manifest.json"); _copy(bm,RESULT_OUT/"5glena_v5_table1_bler_manifest.json") if bm.exists() else None
    mp=Path("results/real_mobility_pair/provenance.csv"); _copy(mp,RESULT_OUT/"real_mobility_provenance.csv") if mp.exists() else None
    _parameter_provenance(cfg).to_csv(RESULT_OUT/"parameter_provenance.csv",index=False); _scenario_definitions(cfg).to_csv(RESULT_OUT/"scenario_definitions.csv",index=False)
    pd.DataFrame(audit).to_csv(RESULT_OUT/"scientific_audit.csv",index=False); pd.DataFrame(figs).to_csv(RESULT_OUT/"figure_manifest.csv",index=False); _key_findings(ds,missing)
    failures=[x for x in audit if x["status"]=="fail"]; sha=_git_sha(); manifest={"campaign":cfg["campaign"]["name"],"generated_utc":datetime.now(timezone.utc).isoformat(),"git_sha":sha,"python":sys.version,"platform":platform.platform(),"config":str(cfgp),"summaries_present":sorted(ds),"missing_external_or_optional":missing,"scientific_audit_failures":failures,"canonical_results_dir":str(RESULT_OUT),"canonical_figures_dir":str(FIG_OUT),"non_claims":cfg["non_claims"]}; (RESULT_OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    status={"canonical_git_sha":sha,"scientific_audit_rows":len(audit),"scientific_audit_failures":len(failures),"registered_experiments":18,"figure_count":len(figs),"figures_present":sum(bool(x["present"]) for x in figs),"missing_external_or_optional_count":len(missing),"status":"pass" if not failures and not missing else "fail","note":"Generated by this run; workflow/artifact IDs are frozen only after successful completion."}; (RESULT_OUT/"audit_summary.json").write_text(json.dumps(status,indent=2)+"\n"); print(json.dumps(manifest,indent=2)); return 1 if failures or missing else 0
if __name__=="__main__":raise SystemExit(main())

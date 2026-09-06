"""Process a simultaneous AMOVFLY pair in a shared WGS84-derived frame.

The public ready CSVs provide real_lat/real_long but no verified common absolute
altitude. Therefore the canonical public-pair run reports measured-dataset-derived
HORIZONTAL separation only and does not fabricate 3D RF performance. If a future
source provides absolute altitude, the existing 3D path can be extended explicitly.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from src.mobility.amovfly import common_origin_from_trajectories,load_ready_csv,parse_takeoff_time,synchronize_pair,trajectory_to_common_enu

def main():
    p=argparse.ArgumentParser(); p.add_argument("--uav1-file",required=True); p.add_argument("--uav1-time",required=True); p.add_argument("--uav2-file",required=True); p.add_argument("--uav2-time",required=True); p.add_argument("--sample-period",type=float,default=0.2); p.add_argument("--output-dir",default="results/real_mobility_pair"); a=p.parse_args()
    g1=load_ready_csv(a.uav1_file,prefer_global=True); g2=load_ready_csv(a.uav2_file,prefer_global=True)
    origin=common_origin_from_trajectories(g1,g2); t1=trajectory_to_common_enu(g1,origin); t2=trajectory_to_common_enu(g2,origin)
    aligned=synchronize_pair(t1,parse_takeoff_time(a.uav1_time),t2,parse_takeoff_time(a.uav2_time),a.sample_period)
    out=Path(a.output_dir); figs=Path("figures/mobility"); out.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True)
    aligned.to_csv(out/"aligned_pair_mobility.csv",index=False)
    horizontal_only=bool((aligned.distance_dimension=="2D_HORIZONTAL").all())
    pd.DataFrame([{"origin_lon_deg":origin[0],"origin_lat_deg":origin[1],"origin_altitude_m":origin[2],"coordinate_frame":aligned.coordinate_frame.iloc[0],"mobility_source":"AMOVFLY public ready CSV","mobility_classification":"MEASURED_DATASET","synchronized_distance_classification":"DERIVED_FROM_MEASURED_DATASET","distance_dimension":"2D_HORIZONTAL" if horizontal_only else "3D","rf_metrics_generated":False,"reason_no_rf":"Public pair lacks verified common absolute altitude; 3D A2A distance is not reconstructed." if horizontal_only else "RF intentionally excluded from this mobility-only canonical run."}]).to_csv(out/"provenance.csv",index=False)
    fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.plot(aligned.elapsed_overlap_s,aligned.a2a_distance_m); ax.set_xlabel("Overlapping flight time [s]"); ax.set_ylabel("Horizontal UAV separation [m]" if horizontal_only else "UAV separation [m]"); ax.set_title("AMOVFLY simultaneous-flight separation (measured mobility)"); ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(figs/"real_pair_distance_vs_time.png",dpi=300); fig.savefig(figs/"real_pair_distance_vs_time.pdf"); plt.close(fig)
    print(aligned.a2a_distance_m.describe().to_string()); print("distance_dimension:",aligned.distance_dimension.iloc[0]); print("RF metrics generated: false")
if __name__=="__main__": main()

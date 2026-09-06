"""Load and synchronize real AMOVFLY UAV telemetry trajectories.

AMOVFLY is a measured mobility/telemetry source, not an RF measurement source.
Published ready CSVs currently expose geodetic coordinates as real_long/real_lat
and local coordinates as gps_x/gps_y/gps_z. The local xyz origins are not assumed
common across UAVs.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

LOCAL_REQUIRED_COLUMNS = ("time", "gps_x", "gps_y", "gps_z")
WGS84_A_M = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)

@dataclass(frozen=True)
class Trajectory:
    uav_name: str
    data: pd.DataFrame
    source: str = "AMOVFLY"
    classification: str = "MEASURED_DATASET"
    coordinate_frame: str = "LOCAL_UNKNOWN_ORIGIN"

def _clean_frame(df):
    unnamed=[c for c in df.columns if str(c).startswith("Unnamed:") or str(c)==""]
    return df.drop(columns=unnamed) if unnamed else df

def load_ready_csv(path, uav_name=None, prefer_global=True):
    path=Path(path); df=_clean_frame(pd.read_csv(path)); name=uav_name or path.stem
    # Support both historical aliases and the column names in the public repository.
    lon_col = "gps_lon" if "gps_lon" in df else ("real_long" if "real_long" in df else None)
    lat_col = "gps_lat" if "gps_lat" in df else ("real_lat" if "real_lat" in df else None)
    alt_col = "altitude" if "altitude" in df else None
    if prefer_global and lon_col and lat_col:
        cols=["time",lon_col,lat_col] + ([alt_col] if alt_col else [])
        out=df.loc[:,cols].rename(columns={"time":"time_s",lon_col:"lon_deg",lat_col:"lat_deg",alt_col:"altitude_m" if alt_col else alt_col})
        out=out.apply(pd.to_numeric,errors="coerce").dropna().sort_values("time_s").drop_duplicates("time_s").reset_index(drop=True)
        if out.empty: raise ValueError("trajectory contains no valid global samples")
        frame="WGS84_GEODETIC_3D" if "altitude_m" in out else "WGS84_GEODETIC_2D"
        return Trajectory(name,out,coordinate_frame=frame)
    missing=[c for c in LOCAL_REQUIRED_COLUMNS if c not in df]
    if missing: raise ValueError(f"missing AMOVFLY columns: {missing}")
    out=df.loc[:,LOCAL_REQUIRED_COLUMNS].rename(columns={"time":"time_s","gps_x":"x_m","gps_y":"y_m","gps_z":"z_m"})
    out=out.apply(pd.to_numeric,errors="coerce").dropna().sort_values("time_s").drop_duplicates("time_s").reset_index(drop=True)
    if out.empty: raise ValueError("trajectory contains no valid samples")
    return Trajectory(name,out,coordinate_frame="LOCAL_UNKNOWN_ORIGIN")

def parse_takeoff_time(value): return datetime.strptime(value.strip(),"%Y/%m/%d %H:%M")

def geodetic_to_ecef(lon_deg,lat_deg,altitude_m):
    lon=np.deg2rad(np.asarray(lon_deg,float)); lat=np.deg2rad(np.asarray(lat_deg,float)); h=np.asarray(altitude_m,float)
    s=np.sin(lat); c=np.cos(lat); n=WGS84_A_M/np.sqrt(1-WGS84_E2*s*s)
    return np.column_stack([(n+h)*c*np.cos(lon),(n+h)*c*np.sin(lon),(n*(1-WGS84_E2)+h)*s])

def ecef_to_enu(ecef_m,origin_lon_deg,origin_lat_deg,origin_altitude_m):
    ecef=np.asarray(ecef_m,float)
    if ecef.ndim!=2 or ecef.shape[1]!=3: raise ValueError("ecef_m must have shape [n,3]")
    origin=geodetic_to_ecef([origin_lon_deg],[origin_lat_deg],[origin_altitude_m])[0]; d=ecef-origin
    lon=np.deg2rad(origin_lon_deg); lat=np.deg2rad(origin_lat_deg)
    r=np.array([[-np.sin(lon),np.cos(lon),0],[-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)],[np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)]])
    return d@r.T

def trajectory_to_common_enu(trajectory,origin):
    if trajectory.coordinate_frame not in {"WGS84_GEODETIC_2D","WGS84_GEODETIC_3D","WGS84_GEODETIC"}: raise ValueError("trajectory must contain WGS84 geodetic coordinates")
    df=trajectory.data; alt=df.altitude_m.to_numpy(float) if "altitude_m" in df else np.zeros(len(df))
    enu=ecef_to_enu(geodetic_to_ecef(df.lon_deg,df.lat_deg,alt),*origin)
    out=pd.DataFrame({"time_s":df.time_s.to_numpy(float),"x_m":enu[:,0],"y_m":enu[:,1],"z_m":enu[:,2]})
    # 2D source has no trustworthy common vertical coordinate: force z=0 and label it.
    if trajectory.coordinate_frame=="WGS84_GEODETIC_2D": out["z_m"]=0.0
    frame="COMMON_ENU_WGS84_3D" if trajectory.coordinate_frame!="WGS84_GEODETIC_2D" else "COMMON_ENU_WGS84_HORIZONTAL_ONLY"
    return Trajectory(trajectory.uav_name,out,classification="DERIVED_FROM_MEASURED_DATASET",coordinate_frame=frame)

def common_origin_from_trajectories(*trajectories):
    if not trajectories: raise ValueError("at least one trajectory is required")
    allowed={"WGS84_GEODETIC_2D","WGS84_GEODETIC_3D","WGS84_GEODETIC"}
    if any(t.coordinate_frame not in allowed for t in trajectories): raise ValueError("all trajectories must be WGS84 geodetic")
    lon=np.mean([float(t.data.lon_deg.iloc[0]) for t in trajectories]); lat=np.mean([float(t.data.lat_deg.iloc[0]) for t in trajectories])
    alts=[float(t.data.altitude_m.iloc[0]) for t in trajectories if "altitude_m" in t.data]
    return float(lon),float(lat),float(np.mean(alts) if alts else 0.0)

def synchronize_pair(first,first_takeoff,second,second_takeoff,sample_period_s=0.2):
    if sample_period_s<=0: raise ValueError("sample_period_s must be positive")
    req={"time_s","x_m","y_m","z_m"}
    if not req.issubset(first.data) or not req.issubset(second.data): raise ValueError("synchronize_pair requires Cartesian trajectories")
    if first.coordinate_frame!=second.coordinate_frame: raise ValueError("trajectory coordinate frames do not match")
    if first.coordinate_frame=="LOCAL_UNKNOWN_ORIGIN": raise ValueError("unsafe local origins")
    a=first.data.copy(); b=second.data.copy(); a["absolute_s"]=first_takeoff.timestamp()+a.time_s; b["absolute_s"]=second_takeoff.timestamp()+b.time_s
    start=max(a.absolute_s.min(),b.absolute_s.min()); end=min(a.absolute_s.max(),b.absolute_s.max())
    if end<=start: raise ValueError("trajectories do not overlap in time")
    grid=np.arange(start,end+0.5*sample_period_s,sample_period_s)
    interp=lambda df,c: np.interp(grid,df.absolute_s.to_numpy(),df[c].to_numpy())
    out=pd.DataFrame({"absolute_time_s":grid,"elapsed_overlap_s":grid-start,"uav1_x_m":interp(a,"x_m"),"uav1_y_m":interp(a,"y_m"),"uav1_z_m":interp(a,"z_m"),"uav2_x_m":interp(b,"x_m"),"uav2_y_m":interp(b,"y_m"),"uav2_z_m":interp(b,"z_m")})
    dx=out.uav1_x_m-out.uav2_x_m; dy=out.uav1_y_m-out.uav2_y_m; dz=out.uav1_z_m-out.uav2_z_m
    out["a2a_distance_m"]=np.sqrt(dx*dx+dy*dy+dz*dz); out["classification"]="DERIVED_FROM_MEASURED_DATASET"; out["coordinate_frame"]=first.coordinate_frame
    out["distance_dimension"]="2D_HORIZONTAL" if "HORIZONTAL_ONLY" in first.coordinate_frame else "3D"
    return out

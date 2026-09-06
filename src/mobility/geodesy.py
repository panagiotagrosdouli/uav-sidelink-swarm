"""Minimal WGS-84 geodesy helpers for putting multiple UAVs in one frame.

These deterministic transforms are used to derive a common Cartesian frame
from measured latitude/longitude/altitude telemetry.  The transformed positions
are DERIVED_FROM_MEASURED_DATASET, not additional measurements.
"""
from __future__ import annotations

import numpy as np

# WGS-84 ellipsoid constants.
WGS84_A_M = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)


def geodetic_to_ecef(
    latitude_deg: float | np.ndarray,
    longitude_deg: float | np.ndarray,
    altitude_m: float | np.ndarray,
) -> np.ndarray:
    """Convert geodetic WGS-84 coordinates to ECEF XYZ in metres."""
    lat = np.deg2rad(np.asarray(latitude_deg, dtype=float))
    lon = np.deg2rad(np.asarray(longitude_deg, dtype=float))
    alt = np.asarray(altitude_m, dtype=float)
    lat, lon, alt = np.broadcast_arrays(lat, lon, alt)
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    sin_lon = np.sin(lon)
    cos_lon = np.cos(lon)
    n = WGS84_A_M / np.sqrt(1.0 - WGS84_E2 * sin_lat**2)
    x = (n + alt) * cos_lat * cos_lon
    y = (n + alt) * cos_lat * sin_lon
    z = (n * (1.0 - WGS84_E2) + alt) * sin_lat
    return np.stack([x, y, z], axis=-1)


def ecef_to_enu(
    ecef_xyz_m: np.ndarray,
    reference_latitude_deg: float,
    reference_longitude_deg: float,
    reference_altitude_m: float,
) -> np.ndarray:
    """Convert ECEF positions to local ENU using one shared WGS-84 reference."""
    xyz = np.asarray(ecef_xyz_m, dtype=float)
    if xyz.shape[-1] != 3:
        raise ValueError("ecef_xyz_m must end in dimension 3")
    ref = geodetic_to_ecef(
        reference_latitude_deg,
        reference_longitude_deg,
        reference_altitude_m,
    )
    d = xyz - ref
    lat0 = np.deg2rad(float(reference_latitude_deg))
    lon0 = np.deg2rad(float(reference_longitude_deg))
    slat, clat = np.sin(lat0), np.cos(lat0)
    slon, clon = np.sin(lon0), np.cos(lon0)
    rotation = np.array(
        [
            [-slon, clon, 0.0],
            [-slat * clon, -slat * slon, clat],
            [clat * clon, clat * slon, slat],
        ],
        dtype=float,
    )
    return np.einsum("...j,ij->...i", d, rotation)


def geodetic_to_enu(
    latitude_deg: float | np.ndarray,
    longitude_deg: float | np.ndarray,
    altitude_m: float | np.ndarray,
    reference_latitude_deg: float,
    reference_longitude_deg: float,
    reference_altitude_m: float,
) -> np.ndarray:
    """Convenience WGS-84 geodetic -> ECEF -> common ENU transform."""
    return ecef_to_enu(
        geodetic_to_ecef(latitude_deg, longitude_deg, altitude_m),
        reference_latitude_deg,
        reference_longitude_deg,
        reference_altitude_m,
    )

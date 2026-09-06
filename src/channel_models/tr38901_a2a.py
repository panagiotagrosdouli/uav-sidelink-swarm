"""3GPP Rel-19 aerial-UE-to-aerial-UE large-scale channel helpers.

Scientific basis
----------------
3GPP TR 38.901 V19.4.0, Clause 7.9.3, Case 9, specifies aerial UE to aerial UE
links for UMi-AV/UMa-AV/RMa-AV by reusing the TRP-aerial-UE models from
3GPP TR 36.777 Annexes A/B, with TRP height set equal to the first aerial UE.

This module implements a deliberately limited, auditable subset suitable for
our first equal-height UMi-AV A2A comparison:
  * equal-height aerial UEs only;
  * 22.5 m < h <= 300 m;
  * d2D <= 4 km;
  * UMi-AV LOS/NLOS pathloss from TR 36.777 Table B-2;
  * Case-9 LOS probability for equal heights from TR 38.901 Table 7.9.3-5.

It is a large-scale model only. It does not implement Annex-B fast fading.
"""
from __future__ import annotations

import numpy as np

C_MPS = 299_792_458.0


def _as_array(x: np.ndarray | float) -> np.ndarray:
    return np.asarray(x, dtype=float)


def fspl_db(distance_m: np.ndarray | float, carrier_ghz: float) -> np.ndarray:
    d = _as_array(distance_m)
    if np.any(d <= 0) or carrier_ghz <= 0:
        raise ValueError("distance and carrier frequency must be positive")
    carrier_hz = carrier_ghz * 1e9
    return 20.0 * np.log10(4.0 * np.pi * d * carrier_hz / C_MPS)


def umi_av_los_path_loss_db(
    d3d_m: np.ndarray | float,
    h_ut_m: float,
    carrier_ghz: float,
) -> np.ndarray:
    """TR 36.777 Table B-2 UMi-AV LOS, aerial-height branch.

    Applicability: 22.5 m < h_UT <= 300 m and d_2D <= 4 km.
    The expression is max(FSPL, aerial-specific LOS expression).
    """
    d = _as_array(d3d_m)
    if not (22.5 < h_ut_m <= 300.0):
        raise ValueError("UMi-AV aerial branch requires 22.5 < h_ut_m <= 300 m")
    if np.any(d <= 0):
        raise ValueError("d3d_m must be positive")
    pl_prime = fspl_db(d, carrier_ghz)
    aerial = (
        30.9
        + (22.25 - 0.5 * np.log10(h_ut_m)) * np.log10(d)
        + 20.0 * np.log10(carrier_ghz)
    )
    return np.maximum(pl_prime, aerial)


def umi_av_nlos_path_loss_db(
    d3d_m: np.ndarray | float,
    h_ut_m: float,
    carrier_ghz: float,
) -> np.ndarray:
    """TR 36.777 Table B-2 UMi-AV NLOS, aerial-height branch."""
    d = _as_array(d3d_m)
    los = umi_av_los_path_loss_db(d, h_ut_m, carrier_ghz)
    nlos_expr = (
        32.4
        + (43.2 - 7.6 * np.log10(h_ut_m)) * np.log10(d)
        + 20.0 * np.log10(carrier_ghz)
    )
    return np.maximum(los, nlos_expr)


def equal_height_case9_los_probability(d2d_m: np.ndarray | float, height_m: float) -> np.ndarray:
    """TR 38.901 V19.4.0 Table 7.9.3-5 for equal-height UMi-AV A2A links.

    For 22.5 < h <= 100 m the table points to UMa-AV Table B-1 in TR 36.777.
    For 100 < h <= 300 m the Case-9 table gives LOS probability 100%.

    This helper intentionally does not generalize unequal-height Case 9 because
    that requires careful first/second-aerial-UE role handling. Our initial
    thesis comparisons use equal-altitude swarms, so the restricted form avoids
    silently introducing an unsupported interpretation.
    """
    d = _as_array(d2d_m)
    if np.any(d < 0):
        raise ValueError("d2d_m must be non-negative")
    if not (22.5 < height_m <= 300.0):
        raise ValueError("implemented Case-9 branch requires 22.5 < height <= 300 m")
    if height_m > 100.0:
        return np.ones_like(d, dtype=float)

    d1 = max(460.0 * np.log10(height_m) - 700.0, 18.0)
    p1 = 4300.0 * np.log10(height_m) - 3800.0
    out = np.ones_like(d, dtype=float)
    mask = d > d1
    dm = d[mask]
    out[mask] = d1 / dm + np.exp(-dm / p1) * (1.0 - d1 / dm)
    return np.clip(out, 0.0, 1.0)


def equal_height_umi_av_shadow_sigma_db(height_m: float, los: bool) -> float:
    """TR 36.777 Table B-3 UMi-AV shadow-fading standard deviation."""
    if not (22.5 < height_m <= 300.0):
        raise ValueError("UMi-AV aerial branch requires 22.5 < height <= 300 m")
    if los:
        return float(max(5.0 * np.exp(-0.01 * height_m), 2.0))
    return 8.0

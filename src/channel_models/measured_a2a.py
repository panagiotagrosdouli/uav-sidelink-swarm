"""Measurement-derived A2A path-loss model from Erdemir et al., VTC 2023-Spring.

Primary peer-reviewed source:
U. Erdemir, B. Kaplan, I. Hokelek, A. Gorcin, H. A. Cirpan,
"Measurement-based Channel Characterization for A2A and A2G Wireless Drone
Communication Systems," IEEE VTC 2023-Spring,
doi:10.1109/VTC2023-Spring57618.2023.10199853.

The A2A fitted parameters reported in Table II are:
    eta = 2.166
    PL0 = 34.650 dB
with reference distance d0 = 1 m in the log-distance model defined in Eq. (3).
"""
from __future__ import annotations

import numpy as np

REFERENCE_DISTANCE_M = 1.0
PATH_LOSS_EXPONENT = 2.166
PL0_DB = 34.650


def path_loss_db(distance_m: np.ndarray | float) -> np.ndarray:
    """Return the measurement-derived A2A fitted path loss in dB.

    Distances below the 1 m reference distance are clipped to d0. The model is
    a fitted large-scale path-loss relation, not raw measured samples and not a
    complete small-scale fading/channel impulse response model.
    """
    d = np.asarray(distance_m, dtype=float)
    if np.any(d < 0):
        raise ValueError("distance_m must be non-negative")
    d = np.maximum(d, REFERENCE_DISTANCE_M)
    return PL0_DB + 10.0 * PATH_LOSS_EXPONENT * np.log10(d / REFERENCE_DISTANCE_M)

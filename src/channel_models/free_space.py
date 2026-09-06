"""Free-space path loss reference model (sanity-check only)."""
from __future__ import annotations

import numpy as np

C_MPS = 299_792_458.0


def path_loss_db(distance_m: np.ndarray | float, carrier_hz: float) -> np.ndarray:
    d = np.asarray(distance_m, dtype=float)
    if np.any(d <= 0):
        raise ValueError("distance_m must be > 0")
    if carrier_hz <= 0:
        raise ValueError("carrier_hz must be > 0")
    wavelength_m = C_MPS / carrier_hz
    return 20.0 * np.log10(4.0 * np.pi * d / wavelength_m)

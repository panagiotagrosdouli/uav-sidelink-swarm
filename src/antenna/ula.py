"""Simple uniform-linear-array (ULA) array-factor model.

This is a physical array-factor extension, not full NR beam management, channel
estimation, hybrid beamforming or MIMO. It assumes isotropic elements, uniform
weights, narrowband plane waves and configurable inter-element spacing.
"""
from __future__ import annotations

import numpy as np


def ula_power_gain_linear(
    observation_angle_deg: float | np.ndarray,
    steering_angle_deg: float,
    n_elements: int,
    spacing_wavelengths: float = 0.5,
) -> np.ndarray:
    """Return absolute ULA array power gain relative to one isotropic element.

    The coherent boresight power gain is N for the normalization used here.
    Angles are measured from broadside using the conventional sin(theta) phase.
    """
    if n_elements < 1:
        raise ValueError("n_elements must be >= 1")
    if spacing_wavelengths <= 0:
        raise ValueError("spacing_wavelengths must be positive")
    theta = np.deg2rad(np.asarray(observation_angle_deg, dtype=float))
    theta0 = np.deg2rad(float(steering_angle_deg))
    n = np.arange(n_elements, dtype=float)
    phase = 2.0 * np.pi * spacing_wavelengths * (
        np.sin(theta)[..., None] - np.sin(theta0)
    ) * n
    field = np.sum(np.exp(1j * phase), axis=-1) / np.sqrt(n_elements)
    return np.abs(field) ** 2


def ula_power_gain_db(
    observation_angle_deg: float | np.ndarray,
    steering_angle_deg: float,
    n_elements: int,
    spacing_wavelengths: float = 0.5,
    floor_db: float = -100.0,
) -> np.ndarray:
    gain = ula_power_gain_linear(
        observation_angle_deg,
        steering_angle_deg,
        n_elements,
        spacing_wavelengths,
    )
    floor_linear = 10.0 ** (floor_db / 10.0)
    return 10.0 * np.log10(np.maximum(gain, floor_linear))

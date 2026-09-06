"""Simple uniform-linear-array factor for optional directionality experiments.

This is a physical array-factor abstraction only. It omits element patterns,
mutual coupling, calibration, channel estimation and NR beam-management logic.
"""
from __future__ import annotations

import numpy as np


def ula_array_gain_linear(
    n_elements: int,
    steering_angle_deg: float,
    arrival_angle_deg: float | np.ndarray,
    element_spacing_wavelengths: float = 0.5,
) -> np.ndarray:
    """Return coherent ULA power gain relative to one isotropic element.

    Angle convention is broadside-referenced and enters through sin(theta).
    At the steering direction the ideal coherent gain equals ``n_elements``.
    """
    if n_elements < 1:
        raise ValueError("n_elements must be >= 1")
    if element_spacing_wavelengths <= 0.0:
        raise ValueError("element spacing must be positive")
    theta0 = np.deg2rad(float(steering_angle_deg))
    theta = np.deg2rad(np.asarray(arrival_angle_deg, dtype=float))
    phase_step = 2.0 * np.pi * element_spacing_wavelengths * (
        np.sin(theta) - np.sin(theta0)
    )
    indices = np.arange(n_elements, dtype=float)
    af = np.sum(np.exp(1j * phase_step[..., None] * indices), axis=-1)
    return np.abs(af) ** 2 / n_elements


def ula_array_gain_db(
    n_elements: int,
    steering_angle_deg: float,
    arrival_angle_deg: float | np.ndarray,
    element_spacing_wavelengths: float = 0.5,
    floor_db: float = -60.0,
) -> np.ndarray:
    gain = ula_array_gain_linear(
        n_elements,
        steering_angle_deg,
        arrival_angle_deg,
        element_spacing_wavelengths,
    )
    floor_linear = 10.0 ** (floor_db / 10.0)
    return 10.0 * np.log10(np.maximum(gain, floor_linear))

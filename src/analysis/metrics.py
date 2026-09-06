"""Cross-experiment metrics with explicit scientific scope."""
from __future__ import annotations

import numpy as np


def jains_fairness(values: np.ndarray | list[float]) -> float:
    """Jain's fairness index for non-negative per-link quantities."""
    x = np.asarray(values, dtype=float).ravel()
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("no finite values")
    if np.any(x < 0.0):
        raise ValueError("Jain fairness requires non-negative values")
    denominator = x.size * float(np.sum(x**2))
    if denominator == 0.0:
        return 1.0
    return float(np.sum(x) ** 2 / denominator)


def communication_energy_j(
    tx_power_dbm: float,
    transmission_time_ms: float,
    expected_attempts: float = 1.0,
) -> float:
    """Idealized radio-transmit energy only; not a UAV battery model."""
    if transmission_time_ms < 0.0 or expected_attempts < 0.0:
        raise ValueError("time and attempts must be non-negative")
    power_w = 10.0 ** ((float(tx_power_dbm) - 30.0) / 10.0)
    return power_w * transmission_time_ms * 1e-3 * expected_attempts


def energy_per_delivered_bit_j(
    tx_power_dbm: float,
    transmission_time_ms: float,
    expected_attempts: float,
    delivered_bits: float,
) -> float:
    """DERIVED communication-energy-per-delivered-bit abstraction."""
    if delivered_bits <= 0.0:
        return float("inf")
    return communication_energy_j(
        tx_power_dbm,
        transmission_time_ms,
        expected_attempts,
    ) / delivered_bits

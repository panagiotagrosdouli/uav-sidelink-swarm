"""Communication-energy abstractions for system-level comparison.

This is NOT a UAV battery/propulsion model. It accounts only for nominal RF
transmit energy and optionally retransmission attempts.
"""
from __future__ import annotations

import math


def dbm_to_watt(tx_power_dbm: float) -> float:
    return 10.0 ** ((float(tx_power_dbm) - 30.0) / 10.0)


def transmit_energy_joule(tx_power_dbm: float, transmission_time_s: float, attempts: float = 1.0) -> float:
    if transmission_time_s < 0 or attempts < 0:
        raise ValueError("time and attempts must be non-negative")
    return dbm_to_watt(tx_power_dbm) * transmission_time_s * attempts


def energy_per_delivered_bit_joule(
    tx_power_dbm: float,
    transmission_time_s: float,
    delivered_bits: float,
    attempts: float = 1.0,
) -> float:
    if delivered_bits <= 0:
        return math.inf
    return transmit_energy_joule(tx_power_dbm, transmission_time_s, attempts) / delivered_bits

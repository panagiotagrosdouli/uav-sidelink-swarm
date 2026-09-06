"""Simple antenna-gain abstraction for beamforming sensitivity studies.

This is not an array-factor/beam-management implementation. Gains are explicit
EXPERIMENTAL_SWEEP inputs unless a future experiment replaces them with values
from a cited antenna/array model.
"""
from __future__ import annotations


def apply_link_budget_gain_db(
    path_loss_db: float,
    tx_beam_gain_dbi: float = 0.0,
    rx_beam_gain_dbi: float = 0.0,
) -> float:
    """Return effective link loss after directional Tx/Rx gains."""
    return float(path_loss_db - tx_beam_gain_dbi - rx_beam_gain_dbi)


def effective_interference_power_dbm(
    interference_rx_power_dbm: float,
    suppression_db: float = 0.0,
) -> float:
    """Apply an explicit interference-suppression sensitivity parameter."""
    return float(interference_rx_power_dbm - suppression_db)

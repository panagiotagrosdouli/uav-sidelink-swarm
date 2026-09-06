"""Simple slotted traffic abstractions for offered-load/activity experiments.

Packet sizes/rates supplied to this module are scenario inputs. Unless a caller
provides a literature source, they remain EXPERIMENTAL_SWEEP values. This is not
a MAC queue/scheduler implementation and does not itself produce E2E latency.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TrafficProfile:
    name: str
    packet_size_bytes: int
    packet_rate_hz: float
    classification: str = "EXPERIMENTAL_SWEEP"

    def __post_init__(self) -> None:
        if self.packet_size_bytes <= 0 or self.packet_rate_hz < 0.0:
            raise ValueError("packet size must be positive and rate non-negative")

    @property
    def offered_load_mbps(self) -> float:
        return self.packet_size_bytes * 8.0 * self.packet_rate_hz / 1e6

    def slot_activity_probability(self, slot_duration_ms: float) -> float:
        """P(at least one Poisson arrival in a slot), used only as load abstraction."""
        if slot_duration_ms <= 0.0:
            raise ValueError("slot_duration_ms must be positive")
        lam = self.packet_rate_hz * slot_duration_ms * 1e-3
        return float(1.0 - np.exp(-lam))


def sample_slot_activity(
    n_links: int,
    probability: float,
    seed: int,
) -> np.ndarray:
    if n_links < 0 or not 0.0 <= probability <= 1.0:
        raise ValueError("invalid n_links/probability")
    rng = np.random.default_rng(seed)
    return rng.random(n_links) < probability

"""Slotted packet-queue abstraction for traffic-load sensitivity.

This is a system-level queue model, not NR MAC/RLC. Arrivals are Poisson and a
queued packet gets at most one transmission attempt per slot with a supplied
success probability.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class QueueResult:
    generated_packets: int
    delivered_packets: int
    remaining_packets: int
    delivery_ratio: float
    mean_latency_ms: float
    p95_latency_ms: float
    mean_queue_length: float
    utilization: float


def simulate_slotted_queue(
    arrival_rate_pps: float,
    slot_duration_ms: float,
    success_probability: float,
    n_slots: int,
    seed: int,
) -> QueueResult:
    if arrival_rate_pps < 0 or slot_duration_ms <= 0 or n_slots < 1:
        raise ValueError("invalid traffic configuration")
    if not 0.0 <= success_probability <= 1.0:
        raise ValueError("success_probability must be in [0,1]")
    rng = np.random.default_rng(seed)
    arrival_lambda = arrival_rate_pps * slot_duration_ms / 1000.0
    queue: deque[int] = deque()
    latencies: list[float] = []
    queue_lengths: list[int] = []
    generated = delivered = attempts = 0

    for slot in range(n_slots):
        arrivals = int(rng.poisson(arrival_lambda))
        generated += arrivals
        queue.extend([slot] * arrivals)
        if queue:
            attempts += 1
            if rng.random() < success_probability:
                arrival_slot = queue.popleft()
                delivered += 1
                latencies.append((slot - arrival_slot + 1) * slot_duration_ms)
        queue_lengths.append(len(queue))

    delivery_ratio = delivered / generated if generated else 1.0
    return QueueResult(
        generated_packets=generated,
        delivered_packets=delivered,
        remaining_packets=len(queue),
        delivery_ratio=float(delivery_ratio),
        mean_latency_ms=float(np.mean(latencies)) if latencies else float("nan"),
        p95_latency_ms=float(np.percentile(latencies, 95)) if latencies else float("nan"),
        mean_queue_length=float(np.mean(queue_lengths)),
        utilization=attempts / n_slots,
    )

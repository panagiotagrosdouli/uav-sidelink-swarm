"""Experimental sidelink resource-allocation abstractions.

These algorithms are system-level research abstractions, NOT normative or
bit-accurate implementations of NR Sidelink Mode 1/Mode 2. They are used to
study how resource reuse changes interference under controlled assumptions.

3GPP background should be cited from TS 38.214/38.213 for final thesis text,
but the algorithms below are deliberately labelled as this work.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AllocationResult:
    resources: np.ndarray
    algorithm: str


def random_allocation(n_links: int, n_resources: int, seed: int) -> AllocationResult:
    if n_links < 0 or n_resources < 1:
        raise ValueError("invalid link/resource count")
    rng = np.random.default_rng(seed)
    return AllocationResult(rng.integers(0, n_resources, size=n_links), "random")


def greedy_distance_aware_allocation(
    tx_positions: np.ndarray,
    rx_positions: np.ndarray,
    n_resources: int,
) -> AllocationResult:
    """Greedy reuse assignment minimizing a simple geometric interference cost.

    For each link, choose the resource with the lowest sum of inverse-squared
    distances from already-assigned transmitters to the candidate receiver and
    from the candidate transmitter to already-assigned receivers.

    This is an EXPERIMENTAL algorithm from this work, not a 3GPP procedure.
    """
    tx = np.asarray(tx_positions, dtype=float)
    rx = np.asarray(rx_positions, dtype=float)
    if tx.shape != rx.shape or tx.ndim != 2 or tx.shape[1] != 3:
        raise ValueError("tx_positions and rx_positions must have shape (N,3)")
    if n_resources < 1:
        raise ValueError("n_resources must be >= 1")

    n = len(tx)
    assigned = np.full(n, -1, dtype=int)
    for i in range(n):
        costs = np.zeros(n_resources, dtype=float)
        for r in range(n_resources):
            prior = np.where(assigned[:i] == r)[0]
            for j in prior:
                d_j_to_i_rx = max(float(np.linalg.norm(tx[j] - rx[i])), 1.0)
                d_i_to_j_rx = max(float(np.linalg.norm(tx[i] - rx[j])), 1.0)
                costs[r] += 1.0 / d_j_to_i_rx**2 + 1.0 / d_i_to_j_rx**2
        assigned[i] = int(np.argmin(costs))
    return AllocationResult(assigned, "greedy_distance_aware")

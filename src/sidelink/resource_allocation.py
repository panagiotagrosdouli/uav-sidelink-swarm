"""Experimental sidelink resource-allocation abstractions.

These algorithms are system-level research abstractions, NOT normative or
bit-accurate implementations of NR Sidelink Mode 1/Mode 2. They are used to
study how resource reuse changes interference under controlled assumptions.
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


def _validate_positions(tx_positions: np.ndarray, rx_positions: np.ndarray, n_resources: int) -> tuple[np.ndarray, np.ndarray]:
    tx = np.asarray(tx_positions, dtype=float)
    rx = np.asarray(rx_positions, dtype=float)
    if tx.shape != rx.shape or tx.ndim != 2 or tx.shape[1] != 3:
        raise ValueError("tx_positions and rx_positions must have shape (N,3)")
    if n_resources < 1:
        raise ValueError("n_resources must be >= 1")
    return tx, rx


def pair_conflict_weights(tx_positions: np.ndarray, rx_positions: np.ndarray) -> np.ndarray:
    """Symmetric geometric conflict matrix used by THIS_WORK allocators.

    Weight(i,j) = 1/d(Tx_i,Rx_j)^2 + 1/d(Tx_j,Rx_i)^2. This is a geometry-only
    interference proxy, not an NR sensing/RSRP measurement.
    """
    tx = np.asarray(tx_positions, dtype=float)
    rx = np.asarray(rx_positions, dtype=float)
    if tx.shape != rx.shape or tx.ndim != 2 or tx.shape[1] != 3:
        raise ValueError("tx_positions and rx_positions must have shape (N,3)")
    n = len(tx)
    w = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d_i_to_j = max(float(np.linalg.norm(tx[i] - rx[j])), 1.0)
            d_j_to_i = max(float(np.linalg.norm(tx[j] - rx[i])), 1.0)
            value = 1.0 / d_i_to_j**2 + 1.0 / d_j_to_i**2
            w[i, j] = value
            w[j, i] = value
    return w


def greedy_distance_aware_allocation(
    tx_positions: np.ndarray,
    rx_positions: np.ndarray,
    n_resources: int,
) -> AllocationResult:
    """Greedy reuse assignment minimizing a simple geometric interference cost."""
    tx, rx = _validate_positions(tx_positions, rx_positions, n_resources)
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


def weighted_conflict_graph_allocation(
    tx_positions: np.ndarray,
    rx_positions: np.ndarray,
    n_resources: int,
) -> AllocationResult:
    """Weighted graph-coloring-like reuse allocator from this work.

    Links are ordered by total geometric conflict weight. Each link is assigned
    the resource that minimizes weighted conflict with already assigned links.
    This requires no arbitrary conflict-distance threshold and is still only a
    THIS_WORK system-level algorithm, not 3GPP Mode 2.
    """
    tx, rx = _validate_positions(tx_positions, rx_positions, n_resources)
    weights = pair_conflict_weights(tx, rx)
    order = np.argsort(-weights.sum(axis=1), kind="stable")
    assigned = np.full(len(tx), -1, dtype=int)
    for i in order:
        costs = np.zeros(n_resources, dtype=float)
        for resource in range(n_resources):
            prior = np.where(assigned == resource)[0]
            costs[resource] = float(weights[i, prior].sum()) if len(prior) else 0.0
        assigned[i] = int(np.argmin(costs))
    return AllocationResult(assigned, "weighted_conflict_graph")

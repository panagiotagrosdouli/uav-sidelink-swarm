"""Deterministic synthetic swarm geometry and mobility generators.

All outputs in this module are SYNTHETIC. They are controlled research
abstractions and must not be presented as measured UAV trajectories.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

GeometryName = Literal["uniform", "grid", "circle", "clustered", "leader_follower"]


def _z(n: int, altitude_m: float) -> np.ndarray:
    return np.full((n, 1), float(altitude_m))


def generate_positions(
    n_uavs: int,
    area_xy_m: float,
    altitude_m: float,
    rng: np.random.Generator,
    geometry: GeometryName = "uniform",
) -> np.ndarray:
    """Generate a controlled equal-altitude synthetic swarm geometry."""
    if n_uavs < 1:
        raise ValueError("n_uavs must be >= 1")
    if area_xy_m <= 0 or altitude_m < 0:
        raise ValueError("invalid area or altitude")

    if geometry == "uniform":
        xy = rng.uniform(0.0, area_xy_m, size=(n_uavs, 2))
    elif geometry == "grid":
        side = int(np.ceil(np.sqrt(n_uavs)))
        coordinates = np.linspace(0.1 * area_xy_m, 0.9 * area_xy_m, side)
        xx, yy = np.meshgrid(coordinates, coordinates)
        xy = np.column_stack([xx.ravel(), yy.ravel()])[:n_uavs]
    elif geometry == "circle":
        center = np.array([area_xy_m / 2.0, area_xy_m / 2.0])
        radius = 0.35 * area_xy_m
        angles = np.linspace(0.0, 2.0 * np.pi, n_uavs, endpoint=False)
        xy = center + radius * np.column_stack([np.cos(angles), np.sin(angles)])
    elif geometry == "clustered":
        # Four mission-target-like clusters; spread is an explicit synthetic rule.
        centers = np.array([
            [0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]
        ]) * area_xy_m
        cluster_id = rng.integers(0, len(centers), size=n_uavs)
        xy = centers[cluster_id] + rng.normal(0.0, 0.06 * area_xy_m, size=(n_uavs, 2))
        xy = np.clip(xy, 0.0, area_xy_m)
    elif geometry == "leader_follower":
        leader = np.array([area_xy_m / 2.0, area_xy_m / 2.0])
        if n_uavs == 1:
            xy = leader.reshape(1, 2)
        else:
            angles = np.linspace(0.0, 2.0 * np.pi, n_uavs - 1, endpoint=False)
            radius = 0.15 * area_xy_m
            followers = leader + radius * np.column_stack([np.cos(angles), np.sin(angles)])
            xy = np.vstack([leader, followers])
    else:
        raise ValueError(f"unknown geometry: {geometry}")
    return np.hstack([xy, _z(n_uavs, altitude_m)])


@dataclass(frozen=True)
class MobilityTrace:
    time_s: np.ndarray
    positions_m: np.ndarray  # shape [time, uav, xyz]
    classification: str = "SYNTHETIC"


def constant_velocity_trace(
    initial_positions_m: np.ndarray,
    velocities_mps: np.ndarray,
    duration_s: float,
    sample_period_s: float,
) -> MobilityTrace:
    initial = np.asarray(initial_positions_m, dtype=float)
    velocity = np.asarray(velocities_mps, dtype=float)
    if initial.ndim != 2 or initial.shape[1] != 3 or velocity.shape != initial.shape:
        raise ValueError("positions and velocities must have shape [n_uavs, 3]")
    if duration_s < 0 or sample_period_s <= 0:
        raise ValueError("invalid duration/sample period")
    time_s = np.arange(0.0, duration_s + 0.5 * sample_period_s, sample_period_s)
    positions = initial[None, :, :] + time_s[:, None, None] * velocity[None, :, :]
    return MobilityTrace(time_s=time_s, positions_m=positions)


def formation_translation_trace(
    initial_positions_m: np.ndarray,
    velocity_mps: tuple[float, float, float],
    duration_s: float,
    sample_period_s: float,
) -> MobilityTrace:
    initial = np.asarray(initial_positions_m, dtype=float)
    velocity = np.tile(np.asarray(velocity_mps, dtype=float), (initial.shape[0], 1))
    return constant_velocity_trace(initial, velocity, duration_s, sample_period_s)

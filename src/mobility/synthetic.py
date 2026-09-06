"""Deterministic synthetic swarm geometry and mobility generators.

All outputs are SYNTHETIC. They are controlled research abstractions and must
not be presented as measured UAV trajectories.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

GeometryName = Literal["uniform", "grid", "circle", "clustered", "leader_follower"]


def _z(n: int, altitude_m: float) -> np.ndarray:
    return np.full((n, 1), float(altitude_m))


def generate_positions(n_uavs: int, area_xy_m: float, altitude_m: float, rng: np.random.Generator, geometry: GeometryName = "uniform") -> np.ndarray:
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
        centers = np.array([[0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]]) * area_xy_m
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
    positions_m: np.ndarray
    classification: str = "SYNTHETIC_MOBILITY"


def constant_velocity_trace(initial_positions_m: np.ndarray, velocities_mps: np.ndarray, duration_s: float, sample_period_s: float) -> MobilityTrace:
    initial = np.asarray(initial_positions_m, dtype=float)
    velocity = np.asarray(velocities_mps, dtype=float)
    if initial.ndim != 2 or initial.shape[1] != 3 or velocity.shape != initial.shape:
        raise ValueError("positions and velocities must have shape [n_uavs, 3]")
    if duration_s < 0 or sample_period_s <= 0:
        raise ValueError("invalid duration/sample period")
    time_s = np.arange(0.0, duration_s + 0.5 * sample_period_s, sample_period_s)
    positions = initial[None, :, :] + time_s[:, None, None] * velocity[None, :, :]
    return MobilityTrace(time_s=time_s, positions_m=positions)


def formation_translation_trace(initial_positions_m: np.ndarray, velocity_mps: tuple[float, float, float], duration_s: float, sample_period_s: float) -> MobilityTrace:
    initial = np.asarray(initial_positions_m, dtype=float)
    velocity = np.tile(np.asarray(velocity_mps, dtype=float), (initial.shape[0], 1))
    return constant_velocity_trace(initial, velocity, duration_s, sample_period_s)


def random_waypoint_trace(
    initial_positions_m: np.ndarray,
    area_xy_m: float,
    speed_mps: float,
    duration_s: float,
    sample_period_s: float,
    seed: int,
) -> MobilityTrace:
    """Piecewise-linear random-waypoint mobility at constant speed, equal altitude."""
    if speed_mps <= 0 or area_xy_m <= 0:
        raise ValueError("speed and area must be positive")
    initial = np.asarray(initial_positions_m, dtype=float)
    if initial.ndim != 2 or initial.shape[1] != 3:
        raise ValueError("initial_positions_m must have shape [n_uavs,3]")
    rng = np.random.default_rng(seed)
    times = np.arange(0.0, duration_s + 0.5 * sample_period_s, sample_period_s)
    n = len(initial)
    positions = np.empty((len(times), n, 3), dtype=float)
    current = initial.copy()
    target = np.column_stack([rng.uniform(0.0, area_xy_m, size=(n, 2)), initial[:, 2]])
    for k, _ in enumerate(times):
        positions[k] = current
        delta = target - current
        delta[:, 2] = 0.0
        distance = np.linalg.norm(delta[:, :2], axis=1)
        reached = distance <= speed_mps * sample_period_s
        if np.any(reached):
            current[reached] = target[reached]
            target[reached, :2] = rng.uniform(0.0, area_xy_m, size=(int(np.sum(reached)), 2))
            delta = target - current
            delta[:, 2] = 0.0
            distance = np.linalg.norm(delta[:, :2], axis=1)
        step = np.minimum(distance, speed_mps * sample_period_s)
        direction = np.zeros_like(delta)
        nonzero = distance > 0
        direction[nonzero, :2] = delta[nonzero, :2] / distance[nonzero, None]
        current = current + direction * step[:, None]
        current[:, :2] = np.clip(current[:, :2], 0.0, area_xy_m)
        current[:, 2] = initial[:, 2]
    return MobilityTrace(time_s=times, positions_m=positions)


def leader_follower_trace(
    initial_positions_m: np.ndarray,
    leader_velocity_mps: tuple[float, float, float],
    duration_s: float,
    sample_period_s: float,
    response: float = 0.25,
) -> MobilityTrace:
    """Leader translation with followers relaxing toward their initial offsets."""
    if not 0.0 < response <= 1.0:
        raise ValueError("response must be in (0,1]")
    initial = np.asarray(initial_positions_m, dtype=float)
    if initial.ndim != 2 or initial.shape[1] != 3:
        raise ValueError("initial_positions_m must have shape [n_uavs,3]")
    times = np.arange(0.0, duration_s + 0.5 * sample_period_s, sample_period_s)
    positions = np.empty((len(times), len(initial), 3), dtype=float)
    offsets = initial - initial[0]
    current = initial.copy()
    velocity = np.asarray(leader_velocity_mps, dtype=float)
    for k, _ in enumerate(times):
        positions[k] = current
        next_leader = current[0] + velocity * sample_period_s
        desired = next_leader + offsets
        current[0] = next_leader
        current[1:] += response * (desired[1:] - current[1:])
    return MobilityTrace(time_s=times, positions_m=positions)

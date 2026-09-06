"""Deterministic SYNTHETIC mobility generators for controlled experiments."""
from __future__ import annotations

import numpy as np


def constant_velocity_tracks(
    initial_positions_m: np.ndarray,
    velocities_mps: np.ndarray,
    times_s: np.ndarray,
) -> np.ndarray:
    """Return shape (T,N,3) tracks under constant Cartesian velocity."""
    p0 = np.asarray(initial_positions_m, dtype=float)
    v = np.asarray(velocities_mps, dtype=float)
    t = np.asarray(times_s, dtype=float)
    if p0.ndim != 2 or p0.shape[1] != 3 or v.shape != p0.shape:
        raise ValueError("positions and velocities must have shape (N,3)")
    if t.ndim != 1 or np.any(np.diff(t) < 0.0):
        raise ValueError("times_s must be a non-decreasing 1D array")
    return p0[None, :, :] + t[:, None, None] * v[None, :, :]


def formation_translation_tracks(
    formation_positions_m: np.ndarray,
    leader_velocity_mps: np.ndarray,
    times_s: np.ndarray,
) -> np.ndarray:
    """Translate an entire formation rigidly; relative geometry is preserved."""
    p0 = np.asarray(formation_positions_m, dtype=float)
    velocity = np.asarray(leader_velocity_mps, dtype=float)
    if velocity.shape != (3,):
        raise ValueError("leader_velocity_mps must have shape (3,)")
    velocities = np.repeat(velocity[None, :], len(p0), axis=0)
    return constant_velocity_tracks(p0, velocities, times_s)


def random_waypoint_tracks(
    initial_positions_m: np.ndarray,
    times_s: np.ndarray,
    area_xy_m: float,
    speed_mps: float,
    seed: int,
) -> np.ndarray:
    """Discrete-time, equal-altitude random-waypoint mobility.

    Waypoints are sampled uniformly in the square study area. UAV altitude is
    held at its initial value. This is a controlled synthetic mobility model,
    not a claim about real swarm flight dynamics.
    """
    p0 = np.asarray(initial_positions_m, dtype=float)
    t = np.asarray(times_s, dtype=float)
    if p0.ndim != 2 or p0.shape[1] != 3:
        raise ValueError("initial_positions_m must have shape (N,3)")
    if t.ndim != 1 or len(t) < 1 or np.any(np.diff(t) < 0.0):
        raise ValueError("times_s must be non-decreasing")
    if area_xy_m <= 0.0 or speed_mps <= 0.0:
        raise ValueError("area and speed must be positive")

    rng = np.random.default_rng(seed)
    n = len(p0)
    current = p0.copy()
    waypoint = np.column_stack(
        [
            rng.uniform(0.0, area_xy_m, n),
            rng.uniform(0.0, area_xy_m, n),
            p0[:, 2],
        ]
    )
    tracks = np.empty((len(t), n, 3), dtype=float)
    tracks[0] = current
    for k in range(1, len(t)):
        dt = float(t[k] - t[k - 1])
        remaining_step = speed_mps * dt
        # Repeatedly consume a step when a waypoint is reached inside this dt.
        for i in range(n):
            step = remaining_step
            while step > 0.0:
                delta = waypoint[i] - current[i]
                delta[2] = 0.0
                distance = float(np.linalg.norm(delta))
                if distance <= 1e-12:
                    waypoint[i, :2] = rng.uniform(0.0, area_xy_m, 2)
                    continue
                if distance > step:
                    current[i] += delta / distance * step
                    step = 0.0
                else:
                    current[i] = waypoint[i]
                    step -= distance
                    waypoint[i, :2] = rng.uniform(0.0, area_xy_m, 2)
            current[i, 2] = p0[i, 2]
        tracks[k] = current
    return tracks


def relative_pair_distance_m(tracks: np.ndarray, first: int, second: int) -> np.ndarray:
    arr = np.asarray(tracks, dtype=float)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError("tracks must have shape (T,N,3)")
    return np.linalg.norm(arr[:, first, :] - arr[:, second, :], axis=1)

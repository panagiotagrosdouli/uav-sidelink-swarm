"""Controlled synthetic UAV swarm geometries for sensitivity experiments.

Every position produced here is SYNTHETIC.  The generators exist to separate
geometry effects from propagation/resource effects; they are not flight data.
"""
from __future__ import annotations

from typing import Literal

import numpy as np

GeometryName = Literal["uniform", "grid", "circle", "clustered", "leader_follower"]


def _with_altitude(xy: np.ndarray, altitude_m: float) -> np.ndarray:
    z = np.full((len(xy), 1), float(altitude_m))
    return np.hstack([np.asarray(xy, dtype=float), z])


def uniform_positions(n_uavs: int, area_xy_m: float, altitude_m: float, rng: np.random.Generator) -> np.ndarray:
    return _with_altitude(rng.uniform(0.0, area_xy_m, size=(n_uavs, 2)), altitude_m)


def grid_positions(n_uavs: int, area_xy_m: float, altitude_m: float) -> np.ndarray:
    side = int(np.ceil(np.sqrt(n_uavs)))
    # Cell-centred placement avoids nodes exactly on the artificial area boundary.
    coords = (np.arange(side, dtype=float) + 0.5) * area_xy_m / side
    xx, yy = np.meshgrid(coords, coords)
    xy = np.column_stack([xx.ravel(), yy.ravel()])[:n_uavs]
    return _with_altitude(xy, altitude_m)


def circle_positions(n_uavs: int, area_xy_m: float, altitude_m: float) -> np.ndarray:
    centre = area_xy_m / 2.0
    radius = 0.35 * area_xy_m
    angles = np.linspace(0.0, 2.0 * np.pi, n_uavs, endpoint=False)
    xy = np.column_stack([centre + radius * np.cos(angles), centre + radius * np.sin(angles)])
    return _with_altitude(xy, altitude_m)


def clustered_positions(
    n_uavs: int,
    area_xy_m: float,
    altitude_m: float,
    rng: np.random.Generator,
    n_clusters: int = 3,
    cluster_std_fraction: float = 0.08,
) -> np.ndarray:
    if n_clusters < 1:
        raise ValueError("n_clusters must be >= 1")
    if cluster_std_fraction <= 0.0:
        raise ValueError("cluster_std_fraction must be positive")
    centres = rng.uniform(0.2 * area_xy_m, 0.8 * area_xy_m, size=(n_clusters, 2))
    labels = np.arange(n_uavs) % n_clusters
    rng.shuffle(labels)
    xy = centres[labels] + rng.normal(
        0.0,
        cluster_std_fraction * area_xy_m,
        size=(n_uavs, 2),
    )
    xy = np.clip(xy, 0.0, area_xy_m)
    return _with_altitude(xy, altitude_m)


def leader_follower_positions(
    n_uavs: int,
    area_xy_m: float,
    altitude_m: float,
    spacing_m: float | None = None,
) -> np.ndarray:
    """Deterministic V-like leader/follower formation centred in the study area."""
    spacing = float(spacing_m if spacing_m is not None else max(10.0, area_xy_m / 20.0))
    centre = np.array([area_xy_m / 2.0, 0.7 * area_xy_m])
    xy = [centre]
    for i in range(1, n_uavs):
        rank = (i + 1) // 2
        side = -1.0 if i % 2 else 1.0
        point = centre + np.array([side * rank * spacing, -rank * spacing])
        xy.append(np.clip(point, 0.0, area_xy_m))
    return _with_altitude(np.asarray(xy), altitude_m)


def generate_positions(
    geometry: GeometryName,
    n_uavs: int,
    area_xy_m: float,
    altitude_m: float,
    seed: int,
) -> np.ndarray:
    if n_uavs < 1 or area_xy_m <= 0.0:
        raise ValueError("n_uavs and area_xy_m must be positive")
    rng = np.random.default_rng(seed)
    if geometry == "uniform":
        return uniform_positions(n_uavs, area_xy_m, altitude_m, rng)
    if geometry == "grid":
        return grid_positions(n_uavs, area_xy_m, altitude_m)
    if geometry == "circle":
        return circle_positions(n_uavs, area_xy_m, altitude_m)
    if geometry == "clustered":
        return clustered_positions(n_uavs, area_xy_m, altitude_m, rng)
    if geometry == "leader_follower":
        return leader_follower_positions(n_uavs, area_xy_m, altitude_m)
    raise ValueError(f"unknown geometry {geometry}")

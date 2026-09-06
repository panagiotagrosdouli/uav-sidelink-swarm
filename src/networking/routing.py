"""Graph-based multi-hop routing helpers for UAV swarms.

Links are supplied by the caller with explicit quality metrics. These helpers do
not pretend to be an NR routing protocol; they provide reproducible graph-level
experiments for minimum-hop and quality-aware route selection.
"""
from __future__ import annotations

import math

import networkx as nx
import pandas as pd


def build_graph(
    links: pd.DataFrame,
    minimum_sinr_db: float,
    *,
    minimum_success_probability: float | None = None,
) -> nx.Graph:
    required = {"tx", "rx", "sinr_db"}
    if not required.issubset(links.columns):
        raise ValueError(f"links must contain {sorted(required)}")
    if minimum_success_probability is not None and not 0.0 <= minimum_success_probability <= 1.0:
        raise ValueError("minimum_success_probability must lie in [0,1]")
    graph = nx.Graph()
    for row in links.itertuples(index=False):
        sinr = float(row.sinr_db)
        if sinr < minimum_sinr_db:
            continue
        success = (
            float(getattr(row, "success_probability"))
            if hasattr(row, "success_probability")
            else None
        )
        if minimum_success_probability is not None:
            if success is None or success < minimum_success_probability:
                continue
        # Lower cost is better; this is a THIS_WORK routing heuristic.
        quality_cost = 1.0 / max(sinr - minimum_sinr_db + 1.0, 1e-6)
        attrs: dict[str, float] = {"sinr_db": sinr, "quality_cost": quality_cost}
        if success is not None:
            attrs["success_probability"] = success
            attrs["reliability_cost"] = -math.log(max(success, 1e-12))
        if hasattr(row, "latency_ms"):
            attrs["latency_ms"] = float(getattr(row, "latency_ms"))
        graph.add_edge(int(row.tx), int(row.rx), **attrs)
    return graph


def minimum_hop_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target)


def quality_aware_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target, weight="quality_cost")


def reliability_aware_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    """Max-product-success route implemented as min sum(-log(success))."""
    for _, _, data in graph.edges(data=True):
        if "reliability_cost" not in data:
            raise ValueError("graph edges need success_probability for reliability-aware routing")
    return nx.shortest_path(graph, source=source, target=target, weight="reliability_cost")


def path_bottleneck_sinr_db(graph: nx.Graph, path: list[int]) -> float:
    if len(path) < 2:
        return float("inf")
    return min(float(graph[u][v]["sinr_db"]) for u, v in zip(path[:-1], path[1:]))


def path_success_probability(graph: nx.Graph, path: list[int]) -> float:
    """Independent-hop product approximation; caller must report this assumption."""
    probability = 1.0
    for u, v in zip(path[:-1], path[1:]):
        if "success_probability" not in graph[u][v]:
            raise ValueError("graph edge lacks success_probability")
        probability *= float(graph[u][v]["success_probability"])
    return probability


def path_latency_ms(graph: nx.Graph, path: list[int]) -> float:
    """Sum modeled per-hop latency; this is not automatically full E2E latency."""
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        if "latency_ms" not in graph[u][v]:
            raise ValueError("graph edge lacks latency_ms")
        total += float(graph[u][v]["latency_ms"])
    return total


def path_metrics(graph: nx.Graph, path: list[int]) -> dict[str, float | int]:
    out: dict[str, float | int] = {
        "hop_count": max(0, len(path) - 1),
        "bottleneck_sinr_db": path_bottleneck_sinr_db(graph, path),
    }
    if len(path) >= 2 and all("success_probability" in graph[u][v] for u, v in zip(path[:-1], path[1:])):
        out["route_success_probability"] = path_success_probability(graph, path)
    if len(path) >= 2 and all("latency_ms" in graph[u][v] for u, v in zip(path[:-1], path[1:])):
        out["route_latency_ms"] = path_latency_ms(graph, path)
    return out

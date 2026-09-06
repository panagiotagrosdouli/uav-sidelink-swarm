"""Graph-based multi-hop routing helpers for UAV swarms.

Links are supplied by the caller with explicit quality metrics. These helpers do
not pretend to be an NR routing protocol; they provide reproducible graph-level
experiments for minimum-hop and quality-aware route selection.
"""
from __future__ import annotations

import math

import networkx as nx
import pandas as pd


def build_graph(links: pd.DataFrame, minimum_sinr_db: float) -> nx.Graph:
    required = {"tx", "rx", "sinr_db"}
    if not required.issubset(links.columns):
        raise ValueError(f"links must contain {sorted(required)}")
    graph = nx.Graph()
    for row in links.itertuples(index=False):
        if float(row.sinr_db) < minimum_sinr_db:
            continue
        sinr = float(row.sinr_db)
        quality_cost = 1.0 / max(sinr - minimum_sinr_db + 1.0, 1e-6)
        attrs = {"sinr_db": sinr, "quality_cost": quality_cost}
        if hasattr(row, "success_probability"):
            p = float(row.success_probability)
            if not 0.0 <= p <= 1.0:
                raise ValueError("success_probability must lie in [0,1]")
            attrs["success_probability"] = p
            attrs["reliability_cost"] = -math.log(max(p, 1e-12))
        if hasattr(row, "latency_ms"):
            latency = float(row.latency_ms)
            if latency < 0:
                raise ValueError("latency_ms must be non-negative")
            attrs["latency_ms"] = latency
        graph.add_edge(int(row.tx), int(row.rx), **attrs)
    return graph


def minimum_hop_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target)


def quality_aware_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target, weight="quality_cost")


def reliability_aware_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    """Max-product success route using additive -log(p) edge cost."""
    for _, _, attrs in graph.edges(data=True):
        if "reliability_cost" not in attrs:
            raise ValueError("graph edges must include success_probability")
    return nx.shortest_path(graph, source=source, target=target, weight="reliability_cost")


def path_bottleneck_sinr_db(graph: nx.Graph, path: list[int]) -> float:
    if len(path) < 2:
        return float("inf")
    return min(float(graph[u][v]["sinr_db"]) for u, v in zip(path[:-1], path[1:]))


def path_success_probability(graph: nx.Graph, path: list[int]) -> float:
    """Product of per-hop success probabilities under explicit independence."""
    probability = 1.0
    for u, v in zip(path[:-1], path[1:]):
        if "success_probability" not in graph[u][v]:
            raise ValueError("graph edges must include success_probability")
        probability *= float(graph[u][v]["success_probability"])
    return probability


def path_latency_ms(graph: nx.Graph, path: list[int]) -> float:
    """Sum explicitly modeled per-hop latency; not a full network-stack delay."""
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        if "latency_ms" not in graph[u][v]:
            raise ValueError("graph edges must include latency_ms")
        total += float(graph[u][v]["latency_ms"])
    return total

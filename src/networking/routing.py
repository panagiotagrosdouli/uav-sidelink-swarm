"""Graph-based multi-hop routing helpers for UAV swarms.

Links are supplied by the caller with explicit quality metrics. These helpers do
not pretend to be an NR routing protocol; they provide reproducible graph-level
experiments for minimum-hop and quality-aware route selection.
"""
from __future__ import annotations

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
        # Lower cost is better; +1 keeps the denominator positive near threshold.
        quality_cost = 1.0 / max(sinr - minimum_sinr_db + 1.0, 1e-6)
        graph.add_edge(int(row.tx), int(row.rx), sinr_db=sinr, quality_cost=quality_cost)
    return graph


def minimum_hop_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target)


def quality_aware_path(graph: nx.Graph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target, weight="quality_cost")


def path_bottleneck_sinr_db(graph: nx.Graph, path: list[int]) -> float:
    if len(path) < 2:
        return float("inf")
    return min(float(graph[u][v]["sinr_db"]) for u, v in zip(path[:-1], path[1:]))

import math

import pandas as pd

from src.networking.routing import (
    build_graph,
    minimum_hop_path,
    path_bottleneck_sinr_db,
    path_latency_ms,
    path_success_probability,
    quality_aware_path,
    reliability_aware_path,
)


def test_routing_helpers():
    links = pd.DataFrame(
        [
            {"tx": 0, "rx": 1, "sinr_db": 10.0},
            {"tx": 1, "rx": 2, "sinr_db": 8.0},
            {"tx": 0, "rx": 2, "sinr_db": 4.0},
        ]
    )
    graph = build_graph(links, minimum_sinr_db=5.0)
    assert minimum_hop_path(graph, 0, 2) == [0, 1, 2]
    assert quality_aware_path(graph, 0, 2) == [0, 1, 2]
    assert path_bottleneck_sinr_db(graph, [0, 1, 2]) == 8.0


def test_route_reliability_and_latency_are_composed_explicitly():
    links = pd.DataFrame(
        [
            {
                "tx": 0,
                "rx": 1,
                "sinr_db": 10.0,
                "success_probability": 0.9,
                "latency_ms": 1.0,
            },
            {
                "tx": 1,
                "rx": 2,
                "sinr_db": 9.0,
                "success_probability": 0.8,
                "latency_ms": 1.5,
            },
            {
                "tx": 0,
                "rx": 2,
                "sinr_db": 7.0,
                "success_probability": 0.6,
                "latency_ms": 0.5,
            },
        ]
    )
    graph = build_graph(links, minimum_sinr_db=0.0)
    reliable = reliability_aware_path(graph, 0, 2)
    assert reliable == [0, 1, 2]
    assert math.isclose(path_success_probability(graph, reliable), 0.72)
    assert math.isclose(path_latency_ms(graph, reliable), 2.5)

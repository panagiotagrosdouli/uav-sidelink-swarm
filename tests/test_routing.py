import pandas as pd

from src.networking.routing import build_graph, minimum_hop_path, path_bottleneck_sinr_db, quality_aware_path


def test_routing_helpers():
    links = pd.DataFrame([
        {"tx": 0, "rx": 1, "sinr_db": 10.0},
        {"tx": 1, "rx": 2, "sinr_db": 8.0},
        {"tx": 0, "rx": 2, "sinr_db": 4.0},
    ])
    graph = build_graph(links, minimum_sinr_db=5.0)
    assert minimum_hop_path(graph, 0, 2) == [0, 1, 2]
    assert quality_aware_path(graph, 0, 2) == [0, 1, 2]
    assert path_bottleneck_sinr_db(graph, [0, 1, 2]) == 8.0

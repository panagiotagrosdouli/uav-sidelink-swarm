import numpy as np

from src.traffic import simulate_slotted_queue


def test_zero_arrival_queue_is_empty():
    r = simulate_slotted_queue(0.0, 0.5, 1.0, 100, seed=1)
    assert r.generated_packets == 0
    assert r.delivered_packets == 0
    assert r.remaining_packets == 0
    assert r.delivery_ratio == 1.0


def test_perfect_service_low_load_delivers_all_or_nearly_all():
    r = simulate_slotted_queue(10.0, 0.5, 1.0, 10000, seed=2)
    assert r.delivery_ratio > 0.99
    assert r.mean_latency_ms >= 0.5


def test_zero_success_accumulates_queue():
    r = simulate_slotted_queue(500.0, 0.5, 0.0, 1000, seed=3)
    assert r.delivered_packets == 0
    assert r.remaining_packets == r.generated_packets
    assert np.isnan(r.mean_latency_ms)

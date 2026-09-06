import numpy as np

from src.antenna.array_factor import ula_array_gain_db
from src.mobility.synthetic import constant_velocity_tracks, formation_translation_tracks, random_waypoint_tracks
from src.traffic import TrafficProfile, sample_slot_activity


def test_constant_velocity_tracks_reference():
    p0 = np.array([[0.0, 0.0, 100.0]])
    v = np.array([[2.0, 0.0, 0.0]])
    tracks = constant_velocity_tracks(p0, v, np.array([0.0, 1.0, 2.0]))
    assert np.allclose(tracks[:, 0, 0], [0.0, 2.0, 4.0])


def test_formation_translation_preserves_relative_distance():
    p0 = np.array([[0.0, 0.0, 100.0], [3.0, 4.0, 100.0]])
    tracks = formation_translation_tracks(p0, np.array([1.0, 2.0, 0.0]), np.array([0.0, 5.0]))
    distance = np.linalg.norm(tracks[:, 0] - tracks[:, 1], axis=1)
    assert np.allclose(distance, 5.0)


def test_random_waypoint_stays_in_area_and_is_reproducible():
    p0 = np.array([[10.0, 10.0, 100.0], [20.0, 20.0, 100.0]])
    times = np.arange(0.0, 10.0, 1.0)
    a = random_waypoint_tracks(p0, times, 100.0, 5.0, seed=7)
    b = random_waypoint_tracks(p0, times, 100.0, 5.0, seed=7)
    assert np.array_equal(a, b)
    assert np.all((a[:, :, :2] >= 0.0) & (a[:, :, :2] <= 100.0))
    assert np.allclose(a[:, :, 2], 100.0)


def test_poisson_activity_profile_is_explicit_and_reproducible():
    profile = TrafficProfile("test", packet_size_bytes=200, packet_rate_hz=100.0)
    assert np.isclose(profile.offered_load_mbps, 0.16)
    p = profile.slot_activity_probability(0.5)
    assert 0.0 < p < 1.0
    assert np.array_equal(sample_slot_activity(20, p, 3), sample_slot_activity(20, p, 3))


def test_ula_peak_gain_equals_element_count_in_db():
    for n in (1, 2, 4, 8):
        peak = float(ula_array_gain_db(n, 0.0, 0.0))
        assert np.isclose(peak, 10.0 * np.log10(n), atol=1e-10)
    off_axis = float(ula_array_gain_db(8, 0.0, 30.0))
    assert off_axis <= 10.0 * np.log10(8)

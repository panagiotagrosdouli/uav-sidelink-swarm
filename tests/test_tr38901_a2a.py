import numpy as np

from src.channel_models.tr38901_a2a import (
    equal_height_case9_los_probability,
    equal_height_umi_av_shadow_sigma_db,
    fspl_db,
    umi_av_los_path_loss_db,
    umi_av_nlos_path_loss_db,
)


def test_fspl_positive_and_increases_with_distance():
    values = fspl_db(np.array([10.0, 100.0, 1000.0]), 3.5)
    assert np.all(np.diff(values) > 0)


def test_umi_av_los_not_below_fspl():
    d = np.array([10.0, 100.0, 1000.0])
    los = umi_av_los_path_loss_db(d, 100.0, 3.5)
    assert np.all(los >= fspl_db(d, 3.5) - 1e-12)


def test_umi_av_nlos_not_below_los():
    d = np.array([10.0, 100.0, 1000.0])
    los = umi_av_los_path_loss_db(d, 100.0, 3.5)
    nlos = umi_av_nlos_path_loss_db(d, 100.0, 3.5)
    assert np.all(nlos >= los - 1e-12)


def test_case9_probability_at_100m_is_bounded():
    p = equal_height_case9_los_probability(np.array([10.0, 100.0, 1000.0]), 100.0)
    assert np.all((0 <= p) & (p <= 1))


def test_case9_probability_above_100m_is_one():
    p = equal_height_case9_los_probability(np.array([10.0, 1000.0, 4000.0]), 120.0)
    assert np.allclose(p, 1.0)


def test_umi_av_shadow_fading_sigma():
    assert equal_height_umi_av_shadow_sigma_db(100.0, los=True) >= 2.0
    assert equal_height_umi_av_shadow_sigma_db(100.0, los=False) == 8.0

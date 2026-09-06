import numpy as np
import pytest

from src.channel_models.measured_a2a import PL0_DB, PATH_LOSS_EXPONENT, path_loss_db


def test_reference_distance_returns_pl0() -> None:
    assert float(path_loss_db(1.0)) == pytest.approx(PL0_DB, abs=1e-12)


def test_ten_meters_matches_manual_equation() -> None:
    expected = PL0_DB + 10.0 * PATH_LOSS_EXPONENT
    assert float(path_loss_db(10.0)) == pytest.approx(expected, rel=1e-12)


def test_vector_input_is_monotonic() -> None:
    distances = np.array([1.0, 10.0, 100.0, 1000.0])
    losses = path_loss_db(distances)
    assert np.all(np.diff(losses) > 0)


def test_negative_distance_rejected() -> None:
    with pytest.raises(ValueError):
        path_loss_db(-1.0)

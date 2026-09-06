import numpy as np

from src.scaling import fit_linear, fit_logarithmic, fit_power_law


def test_linear_fit_exact():
    x = np.array([1, 2, 3, 4], dtype=float)
    y = 2.0 * x + 3.0
    result = fit_linear(x, y)
    assert result.r2 > 0.999999


def test_log_fit_exact():
    x = np.array([1, 2, 4, 8], dtype=float)
    y = 3.0 * np.log(x) + 2.0
    result = fit_logarithmic(x, y)
    assert result.r2 > 0.999999


def test_power_fit_exact():
    x = np.array([1, 2, 4, 8], dtype=float)
    y = 5.0 * x**1.5
    result = fit_power_law(x, y)
    assert result.r2 > 0.999999
    assert np.isclose(result.coefficients[1], 1.5)

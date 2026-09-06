import numpy as np

from src.statistical_tests import paired_comparison


def test_paired_comparison_detects_exact_shift():
    a = np.array([1, 2, 3, 4, 5], dtype=float)
    b = a + 2.0
    result = paired_comparison(a, b)
    assert result.n_pairs == 5
    assert np.isclose(result.mean_difference, 2.0)
    assert np.isclose(result.median_difference, 2.0)
    assert result.ci95_low <= 2.0 <= result.ci95_high

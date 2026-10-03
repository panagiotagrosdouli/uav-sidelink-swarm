import numpy as np

from src.statistical_tests import paired_comparison


def test_paired_comparison_detects_exact_shift():
    a = np.array([1, 2, 3, 4, 5], dtype=float)
    b = a + 2.0
    result = paired_comparison(a, b, bootstrap_resamples=1000)
    assert result.n_pairs == 5
    assert np.isclose(result.mean_difference, 2.0)
    assert np.isclose(result.median_difference, 2.0)
    assert result.ci95_low <= 2.0 <= result.ci95_high
    assert result.bootstrap_ci95_low <= 2.0 <= result.bootstrap_ci95_high
    assert np.isclose(result.bootstrap_ci95_low, 2.0)
    assert np.isclose(result.bootstrap_ci95_high, 2.0)


def test_paired_comparison_bootstrap_is_deterministic():
    a = np.array([0.1, 0.2, 0.4, 0.7, 1.1], dtype=float)
    b = np.array([0.2, 0.5, 0.6, 0.9, 1.5], dtype=float)
    r1 = paired_comparison(a, b, bootstrap_resamples=1000, bootstrap_seed=42)
    r2 = paired_comparison(a, b, bootstrap_resamples=1000, bootstrap_seed=42)
    assert np.isclose(r1.bootstrap_ci95_low, r2.bootstrap_ci95_low)
    assert np.isclose(r1.bootstrap_ci95_high, r2.bootstrap_ci95_high)
    assert 0.0 <= r1.wilcoxon_pvalue <= 1.0

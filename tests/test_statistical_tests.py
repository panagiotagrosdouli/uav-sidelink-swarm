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


def test_paired_bootstrap_interval_is_deterministic_and_contains_mean():
    import numpy as np
    from src.statistical_tests import paired_comparison

    baseline = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    treatment = baseline + np.array([0.05, 0.04, 0.06, 0.05, 0.07])
    a = paired_comparison(baseline, treatment)
    b = paired_comparison(baseline, treatment)
    assert a.bootstrap_ci95_low == b.bootstrap_ci95_low
    assert a.bootstrap_ci95_high == b.bootstrap_ci95_high
    assert a.bootstrap_ci95_low <= a.mean_difference <= a.bootstrap_ci95_high

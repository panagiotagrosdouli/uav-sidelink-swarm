"""Paired statistical comparisons for matched-seed algorithm experiments."""
from __future__ import annotations

import numpy as np
from scipy import stats


def paired_wilcoxon(first, second) -> dict[str, float | int | str]:
    """Paired Wilcoxon signed-rank test plus matched effect summaries.

    Practical magnitude is reported alongside the p-value. This helper should
    only be used when the two arrays represent matched experimental seeds.
    """
    a = np.asarray(first, dtype=float).ravel()
    b = np.asarray(second, dtype=float).ravel()
    if a.shape != b.shape:
        raise ValueError("paired samples must have identical shape")
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    if len(a) < 2:
        raise ValueError("at least two finite pairs are required")
    delta = b - a
    if np.allclose(delta, 0.0):
        statistic, pvalue = 0.0, 1.0
    else:
        result = stats.wilcoxon(delta, zero_method="wilcox", alternative="two-sided")
        statistic, pvalue = float(result.statistic), float(result.pvalue)
    std_delta = float(np.std(delta, ddof=1)) if len(delta) > 1 else 0.0
    paired_cohens_d = float(np.mean(delta) / std_delta) if std_delta > 0.0 else 0.0
    return {
        "n_pairs": int(len(delta)),
        "mean_first": float(np.mean(a)),
        "mean_second": float(np.mean(b)),
        "mean_difference_second_minus_first": float(np.mean(delta)),
        "median_difference_second_minus_first": float(np.median(delta)),
        "paired_cohens_d": paired_cohens_d,
        "wilcoxon_statistic": statistic,
        "p_value": pvalue,
        "test": "paired_wilcoxon_two_sided",
    }

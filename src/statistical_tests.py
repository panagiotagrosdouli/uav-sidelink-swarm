"""Small paired-comparison helpers for matched-seed experiments."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class PairedComparison:
    n_pairs: int
    mean_difference: float
    median_difference: float
    relative_mean_change_percent: float
    ci95_low: float
    ci95_high: float
    cohen_dz: float
    paired_t_pvalue: float


def paired_comparison(baseline, treatment) -> PairedComparison:
    a = np.asarray(baseline, dtype=float)
    b = np.asarray(treatment, dtype=float)
    if a.shape != b.shape or a.ndim != 1 or a.size < 2:
        raise ValueError("baseline and treatment must be matched 1-D arrays with >=2 pairs")
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    if a.size < 2:
        raise ValueError("not enough finite matched pairs")
    d = b - a
    mean_d = float(np.mean(d))
    sd = float(np.std(d, ddof=1))
    se = sd / np.sqrt(len(d))
    delta = 1.96 * se
    baseline_mean = float(np.mean(a))
    relative = 100.0 * mean_d / baseline_mean if baseline_mean != 0 else float("nan")
    dz = mean_d / sd if sd > 0 else (float("inf") if mean_d != 0 else 0.0)
    test = stats.ttest_rel(b, a)
    return PairedComparison(
        n_pairs=int(len(d)),
        mean_difference=mean_d,
        median_difference=float(np.median(d)),
        relative_mean_change_percent=float(relative),
        ci95_low=mean_d - delta,
        ci95_high=mean_d + delta,
        cohen_dz=float(dz),
        paired_t_pvalue=float(test.pvalue),
    )

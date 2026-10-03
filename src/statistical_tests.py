"""Paired-comparison helpers for matched-seed research experiments."""
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
    bootstrap_ci95_low: float
    bootstrap_ci95_high: float
    cohen_dz: float
    paired_t_pvalue: float
    wilcoxon_pvalue: float


def _bootstrap_mean_difference_ci(
    differences: np.ndarray,
    *,
    confidence: float = 0.95,
    n_resamples: int = 10000,
    seed: int = 2027,
) -> tuple[float, float]:
    if differences.ndim != 1 or differences.size < 2:
        raise ValueError("differences must be a 1-D array with at least two values")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")
    if n_resamples < 100:
        raise ValueError("n_resamples must be at least 100")

    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(differences), size=(n_resamples, len(differences)))
    bootstrap_means = np.mean(differences[indices], axis=1)
    alpha = 1.0 - confidence
    low, high = np.quantile(bootstrap_means, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(low), float(high)


def paired_comparison(
    baseline,
    treatment,
    *,
    bootstrap_resamples: int = 10000,
    bootstrap_seed: int = 2027,
) -> PairedComparison:
    """Compare matched observations with parametric and non-parametric checks.

    The primary estimand is the matched mean difference treatment - baseline.
    A Student-t 95% CI, deterministic percentile-bootstrap 95% CI, Cohen dz,
    paired t-test and Wilcoxon signed-rank p-value are reported. The inferential
    statistics describe repeated simulation seeds, not independent field trials.
    """
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
    critical = float(stats.t.ppf(0.975, df=len(d) - 1))
    delta = critical * se

    baseline_mean = float(np.mean(a))
    relative = 100.0 * mean_d / baseline_mean if baseline_mean != 0 else float("nan")
    dz = mean_d / sd if sd > 0 else (float("inf") if mean_d != 0 else 0.0)
    ttest = stats.ttest_rel(b, a)

    bootstrap_low, bootstrap_high = _bootstrap_mean_difference_ci(
        d,
        n_resamples=bootstrap_resamples,
        seed=bootstrap_seed,
    )

    if np.allclose(d, 0.0):
        wilcoxon_pvalue = 1.0
    else:
        try:
            wilcoxon_pvalue = float(
                stats.wilcoxon(
                    d,
                    alternative="two-sided",
                    zero_method="wilcox",
                    correction=False,
                    method="auto",
                ).pvalue
            )
        except ValueError:
            wilcoxon_pvalue = float("nan")

    return PairedComparison(
        n_pairs=int(len(d)),
        mean_difference=mean_d,
        median_difference=float(np.median(d)),
        relative_mean_change_percent=float(relative),
        ci95_low=mean_d - delta,
        ci95_high=mean_d + delta,
        bootstrap_ci95_low=bootstrap_low,
        bootstrap_ci95_high=bootstrap_high,
        cohen_dz=float(dz),
        paired_t_pvalue=float(ttest.pvalue),
        wilcoxon_pvalue=wilcoxon_pvalue,
    )

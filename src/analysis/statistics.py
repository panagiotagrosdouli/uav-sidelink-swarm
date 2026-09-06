"""Deterministic statistical summaries used by final experimental campaigns."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy import stats


def _clean(values: np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float).ravel()
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError("no finite observations")
    return arr


def summarize(values: np.ndarray | list[float], confidence: float = 0.95) -> dict[str, float | int]:
    """Return n/mean/median/std/p05/p95 and Student-t CI for the mean."""
    arr = _clean(values)
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0,1)")
    n = int(arr.size)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    if n > 1:
        sem = std / np.sqrt(n)
        critical = float(stats.t.ppf(0.5 + confidence / 2.0, df=n - 1))
        margin = critical * sem
    else:
        margin = 0.0
    return {
        "n": n,
        "mean": mean,
        "median": float(np.median(arr)),
        "std": std,
        "p05": float(np.percentile(arr, 5.0)),
        "p95": float(np.percentile(arr, 95.0)),
        "ci95_low": mean - margin,
        "ci95_high": mean + margin,
    }


def bootstrap_interval(
    values: np.ndarray | list[float],
    statistic: Callable[[np.ndarray], float] = np.median,
    confidence: float = 0.95,
    n_resamples: int = 2000,
    seed: int = 0,
) -> tuple[float, float]:
    """Deterministic percentile bootstrap interval for non-Gaussian metrics."""
    arr = _clean(values)
    if n_resamples < 100:
        raise ValueError("n_resamples must be >= 100")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0,1)")
    rng = np.random.default_rng(seed)
    samples = rng.choice(arr, size=(n_resamples, arr.size), replace=True)
    estimates = np.asarray([statistic(row) for row in samples], dtype=float)
    alpha = (1.0 - confidence) / 2.0
    return (
        float(np.quantile(estimates, alpha)),
        float(np.quantile(estimates, 1.0 - alpha)),
    )


def paired_difference(
    first: np.ndarray | list[float],
    second: np.ndarray | list[float],
    confidence: float = 0.95,
) -> dict[str, float | int]:
    """Summarize paired ``second-first`` differences for matched-seed studies."""
    a = np.asarray(first, dtype=float).ravel()
    b = np.asarray(second, dtype=float).ravel()
    if a.shape != b.shape:
        raise ValueError("paired arrays must have identical shape")
    mask = np.isfinite(a) & np.isfinite(b)
    if not np.any(mask):
        raise ValueError("no finite paired observations")
    result = summarize(b[mask] - a[mask], confidence=confidence)
    result["mean_absolute_first"] = float(np.mean(a[mask]))
    result["mean_absolute_second"] = float(np.mean(b[mask]))
    baseline = float(np.mean(a[mask]))
    result["mean_percent_change"] = (
        float((np.mean(b[mask]) - baseline) / abs(baseline) * 100.0)
        if baseline != 0.0
        else float("nan")
    )
    return result

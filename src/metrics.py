"""Common system-level metrics for thesis experiments."""
from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np


def jain_fairness(values: Iterable[float]) -> float:
    """Return Jain's fairness index in [0,1].

    Zero-only vectors return 0 because no useful allocation is delivered.
    """
    x = np.asarray(list(values), dtype=float)
    if x.size == 0:
        raise ValueError("values must not be empty")
    if np.any(x < 0) or not np.all(np.isfinite(x)):
        raise ValueError("fairness inputs must be finite and non-negative")
    denominator = x.size * float(np.sum(x * x))
    if denominator == 0.0:
        return 0.0
    return float(np.sum(x) ** 2 / denominator)


def mean_ci95(values: Iterable[float]) -> tuple[float, float, float]:
    """Mean and normal-approximation 95% CI for independent replications."""
    x = np.asarray(list(values), dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("no finite values")
    mean = float(np.mean(x))
    if x.size == 1:
        return mean, mean, mean
    se = float(np.std(x, ddof=1) / math.sqrt(x.size))
    delta = 1.96 * se
    return mean, mean - delta, mean + delta


def summarize(values: Iterable[float]) -> dict[str, float | int]:
    x = np.asarray(list(values), dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("no finite values")
    mean, lo, hi = mean_ci95(x)
    return {
        "n": int(x.size),
        "mean": mean,
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "p05": float(np.percentile(x, 5)),
        "p95": float(np.percentile(x, 95)),
        "ci95_low": lo,
        "ci95_high": hi,
    }

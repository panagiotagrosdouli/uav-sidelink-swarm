"""Small transparent scaling-law diagnostics for experiment interpretation.

Fits are descriptive only. The caller must not claim a physical scaling law
solely because one candidate has a high R² over a limited N range.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FitResult:
    model: str
    coefficients: tuple[float, ...]
    r2: float


def _r2(y: np.ndarray, prediction: np.ndarray) -> float:
    ss_res = float(np.sum((y - prediction) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 if ss_tot == 0.0 and ss_res == 0.0 else (1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"))


def fit_linear(x, y) -> FitResult:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    coef = np.polyfit(x, y, 1)
    pred = np.polyval(coef, x)
    return FitResult("linear", tuple(float(v) for v in coef), _r2(y, pred))


def fit_logarithmic(x, y) -> FitResult:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if np.any(x <= 0):
        raise ValueError("logarithmic fit requires x > 0")
    lx = np.log(x)
    coef = np.polyfit(lx, y, 1)
    pred = np.polyval(coef, lx)
    return FitResult("logarithmic", tuple(float(v) for v in coef), _r2(y, pred))


def fit_power_law(x, y) -> FitResult:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if np.any(x <= 0) or np.any(y <= 0):
        raise ValueError("power-law fit requires x,y > 0")
    coef = np.polyfit(np.log(x), np.log(y), 1)
    a = float(np.exp(coef[1]))
    b = float(coef[0])
    pred = a * x**b
    return FitResult("power_law", (a, b), _r2(y, pred))

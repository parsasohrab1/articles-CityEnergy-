from __future__ import annotations

import numpy as np


def seasonal_naive(load: np.ndarray, idx: np.ndarray, lag: int = 168) -> np.ndarray:
    """Forecast = load one week earlier."""
    return load[idx - lag]


def features(temp, hour, dow):
    """Design matrix: hour x weekend one-hot, cooling / heating degrees."""
    h = np.eye(24)[hour]
    we = (dow >= 5).astype(float)[:, None]
    cool = np.maximum(temp - 22, 0)[:, None]
    heat = np.maximum(15 - temp, 0)[:, None]
    return np.hstack([h, h * we, cool, heat, cool * h[:, [14]]])


def fit_ridge(X, y, lam: float = 1.0):
    A = X.T @ X + lam * np.eye(X.shape[1])
    return np.linalg.solve(A, X.T @ y)


def predict(w, X):
    return X @ w


def conformal_halfwidth(y, yhat, alpha: float = 0.1) -> float:
    """Split-conformal half-width on relative absolute residuals."""
    r = np.abs(y - yhat) / np.maximum(np.abs(yhat), 1e-9)
    n = len(r)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return float(np.sort(r)[min(k, n) - 1])


def coverage(y, yhat, half) -> float:
    return float(np.mean(np.abs(y - yhat) <= half * np.abs(yhat)))


def mape(y, yhat) -> float:
    return float(np.mean(np.abs(y - yhat) / y))

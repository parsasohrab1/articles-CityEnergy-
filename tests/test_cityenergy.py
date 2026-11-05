import numpy as np

from cityenergy.models import (
    conformal_halfwidth,
    coverage,
    features,
    fit_ridge,
    mape,
    predict,
    seasonal_naive,
)
from cityenergy.synth import make_series


def test_series_shape_and_positive():
    load, temp, hour, dow = make_series(0, weeks=4)
    assert len(load) == 24 * 7 * 4 == len(temp) == len(hour) == len(dow)
    assert (load > 0).all()


def test_heat_shift_raises_late_temperature_only():
    _, t0, _, _ = make_series(1, 0.0, weeks=8)
    _, t1, _, _ = make_series(1, 5.0, weeks=8)
    n = len(t0)
    assert np.allclose(t0[: int(0.75 * n)], t1[: int(0.75 * n)])
    assert np.allclose(t1[int(0.75 * n):] - t0[int(0.75 * n):], 5.0)


def test_cool_gain_changes_load_only_after_shift_start():
    a = make_series(3, 0.0, weeks=8, cool_gain=1.0, shift_start=500)[0]
    b = make_series(3, 0.0, weeks=8, cool_gain=1.5, shift_start=500)[0]
    assert np.allclose(a[:500], b[:500])
    assert (b[500:] >= a[500:] - 1e-9).all()


def test_seasonal_naive_is_lag():
    x = np.arange(400.0)
    assert (seasonal_naive(x, np.array([200, 300])) == np.array([32.0, 132.0])).all()


def test_ridge_beats_naive_on_synthetic():
    load, temp, hour, dow = make_series(2, weeks=40)
    X = features(temp, hour, dow)
    tr = np.arange(168, 24 * 7 * 28)
    te = np.arange(24 * 7 * 28, len(load))
    w = fit_ridge(X[tr], load[tr])
    assert mape(load[te], predict(w, X[te])) < mape(load[te], seasonal_naive(load, te))


def test_conformal_coverage_exchangeable():
    rng = np.random.default_rng(0)
    yhat = np.full(4000, 100.0)
    y = yhat * (1 + rng.normal(0, 0.05, 4000))
    h = conformal_halfwidth(y[:2000], yhat[:2000], 0.1)
    assert abs(coverage(y[2000:], yhat[2000:], h) - 0.9) < 0.03

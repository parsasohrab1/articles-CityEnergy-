"""Synthetic study (104 weeks): train weeks 1-52, calibrate 53-68, test 69-104.

Scenarios start at week 70 (inside the test window): none, heatwave +4 C, cooling-response drift x1.4.
"""

import json
from pathlib import Path

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

W = 24 * 7
START = 70 * W


def run(seed: int, heat: float, gain: float):
    load, temp, hour, dow = make_series(seed, heat, 104, gain, START)
    X = features(temp, hour, dow)
    tr = np.arange(W, 52 * W)
    cal = np.arange(52 * W, 68 * W)
    te = np.arange(69 * W, len(load))
    pre = te[te < START]
    post = te[te >= START]
    w = fit_ridge(X[tr], load[tr])
    out = {}
    for name, f in (("ridge", lambda i: predict(w, X[i])), ("seasonal_naive", lambda i: seasonal_naive(load, i))):
        h = conformal_halfwidth(load[cal], f(cal), 0.1)
        out[name] = {
            "mape_pre": mape(load[pre], f(pre)),
            "mape_post": mape(load[post], f(post)),
            "coverage_pre": coverage(load[pre], f(pre), h),
            "coverage_post": coverage(load[post], f(post), h),
            "rel_halfwidth": h,
        }
    return out


def main():
    res = {"note": "synthetic hourly series, 104 weeks, 10 seeds; interval target coverage 0.90"}
    for label, heat, gain in (("no_shift", 0.0, 1.0), ("heatwave_+4C", 4.0, 1.0), ("cooling_drift_x1.4", 0.0, 1.4)):
        runs = [run(s, heat, gain) for s in range(20, 30)]
        res[label] = {"n_seeds": len(runs)}
        for m in runs[0]:
            res[label][m] = {k: float(np.mean([r[m][k] for r in runs])) for k in runs[0][m]}
    Path(__file__).with_name("results.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        if isinstance(v, dict):
            print(k, {m: {a: round(b, 3) for a, b in d.items()} for m, d in v.items() if isinstance(d, dict)})


if __name__ == "__main__":
    main()

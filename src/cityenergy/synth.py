"""Synthetic hourly load generator (labelled synthetic; not real metered data)."""

from __future__ import annotations

import numpy as np

HOURS = 24 * 7 * 52


def make_series(seed: int, heat_shift: float = 0.0, weeks: int = 104, cool_gain: float = 1.0,
                shift_start: int | None = None):
    """Return (load, temp, hour, dow) arrays.

    load = base * daily profile * weekday factor + cooling*max(T-22,0) + heating*max(15-T,0) + noise.
    ``heat_shift`` adds degrees C to temperature and ``cool_gain`` scales the cooling response
    (structural drift) from ``shift_start`` (default: 75 % of the series) onward.
    """
    rng = np.random.default_rng(seed)
    n = 24 * 7 * weeks
    t = np.arange(n)
    hour = t % 24
    dow = (t // 24) % 7
    day = t / 24.0
    temp = 14 + 9 * np.sin(2 * np.pi * (day - 110) / 365) + 4 * np.sin(2 * np.pi * (hour - 9) / 24)
    temp = temp + rng.normal(0, 1.5, n)
    temp = temp + np.convolve(rng.normal(0, 1.2, n), np.ones(48) / 48 * 6, mode="same")
    s0 = int(0.75 * n) if shift_start is None else shift_start
    temp[s0:] += heat_shift
    gain = np.where(t >= s0, cool_gain, 1.0)
    profile = 1.0 + 0.35 * np.sin(2 * np.pi * (hour - 14) / 24) + 0.15 * np.sin(4 * np.pi * (hour - 8) / 24)
    wk = np.where(dow >= 5, 0.82, 1.0)
    load = 500 * profile * wk + 18 * gain * np.maximum(temp - 22, 0) + 9 * np.maximum(15 - temp, 0)
    load = load * (1 + rng.normal(0, 0.04, n))
    return load, temp, hour, dow

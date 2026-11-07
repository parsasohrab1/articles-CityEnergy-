"""Building-wise split and split-conformal electricity intervals.

The interval is inductive split-conformal regression (Vovk, Gammerman and
Shafer, 2005; Lei, G'Sell, Rinaldo, Tibshirani and Wasserman, JASA 2018).
The next-year forecast is a locally weighted absolute residual. The weight is
that building's mean absolute residual on the previous year. The shared-width
helpers remain for the transferred-profile comparison.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict

import numpy as np
import pandas as pd

ALPHA = 0.10
FORECAST_START = pd.Timestamp("2017-01-01")
MAX_BUILDINGS = 40
# 95 percent, compared in integers: count / n_rows >= 19/20.
COMPLETENESS_NUM = 19
COMPLETENESS_DEN = 20
# Integer form of the SHA-256 bucket cuts at 0.60 and 0.80 of 2**32.
TRAIN_BELOW = 2_576_980_377
CALIBRATION_BELOW = 3_435_973_836
SELECTION_RULE = (
    "Keep electricity meters whose non-null hour count is at least 95 percent "
    "of the file (integer test 20*count >= 19*n_rows) and whose floor area is "
    "positive. Choose the site with the most such meters; break ties by site_id "
    "alphabetical order. If that site has more than 40 meters, keep 40 spread "
    "evenly across the sorted building_id list. Assign each kept building with "
    "the first 4 bytes of SHA-256: raw <= 2576980377 train, raw <= 3435973836 "
    "calibration, otherwise test."
)


def fold_name(building_id: str) -> str:
    raw = int.from_bytes(hashlib.sha256(building_id.encode("utf-8")).digest()[:4], "big")
    if raw <= TRAIN_BELOW:
        return "train"
    if raw <= CALIBRATION_BELOW:
        return "calibration"
    return "test"


def spread_take(building_ids: list[str], limit: int) -> list[str]:
    ordered = sorted(building_ids)
    if len(ordered) <= limit:
        return ordered
    if limit < 1:
        raise ValueError("limit must be positive")
    picked: list[str] = []
    seen: set[str] = set()
    last = len(ordered) - 1
    for step in range(limit):
        index = round(step * last / (limit - 1))
        item = ordered[index]
        if item not in seen:
            picked.append(item)
            seen.add(item)
    if len(picked) < limit:
        for item in ordered:
            if item not in seen:
                picked.append(item)
                seen.add(item)
            if len(picked) == limit:
                break
    return sorted(picked)


def assign_folds(building_ids: list[str]) -> dict[str, list[str]]:
    folds: dict[str, list[str]] = {"train": [], "calibration": [], "test": []}
    for building_id in sorted(building_ids):
        folds[fold_name(building_id)].append(building_id)
    empty = [name for name, ids in folds.items() if not ids]
    if empty:
        raise RuntimeError(f"building split left an empty fold: {empty}")
    return folds


def select_buildings(meters: pd.DataFrame, metadata: pd.DataFrame) -> dict[str, object]:
    if "timestamp" not in meters.columns:
        raise ValueError("meters need a timestamp column")
    n_rows = len(meters)
    if n_rows == 0:
        raise ValueError("meter table is empty")
    meta = metadata.set_index("building_id")
    qualifying: list[str] = []
    for building_id in meters.columns:
        if building_id == "timestamp" or building_id not in meta.index:
            continue
        count = int(meters[building_id].notna().sum())
        area = meta.loc[building_id, "sqm"]
        if pd.isna(area) or float(area) <= 0:
            continue
        if count * COMPLETENESS_DEN >= COMPLETENESS_NUM * n_rows:
            qualifying.append(str(building_id))
    if not qualifying:
        raise RuntimeError("no electricity meter met the 95 percent completeness rule")
    by_site: dict[str, list[str]] = defaultdict(list)
    for building_id in qualifying:
        by_site[str(meta.loc[building_id, "site_id"])].append(building_id)
    site_id = sorted(by_site, key=lambda site: (-len(by_site[site]), site))[0]
    chosen = spread_take(by_site[site_id], MAX_BUILDINGS)
    usage: dict[str, int] = defaultdict(int)
    for building_id in chosen:
        usage[str(meta.loc[building_id, "primaryspaceusage"])] += 1
    return {
        "site_id": site_id,
        "building_ids": chosen,
        "n_qualifying_total": len(qualifying),
        "n_qualifying_on_site": len(by_site[site_id]),
        "primaryspaceusage_counts": dict(sorted(usage.items())),
    }


def conformal_quantile(scores: list[float], alpha: float = ALPHA) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    if not scores:
        raise ValueError("no calibration scores")
    ordered = sorted(scores)
    n = len(ordered)
    rank = math.ceil((n + 1) * (1.0 - alpha))
    if rank > n:
        raise ValueError("calibration set is too small for a finite interval at this alpha")
    return float(ordered[rank - 1])


def hour_of_week_keys(timestamps: pd.Series) -> np.ndarray:
    stamps = pd.DatetimeIndex(timestamps)
    return (stamps.dayofweek.to_numpy(dtype=np.int64) * 24) + stamps.hour.to_numpy(dtype=np.int64)


def fit_hour_of_week(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
) -> np.ndarray:
    sums = np.zeros(168, dtype=np.float64)
    counts = np.zeros(168, dtype=np.int64)
    for building_id in buildings:
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        np.add.at(sums, hour_keys[valid], values[valid])
        np.add.at(counts, hour_keys[valid], 1)
    total = int(counts.sum())
    if total == 0:
        raise RuntimeError("training buildings have no electricity readings")
    fallback = float(sums.sum() / total)
    means = np.empty(168, dtype=np.float64)
    for slot in range(168):
        means[slot] = float(sums[slot] / counts[slot]) if counts[slot] else fallback
    return means


def absolute_residuals(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    means: np.ndarray,
) -> list[float]:
    scores: list[float] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        residual = np.abs(values[valid] - means[hour_keys[valid]])
        scores.extend(float(item) for item in residual)
    return scores


def evaluate_interval(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    means: np.ndarray,
    quantile: float,
) -> dict[str, object]:
    n_hours = 0
    n_covered = 0
    n_negative = 0
    abs_error = 0.0
    load = 0.0
    per_building: list[dict[str, object]] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        observed = values[valid]
        predicted = means[hour_keys[valid]]
        low = predicted - quantile
        high = predicted + quantile
        covered = int(np.count_nonzero((observed >= low) & (observed <= high)))
        count = int(observed.size)
        n_hours += count
        n_covered += covered
        n_negative += int(np.count_nonzero(observed < 0))
        abs_error += float(np.abs(observed - predicted).sum())
        load += float(observed.sum())
        per_building.append({"building_id": building_id, "n_hours": count, "n_covered": covered})
    if n_hours == 0:
        raise RuntimeError("test buildings have no electricity readings")
    rates = [row["n_covered"] / row["n_hours"] for row in per_building]
    return {
        "n_hours": n_hours,
        "n_covered": n_covered,
        "n_negative": n_negative,
        "abs_error_sum": abs_error,
        "load_sum": load,
        "per_building": per_building,
        "per_building_coverage_min": float(min(rates)),
        "per_building_coverage_median": _median(rates),
        "per_building_coverage_max": float(max(rates)),
    }


def fit_area_profiles(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    area_m2: dict[str, float],
    usage: dict[str, str],
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Hour-of-week mean of kWh per square metre, by primary space use."""
    sums: dict[str, np.ndarray] = defaultdict(lambda: np.zeros(168, dtype=np.float64))
    counts: dict[str, np.ndarray] = defaultdict(lambda: np.zeros(168, dtype=np.int64))
    overall_sum = np.zeros(168, dtype=np.float64)
    overall_count = np.zeros(168, dtype=np.int64)
    for building_id in buildings:
        area = float(area_m2[building_id])
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        intensity = values[valid] / area
        keys = hour_keys[valid]
        label = usage[building_id]
        np.add.at(sums[label], keys, intensity)
        np.add.at(counts[label], keys, 1)
        np.add.at(overall_sum, keys, intensity)
        np.add.at(overall_count, keys, 1)
    total = int(overall_count.sum())
    if total == 0:
        raise RuntimeError("training buildings have no electricity readings")
    fallback = float(overall_sum.sum() / total)
    overall = np.array(
        [
            float(overall_sum[slot] / overall_count[slot]) if overall_count[slot] else fallback
            for slot in range(168)
        ]
    )
    profiles = {
        label: np.array(
            [
                (
                    float(sums[label][slot] / counts[label][slot])
                    if counts[label][slot]
                    else overall[slot]
                )
                for slot in range(168)
            ]
        )
        for label in sums
    }
    return profiles, overall


def predict_from_area(
    hour_keys: np.ndarray,
    building_id: str,
    profiles: dict[str, np.ndarray],
    overall: np.ndarray,
    area_m2: dict[str, float],
    usage: dict[str, str],
) -> np.ndarray:
    profile = profiles.get(usage[building_id], overall)
    return profile[hour_keys] * float(area_m2[building_id])


def area_residual_scores(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    profiles: dict[str, np.ndarray],
    overall: np.ndarray,
    area_m2: dict[str, float],
    usage: dict[str, str],
) -> list[float]:
    scores: list[float] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        predicted = predict_from_area(hour_keys, building_id, profiles, overall, area_m2, usage)
        area = float(area_m2[building_id])
        residual = np.abs(values[valid] - predicted[valid]) / area
        scores.extend(float(item) for item in residual)
    return scores


def evaluate_area_interval(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    profiles: dict[str, np.ndarray],
    overall: np.ndarray,
    area_m2: dict[str, float],
    usage: dict[str, str],
    intensity_quantile: float,
) -> dict[str, object]:
    n_hours = 0
    n_covered = 0
    n_negative = 0
    abs_error = 0.0
    load = 0.0
    width_sum = 0.0
    per_building: list[dict[str, object]] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        valid = ~np.isnan(values)
        observed = values[valid]
        point = predict_from_area(hour_keys, building_id, profiles, overall, area_m2, usage)
        predicted = point[valid]
        half = intensity_quantile * float(area_m2[building_id])
        inside = (observed >= predicted - half) & (observed <= predicted + half)
        covered = int(np.count_nonzero(inside))
        count = int(observed.size)
        n_hours += count
        n_covered += covered
        n_negative += int(np.count_nonzero(observed < 0))
        abs_error += float(np.abs(observed - predicted).sum())
        load += float(observed.sum())
        width_sum += (2.0 * half) * count
        per_building.append({"building_id": building_id, "n_hours": count, "n_covered": covered})
    if n_hours == 0:
        raise RuntimeError("test buildings have no electricity readings")
    rates = [row["n_covered"] / row["n_hours"] for row in per_building]
    return {
        "n_hours": n_hours,
        "n_covered": n_covered,
        "n_negative": n_negative,
        "abs_error_sum": abs_error,
        "load_sum": load,
        "width_sum": width_sum,
        "per_building": per_building,
        "per_building_coverage_min": float(min(rates)),
        "per_building_coverage_median": _median(rates),
        "per_building_coverage_max": float(max(rates)),
    }


def forecast_masks(timestamps: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Hours before 2017 are the previous year. Later hours are the test year."""
    stamps = pd.DatetimeIndex(pd.to_datetime(timestamps))
    if stamps.tz is not None:
        raise RuntimeError("timestamps must be timezone-naive")
    past = np.asarray(stamps < FORECAST_START, dtype=bool)
    if not past.any() or bool(past.all()):
        raise RuntimeError("forecast start does not split the timestamps")
    return past, ~past


def _ordered_sum(values: np.ndarray) -> float:
    total = np.zeros(1, dtype=np.float64)
    np.add.at(total, np.zeros(values.size, dtype=np.int64), values)
    return float(total[0])


def previous_year_forecast(
    values: np.ndarray,
    hour_keys: np.ndarray,
    past: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Hour-of-week mean fit on previous-year hours, and that fit's mean absolute residual."""
    if values.shape != hour_keys.shape or values.shape != past.shape:
        raise ValueError("values, hour keys, and the past mask must share a shape")
    valid_past = past & ~np.isnan(values)
    if not bool(valid_past.any()):
        raise RuntimeError("no previous-year readings")
    sums = np.zeros(168, dtype=np.float64)
    counts = np.zeros(168, dtype=np.int64)
    np.add.at(sums, hour_keys[valid_past], values[valid_past])
    np.add.at(counts, hour_keys[valid_past], 1)
    total = int(counts.sum())
    fallback = float(sums.sum() / total)
    means = np.empty(168, dtype=np.float64)
    for slot in range(168):
        means[slot] = float(sums[slot] / counts[slot]) if counts[slot] else fallback
    predicted = means[hour_keys]
    residual = np.abs(values[valid_past] - predicted[valid_past])
    scale = _ordered_sum(residual) / residual.size
    if scale == 0.0:
        level = _ordered_sum(np.abs(values[valid_past])) / int(valid_past.sum())
        scale = level if level > 0.0 else 1.0
    return predicted, float(scale)


def normalized_residual_scores(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    past: np.ndarray,
    future: np.ndarray,
) -> list[float]:
    scores: list[float] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        predicted, scale = previous_year_forecast(values, hour_keys, past)
        valid = future & ~np.isnan(values)
        residual = np.abs(values[valid] - predicted[valid]) / scale
        scores.extend(float(item) for item in residual)
    if not scores:
        raise RuntimeError("no test-year readings on the calibration buildings")
    return scores


def evaluate_scaled_interval(
    values_by_building: dict[str, np.ndarray],
    hour_keys: np.ndarray,
    buildings: list[str],
    past: np.ndarray,
    future: np.ndarray,
    quantile: float,
) -> dict[str, object]:
    n_hours = 0
    n_covered = 0
    n_negative = 0
    abs_error = 0.0
    load = 0.0
    width_sum = 0.0
    per_building: list[dict[str, object]] = []
    for building_id in buildings:
        values = values_by_building[building_id]
        predicted, scale = previous_year_forecast(values, hour_keys, past)
        valid = future & ~np.isnan(values)
        observed = values[valid]
        point = predicted[valid]
        half = quantile * scale
        covered = int(np.count_nonzero((observed >= point - half) & (observed <= point + half)))
        count = int(observed.size)
        n_hours += count
        n_covered += covered
        n_negative += int(np.count_nonzero(observed < 0))
        abs_error += _ordered_sum(np.abs(observed - point))
        load += _ordered_sum(observed)
        width_sum += (2.0 * half) * count
        per_building.append({"building_id": building_id, "n_hours": count, "n_covered": covered})
    if n_hours == 0:
        raise RuntimeError("test buildings have no test-year readings")
    rates = [row["n_covered"] / row["n_hours"] for row in per_building]
    return {
        "n_hours": n_hours,
        "n_covered": n_covered,
        "n_negative": n_negative,
        "abs_error_sum": abs_error,
        "load_sum": load,
        "width_sum": width_sum,
        "per_building": per_building,
        "per_building_coverage_min": float(min(rates)),
        "per_building_coverage_median": _median(rates),
        "per_building_coverage_max": float(max(rates)),
    }


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)

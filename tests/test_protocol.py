from __future__ import annotations

import math

import numpy as np
import pandas as pd

from cityenergy.protocol import (
    assign_folds,
    conformal_quantile,
    evaluate_interval,
    fit_hour_of_week,
    fold_name,
    select_buildings,
    spread_take,
)


def test_conformal_quantile_rank():
    scores = [float(value) for value in range(1, 11)]
    assert conformal_quantile(scores, 0.10) == 10.0
    assert conformal_quantile(scores, 0.20) == 9.0


def test_conformal_quantile_rejects_a_tiny_calibration_set():
    try:
        conformal_quantile([1.0, 2.0], 0.10)
    except ValueError:
        return
    raise AssertionError("expected a finite-interval refusal")


def test_folds_partition_every_building():
    buildings = [f"site_usage_{index}" for index in range(50)]
    folds = assign_folds(buildings)
    flat = folds["train"] + folds["calibration"] + folds["test"]
    assert sorted(flat) == sorted(buildings)
    assert set(folds["train"]).isdisjoint(folds["calibration"])
    assert set(folds["train"]).isdisjoint(folds["test"])
    assert fold_name(buildings[0]) == fold_name(buildings[0])


def test_spread_take_is_a_sorted_subset():
    source = [f"b{index:02d}" for index in range(10)]
    picked = spread_take(source, 4)
    assert picked == sorted(picked)
    assert len(picked) == 4
    assert set(picked).issubset(source)
    assert spread_take(source, 4) == picked


def test_select_buildings_uses_the_largest_site_without_scores():
    timestamps = pd.date_range("2016-01-01", periods=20, freq="h")
    frame = pd.DataFrame({"timestamp": timestamps})
    # 20/20 non-null on site A (3 meters) and site B (1 meter). One incomplete meter.
    for name, fill in (("A_one", 1.0), ("A_two", 2.0), ("A_three", 3.0), ("B_one", 4.0)):
        frame[name] = fill
    frame["A_gap"] = float("nan")
    metadata = pd.DataFrame(
        {
            "building_id": ["A_one", "A_two", "A_three", "A_gap", "B_one"],
            "site_id": ["A", "A", "A", "A", "B"],
            "primaryspaceusage": ["Office", "Office", "Lab", "Office", "Office"],
        }
    )
    selected = select_buildings(frame, metadata)
    assert selected["site_id"] == "A"
    assert selected["building_ids"] == ["A_one", "A_three", "A_two"]
    assert selected["n_qualifying_total"] == 4
    assert selected["primaryspaceusage_counts"] == {"Lab": 1, "Office": 2}


def test_hour_of_week_mean_uses_only_train_buildings():
    keys = np.array([0, 0, 1], dtype=np.int64)
    values = {
        "train": np.array([10.0, 30.0, 5.0]),
        "other": np.array([1000.0, 1000.0, 1000.0]),
    }
    means = fit_hour_of_week(values, keys, ["train"])
    assert means[0] == 20.0
    assert means[1] == 5.0
    outcome = evaluate_interval(values, keys, ["train"], means, 10.0)
    assert outcome["n_hours"] == 3
    assert outcome["n_covered"] == 3
    assert math.isclose(outcome["per_building_coverage_min"], 1.0)

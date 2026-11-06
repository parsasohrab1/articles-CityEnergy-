"""Run the building-wise interval protocol and return a results document."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from research.loader import (
    DATA_LICENSE,
    DATASET_DOI,
    DATASET_NAME,
    DATASET_VERSION,
    PAPER_DOI,
    load_tables,
)

from cityenergy.protocol import (
    ALPHA,
    SELECTION_RULE,
    absolute_residuals,
    assign_folds,
    conformal_quantile,
    evaluate_interval,
    fit_hour_of_week,
    hour_of_week_keys,
    select_buildings,
)


def run() -> dict[str, Any]:
    meters, metadata, hashes = load_tables()
    selection = select_buildings(meters, metadata)
    folds = assign_folds(list(selection["building_ids"]))
    hour_keys = hour_of_week_keys(meters["timestamp"])
    columns = folds["train"] + folds["calibration"] + folds["test"]
    values = {
        building_id: meters[building_id].to_numpy(dtype=np.float64)
        for building_id in columns
    }
    means = fit_hour_of_week(values, hour_keys, folds["train"])
    calibration_scores = absolute_residuals(values, hour_keys, folds["calibration"], means)
    train_scores = absolute_residuals(values, hour_keys, folds["train"], means)
    quantile = conformal_quantile(calibration_scores, ALPHA)
    train_quantile = conformal_quantile(train_scores, ALPHA)
    calibrated = evaluate_interval(values, hour_keys, folds["test"], means, quantile)
    train_interval = evaluate_interval(values, hour_keys, folds["test"], means, train_quantile)
    n_test = int(calibrated["n_hours"])
    return {
        "dataset": {
            "name": DATASET_NAME,
            "version": DATASET_VERSION,
            "doi": DATASET_DOI,
            "paper_doi": PAPER_DOI,
            "license": DATA_LICENSE,
            "electricity_sha256": hashes["electricity_sha256"],
            "metadata_sha256": hashes["metadata_sha256"],
            "n_timestamps": int(len(meters)),
            "timestamp_start": pd.Timestamp(meters["timestamp"].iloc[0]).isoformat(),
            "timestamp_end": pd.Timestamp(meters["timestamp"].iloc[-1]).isoformat(),
        },
        "protocol": {
            "name": "inductive_split_conformal_absolute_residual",
            "point_model": "hour_of_week_mean_from_train_buildings",
            "split": "by_building",
            "alpha": ALPHA,
            "nominal_coverage": 1.0 - ALPHA,
            "selection_rule": SELECTION_RULE,
            "citation": "Lei et al., JASA 2018; Vovk, Gammerman and Shafer, 2005",
        },
        "selection": {
            "site_id": selection["site_id"],
            "n_qualifying_total": selection["n_qualifying_total"],
            "n_qualifying_on_site": selection["n_qualifying_on_site"],
            "primaryspaceusage_counts": selection["primaryspaceusage_counts"],
            "train_buildings": folds["train"],
            "calibration_buildings": folds["calibration"],
            "test_buildings": folds["test"],
            "n_train_buildings": len(folds["train"]),
            "n_calibration_buildings": len(folds["calibration"]),
            "n_test_buildings": len(folds["test"]),
        },
        "metrics": {
            "n_calibration_hours": len(calibration_scores),
            "n_test_hours": n_test,
            "n_covered": int(calibrated["n_covered"]),
            "n_negative_test_hours": int(calibrated["n_negative"]),
            "absolute_residual_quantile_kwh": quantile,
            "interval_width_kwh": quantile * 2.0,
            "mae_kwh": float(calibrated["abs_error_sum"]) / n_test,
            "mean_test_load_kwh": float(calibrated["load_sum"]) / n_test,
            "per_building_coverage_min": calibrated["per_building_coverage_min"],
            "per_building_coverage_median": calibrated["per_building_coverage_median"],
            "per_building_coverage_max": calibrated["per_building_coverage_max"],
            "per_test_building": calibrated["per_building"],
            "train_quantile_n_covered": int(train_interval["n_covered"]),
            "train_quantile_width_kwh": train_quantile * 2.0,
        },
    }


def results_block(payload: dict[str, Any]) -> str:
    """Prose rendered only from a results document. Do not hand-edit the numbers."""
    metrics = payload["metrics"]
    selection = payload["selection"]
    covered = int(metrics["n_covered"])
    hours = int(metrics["n_test_hours"])
    train_covered = int(metrics["train_quantile_n_covered"])
    coverage = covered / hours
    train_coverage = train_covered / hours
    return "\n".join(
        [
            f"Site {selection['site_id']}: {selection['n_train_buildings']} train buildings, "
            f"{selection['n_calibration_buildings']} calibration buildings, "
            f"{selection['n_test_buildings']} test buildings.",
            f"Split-conformal interval on held-out buildings: {covered}/{hours} hours "
            f"inside the interval ({coverage:.4f}), nominal coverage "
            f"{payload['protocol']['nominal_coverage']:.4f}, width "
            f"{metrics['interval_width_kwh']:.4f} kWh.",
            f"Train-residual quantile on the same test hours: {train_covered}/{hours} "
            f"({train_coverage:.4f}), width {metrics['train_quantile_width_kwh']:.4f} kWh.",
            f"Point-forecast MAE {metrics['mae_kwh']:.4f} kWh. "
            f"Mean test load {metrics['mean_test_load_kwh']:.4f} kWh.",
            "Per test building, coverage min "
            f"{metrics['per_building_coverage_min']:.4f}, median "
            f"{metrics['per_building_coverage_median']:.4f}, max "
            f"{metrics['per_building_coverage_max']:.4f}.",
        ]
    )


def replace_results_block(text: str, block: str) -> str:
    start = "<!-- results:start -->"
    end = "<!-- results:end -->"
    if start not in text or end not in text:
        raise ValueError("results markers are missing")
    prefix, rest = text.split(start, 1)
    _, suffix = rest.split(end, 1)
    return f"{prefix}{start}\n{block}\n{end}{suffix}"

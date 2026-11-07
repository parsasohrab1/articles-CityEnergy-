"""Run the next-year interval protocol and return a results document."""

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
    FORECAST_START,
    SELECTION_RULE,
    area_residual_scores,
    assign_folds,
    conformal_quantile,
    evaluate_area_interval,
    evaluate_scaled_interval,
    fit_area_profiles,
    forecast_masks,
    hour_of_week_keys,
    normalized_residual_scores,
    select_buildings,
)


def _future_only(
    values: dict[str, np.ndarray],
    building_ids: list[str],
    past: np.ndarray,
) -> dict[str, np.ndarray]:
    held: dict[str, np.ndarray] = {}
    for building_id in building_ids:
        series = values[building_id].copy()
        series[past] = np.nan
        held[building_id] = series
    return held


def run() -> dict[str, Any]:
    meters, metadata, hashes = load_tables()
    selection = select_buildings(meters, metadata)
    folds = assign_folds(list(selection["building_ids"]))
    hour_keys = hour_of_week_keys(meters["timestamp"])
    past, future = forecast_masks(meters["timestamp"])
    columns = folds["train"] + folds["calibration"] + folds["test"]
    values = {
        building_id: meters[building_id].to_numpy(dtype=np.float64)
        for building_id in columns
    }
    meta = metadata.set_index("building_id")
    area = {building_id: float(meta.loc[building_id, "sqm"]) for building_id in columns}
    usage = {
        building_id: str(meta.loc[building_id, "primaryspaceusage"]) for building_id in columns
    }
    calibration_scores = normalized_residual_scores(
        values, hour_keys, folds["calibration"], past, future
    )
    normalized_quantile = conformal_quantile(calibration_scores, ALPHA)
    calibrated = evaluate_scaled_interval(
        values,
        hour_keys,
        folds["test"],
        past,
        future,
        normalized_quantile,
    )
    train_past = {
        building_id: np.where(future, np.nan, values[building_id]) for building_id in folds["train"]
    }
    profiles, overall = fit_area_profiles(train_past, hour_keys, folds["train"], area, usage)
    transfer_scores = area_residual_scores(
        _future_only(values, folds["calibration"], past),
        hour_keys,
        folds["calibration"],
        profiles,
        overall,
        area,
        usage,
    )
    transfer_quantile = conformal_quantile(transfer_scores, ALPHA)
    transfer = evaluate_area_interval(
        _future_only(values, folds["test"], past),
        hour_keys,
        folds["test"],
        profiles,
        overall,
        area,
        usage,
        transfer_quantile,
    )
    n_test = int(calibrated["n_hours"])
    if int(transfer["n_hours"]) != n_test:
        raise RuntimeError("transfer baseline is not on the same test hours")
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
            "n_previous_year_timestamps": int(past.sum()),
            "n_test_year_timestamps": int(future.sum()),
            "timestamp_start": pd.Timestamp(meters["timestamp"].iloc[0]).isoformat(),
            "timestamp_end": pd.Timestamp(meters["timestamp"].iloc[-1]).isoformat(),
        },
        "protocol": {
            "name": "next_year_scaled_split_conformal",
            "point_model": "own_building_hour_of_week_before_forecast_start",
            "interval": "absolute_residual_divided_by_previous_year_mae",
            "split": "by_building_for_the_interval",
            "alpha": ALPHA,
            "nominal_coverage": 1.0 - ALPHA,
            "forecast_start": FORECAST_START.isoformat(),
            "selection_rule": SELECTION_RULE,
            "citation": (
                "Lei et al., JASA 2018, locally weighted by the previous-year "
                "mean absolute residual; Vovk, Gammerman and Shafer, 2005"
            ),
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
            "normalized_quantile": normalized_quantile,
            "mean_interval_width_kwh": float(calibrated["width_sum"]) / n_test,
            "mae_kwh": float(calibrated["abs_error_sum"]) / n_test,
            "mean_test_load_kwh": float(calibrated["load_sum"]) / n_test,
            "transfer_n_covered": int(transfer["n_covered"]),
            "transfer_intensity_quantile_kwh_per_m2": transfer_quantile,
            "transfer_mean_interval_width_kwh": float(transfer["width_sum"]) / n_test,
            "transfer_mae_kwh": float(transfer["abs_error_sum"]) / n_test,
            "per_building_coverage_min": calibrated["per_building_coverage_min"],
            "per_building_coverage_median": calibrated["per_building_coverage_median"],
            "per_building_coverage_max": calibrated["per_building_coverage_max"],
            "per_test_building": calibrated["per_building"],
        },
    }


def results_block(payload: dict[str, Any]) -> str:
    """Prose rendered only from a results document. Do not hand-edit the numbers."""
    metrics = payload["metrics"]
    selection = payload["selection"]
    covered = int(metrics["n_covered"])
    hours = int(metrics["n_test_hours"])
    transfer_covered = int(metrics["transfer_n_covered"])
    coverage = covered / hours
    transfer_coverage = transfer_covered / hours
    return "\n".join(
        [
            f"Site {selection['site_id']}: {selection['n_train_buildings']} train buildings, "
            f"{selection['n_calibration_buildings']} calibration buildings, "
            f"{selection['n_test_buildings']} test buildings. "
            f"Test year starts at {payload['protocol']['forecast_start']}.",
            f"Own-history forecast on the test year: {covered}/{hours} hours "
            f"inside the interval ({coverage:.4f}), nominal coverage "
            f"{payload['protocol']['nominal_coverage']:.4f}, mean width "
            f"{metrics['mean_interval_width_kwh']:.4f} kWh.",
            f"Own-history MAE {metrics['mae_kwh']:.4f} kWh. "
            f"Mean test-year load {metrics['mean_test_load_kwh']:.4f} kWh.",
            f"Profile transferred from other buildings' previous year, same test hours: "
            f"{transfer_covered}/{hours} ({transfer_coverage:.4f}), mean width "
            f"{metrics['transfer_mean_interval_width_kwh']:.4f} kWh, MAE "
            f"{metrics['transfer_mae_kwh']:.4f} kWh.",
            "Per test building, own-history coverage min "
            f"{metrics['per_building_coverage_min']:.4f}, median "
            f"{metrics['per_building_coverage_median']:.4f}, max "
            f"{metrics['per_building_coverage_max']:.4f}.",
        ]
    )


def _reading(metrics: dict[str, Any], nominal: float) -> str:
    coverage = int(metrics["n_covered"]) / int(metrics["n_test_hours"])
    width = float(metrics["mean_interval_width_kwh"])
    load = float(metrics["mean_test_load_kwh"])
    mae = float(metrics["mae_kwh"])
    transfer_mae = float(metrics["transfer_mae_kwh"])
    sentences = []
    if mae < transfer_mae:
        sentences.append(
            "On these held-out buildings the previous-year profile has a lower "
            "mean absolute error than the profile transferred from other buildings."
        )
    else:
        sentences.append(
            "On these held-out buildings the previous-year profile does not have a "
            "lower mean absolute error than the profile transferred from other buildings."
        )
    if coverage + 1e-12 >= nominal:
        sentences.append("The measured coverage is at or above the nominal level.")
    else:
        sentences.append("The measured coverage is below the nominal level.")
    if width < 2.0 * load:
        sentences.append(
            "The mean interval width is less than twice the mean test-year load."
        )
    else:
        sentences.append(
            "The mean interval width is at least twice the mean test-year load."
        )
    return " ".join(sentences)


def manuscript_text(payload: dict[str, Any]) -> str:
    """Double-blind manuscript. Measured figures come only from ``payload``."""
    metrics = payload["metrics"]
    selection = payload["selection"]
    nominal = float(payload["protocol"]["nominal_coverage"])
    covered = int(metrics["n_covered"])
    hours = int(metrics["n_test_hours"])
    start = payload["protocol"]["forecast_start"]
    site = selection["site_id"]
    abstract = (
        "We forecast hourly electricity in the next calendar year from the same "
        f"building's previous year. On site {site} of the Building Data Genome "
        f"Project 2, the hour-of-week mean is fit only on hours before {start}. "
        f"{selection['n_calibration_buildings']} other buildings set a "
        "split-conformal interval and "
        f"{selection['n_test_buildings']} buildings are scored on the later year. "
        f"The interval covered {covered}/{hours} test-year hours "
        f"({covered / hours:.4f}) at a nominal coverage of {nominal:.4f}. Its mean "
        f"width was {metrics['mean_interval_width_kwh']:.4f} kWh. The mean test-year "
        f"load was {metrics['mean_test_load_kwh']:.4f} kWh and the mean absolute "
        f"error was {metrics['mae_kwh']:.4f} kWh. A profile transferred from other "
        "buildings, fit without the target building's own year, had mean absolute "
        f"error {metrics['transfer_mae_kwh']:.4f} kWh and mean width "
        f"{metrics['transfer_mean_interval_width_kwh']:.4f} kWh on the same hours."
    )
    reading = _reading(metrics, nominal)
    sections = [
        ("Abstract", abstract),
        (
            "1. Question",
            "The question is whether the next year of hourly electricity on a "
            "building can be forecast from that building's previous year, with an "
            "interval that is calibrated on other buildings and narrow enough to "
            "sit near the load.",
        ),
        (
            "2. Data",
            "The meters are the cleaned hourly electricity file and the building "
            "metadata in Building Data Genome Project 2, release v1.0 "
            "(doi:10.5281/zenodo.3887306), described by Miller et al. (2020). "
            "The data license is CC BY 4.0. The ASHRAE Kaggle competition files "
            "were not used. A meter is kept when at least 95 percent of its hours "
            "are present and its floor area is positive. The site with the most "
            "such meters is used. At most 40 meters are kept, spread across the "
            "sorted building identifiers. Each kept building is assigned to "
            "training, calibration, or test by a fixed hash of its identifier. "
            f"Hours before {start} are the previous year. Later hours are the test "
            "year. The point forecast for a building uses only that building's "
            "previous year. The interval quantile uses the test year of the "
            "calibration buildings and does not use the test buildings. The "
            "training buildings are used only for the transferred-profile comparison.",
        ),
        (
            "3. Forecast",
            "The point forecast is the mean load at that hour of the week in the "
            "previous year of the same building. The interval is inductive "
            "split-conformal regression with a locally weighted absolute residual "
            "(Vovk, Gammerman and Shafer, 2005; Lei et al., 2018). The weight is "
            "that building's mean absolute residual in the previous year, which is "
            "known before the test year. The quantile uses rank "
            "ceil((n+1)*(1-alpha)) on the calibration buildings' test-year scores, "
            "with alpha equal to 0.10. The half-width on a building is that "
            "quantile times its previous-year mean absolute residual. The "
            "comparison forecast is a usage-specific hour-of-week mean of kWh per "
            "square metre, fit on the previous year of the training buildings and "
            "multiplied by floor area, with its own area-weighted split-conformal "
            "interval. A language model assisted with wording. The measurements "
            "were checked against the script output.",
        ),
        ("4. Measurement", results_block(payload)),
        (
            "5. Reading the measurement",
            reading
            + " The nominal level applies to the pooled test-year hours. The lowest "
            "building in the measurement section can fall below that level. A "
            "symmetric interval can extend below zero. Weather is not an input. "
            "One site is not another site. This is not a building-management "
            "deployment.",
        ),
        (
            "6. Conclusion",
            reading + " The file reports that forecast and no stronger one.",
        ),
        (
            "References",
            "Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J., and Wasserman, L. "
            "Distribution-free predictive inference for regression. Journal of the "
            "American Statistical Association, 113(523), 1094-1111, 2018.\n"
            "Miller, C., et al. The Building Data Genome Project 2. Scientific Data, "
            "7, 368, 2020. doi:10.1038/s41597-020-00712-x.\n"
            "Vovk, V., Gammerman, A., and Shafer, G. Algorithmic Learning in a Random "
            "World. Springer, 2005.\n"
            "Dataset archive: doi:10.5281/zenodo.3887306. License: CC BY 4.0.",
        ),
    ]
    lines = [
        "Previous-year hourly electricity forecasts the next year",
        "",
    ]
    for heading, body in sections:
        lines.append(heading)
        lines.append(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def replace_results_block(text: str, block: str) -> str:
    start = "<!-- results:start -->"
    end = "<!-- results:end -->"
    if start not in text or end not in text:
        raise ValueError("results markers are missing")
    prefix, rest = text.split(start, 1)
    _, suffix = rest.split(end, 1)
    return f"{prefix}{start}\n{block}\n{end}{suffix}"

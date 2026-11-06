# Software requirements — CityEnergy

Laboratory scope: reproduce one building-wise electricity interval on Building Data Genome 2 v1.0 and write the measured counts.

| ID | Requirement | Satisfied by |
|---|---|---|
| FR-01 | Download `electricity_cleaned.csv` and `metadata.csv` from the v1.0 URLs and stop if the SHA-256 or the electricity byte size differs from the pin. | `research/loader.py` |
| FR-02 | Record CC BY 4.0 for the data, and record that the upstream repository MIT license is not the data license. | `research/DATA.md` |
| FR-03 | Keep meters with at least 95% non-null hours, then the single site with the most such meters, then at most 40 meters spread across sorted ids. | `select_buildings`, `tests/test_protocol.py` |
| FR-04 | Assign each kept building to train, calibration, or test. The three sets are disjoint and cover the kept list. | `assign_folds` |
| FR-05 | Fit the hour-of-week mean on training buildings only. | `fit_hour_of_week` |
| FR-06 | Set the absolute-residual quantile on calibration buildings at alpha 0.10, using rank `ceil((n+1)*(1-alpha))`. | `conformal_quantile` |
| FR-07 | On test buildings, count covered hours, width, MAE, mean load, and per-building coverage. Also count the same hours against the train-residual quantile. | `evaluate_interval`, `cityenergy.experiment.run` |
| FR-08 | Write `results/results.json` from that run and regenerate the marked README and TRL blocks from the same object. | `scripts/run_experiment.py`, `tests/test_results.py` |

The software does not impute missing hours, does not clip negative interval bounds, and does not read weather.

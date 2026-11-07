# Technology readiness — CityEnergy

| Level | Status | Evidence |
|---|---|---|
| TRL 1–3 | done | Next-year forecast, building-wise interval split, and the transferred-profile comparison are implemented in `src/cityenergy/protocol.py`. |
| TRL 4 | not used as evidence | This repository does not report a synthetic-data performance number. |
| TRL 5 | measured offline | The forecast was run on real Building Data Genome Project 2 electricity meters. The test year of each scored building is held out of its profile and of the interval quantile. Counts are in `results/results.json`. This is not a live building and not a BMS integration. |
| TRL 6+ | not reached | Needs a second site campaign or an operator-facing deployment. The AIEI 2027 journal-fit gate is recorded in `docs/JOURNAL_FIT.md`. |

## Measured result

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings. Test year starts at 2017-01-01T00:00:00.
Own-history forecast on the test year: 65865/69506 hours inside the interval (0.9476), nominal coverage 0.9000, mean width 49.8700 kWh.
Own-history MAE 9.9583 kWh. Mean test-year load 36.2297 kWh.
Profile transferred from other buildings' previous year, same test hours: 65880/69506 (0.9478), mean width 151.8214 kWh, MAE 14.7358 kWh.
Per test building, own-history coverage min 0.8593, median 0.9658, max 0.9925.
<!-- results:end -->

The nominal 90% is the reference level of the interval on the pooled test-year hours. The measured coverage above is the result, including the lowest building. A symmetric residual interval can extend below zero. Weather is not used. One site does not establish another site.

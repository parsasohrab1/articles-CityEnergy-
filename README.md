# CityEnergy

Offline next-year forecast of hourly electricity on real non-residential meters from the Building Data Genome Project 2. Each building's point forecast is its own hour-of-week mean from the previous year. The interval is inductive split-conformal regression, locally weighted by that building's previous-year mean absolute error (Lei et al., JASA 2018; Vovk, Gammerman and Shafer, 2005). The quantile is fit on other buildings. A transferred profile that never sees the target building is the comparison.

This repository does not report a synthetic-data performance number.

The target venue is AIEI 2027 at https://www.aiei2027.org/ (deadline 15 February 2027). The journal-fit gate is in `docs/JOURNAL_FIT.md`. The anonymized manuscript is `article/manuscript.pdf`. It reports this next-year forecast. Upload steps that only an author can finish are in `docs/SUBMISSION.md`. Nothing has been uploaded.

## Measured result

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings. Test year starts at 2017-01-01T00:00:00.
Own-history forecast on the test year: 65865/69506 hours inside the interval (0.9476), nominal coverage 0.9000, mean width 49.8700 kWh.
Own-history MAE 9.9583 kWh. Mean test-year load 36.2297 kWh.
Profile transferred from other buildings' previous year, same test hours: 65880/69506 (0.9478), mean width 151.8214 kWh, MAE 14.7358 kWh.
Per test building, own-history coverage min 0.8593, median 0.9658, max 0.9925.
<!-- results:end -->

## Data and method limits

The loader, the CC BY 4.0 record, and the pinned file hashes are in `research/`. Meter files stay in `data/cache/` and are not committed. `results/results.json` is written only by `scripts/run_experiment.py`.

- The site and the meters follow a fixed completeness rule, applied before any score is computed. The year cut is 2017-01-01.
- The forecast uses the calendar and that building's previous year. Weather is not an input.
- The interval width scales with the previous-year error, so a steadier building gets a narrower interval. The nominal 90% applies to the pooled test-year hours. One building can fall below that level. Compare the width with the mean test-year load in the measured block.
- A symmetric residual interval can extend below zero even though a meter does not.
- The comparison profile is fit on other buildings and does not use the target meter.
- There is no building-management integration and no operator study.

## Reproduce

```bash
pip install -r requirements.txt pytest==8.3.3 ruff==0.16.0
python scripts/run_experiment.py
ruff check src tests scripts research
pytest -q
```

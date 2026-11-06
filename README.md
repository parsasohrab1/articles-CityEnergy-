# CityEnergy

Offline check of a nominal 90% electricity interval on real non-residential meters from the Building Data Genome Project 2. The split unit is the building. The point forecast is the hour-of-week mean fit on training buildings only. The interval is inductive split-conformal regression with absolute residuals (Lei et al., JASA 2018; Vovk, Gammerman and Shafer, 2005).

This repository does not report a synthetic-data performance number.

The target venue is AIEI 2027 at https://www.aiei2027.org/ (deadline 15 February 2027). The journal-fit gate is in `docs/JOURNAL_FIT.md`. The anonymized manuscript is `article/manuscript.pdf`. It states the negative finding: the measured interval is too wide relative to the test load to support a useful-forecast claim. Upload steps that only an author can finish are in `docs/SUBMISSION.md`. Nothing has been uploaded. The interval implemented here is the published absolute-residual construction cited above. No other conformity score is described.

## Measured result

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings.
Split-conformal interval on held-out buildings: 139372/139372 hours inside the interval (1.0000), nominal coverage 0.9000, width 452.8592 kWh.
Train-residual quantile on the same test hours: 138969/139372 (0.9971), width 270.5115 kWh.
Point-forecast MAE 61.0987 kWh. Mean test load 37.7539 kWh.
Per test building, coverage min 1.0000, median 1.0000, max 1.0000.
<!-- results:end -->

## Data and method limits

The loader, the CC BY 4.0 record, and the pinned file hashes are in `research/`. Meter files stay in `data/cache/` and are not committed. `results/results.json` is written only by `scripts/run_experiment.py`.

- The site and the meters follow a fixed completeness rule, applied before any score is computed.
- The forecast uses the calendar only. Weather is not an input.
- One absolute-residual width is shared by every building. A large calibration meter sets a width that can dwarf a smaller test meter, so a high coverage can be an uninformative interval. Compare the width with the mean test load in the measured block.
- A symmetric residual interval can extend below zero even though a meter does not.
- Holding out whole buildings is a shift test. The nominal 90% is a reference for that test, not a guarantee on a new building.
- There is no building-management integration and no operator study.

## Reproduce

```bash
pip install -r requirements.txt pytest==8.3.3 ruff==0.16.0
python scripts/run_experiment.py
ruff check src tests scripts research
pytest -q
```

# Technology readiness — CityEnergy

| Level | Status | Evidence |
|---|---|---|
| TRL 1–3 | done | Interval protocol and building-wise split are implemented in `src/cityenergy/protocol.py`. |
| TRL 4 | not used as evidence | This repository does not report a synthetic-data performance number. |
| TRL 5 | measured offline | The same protocol was run on real Building Data Genome 2 electricity meters, with whole buildings held out. Counts are in `results/results.json`. The shared absolute-residual width is large relative to the mean test load, so the coverage is not evidence of a tight interval. This is not a live building and not a BMS integration. |
| TRL 6+ | not reached | Needs a second site campaign or an operator-facing deployment, plus the journal-fit gate and patent-counsel review before AIEI 2027. |

## Measured result

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings.
Split-conformal interval on held-out buildings: 139372/139372 hours inside the interval (1.0000), nominal coverage 0.9000, width 452.8592 kWh.
Train-residual quantile on the same test hours: 138969/139372 (0.9971), width 270.5115 kWh.
Point-forecast MAE 61.0987 kWh. Mean test load 37.7539 kWh.
Per test building, coverage min 1.0000, median 1.0000, max 1.0000.
<!-- results:end -->

The nominal 90% is the reference level of the interval. The measured coverage above is the result, including when it is below that reference. A symmetric residual interval can extend below zero. Weather is not used. One site does not establish another site.

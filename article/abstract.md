# Abstract draft

**Title:** A shared absolute-residual electricity interval on held-out buildings

**Target:** AIEI 2027, https://www.aiei2027.org/ — not submitted. See `docs/JOURNAL_FIT.md`.

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings.
Split-conformal interval on held-out buildings: 139372/139372 hours inside the interval (1.0000), nominal coverage 0.9000, width 452.8592 kWh.
Train-residual quantile on the same test hours: 138969/139372 (0.9971), width 270.5115 kWh.
Point-forecast MAE 61.0987 kWh. Mean test load 37.7539 kWh.
Per test building, coverage min 1.0000, median 1.0000, max 1.0000.
<!-- results:end -->

The point forecast is an hour-of-week mean fit on other buildings. The interval is inductive split-conformal regression with one absolute residual for every building (Lei et al., JASA 2018). Because that single width is set by larger calibration meters, covering every test hour is not a useful forecast. The draft is not submitted.

**Keywords:** building electricity; prediction interval; split conformal; Building Data Genome 2

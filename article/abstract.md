# Abstract draft

**Title:** Previous-year hourly electricity forecasts the next year

**Target:** AIEI 2027, https://www.aiei2027.org/ — not submitted. See `docs/JOURNAL_FIT.md`.

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings. Test year starts at 2017-01-01T00:00:00.
Own-history forecast on the test year: 65865/69506 hours inside the interval (0.9476), nominal coverage 0.9000, mean width 49.8700 kWh.
Own-history MAE 9.9583 kWh. Mean test-year load 36.2297 kWh.
Profile transferred from other buildings' previous year, same test hours: 65880/69506 (0.9478), mean width 151.8214 kWh, MAE 14.7358 kWh.
Per test building, own-history coverage min 0.8593, median 0.9658, max 0.9925.
<!-- results:end -->

The point forecast is the hour-of-week mean of the same building before 2017. The interval is inductive split-conformal regression, locally weighted by that building's previous-year mean absolute error (Lei et al., JASA 2018). The comparison is a profile transferred from other buildings. The draft is not submitted.

**Keywords:** building electricity; next-year forecast; prediction interval; Building Data Genome 2

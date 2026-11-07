# Journal fitness — AIEI 2027

Call checked: Artificial Intelligence in Energy and Infrastructure, https://www.aiei2027.org/cfp.html (Institute for Computational Science and Artificial Intelligence, Van Lang University, Ho Chi Minh City, 20–22 May 2027).

This is not the IEEE International Conference on AI Engineering and Innovation (Bangalore). That call’s paper deadline was 30 September 2026.

| Item | What the call page says |
|---|---|
| Scope | Original work at the intersection of artificial intelligence, energy and infrastructure. Track 1 includes “Intelligent energy forecasting”. |
| Deadline | Abstract or full paper, 15 February 2027. Acceptance 15 March 2027. Camera-ready 15 April 2027. |
| Length | English, at most 6 pages including figures and references. |
| Publication | Original, not under review elsewhere. An accepted paper must be registered and presented. |

Checked on 6 November 2026 from the call page above.

## Fit

Topic overlap is direct. Next-year hourly electricity on non-residential buildings is energy forecasting, which is inside Track 1. The run is not deep learning, storage control, a smart grid, or a deployed building system.

The product is CityEnergy on public Building Data Genome 2 electricity meters. It is a different measurement from the iEMS carbon-management abstract already mapped to the Asia Pacific CCUS Conference.

## Evidence

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings. Test year starts at 2017-01-01T00:00:00.
Own-history forecast on the test year: 65865/69506 hours inside the interval (0.9476), nominal coverage 0.9000, mean width 49.8700 kWh.
Own-history MAE 9.9583 kWh. Mean test-year load 36.2297 kWh.
Profile transferred from other buildings' previous year, same test hours: 65880/69506 (0.9478), mean width 151.8214 kWh, MAE 14.7358 kWh.
Per test building, own-history coverage min 0.8593, median 0.9658, max 0.9925.
<!-- results:end -->

The point forecast uses only the previous year of the scored building. The interval quantile uses other buildings. Read the own-history error next to the transferred-profile error, and the mean width next to the mean test-year load.

## Decision

The manuscript reports this next-year forecast. The anonymized file `article/manuscript.pdf` is the full paper: English, no author names, and within five pages. `article/PORTAL.txt` holds the portal fields. `docs/SUBMISSION.md` lists the portal steps. The publication-right form still needs the author's signature. Nothing has been uploaded.

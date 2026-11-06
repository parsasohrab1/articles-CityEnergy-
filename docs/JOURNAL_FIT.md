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

Topic overlap is partial. Hourly electricity on non-residential buildings is energy forecasting, which is inside Track 1. The run is not deep learning, storage control, a smart grid, or a deployed building system.

The product is CityEnergy on public Building Data Genome 2 electricity meters. It is a different measurement from the iEMS carbon-management abstract already mapped to the Asia Pacific CCUS Conference.

## Evidence

<!-- results:start -->
Site Rat: 24 train buildings, 8 calibration buildings, 8 test buildings.
Split-conformal interval on held-out buildings: 139372/139372 hours inside the interval (1.0000), nominal coverage 0.9000, width 452.8592 kWh.
Train-residual quantile on the same test hours: 138969/139372 (0.9971), width 270.5115 kWh.
Point-forecast MAE 61.0987 kWh. Mean test load 37.7539 kWh.
Per test building, coverage min 1.0000, median 1.0000, max 1.0000.
<!-- results:end -->

One shared absolute-residual width is applied to every test building. Read the width next to the mean test load in the block above. A coverage of every test hour, at a nominal 90%, is not evidence of a useful forecast when that width is many times the mean load.

## Decision

Do not submit this measurement as a successful interval. The anonymized file `article/manuscript.pdf` is the full paper for the negative finding: English, no author names, and within the six-page limit. `docs/SUBMISSION.md` lists the portal steps. Nothing has been uploaded.

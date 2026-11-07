# Business requirements — CityEnergy

Scope of this release: an offline, reproducible next-year forecast of hourly electricity on public Building Data Genome 2 meters. The interval quantile is fit on other buildings. The target discussion venue is AIEI 2027 (deadline 2027-02-15). This document is not a submission.

| ID | Requirement | Evidence |
|---|---|---|
| BR-01 | Use a public building-meter source whose license has been read and recorded. | `research/DATA.md`, `research/loader.py` |
| BR-02 | Do not treat a synthetic series as a performance claim. | README and `docs/TRL.md` state that no synthetic-data performance number is reported. The only performance document is `results/results.json`. |
| BR-03 | Keep the test year out of that building's profile and out of the interval quantile. | Year cut and building-wise interval split in `src/cityenergy/protocol.py` |
| BR-04 | Publish the measured coverage, width, and point-forecast error from the script, including the transferred-profile comparison. | `results/results.json` and the generated blocks in README and `docs/TRL.md` |
| BR-05 | Describe only the published locally weighted absolute-residual interval. The weight is the previous-year mean absolute residual. | `src/cityenergy/protocol.py` cites Lei et al. (2018) and Vovk, Gammerman and Shafer (2005). |
| BR-06 | Meet the AIEI 2027 full-paper conditions with this next-year forecast. | `docs/JOURNAL_FIT.md`, `article/manuscript.pdf`, `docs/SUBMISSION.md`. |

Out of scope: a live building, a control set-point, a tariff decision, and a second data source.

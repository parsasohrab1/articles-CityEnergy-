# Building Data Genome 2 — source and license

The meters used by this repository are the cleaned electricity measurements and the building metadata from Building Data Genome Project 2, release v1.0.

## What was checked

- Zenodo record 3887306 (`https://doi.org/10.5281/zenodo.3887306`) publishes that release with license id `cc-by-4.0` (Creative Commons Attribution 4.0 International).
- The data descriptor is Miller et al., Scientific Data 7, 368 (2020), `https://doi.org/10.1038/s41597-020-00712-x`.
- The GitHub tag `v1.0` of `buds-lab/building-data-genome-project-2` is the same release. Its `LICENSE` file is the MIT license and applies to the project software. That MIT text is not the license of the meter tables.
- The Kaggle packaging of the ASHRAE Great Energy Predictor III competition was not downloaded. Those competition terms are separate from the CC BY 4.0 Zenodo release. BDG2 is the dataset that was used, because its license is public and explicit.

## Files the loader fetches

| File | URL | Pinned SHA-256 |
|---|---|---|
| `data/meters/cleaned/electricity_cleaned.csv` | `https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/v1.0/data/meters/cleaned/electricity_cleaned.csv` | `b01056f4ceec1992ce019297e674d6d6ecd0240e50a2aaeb6f958c65efdc282d` |
| `data/metadata/metadata.csv` | `https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/v1.0/data/metadata/metadata.csv` | `992d0b29f24f96ad4332bc4dbb534b7bdd7dd2689aad093f94e93068ecddca02` |

The loader writes both files under `data/cache/` and refuses to continue if the bytes do not match the pinned hash. The cache is not committed.

Electricity values are the published meter units, kWh. Timestamps are used as published (site local time in the BDG2 release) and are not shifted.

## Attribution

Miller, C., Kathirgamanathan, A., Picchetti, B., Arjunan, P., Park, J. Y., Nagy, Z., Raftery, P., Hobson, B. W., Shi, Z., and Meggers, F. The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition. Scientific Data 7, 368 (2020). https://doi.org/10.1038/s41597-020-00712-x

Dataset archive: https://doi.org/10.5281/zenodo.3887306 (CC BY 4.0).

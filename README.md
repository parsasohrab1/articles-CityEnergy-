# articles-CityEnergy-

Hourly electricity-load forecasting for urban buildings with split-conformal
intervals. TRL 4 (laboratory validation on a **synthetic** generator only).

- `src/cityenergy/` – synthetic generator, seasonal-naive baseline, temperature-aware ridge model, conformal interval.
- `research/run_study.py` – 104-week study (train 52 / calibrate 16 / test 36 weeks), 10 seeds, three scenarios; writes `research/results.json`.
- `docs/` – BRS, SRS, TRL.

```
pip install -e ".[dev]" && python -m pytest && python research/run_study.py
```

No metered city data were used. No claim on real buildings is made.

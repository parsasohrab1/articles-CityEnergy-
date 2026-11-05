# TRL assessment – CityEnergy

**Claimed level: TRL 4** (component validated in a simulated environment).

Mean over 10 synthetic seeds, before / after the scenario start (interval target 0.90):

| Scenario | Ridge MAPE % | Ridge coverage | Seasonal-naive MAPE % | Seasonal-naive coverage |
|---|---|---|---|---|
| no_shift | 3.4 / 3.2 | 0.878 / 0.897 | 5.7 / 5.9 | 0.921 / 0.886 |
| heatwave_+4C | 3.4 / 3.2 | 0.878 / 0.897 | 5.7 / 6.8 | 0.921 / 0.839 |
| cooling_drift_x1.4 | 3.4 / 3.5 | 0.878 / 0.856 | 5.7 / 6.4 | 0.921 / 0.859 |

Honest notes:
- Ridge MAPE ~3.3 % vs ~5.8 % for the weekly naive baseline on this generator.
- Ridge coverage before the scenario is 0.878 (below 0.90, calibration block is a different season).
- The heatwave does not hurt ridge because temperature is an input and the generator's response is exactly the model's hinge form; it does hurt the naive baseline (coverage 0.839). This favourable result is a property of the synthetic generator.
- A structural cooling-response drift (x1.4) lowers ridge coverage to 0.856 – recalibration would be needed.
- Everything is synthetic; results show method behaviour, not performance on real buildings.

Not reached for TRL 5: validation on metered building or feeder data.

# Software Requirements Specification – CityEnergy

- SR-1 `make_series(seed, heat_shift, weeks, cool_gain, shift_start)` generates hourly load, temperature, hour, weekday (synthetic).
- SR-2 `seasonal_naive` forecasts the load one week earlier.
- SR-3 `features`/`fit_ridge`/`predict`: hour × weekday/weekend profile plus cooling and heating degrees; closed-form ridge.
- SR-4 `conformal_halfwidth` computes a split-conformal relative half-width on a calibration block; `coverage`, `mape` evaluate.
- SR-5 Study separates train, calibration and test blocks; shifts start inside the test block.
- SR-6 Six unit tests cover generator, shift parameters, baseline, model vs baseline, conformal coverage.

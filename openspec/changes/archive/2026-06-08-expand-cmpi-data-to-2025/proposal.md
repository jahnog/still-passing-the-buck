## Why

The current Argentina CMPI notebook is capped at 2019 even though the local World Bank extract already contains newer observations for several required series. Extending the analysis through 2025 requires a coordinated refresh of the WDI-derived dataset, the auxiliary interest-rate data, and the notebook logic so the results are based on real published values instead of stale local inputs.

## What Changes

- Refresh the Argentina-focused World Development Indicators extract and regenerate the project data files with the latest published values needed by the notebook through 2025.
- Extend the auxiliary interest-rate dataset beyond 2019 using a documented real-data source that remains compatible with the existing CMPI methodology.
- Update the notebook narrative, constants, administration coverage, and output calculations so the analysis and charts include post-2019 years.
- Add validation steps for missing or unpublished indicators so the data refresh process clearly identifies gaps before notebook execution.

## Capabilities

### New Capabilities
- `cmpi-analysis-refresh`: Keep the Argentina CMPI notebook and its local data assets synchronized with the latest published macroeconomic inputs through 2025, with explicit handling for missing or stale source series.

### Modified Capabilities
- None.

## Impact

- Affected data assets: `Indicators.csv`, `Indicators.csv.gz`, and `data/argentina/interest/wb-ids-arg.csv`.
- Affected analysis surface: `Still_Passing_the_Buck.ipynb`, including narrative text, year bounds, administration ranges, and ranking outputs.
- Affected workflow: the project needs a reproducible refresh path for WDI exports and verification of required series availability, especially for the missing wholesale-price series and post-2019 interest observations.
## Context

The current notebook in `Still_Passing_the_Buck.ipynb` hard-codes `DATA_END_YEAR = 2019` and only defines administrations through the Macri term. The local `Indicators.csv.gz` file already contains newer Argentina observations for GDP deflator growth, exchange rate, and GDP per-capita growth, but the notebook's required wholesale-price series (`FP.WPI.TOTL`) is absent from the local WDI extracts and the auxiliary interest dataset ends at 2019. The change therefore needs both a data refresh and explicit handling of source gaps so the CMPI output is extended with real data rather than silent missing values.

## Goals / Non-Goals

**Goals:**
- Refresh the repo-local WDI-derived indicator files and the auxiliary interest dataset through the 2025 analysis window.
- Extend notebook text, constants, administration metadata, and result generation to include post-2019 years.
- Add an explicit validation step that checks required series coverage before notebook calculations proceed.
- Preserve the existing CMPI methodology unless a required source series is unavailable, in which case the gap must be documented and surfaced.

**Non-Goals:**
- Rework the CMPI formula or redesign the analysis around a different macroeconomic index.
- Convert the notebook into a package or web application.
- Build a fully generalized ingestion framework for countries other than Argentina.

## Decisions

### Keep the notebook bound to versioned local datasets
The notebook should continue reading repo-local CSV assets instead of downloading live data at runtime. This keeps the analysis reproducible, reviewable in git, and usable without network access. The alternative is to fetch WDI and interest data during notebook execution, but that makes results sensitive to network state and external schema changes.

### Separate data refresh validation from downstream notebook calculations
The implementation should validate country, indicator, and year coverage before the notebook reaches joins and scoring logic. This is necessary because the current workflow can reach empty or partial inputs, especially for wholesale-price and post-2019 interest data. The alternative is to rely on later notebook failures or NaN-heavy outputs, which obscures the real source problem.

### Extend term metadata through 2025, including partial administrations
To satisfy the requested time horizon, the notebook should represent administrations that overlap 2020-2025, including incomplete terms. This preserves chronological coverage for the requested period. The alternative is to stop at the last completed presidency, which would leave the requested years out of scope.

### Resolve the wholesale-price gap explicitly
Because `FP.WPI.TOTL` is not present in the current local WDI extracts, the implementation must either add a vetted source for that series or fail the refresh with a clear message that the notebook cannot claim complete 2025 coverage yet. The alternative is to silently average or rank with missing inflation components, which would make the CMPI output unreliable.

## Risks / Trade-offs

- [2025 publication lag] -> Validate the maximum year per required series and report the exact missing series or year instead of inferring data.
- [Interest source drift after 2019] -> Keep the historical definition documented and compare any new source against the existing file before replacing it.
- [Partial-term comparisons can bias rankings] -> Label post-2019 administrations as partial-period results where applicable.
- [Manual refresh steps can become inconsistent] -> Capture the refresh inputs and transformation sequence alongside the updated data assets.

## Migration Plan

1. Acquire the latest Argentina WDI export and the chosen real-data source for post-2019 interest values.
2. Regenerate the local indicator assets consumed by the notebook and validate required series coverage through 2025.
3. Update notebook bounds, term metadata, and narrative text to include the refreshed years.
4. Recompute notebook outputs and verify that plots and rankings reflect the extended period.
5. If required inputs remain unavailable, stop short of publishing a 2025 CMPI update and retain the previous data files.

## Open Questions (resolved)

- Wholesale-price coverage: resolved with the official INDEC IPIM (`sipm-*.xls`), chained and rebased to 2010 = 100 in `refresh_argentina_indicators.py`.
- Interest series through 2025: resolved with a documented source transition — the historical EMBI-style series is preserved through 2019 and extended from 2020 with the official BCRA external-obligations proxy (`extser.xls`).
- GDP per-capita growth for 2025 (the last remaining gap, since the World Bank API stops at 2024): resolved with a documented INDEC fallback — official annual real GDP (PIB) growth (2025 = +4.4%) converted to a per-capita rate using INDEC's 2022-census mid-year population projections, yielding ≈ +4.21% for 2025. The fallback only fills years missing from the live World Bank API.
- Partial administrations (e.g. Milei 2024-2025): included in the main ranking, with term bounds driven by the latest fully available CMPI year (`DATA_END_YEAR`).
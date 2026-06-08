## Why

The 2025 FPI debt stock ratios (Debt/GDP and Debt/Exports) are NaN in the committed data because final World Bank 2025 nominal GDP and exports have not been published. This blocks full notebook execution for the 2025 analysis window (the FPI NaN audit fails) and leaves Milei's FPI and Overall scores incomplete for the latest year. The project already successfully bridges 2025 CMPI per-capita growth using documented INDEC data; the same pattern should be applied to FPI debt ratios so the entire 1853–2025 framework can run cleanly and consistently.

## What Changes

- Extend the modern debt ratio logic in `scripts/build_fpi_data.py` (Step 2) to compute provisional 2025 `Debt_GDP` and `Debt_Exports` (and the _official variants) using the best available documented official estimates (INDEC nominal accounts + population/exchange data, or Sec. Finanzas/BCRA provisional figures) when World Bank series return no value for 2025.
- Populate the 2025 row in the generated `fpi-fiscal-1853-2025.csv` with these values, plus clear "PROVISIONAL" markers in comments/Source fields and a note that final World Bank numbers will supersede them later (exactly parallel to the existing CMPI 2025 per-capita growth bridge).
- Update `data/argentina/README.md` to document the new provisional FPI logic under the FPI data sources and "Current caveats" sections, with the same transparency and supersession language used for CMPI 2025 growth.
- Re-generate the FPI CSV (via `build_fpi_data.py`) so the notebook's strict FPI NaN audit for 2025 passes and full end-to-end execution (including Milei 2024-25 FPI/Overall) succeeds.
- Minor updates to notebook diagnostics or §11 Limitations if needed to reference the new provisional FPI 2025 data.

No changes to CMPI logic, FPI formula, or historical data.

## Capabilities

### New Capabilities
- `provision-2025-fpi-debt-ratios`: Capability to generate complete, reproducible, and explicitly provisional 2025 Debt/GDP and Debt/Exports ratios for the Fiscal Pressure Index using documented official Argentine sources (INDEC/BCRA/Sec. Finanzas) when final World Bank data is unavailable. Includes clear PROVISIONAL markers, source provenance, and automatic supersession behavior when official WB numbers arrive.

### Modified Capabilities
- `fpi-data-pipeline`: The requirements for producing 2019–2025 FPI debt stock ratios now explicitly include support for provisional 2025 estimates (with the same documentation and fallback standards already required for CMPI 2025 growth data).

## Impact

- `scripts/build_fpi_data.py` (primary logic addition in modern debt step)
- `data/argentina/fiscal/fpi-fiscal-1853-2025.csv` (regenerated with 2025 provisional values)
- `data/argentina/README.md` (documentation updates for sources and caveats)
- `Historical_CMPI_Extension.ipynb` (minor: possible updates to FPI 2025 diagnostics or Limitations section; the core scoring and NaN audit will now succeed for 2025)
- `scripts/adjust_fpi_debt.py` (may need small note if it is used for post-build corrections on 2025 data)
- Enables full notebook re-execution and verified 2025 FPI/Overall results for Milei without changing any index methodology.

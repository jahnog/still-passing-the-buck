## ADDED Requirements

### Requirement: Provisional 2025 debt stock ratios for FPI
The FPI data build pipeline SHALL compute and emit provisional 2025 `Debt_GDP` and `Debt_Exports` (plus the corresponding `_official` columns) when final World Bank `NY.GDP.MKTP.CD` and `BX.GSR.TOTL.CD` values are not yet available, using the best documented official Argentine estimates available at refresh time.

#### Scenario: 2025 WB denominators missing
- **WHEN** `build_fpi_data.py` (or `adjust_fpi_debt.py`) runs for year 2025 and World Bank series return no value for nominal GDP or exports
- **THEN** the script uses documented INDEC nominal accounts / "Informe de avance" data + appropriate exchange rate (or published provisional Debt/PIB ratios from Sec. Finanzas/BCRA) to derive the ratios
- **AND** the emitted values for 2025 are clearly marked PROVISIONAL in code comments, CSV notes, and README
- **AND** a note states that final World Bank numbers will supersede on the next refresh

#### Scenario: Primary result ratios remain from official budget data
- **WHEN** building 2025 FPI data
- **THEN** `Result_Revenue` and `Result_DebtServ` continue to come exclusively from the `datos.gob.ar` budget execution feed (no provisional fallback for these)

### Requirement: Reproducibility and provenance of provisional 2025 FPI data
All provisional 2025 FPI debt ratios SHALL be produced by code in the repository (not hand-edited CSVs) and SHALL carry explicit source, date, and "PROVISIONAL / will be superseded by final WB" provenance so that the generated `fpi-fiscal-1853-2025.csv` remains auditable and the notebook can run a complete 2025 FPI/Overall analysis.

#### Scenario: Regenerating the FPI CSV with 2025 provisionals
- **WHEN** a maintainer runs the documented refresh steps (`build_fpi_data.py` or the lighter adjust path) after the provisional logic is added
- **THEN** the 2025 row in the output CSV contains non-NaN debt ratios with clear provenance
- **AND** the notebook's FPI NaN audit for 2025 now passes
- **AND** Milei (2024-25) receives a complete FPI component score

### Requirement: Documentation parity with CMPI 2025 growth bridge
The provisional 2025 FPI debt ratio logic and data SHALL be documented in `data/argentina/README.md` using the same style, source citation, and supersession language already used for the CMPI 2025 per-capita growth INDEC bridge.

#### Scenario: Reader inspects FPI data lineage for 2025
- **WHEN** a reader consults `data/argentina/README.md` (FPI sources section or Current caveats)
- **THEN** they find an entry for the 2025 provisional debt ratios that is parallel in structure and clarity to the existing CMPI 2025 per-capita growth bullet (including the exact INDEC/BCRA/Sec. Finanzas release or report used and the note that official WB data supersedes it)

### Requirement: No change to index semantics or historical data
The addition of 2025 provisional FPI debt ratios SHALL NOT alter the CMPI formula, FPI innovation/percentile scoring rules, any pre-2025 data, or the meaning of any administration's scores. It only fills the missing 2025 denominators so that the existing methodology can be applied to the full requested window.

#### Scenario: Re-running the full notebook after the change
- **WHEN** the notebook is re-executed (or rendered) with the regenerated FPI CSV
- **THEN** the FPI NaN audit for 2025 passes
- **AND** the numerical CMPI, FPI, and Overall rankings for all terms (including Milei) are produced using exactly the same formulas as before
- **AND** only the 2025 FPI debt components for the latest term are newly populated from the provisional path

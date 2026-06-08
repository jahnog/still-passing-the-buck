## Context

The FPI data pipeline in `scripts/build_fpi_data.py` produces `data/argentina/fiscal/fpi-fiscal-1853-2025.csv`. For 2019–2025 it computes Debt/GDP and Debt/Exports by dividing Secretaría de Finanzas debt (USD) by World Bank nominal GDP (`NY.GDP.MKTP.CD`) and exports (`BX.GSR.TOTL.CD`).

For 2025, World Bank has not yet published final values for those denominators (as explicitly documented in `data/argentina/README.md`: "2025 GDP/exports use official estimates pending final World Bank publication"). This leaves NaNs in the 2025 debt ratios.

Meanwhile, the primary-result ratios for 2025 *are* available from `datos.gob.ar`, and the CMPI side already has a working, documented 2025 provisional bridge for per-capita growth using INDEC real PIB + population projections (with the note that official WB data will supersede later).

The notebook re-uses `DATA_END_YEAR` (driven by CMPI coverage) for the FPI pool. The strict NaN audit in the FPI innovation/scoring code then fails for 2025, blocking full end-to-end execution and leaving Milei's FPI/Overall incomplete.

The goal is to apply the exact same "provisional + documented + supersedable" pattern already proven for CMPI 2025 growth to the FPI debt ratios (options 1 + 5 from the analysis).

## Goals / Non-Goals

**Goals:**
- Make the 2025 FPI debt stock ratios (Debt_GDP, Debt_Exports and their _official variants) computable using the best available official Argentine estimates at refresh time.
- Follow the exact same transparency, sourcing, and "official data will supersede" contract already used for the CMPI 2025 per-capita growth bridge.
- Populate the values with clear PROVISIONAL markers so downstream consumers (notebook, audits, readers) understand the data quality.
- Allow the full notebook (including FPI NaN audit and Milei 2024-25 FPI/Overall) to execute cleanly for the requested 2025 window.
- Keep the change minimal and localized to the modern debt step in the FPI build pipeline + documentation.

**Non-Goals:**
- Do not change CMPI logic, FPI formula, innovation/percentile methodology, or any historical data.
- Do not invent new estimation methodologies; reuse/adapt the existing INDEC + documented fallback pattern.
- Do not remove the strict NaN audit (once provisional data is present the audit will pass).
- Do not make 2025 FPI data "final" — it must remain explicitly provisional.

## Decisions

**Decision: Compute provisional 2025 debt ratios inside Step 2 of build_fpi_data.py (the modern debt block), using the same WB fallback pattern as the CMPI 2025 growth bridge.**

Rationale: The debt ratio calculation already lives right next to the WB `gdp_usd` / `exports_usd` fetches. Adding a documented fallback here keeps all modern FPI debt logic co-located, exactly parallel to how the per-capita growth fallback was added in the indicator refresh + notebook.

Alternatives considered:
- Put the fallback only in `adjust_fpi_debt.py`: rejected because the primary generation path should be complete.
- Hard-code values in the CSV only: rejected — must be reproducible via the build script (like the quasi-fiscal generator).
- Use a completely different source for debt/GDP (e.g. always prefer Sec. Finanzas published ratios): possible future improvement, but for now we stay consistent with the existing "debt from Finanzas ÷ WB/INDEC GDP+exports" formula.

**Decision: Use the best available documented official sources for the 2025 denominators (INDEC nominal accounts + exchange rate, or published provisional Debt/PIB figures from official reports), with explicit source strings.**

Rationale: Matches the CMPI 2025 growth implementation ("INDEC 'Informe de avance...' published 2026-03-20" + population projections + clear supersession note).

**Decision: Write the provisional values into both the adjusted and _official columns, and add provenance in the build output / README.**

For 2025 we can set `Cepo_Factor=1.0` (no cepo distortion assumed or use the same logic as 2024 if available) and `BCRA_QuasiFiscal_GDP=0.0` (already the case).

**Decision: Update data/argentina/README.md in the FPI sources section and the "Current caveats" list, mirroring the exact language style used for the CMPI 2025 growth bridge.**

This makes the provisional nature visible to anyone reading the data lineage.

**Decision: After the code change, the generated CSV + notebook will make the FPI 2025 NaN audit pass without relaxing any checks.**

No behavior change to scoring logic.

## Risks / Trade-offs

- [Provisional data quality] The 2025 GDP/export estimates will be replaced by final World Bank numbers later. Mitigation: identical supersession language and source notes as the existing CMPI 2025 bridge; the build script will automatically use real WB data on next refresh once published.
- [Source selection for 2025 denominators] Multiple possible official numbers (INDEC vs Sec. Finanzas vs BCRA estimates) could exist. Mitigation: document the exact source(s) chosen in the build script comments and README (same discipline as the quasi-fiscal anchors and the CMPI growth bridge). Prefer the same INDEC "Informe de avance" family of releases used for CMPI growth where possible.
- [Debt definition seam for 2025] The 2019+ data already uses broader SPN debt while historical uses central government. The provisional 2025 numbers will follow the same modern convention. Mitigation: already documented in the README "Note on the debt definition seam".
- [Notebook execution for 2025] Once the CSV is regenerated the FPI audit will pass and full render will succeed. No other notebook changes required for the core feature.

## Migration Plan

1. Implement the provisional fallback logic inside the `for year in MODERN_YEARS` debt block in `scripts/build_fpi_data.py` (after the existing WB fetch, before or inside the `modern_debt[year]` assignment for 2025).
2. Add clear comments: "2025 provisional using [exact INDEC/BCRA/SecFinanzas source + date] — will be superseded by final World Bank NY.GDP.MKTP.CD / BX.GSR.TOTL.CD".
3. Run `./.venv/bin/python scripts/build_fpi_data.py` (or the lighter `adjust_fpi_debt.py` path if only patching 2025) to produce the updated CSV.
4. Update the FPI data sources paragraph and the "Current caveats" list in `data/argentina/README.md` (add a bullet parallel to the existing CMPI 2025 per-capita growth bullet).
5. (Optional but recommended) Add a small diagnostic print or table in `Historical_CMPI_Extension.ipynb` §6 when 2025 FPI data is provisional, mirroring the existing CMPI 2025 growth diagnostic.
6. Re-run `scripts/validate_cmpi_inputs.py --target-year 2025` and a full notebook render to confirm the FPI NaN audit now passes and 2025 results are produced.
7. Commit the updated `build_fpi_data.py`, the regenerated CSV, and the README. The change is backward-compatible; older runs without 2025 data remain possible by checking out an earlier CSV if needed.

Rollback: Revert the build script change and restore a previous version of the CSV (the generator for quasi-fiscal and the historical Excel path are unaffected).

## Open Questions

- Exact best source for 2025 nominal GDP in USD and exports in USD at the moment of implementation (INDEC "Informe de avance" + exchange rate vs. any published provisional Debt/PIB ratio from official channels). Will be resolved by inspecting the latest available releases when coding the fallback (document the chosen source the same way the CMPI growth bridge documents its INDEC release date).
- Whether to also provide a provisional 2025 "official" (pre-adjustment) debt ratio or only the final adjusted one. Leaning toward both, for consistency with the existing columns.

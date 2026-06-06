## 1. Refresh source inputs

- [x] 1.1 Audit the latest Argentina WDI export for the CMPI indicator codes and record the maximum published year for each required series.
- [x] 1.2 Select and document the real-data sources needed to extend post-2019 interest coverage and any missing wholesale-price coverage.
- [x] 1.3 Regenerate `Indicators.csv` and `Indicators.csv.gz` in the existing long-form schema with the refreshed Argentina indicator rows.

## 2. Add coverage validation

- [x] 2.1 Add a repeatable validation step that checks the required CMPI series and target-year coverage before notebook calculations run.
- [x] 2.2 Make the validation report the exact missing series or year and block silent claims of completed 2025 coverage when inputs are incomplete.

## 3. Extend notebook analysis

- [x] 3.1 Update `Still_Passing_the_Buck.ipynb` data-loading references, year bounds, and narrative text to reflect the refreshed analysis window.
- [x] 3.2 Extend administration metadata and output logic so post-2019 presidencies appear in the notebook's plots, tables, and ranking summaries.

## 4. Verify and document results

- [x] 4.1 Recompute the notebook with the refreshed local datasets and verify that outputs no longer stop at 2019.
- [x] 4.2 Document the lineage and refresh steps for each updated local dataset, including any remaining caveats for partial 2025 coverage.
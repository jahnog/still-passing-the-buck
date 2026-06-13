# CMPI data layout

## Folders

| Folder | Purpose |
|--------|---------|
| `data/raw/<provider>/` | Downloaded source files (`<source>_<file>_<from>_<to>.<ext>`) |
| `data/processed/<purpose>/` | Generated notebook inputs (`converted_<purpose>_<input>_<from>_<to>.csv`) |
| `data/provided/` | Curated exceptions: `Indicators.csv*`, `WDIData2.csv`, `data_a_2018.xlsx`, `alt-cpi-2007-2015.csv`, `data-quality-flags.csv`, `fiscal-default-adjustments.csv`, `fiscal-one-offs.csv`, `official-vs-revised-gdp-2005-2015.csv` |

Curated CSVs carry per-row `Source`/`Note` provenance; generated CSVs get a `.meta.json`
sidecar (generator, sources, timestamp — `scripts/data_io.write_meta_sidecar`). Data revisions
and baseline-affecting changes are logged in [`data/REVISIONS.md`](REVISIONS.md).

## Download scripts (`scripts/download_<provider>_<source>_<file>.py`)

One script per provider-external-file combination. Each writes to `data/raw/` using atomic temp-then-move.

| Script | Output |
|--------|--------|
| `download_worldbank_wdi_wdi-csv.py` | `raw/worldbank/wdi_wdi-csv_*.zip` |
| `download_worldbank_api_indicators-arg.py` | `raw/worldbank/api_*.json` (one per indicator) |
| `download_indec_economia_serie-ipc-divisiones.py` | INDEC IPC CSV |
| `download_indec_economia_sipm-serie56-95.py` | INDEC IPIM 1956-95 |
| `download_indec_economia_sipm-dde1996.py` | INDEC IPIM 1996+ |
| `download_indec_economia_series-sipm-dic2015.py` | INDEC IPIM reference |
| `download_indec_poblacion_proyecciones-nacionales-2022-2040.py` | INDEC population |
| `download_bcra_publicaciones_com3500.py` | BCRA exchange workbook |
| `download_bcra_api-monetarias.py` | `raw/bcra/api_monetarias-*.json` — Estadísticas Monetarias v4 API: monthly historical inflation (series 27, 1943→) and the remunerated-liability daily stocks (1258/1259/1260/1262, plus 196 LEFI as a cross-check) |
| `download_bcrp_estadisticas_pd04710xd.py` | BCRP EMBIG JSON |
| `download_argentinadatos_api_cotizaciones-ccl.py` | CCL quotes JSON |
| `download_argentinadatos_api_cotizaciones-blue.py` | Blue quotes JSON |
| `download_finanzas_deuda_deuda-publica.py` | Annual debt xlsx (2019+) |
| `download_mecon_datasets_totales-de-presupuesto.py` | Budget zip |
| `download_finanzas_sector-publico_sector-publico-base-caja.py` | IMIG workbook |
| `download_github_still-passing-the-buck_data-a-2018.py` | `provided/data_a_2018.xlsx` |

## Upload script

`upload_s3_notebook-data.py` (`make upload`) syncs everything the notebook reads — the
data files above, their `.meta.json` sidecars, `assets/portraits/*.jpg`, and the two
helper modules — to the public S3 mirror used by Colab/standalone runs
(`https://jnpublicdata.s3.us-east-1.amazonaws.com/still-passing-the-buck/`). AWS
credentials come from the OS keyring (service `stillpassingthebuck`, see `.env.example`);
unchanged files are skipped via ETag comparison.

## Generate scripts (`scripts/generate_<purpose>_<input>.py`)

| Script | Output |
|--------|--------|
| `generate_indicators_wdi-argentina.py` | `provided/Indicators.csv` + `.gz` |
| `generate_interest_wb-ids-arg.py` | `processed/interest/converted_interest_wb-ids-arg_*.csv` — **reads its own output** for the 1958–1997 legacy rows (paper term averages; primary data, not regenerable from any download — never delete the committed CSV) |
| `generate_exchange_parallel-cepo.py` | `processed/exchange/converted_exchange_parallel-cepo_*.csv` |
| `generate_exchange_paper-devaluation.py` | `processed/exchange/converted_exchange_paper-devaluation_*.csv` |
| `generate_exchange_bcra-dec-dec.py` | `processed/exchange/converted_exchange_bcra-dec-dec_*.csv` |
| `generate_exchange_dec-dec-modern.py` | `processed/exchange/converted_exchange_dec-dec_1999-01_2025-12.csv` — December-quotation devaluation for 2000–2025 (December TCNPM from the BCRA com3500 raw on free years; December CCL/blue daily averages on cepo years; Convertibility 1:1 for 1999–2001). Extends the paper's December convention to the full sample |
| `generate_historical_historical-cmpi.py` | `processed/historical/converted_historical_historical-cmpi_*.csv` |
| `generate_historical_data-a-2018-excel.py` | `processed/historical/converted_historical_data-a-2018-excel_*.csv` (from `provided/data_a_2018.xlsx`) |
| `generate_inflation_bcra-monthly.py` | `processed/inflation/converted_inflation_cpi-wpi-blend_*.csv` — Dec/Dec annual CPI (BCRA API series 27), IPIM (INDEC SIPM workbooks) and their blend; feeds the §9 reproducible-CPI sensitivity variant only |
| `generate_fiscal_bcra-quasi-fiscal.py` | `processed/fiscal/converted_fiscal_bcra-quasi-fiscal_*.csv` — remunerated-liability stock (consolidated into the FPI): measured BCRA-API December year-end stocks for 2002–2024 (series 1258+1260+1262, plus 1259 through 2017), curated anchors as offline fallback and printed cross-check; plus the nominal quasi-fiscal interest flow (documented, notebook §6.0 E) and the importer-arrears/BOPREAL series for the paired sensitivity |
| `generate_fiscal_fpi-fiscal.py` | `processed/fiscal/converted_fiscal_fpi-fiscal_*.csv` — 2019–2025 primary-result ratios follow the **Sector Público Nacional base-caja** concept (Hacienda/OPC; curated `KNOWN_FISCAL`, provenance note in the script). The datos.gob.ar AN-devengado zip is parsed at generation time only as a cross-reference and upstream-revision tripwire (different concept: its revenues include BCRA/FGS rents). Emits the §6.0 C–E sensitivity memo columns (`Debt_GDP_holdouts`, `Result_DebtServ_accrual`, `Result_Revenue_structural`, `Debt_GDP_arrears`, `DefaultFlag`) from the curated files in `data/provided/`. The §6.0 cepo factor needs the official FX rate (raw `PA.NUS.FCRF` + BCRA-supplemented `PA.NUS.ATLS`) and **fails loudly** if a cepo year lacks one |
| `generate_fiscal_fpi-debt-adjustments.py` | Re-applies debt corrections to FPI CSV |

## Refresh order

1. Run all `download_*.py` scripts (network required).
2. `generate_indicators_wdi-argentina.py` (needs `data/provided/WDIData2.csv` + raw INDEC/BCRA/WB files).
3. `generate_interest_wb-ids-arg.py`, `generate_exchange_parallel-cepo.py`.
4. `generate_inflation_bcra-monthly.py`, `generate_fiscal_bcra-quasi-fiscal.py`, `generate_fiscal_fpi-fiscal.py` (or `generate_fiscal_fpi-debt-adjustments.py` for corrections only).
5. `generate_exchange_paper-devaluation.py`, `generate_historical_historical-cmpi.py`, `generate_exchange_bcra-dec-dec.py`, `generate_exchange_dec-dec-modern.py`.
6. `./.venv/bin/python scripts/validate_cmpi_inputs.py --target-year 2025` — also audits
   `data/provided/data-quality-flags.csv` (full grade coverage for every ranked year) and warns
   when a grade-D (provisional) cell can be superseded by a published World Bank year.

Path constants for notebooks and validators live in `data/paths.py`.

Legacy lineage notes remain in `data/argentina/README.md`.

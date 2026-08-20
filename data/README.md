# CMPI data layout

## Folders

| Folder | Purpose |
|--------|---------|
| `data/raw/<provider>/` | Downloaded source files (`<source>_<file>_<from>_<to>.<ext>`) |
| `data/processed/<purpose>/` | Generated notebook inputs (`converted_<purpose>_<input>_<from>_<to>.csv`) |
| `data/provided/` | Curated inputs that are not regenerated from downloads: `data_a_1999.xlsx`, `data-quality-flags.csv`, `correction-taxonomy.csv`, `official-fiscal-correction-operands.csv`, `fiscal-default-adjustments.csv`, `official-vs-revised-gdp-2005-2015.csv`, `bcra-quasi-fiscal-anchors.csv`, `bcra-quasi-fiscal-historical.csv`, `ipcba-vs-indec.csv`, `parallel-fx-historical.csv`, `restructuring-2005-sensitivity.csv` |

Downloaded and generated files carry `.meta.json` sidecars. For headline corrections,
`data/processed/provenance/converted_provenance_source-registry.csv` records the exact official URL, retained artifact, retrieval date,
byte size, and SHA-256; `converted_provenance_row-source-links.csv` joins each generated row to its source
locator, extraction formula, evidence class, and uncertainty statement. A URL by itself is not
sufficient. Baseline-affecting construction is documented in this file and in
[`data/argentina/README.md`](argentina/README.md). Hashes live in
`data/processed/checksums.json` and `data/file-manifest.json`.

## Pipeline year (`TARGET_YEAR`)

The analysis horizon is centralized in `scripts/pipeline_config.py`. Set it via environment
variable `CMPI_TARGET_YEAR` or `TARGET_YEAR`, or pass `--target-year` to validators:

```bash
make validate TARGET_YEAR=2026
CMPI_TARGET_YEAR=2026 uv run python scripts/validate_cmpi_inputs.py
```

Download scripts that name raw files with an end date call `pipeline_config.date_to()` (December
of the target year). Exceptions: SIPM 1956–95 (`1995-12`), BCRA monetarias API
(`target_year + 1` so monthly series stay current), and BCRP EMBIG (dynamic through today).

## Download targets

| Make target | Scope |
|-------------|--------|
| `make download-data` | Statistical raw files (`scripts/download_*.py` except portraits), then retain the current file and the immediately preceding copy |
| `make download-assets` | President/minister portraits (`download_presidency_portraits.py`) |
| `make download` | Both (full network refresh) |
| `make cleanup-raw` | Keep only the last two copies of each rotated raw dest (`scripts/cleanup_raw_downloads.py`) |

JSON downloads from the World Bank indicator API, BCRA monetarias API, and argentinadatos
cotizaciones endpoints are structurally validated in-script (`scripts/download_schemas.py`;
offline fixtures in `tests/test_download_schemas.py`).

## Download scripts (`scripts/download_<provider>_<source>_<file>.py`)

One script per provider-external-file combination. Each writes to `data/raw/` using atomic temp-then-move. If the dest already exists, it is renamed to the next free `<stem>_N.<ext>` before the new file is written. `scripts/cleanup_raw_downloads.py` (`make cleanup-raw`, also run at the end of `make download-data`) keeps only the live dest plus the newest previous copy and deletes older rotated copies. Pinned official reports that are never overwritten are left alone; year tokens such as `imig-anual_2017.xlsx` are not treated as rotation generations.

| Script | Output |
|--------|--------|
| `download_worldbank_wdi_wdi-csv.py` | `raw/worldbank/wdi_wdi-csv_*.zip` |
| `download_worldbank_api_indicators-arg.py` | `raw/worldbank/api_*.json` (one per indicator) |
| `download_indec_economia_serie-ipc-divisiones.py` | INDEC IPC CSV |
| `download_indec_economia_sipm-serie56-95.py` | INDEC IPIM 1956-95 |
| `download_indec_economia_sipm-dde1996.py` | INDEC IPIM 1996+ |
| `download_indec_economia_series-sipm-dic2015.py` | INDEC IPIM reference |
| `download_bcra_publicaciones_com3500.py` | BCRA exchange workbook |
| `download_bcra_api-monetarias.py` | `raw/bcra/api_monetarias-*.json` — Estadísticas Monetarias v4 API: monthly historical inflation (series 27, 1943→) and the remunerated-liability daily stocks (1258/1259/1260/1262, plus 196 LEFI as a cross-check) |
| `download_bcra_importer-debt-bopreal.py` | Current BCRA private-external-debt workbook plus the pinned audited 2025 financial-statements PDF containing comparative 2024–2025 BOPREAL residual values |
| `download_bcrp_estadisticas_pd04710xd.py` | BCRP EMBIG JSON |
| `download_argentinadatos_api_cotizaciones-ccl.py` | CCL quotes JSON |
| `download_argentinadatos_api_cotizaciones-blue.py` | Blue quotes JSON |
| `download_finanzas_deuda_deuda-publica.py` | Secretaría de Finanzas year-end debt workbooks (2019–current) used for the A.2.5 Sector Público Nacional gross-debt stock |
| `download_mecon_datasets_totales-de-presupuesto.py` | Budget zip |
| `download_hacienda_spn-base-caja-historical.py` | Hacienda dataset-379 SPN base-caja CSVs (1993–2025) plus IMIG 2017/2018 validation workbooks |
| `download_fed_h15-tips10y.py` | Fed H.15 annual 10y TIPS yield via DBnomics (`raw/fed/h15_tips10y-annual_*.json`) — updates `processed/interest/converted_interest_us-real-yield-10y_*.csv` 2003+ measured rows |
| `download_bcra_fiscal-annual-reports.py` | Pinned BCRA reports containing measured FGS property income and booked BCRA transfers |
| `download_afip_arca_fiscal-reports.py` | Pinned AFIP/ARCA reports containing exact 2016–2017 and measured 2024 regularization receipts |
| `download_opc_fiscal-reports.py` | Pinned OPC budget/debt-operation reports for the 2021 SDR booking and 2024–2025 capitalized interest |
| `download_official_provincial-cpi.py` | Pinned Santa Fe IPEC, CABA DGEYC, and San Luis DPEyC CPI artifacts |
| `download_presidency_portraits.py` | **`make download-assets` only** — resizes Wikimedia portraits to `assets/portraits/*.jpg` |

### Hacienda fiscal actuals

The modern baseline derives every 2000–2025 SPN **base-caja** primary-result ratio from
datos.gob.ar dataset 379. Distribution 379.3 supplies 2015–2025 at a stable official URL and is
committed with a hash-pinned sidecar. The generator retains current revenue, primary result,
financial result, and net interest before calculating the two FPI ratios.

`data/provided/data_a_1999.xlsx` is a committed paper-author workbook, not a
network-refreshed official source. Validate its bounds with
`scripts/validate_data_a_1999.py`; all 2000+ observations are sourced from the
provider downloads above and the fiscal/debt generators below.

### Official correction sources

The complete URL-and-hash inventory is `data/processed/provenance/converted_provenance_source-registry.csv`.
Key exact URLs are:

- Hacienda dataset 379.1/379.2/379.3:
  `https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.1/download/sector-publico-nacional-valores-anuales-93-06.csv`,
  `https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.2/download/sector-publico-nacional-valores-anuales-07-14.csv`,
  and
  `https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.3/download/sector-publico-nacional-valores-anuales-17.csv`.
- BCRA annual reports, beginning with
  `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/inf2009.pdf`;
  the registry lists the exact 2010–2015 URLs and hashes separately.
- BCRA paired importer-debt/BOPREAL operands:
  `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/ANEXODEUDAPRIVADA_6401.xlsx`
  and
  `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/estados-contables-2025.pdf`.
- AFIP/ARCA fiscal reports:
  `https://contenidos.afip.gob.ar/institucional/estudios/archivos/informe.4.trimestre.2017.pdf`,
  `https://www.afip.gob.ar/institucional/documentos/ARCA-Recaudacion-ANUAL2024.pdf`, and
  `https://www.arca.gob.ar/institucional/documentos/recaudacion-tributaria-112024.pdf`.
- OPC:
  `https://opc.gob.ar/download/19142/` for the 2021 SDR booking,
  `https://opc.gob.ar/download/40009/?tmstv=1738608772` for 2024 capitalized
  interest, and the twelve exact 2025 monthly URLs listed in the registry.
- Official local CPI:
  `https://www.santafe.gov.ar/index.php/web/content/download/109537/540514/file/cIndice%20Pcia%202005-2013.xls`,
  `https://www.santafe.gov.ar/index.php/web/content/download/243468/1282154/version/2/file/1217.pdf`,
  `https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2022/02/Evol_gral_bs_svcios.xlsx`,
  and
  `https://estadistica.sanluis.gov.ar/documents/Economia/Precios/IPC%20San%20Luis/lbycc1cu.pdf`.

The 2007–2015 headline CPI is the continuous Santa Fe IPEC
December-to-December chain. CABA and San Luis are official-local sensitivity
columns only where their pinned files overlap; they are not averaged into the
headline.

## Upload script

`upload_s3_notebook-data.py` (`make upload`) syncs everything the notebook reads — the
data files above, their `.meta.json` sidecars, `assets/portraits/*.jpg`,
`scripts/cmpi_core.py`, `scripts/presidency_portraits.py`, and `pyproject.toml` — to the public S3 mirror used by Colab/standalone runs
(`https://jnpublicdata.s3.us-east-1.amazonaws.com/still-passing-the-buck/`). AWS
credentials come from the OS keyring (service `stillpassingthebuck`, see `.env.example`);
unchanged files are skipped via ETag comparison.

## Generate scripts (`scripts/generate_<purpose>_<input>.py`)

| Script | Output |
|--------|--------|
| `generate_indicators_wdi-argentina.py` | `processed/indicators/converted_indicators_wdi-argentina_*.csv` + `.gz` — Argentina rows from the WDI bulk zip, overlaid with World Bank API JSON, INDEC IPC/IPIM, and BCRA com3500 |
| `generate_interest_wb-ids-arg.py` | `processed/interest/converted_interest_wb-ids-arg_*.csv` — the 1958–1997 rows are paper term averages (primary data, not regenerable from downloads); the generator reads its own output for those rows |
| `generate_interest_us-real-yield-10y.py` | `processed/interest/converted_interest_us-real-yield-10y_*.csv` — retains 1998–2002 seam estimates; regenerates 2003–2025 from the retained Fed H.15 annual JSON (complete 2025 required) |
| `generate_exchange_parallel-cepo.py` | `processed/exchange/converted_exchange_parallel-cepo_*.csv` |
| `generate_exchange_paper-devaluation.py` | `processed/exchange/converted_exchange_paper-devaluation_*.csv` |
| `generate_exchange_dec-dec-modern.py` | `processed/exchange/converted_exchange_dec-dec_1999-01_2025-12.csv` — December quotations for 2000–2025 (TCNPM on free years; CCL/blue on cepo years; Convertibility 1:1 for 1999–2001) |
| `generate_historical_historical-cmpi.py` | `processed/historical/converted_historical_historical-cmpi_*.csv` |
| `generate_historical_data-a-1999-excel.py` | `processed/historical/converted_historical_data-a-1999-excel_*.csv` (from `provided/data_a_1999.xlsx`, cols D–F, 1853–1963) |
| `generate_inflation_bcra-monthly.py` | `processed/inflation/converted_inflation_cpi-wpi-blend_*.csv` — Dec/Dec CPI (BCRA series 27), IPIM, and blend; notebook §9 sensitivity only |
| `generate_inflation_official-provincial-cpi.py` | `processed/inflation/converted_inflation_official-provincial-cpi_*.csv` — Santa Fe IPEC headline chain plus official CABA/San Luis overlap variants |
| `generate_fiscal_bcra-importer-debt-bopreal.py` | `processed/fiscal/converted_fiscal_bcra-importer-debt-bopreal_2022-01_2025-12.csv` |
| `generate_fiscal_bcra-quasi-fiscal.py` | `processed/fiscal/converted_fiscal_bcra-quasi-fiscal_*.csv` — December year-end remunerated-liability stocks (BCRA API) with curated anchors as fallback |
| `generate_fiscal_official-corrections.py` | `processed/fiscal/converted_fiscal_official-one-offs_*.csv` and `converted_fiscal_official-capitalized-interest_*.csv` |
| `generate_official_provenance-registry.py` | `processed/provenance/converted_provenance_source-registry.csv` and `converted_provenance_row-source-links.csv` |
| `generate_fiscal_fpi-fiscal.py` | `processed/fiscal/converted_fiscal_fpi-fiscal_*.csv` — 1853–2025 FPI operands and corrected headline columns. 1861–63 primary-result ratios are interpolated; all 2000–2025 primary-result ratios are parsed from dataset 379 |
| `generate_fiscal_fpi-debt-adjustments.py` | Re-applies debt corrections to the FPI CSV |
| `generate_fiscal_denominator-neutral.py` | `processed/fiscal/converted_fiscal_denominator-neutral_1960-01_2025-12.csv` — US$ price deflators (2003 = 1.000) for FPI debt-ratio denominators. Sensitivity input only (notebook §9.8) |

## Checksums

`data/processed/checksums.json` records SHA-256 hashes of every processed CSV plus
`converted_indicators_wdi-argentina_*.csv.gz`. After intentional generator changes:

```bash
make generate
uv run python scripts/update_processed_checksums.py
```

`make verify` and `tests/test_generate_regression.py` run `make generate` offline and fail when
outputs diverge from the manifest.

## Refresh order

1. `make download-data` (and `make download-assets` if portraits need refreshing).
2. `generate_indicators_wdi-argentina.py` (needs the WDI bulk zip + raw INDEC/BCRA/WB API files).
3. `generate_interest_wb-ids-arg.py`, `generate_interest_us-real-yield-10y.py`,
   `generate_exchange_parallel-cepo.py`.
4. Generate the BCRA blend and official provincial CPI, then run
   `generate_fiscal_bcra-quasi-fiscal.py`, `generate_fiscal_official-corrections.py`,
   `generate_fiscal_fpi-fiscal.py`,
   and `generate_official_provenance-registry.py`.
5. `generate_exchange_paper-devaluation.py`, `generate_historical_historical-cmpi.py`, `generate_exchange_dec-dec-modern.py`.
6. `make validate` (or `uv run python scripts/validate_cmpi_inputs.py --target-year 2025`) — validates that the
   paper-author workbook stops at 1999, audits `data/provided/data-quality-flags.csv` (full grade
   coverage for every ranked year), and warns when a grade-D (provisional) cell can be superseded by
   a published World Bank year.
7. `./.venv/bin/python scripts/validate_provenance.py` — validates the correction taxonomy and the
   expanded fiscal actuals provenance schema.
8. After intentional data or generated-paper changes, run
   `./.venv/bin/python scripts/write_data_manifest.py`; use
   `./.venv/bin/python scripts/verify_data_manifest.py` to check the recorded SHA256 hashes.

Path constants for notebooks and validators live in `data/paths.py`.

Series lineage is in `data/argentina/README.md`.

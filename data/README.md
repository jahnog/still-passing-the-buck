# CMPI data layout

## Folders

| Folder | Purpose |
|--------|---------|
| `data/raw/<provider>/` | Downloaded source files (`<source>_<file>_<from>_<to>.<ext>`) |
| `data/processed/<purpose>/` | Generated notebook inputs (`converted_<purpose>_<input>_<from>_<to>.csv`) |
| `data/provided/` | Curated exceptions: `Indicators.csv*`, `data_a_2018.xlsx`, `alt-cpi-2007-2015.csv` |

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
| `download_bcrp_estadisticas_pd04710xd.py` | BCRP EMBIG JSON |
| `download_argentinadatos_api_cotizaciones-ccl.py` | CCL quotes JSON |
| `download_argentinadatos_api_cotizaciones-blue.py` | Blue quotes JSON |
| `download_finanzas_deuda_deuda-publica.py` | Annual debt xlsx (2019+) |
| `download_mecon_datasets_totales-de-presupuesto.py` | Budget zip |
| `download_finanzas_sector-publico_sector-publico-base-caja.py` | IMIG workbook |
| `download_github_still-passing-the-buck_data-a-2018.py` | `provided/data_a_2018.xlsx` |

## Generate scripts (`scripts/generate_<purpose>_<input>.py`)

| Script | Output |
|--------|--------|
| `generate_indicators_wdi-argentina.py` | `provided/Indicators.csv` + `.gz` |
| `generate_interest_wb-ids-arg.py` | `processed/interest/converted_interest_wb-ids-arg_*.csv` — **reads its own output** for the 1958–1997 legacy rows (paper term averages; primary data, not regenerable from any download — never delete the committed CSV) |
| `generate_exchange_parallel-cepo.py` | `processed/exchange/converted_exchange_parallel-cepo_*.csv` |
| `generate_exchange_paper-devaluation.py` | `processed/exchange/converted_exchange_paper-devaluation_*.csv` |
| `generate_exchange_bcra-dec-dec.py` | `processed/exchange/converted_exchange_bcra-dec-dec_*.csv` |
| `generate_historical_historical-cmpi.py` | `processed/historical/converted_historical_historical-cmpi_*.csv` |
| `generate_historical_data-a-2018-excel.py` | `processed/historical/converted_historical_data-a-2018-excel_*.csv` (from `provided/data_a_2018.xlsx`) |
| `generate_fiscal_bcra-quasi-fiscal.py` | `processed/fiscal/converted_fiscal_bcra-quasi-fiscal_*.csv` |
| `generate_fiscal_fpi-fiscal.py` | `processed/fiscal/converted_fiscal_fpi-fiscal_*.csv` — 2019–2025 primary-result ratios are manually transcribed from datos.gob.ar budget execution (documented in the script). The §6.0 cepo factor needs the official FX rate (raw `PA.NUS.FCRF` + BCRA-supplemented `PA.NUS.ATLS`) and **fails loudly** if a cepo year lacks one |
| `generate_fiscal_fpi-debt-adjustments.py` | Re-applies debt corrections to FPI CSV |

## Refresh order

1. Run all `download_*.py` scripts (network required).
2. `generate_indicators_wdi-argentina.py` (needs `WDIData2.csv` at repo root + raw INDEC/BCRA/WB files).
3. `generate_interest_wb-ids-arg.py`, `generate_exchange_parallel-cepo.py`.
4. `generate_fiscal_bcra-quasi-fiscal.py`, `generate_fiscal_fpi-fiscal.py` (or `generate_fiscal_fpi-debt-adjustments.py` for corrections only).
5. `generate_exchange_paper-devaluation.py`, `generate_historical_historical-cmpi.py`, `generate_exchange_bcra-dec-dec.py`.
6. `./.venv/bin/python scripts/validate_cmpi_inputs.py --target-year 2025`

Path constants for notebooks and validators live in `data/paths.py`.

Legacy lineage notes remain in `data/argentina/README.md`.

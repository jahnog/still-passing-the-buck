## 1. Infrastructure

- [x] 1.1 Add `scripts/data_io.py` with `atomic_download`, `raw_path`, `processed_path`, and `rotate_existing` helpers
- [x] 1.2 Create `data/raw/`, `data/processed/`, and `data/provided/` directory scaffolding
- [x] 1.3 Add `data/paths.py` centralising notebook/validator paths to processed and provided files
- [x] 1.4 `git mv` `Indicators.csv`, `Indicators.csv.gz`, and `data/argentina/historical/data_a_2018.xlsx` into `data/provided/`

## 2. Download scripts — World Bank & INDEC

- [x] 2.1 Implement `download_worldbank_wdi_wdi-csv.py` (bulk WDI zip → `data/raw/worldbank/`)
- [x] 2.2 Implement `download_worldbank_api_indicators-arg.py` (single script for all required WB indicator codes; one dated JSON raw file per code fetched)
- [x] 2.3 Implement INDEC download scripts: `serie-ipc-divisiones`, `sipm-serie56-95`, `sipm-dde1996`, `series-sipm-dic2015`, `proyecciones-nacionales-2022-2040`

## 3. Download scripts — BCRA, BCRP, Argentinadatos, Finanzas

- [x] 3.1 Implement `download_bcra_publicaciones_com3500.py`
- [x] 3.2 Implement `download_bcrp_estadisticas_pd04710xd.py`
- [x] 3.3 Implement `download_argentinadatos_api_cotizaciones-ccl.py` and `download_argentinadatos_api_cotizaciones-blue.py`
- [x] 3.4 Implement `download_finanzas_deuda_deuda-publica.py` (one script for the `deuda_publica_31-12-{year}.xlsx` pattern; writes one dated raw file per year)
- [x] 3.5 Implement `download_mecon_datasets_totales-de-presupuesto.py` and `download_finanzas_sector-publico_sector-publico-base-caja.py`
- [x] 3.6 Implement optional `download_github_still-passing-the-buck_data-a-2018.py` targeting `data/provided/data_a_2018.xlsx`

## 4. Generate scripts — indicators, interest, exchange

- [x] 4.1 Port `refresh_argentina_indicators.py` logic to `generate_indicators_wdi-argentina.py`; write `data/provided/Indicators.csv` + `.gz`
- [x] 4.2 Port `refresh_argentina_interest.py` to `generate_interest_wb-ids-arg.py` → `data/processed/interest/converted_interest_wb-ids-arg_<dates>.csv`
- [x] 4.3 Port `refresh_argentina_exchange.py` to `generate_exchange_parallel-cepo.py` → `data/processed/exchange/converted_exchange_parallel-cepo_<dates>.csv`
- [x] 4.4 Port `_gen_paper_devaluation.py` to `generate_exchange_paper-devaluation.py` (read `data/provided/data_a_2018.xlsx`)
- [x] 4.5 Port `_gen_historical_cmpi.py` to `generate_historical_historical-cmpi.py`
- [x] 4.6 Port `build_bcra_dec_dec.py` to `generate_exchange_bcra-dec-dec.py`

## 5. Generate scripts — fiscal / FPI

- [x] 5.1 Port `_gen_bcra_quasi_fiscal.py` to `generate_fiscal_bcra-quasi-fiscal.py`
- [x] 5.2 Port `build_fpi_data.py` download logic removal and transformation to `generate_fiscal_fpi-fiscal.py` (reads raw finanzas/mecon/WB + provided Excel)
- [x] 5.3 Port `adjust_fpi_debt.py` to `generate_fiscal_fpi-debt-adjustments.py`

## 6. Consumers, docs, and cleanup

- [x] 6.1 Update `scripts/validate_cmpi_inputs.py` to use `data/paths.py` / new processed and provided locations
- [x] 6.2 Update `Historical_CMPI_Extension.ipynb` path constants and hard-coded reads to new layout
- [x] 6.3 Move `alt-cpi-2007-2015.csv` to `data/provided/` and update references
- [x] 6.4 Update `data/argentina/README.md` (or add `data/README.md`) with download/generate inventory and refresh order
- [x] 6.5 Update `tests/test_data_downloads.py` and any path-dependent tests
- [x] 6.6 Remove deprecated scripts (`refresh_argentina_*.py`, `build_fpi_data.py`, `adjust_fpi_debt.py`, `_gen_*.py`, `build_bcra_dec_dec.py`) after parity validation
- [x] 6.7 Run full refresh + `validate_cmpi_inputs.py --target-year 2025` to confirm notebook inputs unchanged in substance

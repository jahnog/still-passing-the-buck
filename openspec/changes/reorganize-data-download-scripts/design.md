## Context

`Historical_CMPI_Extension.ipynb` consumes a dozen local CSV/XLSX assets. Today, three monolithic refresh scripts (`refresh_argentina_indicators.py`, `refresh_argentina_interest.py`, `refresh_argentina_exchange.py`) and `build_fpi_data.py` interleave HTTP fetches with parsing, merging, and writing notebook inputs. Raw inputs (`WDIData2.csv`, `Indicators.csv*`) sit at the repo root; processed outputs live under ad hoc `data/argentina/<topic>/` paths. The notebook also references GitHub raw URLs for offline bootstrap.

The reorganisation standardises layout into `data/raw/<provider>/`, `data/processed/<purpose>/`, and `data/provided/` with strict script naming, dated filenames, atomic downloads, and collision policies.

## Goals / Non-Goals

**Goals:**

- One `download_<provider>_<data-source>_<data-file>.py` per **provider-external-file** combination (period bounds live in output filenames, not script names).
- When one external file bundles multiple series, one downloader covers that external file (series splitting belongs in `generate_*`).
- When one external file pattern recurs across periods (Finanzas annual debt), one downloader writes multiple dated raw outputs.
- One `generate_<purpose>_<input-data-file>.py` per notebook input derived from raw/provided sources.
- Shared utilities for temp-download, dated naming, raw collision rename (`_1`, `_2`, …), and processed overwrite.
- Migrate `Indicators.csv`, `Indicators.csv.gz`, and `data_a_2018.xlsx` to `data/provided/`.
- Update notebook, validator, tests, and README to new paths.
- Preserve existing data semantics (INDEC fallbacks, EMBIG splice, cepo FX, FPI corrections).

**Non-Goals:**

- Changing CMPI formulas, scoring logic, or notebook analysis methodology.
- Automating download of curated `alt-cpi-2007-2015.csv` (remains manually maintained).
- Rewriting `cmpi_core.py` or paper-rendering tooling beyond path updates.
- Live notebook downloads at runtime (notebook continues to read repo-local files).

## Decisions

### 1. Shared module `scripts/data_io.py`

Centralise:

- `atomic_download(url, dest_path, …)` — write `dest_path.tmp.<pid>`, validate size/checksum if applicable, rotate existing file on collision, then `os.replace` to final name.
- `raw_path(provider, data_source, data_file, date_from, date_to, ext)` — builds `data/raw/<provider>/…` filename.
- `processed_path(purpose, input_token, date_from, date_to)` — builds `data/processed/<purpose>/converted_…csv`.
- `rotate_existing(path)` — renames `file.ext` → `file_1.ext`, `file_1.ext` → `file_2.ext`, etc.

**Alternative considered:** duplicate 20 lines per script. Rejected — collision and atomic semantics must be identical everywhere.

### 2. Download script granularity

**Rule:** one script per **provider-external-file combination**. The external file is the remote resource (URL path or API endpoint), not an individual time slice or data series inside it.

- A file containing multiple series (INDEC IPC divisions, BCRA com3500, argentinadatos quote feeds) → **one script**.
- A recurring file pattern that differs only by year in the URL (Finanzas `deuda_publica_31-12-{year}.xlsx`) → **one script** that loops applicable years and writes one dated raw file per fetch.
- Distinct external resources from the same provider (INDEC IPC CSV vs three SIPM workbooks vs population projections) → **separate scripts** because each is a different external file.

Period bounds (`date-from`, `date-to`) are embedded in each **output** raw filename, not in the script name.

### 3. Download inventory (split from current monoliths)

| New script | Provider | External file | Raw output(s) |
|---|---|---|---|
| `download_worldbank_wdi_wdi-csv.py` | `worldbank` | WDI bulk ZIP | `wdi_wdi-csv_<dates>.zip` |
| `download_worldbank_api_indicators-arg.py` | `worldbank` | WB country/indicator API (all CMPI + FPI codes) | one JSON per indicator code fetched, each dated |
| `download_indec_economia_serie-ipc-divisiones.py` | `indec` | INDEC FTP IPC CSV | `economia_serie-ipc-divisiones_<dates>.csv` |
| `download_indec_economia_sipm-serie56-95.py` | `indec` | INDEC SIPM xls (1956–95) | … |
| `download_indec_economia_sipm-dde1996.py` | `indec` | INDEC SIPM xls (1996+) | … |
| `download_indec_economia_series-sipm-dic2015.py` | `indec` | INDEC SIPM reference xls | … |
| `download_indec_poblacion_proyecciones-nacionales-2022-2040.py` | `indec` | INDEC population CSV | … |
| `download_bcra_publicaciones_com3500.py` | `bcra` | BCRA com3500.xls | … |
| `download_bcrp_estadisticas_pd04710xd.py` | `bcrp` | BCRP EMBIG JSON API | … |
| `download_argentinadatos_api_cotizaciones-ccl.py` | `argentinadatos` | CCL API | … |
| `download_argentinadatos_api_cotizaciones-blue.py` | `argentinadatos` | blue API | … |
| `download_finanzas_deuda_deuda-publica.py` | `finanzas` | `deuda_publica_31-12-{year}.xlsx` pattern | one raw xlsx per year (2019–2025+) |
| `download_mecon_datasets_totales-de-presupuesto.py` | `mecon` | budget execution zip | … |
| `download_finanzas_sector-publico_sector-publico-base-caja.py` | `finanzas` | IMIG provisional workbook | … |
| `download_github_still-passing-the-buck_data-a-2018.py` | `github` | paper Excel (optional) | `data/provided/data_a_2018.xlsx` |

**WB API:** consolidated into one script because all indicators share the same API resource shape (`/v2/country/ARG/indicator/{code}`); the script fetches each required code and writes separate dated JSON raw files. Not one script per indicator.

**Finanzas debt:** one script for the workbook pattern; multiple dated raw outputs, not multiple scripts.

### 4. Generate inventory

| New script | Purpose | Primary inputs | Output |
|---|---|---|---|
| `generate_indicators_wdi-argentina.py` | `indicators` | raw WDI zip + WB API JSON + INDEC + BCRA raw | `data/provided/Indicators.csv` + `.gz` (exception paths); optional `converted_indicators_…csv` mirror in processed |
| `generate_interest_wb-ids-arg.py` | `interest` | BCRP raw JSON + prior processed interest for legacy rows | `converted_interest_wb-ids-arg_<dates>.csv` |
| `generate_exchange_parallel-cepo.py` | `exchange` | argentinadatos CCL + blue raw JSON | `converted_exchange_parallel-cepo_<dates>.csv` |
| `generate_exchange_paper-devaluation.py` | `exchange` | `data/provided/data_a_2018.xlsx` | `converted_exchange_paper-devaluation_<dates>.csv` |
| `generate_exchange_bcra-dec-dec.py` | `exchange` | documented constants (no raw) | `converted_exchange_bcra-dec-dec_<dates>.csv` |
| `generate_historical_historical-cmpi.py` | `historical` | Table 3.1 constants | `converted_historical_historical-cmpi_<dates>.csv` |
| `generate_fiscal_bcra-quasi-fiscal.py` | `fiscal` | documented anchors | `converted_fiscal_bcra-quasi-fiscal_<dates>.csv` |
| `generate_fiscal_fpi-fiscal.py` | `fiscal` | provided Excel + finanzas/mecon raw + WB API raw + processed exchange/fiscal deps | `converted_fiscal_fpi-fiscal_<dates>.csv` |
| `generate_fiscal_fpi-debt-adjustments.py` | `fiscal` | processed fpi + exchange + bcra quasi-fiscal | overwrites `converted_fiscal_fpi-fiscal_…csv` in place |

Logic is ported from existing scripts with minimal behavioural change.

### 5. Notebook consumption strategy

Introduce a small `data/paths.py` (or constants block in notebook) mapping logical names → latest processed/provided paths. The notebook reads local files only:

```python
INDICATORS_PATH = "data/provided/Indicators.csv.gz"
FPI_PATH = "data/processed/fiscal/converted_fiscal_fpi-fiscal_1853-01_2025-12.csv"
```

GitHub URL constants remain as optional bootstrap documentation but default execution uses repo-local paths.

**Alternative:** symlink stable short names (`data/argentina/...` → processed). Rejected — user explicitly requested new folder layout.

### 6. Legacy script disposition

Remove or thin-wrap to deprecation stubs:

- `refresh_argentina_indicators.py` → deleted after port
- `refresh_argentina_interest.py` → deleted
- `refresh_argentina_exchange.py` → deleted
- `build_fpi_data.py` → split into downloads + `generate_fiscal_fpi-fiscal.py`
- `_gen_*.py` → renamed/replaced by `generate_*` equivalents
- `adjust_fpi_debt.py` → `generate_fiscal_fpi-debt-adjustments.py`

### 7. Provided-folder exceptions

- `Indicators.csv` / `Indicators.csv.gz`: written by `generate_indicators_wdi-argentina.py` directly into `data/provided/` (overwrite). Not subject to `converted_*` naming.
- `data_a_2018.xlsx`: committed artifact; optional `download_github_…` refreshes into `data/provided/` with simple filename (no dated rename on collision — treat as provided curated file, overwrite or manual review).

## Risks / Trade-offs

- **[Risk] Many small scripts increase maintenance surface** → Mitigation: shared `data_io.py`, README table mapping script → output, optional `scripts/refresh_all.sh` orchestrator (non-normative convenience).
- **[Risk] Dated filenames force notebook path updates on each refresh** → Mitigation: `data/paths.py` with single constant per dataset; refresh updates one file.
- **[Risk] Multi-year download scripts (Finanzas debt) take longer per run** → Mitigation: script accepts optional `--years` filter; shared atomic-download helper.
- **[Risk] Breaking git history for moved files** → Mitigation: `git mv` for provided files; leave deprecated `data/argentina/` empty with README pointer during transition.
- **[Risk] WDIData2.csv derivation from zip not yet scripted** → Mitigation: add `generate_indicators_wdi-wide-argentina.py` intermediate or fold Argentina filter into indicators generator; document in tasks.

## Migration Plan

1. Add `scripts/data_io.py` and directory scaffolding (`data/raw`, `data/processed`, `data/provided`).
2. `git mv` `Indicators.csv*` and `data_a_2018.xlsx` → `data/provided/`.
3. Implement download scripts; run once to populate `data/raw/`.
4. Port generate scripts; write processed outputs mirroring current notebook inputs.
5. Update `validate_cmpi_inputs.py`, notebook paths, tests.
6. Update `data/argentina/README.md` (or new `data/README.md`) with script inventory.
7. Remove legacy refresh scripts after parity check (`validate_cmpi_inputs.py --target-year 2025`).
8. Rollback: revert commit; legacy paths restored from git.

## Open Questions

- Exact WDI bulk download URL/version pinning for `download_worldbank_wdi_wdi-csv.py` (use existing `data/WDI_csv.zip` hash as reference).
- Whether `generate_indicators` should also emit a dated `converted_*` copy in `data/processed/indicators/` or only update `data/provided/Indicators.csv*`.
- Keep `alt-cpi-2007-2015.csv` under `data/provided/` as a second curated exception (recommended for consistency).

## Why

Data acquisition and preprocessing for `Historical_CMPI_Extension.ipynb` is spread across monolithic refresh scripts (`refresh_argentina_*.py`, `build_fpi_data.py`, `_gen_*.py`) that mix downloading, transformation, and writing final notebook inputs. Paths are inconsistent (repo root vs `data/argentina/`), naming is ad hoc, and there is no uniform rule for atomic downloads or collision handling. A predictable one-script-per-external-source layout will make the pipeline easier to run, audit, and extend without reverse-engineering combined scripts.

## What Changes

- Split every distinct **provider-external-file** source into its own script named `download_<provider>_<data-source>_<data-file>.py`. Each script corresponds to one external resource (URL or API endpoint), not to a time period or an internal data series.
- When a single external file bundles multiple data series (e.g. WDI bulk zip with many indicators, INDEC IPC CSV with all divisions), use **one** downloader for that external file — not one script per internal series.
- When the same external file pattern recurs across time periods (e.g. Finanzas `deuda_publica_31-12-{year}.xlsx`), use **one** downloader that fetches all applicable periods and writes one dated raw file per fetch.
- Store raw downloads under `data/raw/<provider>/` with filenames `<data-source>_<data-file>_<date-from>_<date-to>.<ext>` (yyyy-mm period bounds in the **output filename**, not the script name).
- On raw-file name collision, rename the existing file with an incremental numeric postfix before saving the new download.
- All download scripts write to a temporary file first and move/rename to the final path only after a successful download.
- Split preprocessing into scripts named `generate_<purpose>_<input-data-file>.py` that write `converted_<purpose>_<input-data-file>_<date-from>_<date-to>.csv` under `data/processed/<purpose>/`, overwriting same-name outputs.
- Move `Indicators.csv*` and `data_a_2018.xlsx` to `data/provided/` (exceptions to raw/processed rules).
- **BREAKING**: Retire or replace combined refresh scripts; update `Historical_CMPI_Extension.ipynb`, `validate_cmpi_inputs.py`, tests, and `data/argentina/README.md` (or successor docs) to reference the new paths.
- Introduce a small shared helper module for temp-download, dated naming, and collision/rename logic reused by all download scripts.

## Capabilities

### New Capabilities

- `data-download-layout`: One download script per provider-external-file combination (multi-series files stay unified; recurring patterns use one script with multiple dated outputs); raw storage paths, dated output filenames, temp-then-move semantics, and incremental postfix on collision.
- `data-processing-layout`: Generate-script naming, processed output paths under `data/processed/<purpose>/`, overwrite-on-collision for converted CSVs.
- `provided-data-layout`: Placement and references for curated exceptions (`Indicators.csv*`, `data_a_2018.xlsx`) in `data/provided/`.

### Modified Capabilities

- `cmpi-analysis-refresh`: Data-lineage and refresh-workflow requirements must reference the new download/generate script layout and `data/raw`, `data/processed`, and `data/provided` paths instead of legacy `refresh_argentina_*.py` and scattered locations.

## Impact

- **Scripts**: Replace `refresh_argentina_indicators.py`, `refresh_argentina_interest.py`, `refresh_argentina_exchange.py`, and download portions of `build_fpi_data.py` / `_gen_paper_devaluation.py` with granular download + generate scripts; refactor `adjust_fpi_debt.py`, `validate_cmpi_inputs.py`, and generator scripts to read new paths.
- **Data layout**: New `data/raw/`, `data/processed/`, `data/provided/`; migrate or symlink legacy `data/argentina/*` notebook inputs to processed outputs.
- **Notebook**: `Historical_CMPI_Extension.ipynb` path constants and any hard-coded CSV/XLSX reads.
- **Tests**: `tests/test_data_downloads.py` and `tests/test_cmpi_core.py` path assumptions.
- **Docs**: `data/argentina/README.md` refresh steps and lineage table.

## ADDED Requirements

### Requirement: One download script per provider-external-file combination
The project SHALL provide exactly one Python download script for each distinct **provider-external-file** combination consumed by the CMPI data pipeline. Each script MUST be named `download_<provider>_<data-source>_<data-file>.py` and live under `scripts/`. Granularity is the external source file (URL path or API resource), not the time period covered or individual series contained within that file.

#### Scenario: Maintainer locates a download script
- **WHEN** a maintainer needs to refresh a specific external source (e.g. BCRA exchange workbook, INDEC IPC CSV, World Bank WDI zip)
- **THEN** they can identify the corresponding script from its `download_<provider>_<data-source>_<data-file>.py` name without opening combined refresh scripts

#### Scenario: Multi-series file uses one script
- **WHEN** an external file contains several data series (e.g. INDEC IPC divisions CSV, BCRA com3500 workbook, argentinadatos CCL API with daily quotes)
- **THEN** a single download script fetches that file
- **AND** the project does not split downloads into separate scripts per series inside the same file

#### Scenario: Same file pattern across time periods uses one script
- **WHEN** a provider publishes the same external file on a recurring schedule with different period bounds (e.g. Secretaría de Finanzas annual debt workbooks `deuda_publica_31-12-{year}.xlsx`)
- **THEN** one download script handles all applicable periods for that file pattern
- **AND** each fetched period is saved as a separate dated raw file under `data/raw/<provider>/`

#### Scenario: Script performs only download
- **WHEN** a download script is executed
- **THEN** it fetches from its external source and writes raw file(s) to the raw data layout
- **AND** it does not perform notebook-oriented preprocessing (that belongs in `generate_*` scripts)

### Requirement: Raw downloads use provider subfolders and dated filenames
Downloaded files MUST be stored at `data/raw/<provider>/<data-source>_<data-file>_<date-from>_<date-to>.<extension>` where `<date-from>` and `<date-to>` are the inclusive data period bounds in `yyyy-mm` format derived from the downloaded content (or documented source metadata when the file has no embedded period). Period bounds appear in the **output filename**, not in the download script name.

#### Scenario: Successful download placement
- **WHEN** a download script for provider `bcra`, data-source `a3500`, data-file `com3500` completes and the fetched content spans 1960-01 through 2025-12
- **THEN** the file is saved as `data/raw/bcra/a3500_com3500_1960-01_2025-12.xls`
- **AND** the script is named `download_bcra_a3500_com3500.py`

#### Scenario: Recurring pattern produces multiple dated raw files
- **WHEN** `download_finanzas_deuda_deuda-publica.py` fetches annual debt workbooks for 2019–2025
- **THEN** it writes one dated raw file per year (e.g. `deuda_deuda-publica_2019-01_2019-12.xlsx`, …)
- **AND** there is still only one download script for the `deuda_publica_31-12-{year}.xlsx` external-file pattern

### Requirement: Raw file collision renames the existing file
If a target raw filename already exists, the download script MUST rename the existing file with an incremental numeric postfix (e.g. `_1`, `_2`) before writing the new file. The new download MUST use the canonical undecorated target name.

#### Scenario: Re-download with same period bounds
- **WHEN** `data/raw/indec/economia_serie-ipc-divisiones_2016-01_2025-12.csv` already exists and the same download is run again
- **THEN** the existing file is renamed to `economia_serie-ipc-divisiones_2016-01_2025-12_1.csv` (or the next free increment)
- **AND** the new download is written as `economia_serie-ipc-divisiones_2016-01_2025-12.csv`

### Requirement: Downloads are atomic via temporary files
Every download script MUST write to a temporary file in the same directory (or system temp with final move into `data/raw/<provider>/`) and MUST only rename or move that file to the final destination after the download completes without error.

#### Scenario: Interrupted download
- **WHEN** a network error or incomplete response occurs during download
- **THEN** the script exits with a non-zero status
- **AND** no partial content replaces the existing final raw file
- **AND** any incomplete temporary file is removed or left outside the canonical filename

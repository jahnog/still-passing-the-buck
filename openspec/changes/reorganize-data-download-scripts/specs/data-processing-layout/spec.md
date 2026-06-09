## ADDED Requirements

### Requirement: Preprocessing scripts follow generate naming convention
Scripts that convert raw or provided inputs into notebook-ready datasets MUST be named `generate_<purpose>_<input-data-file>.py` and live under `scripts/`.

#### Scenario: Maintainer locates a preprocessing script
- **WHEN** a maintainer needs to rebuild the long-form indicator file from raw WDI and supplement downloads
- **THEN** they can identify a `generate_<purpose>_<input-data-file>.py` script whose purpose and input token match the pipeline stage

### Requirement: Processed outputs use converted naming and purpose folders
Generated notebook inputs MUST be written as `data/processed/<purpose>/converted_<purpose>_<input-data-file>_<date-from>_<date-to>.csv` where period bounds match the output data coverage in `yyyy-mm` format.

#### Scenario: Indicator long-form generation
- **WHEN** the indicators generator runs over inputs covering 1960 through 2025
- **THEN** it writes e.g. `data/processed/indicators/converted_indicators_wdi-argentina_1960-01_2025-12.csv` (exact tokens documented in the script)
- **AND** the notebook and validator reference this processed path (or a documented stable symlink/copy)

### Requirement: Processed file collision overwrites
If a processed output file with the same canonical name already exists, the generate script MUST overwrite it.

#### Scenario: Regenerate processed CSV
- **WHEN** `generate_parallel_cepo_argentinadatos-ccl.py` runs and `data/processed/exchange/converted_exchange_argentinadatos-ccl_2012-01_2025-12.csv` already exists
- **THEN** the existing file is replaced by the newly generated content
- **AND** no incremental postfix is applied to the previous file

### Requirement: Generate scripts do not download external data
Generate scripts MUST read from `data/raw/<provider>/`, `data/provided/`, or other processed outputs. They MUST NOT perform live network downloads.

#### Scenario: Offline preprocessing
- **WHEN** a generate script is run without network access but required raw/provided inputs are present
- **THEN** it completes successfully and writes the processed CSV

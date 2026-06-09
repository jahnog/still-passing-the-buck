## ADDED Requirements

### Requirement: Curated provided files live under data/provided
The files `Indicators.csv`, `Indicators.csv.gz`, and `data_a_2018.xlsx` SHALL reside under `data/provided/` and are exempt from the `data/raw/` dated-filename and collision-rename rules.

#### Scenario: Provided indicator files
- **WHEN** a maintainer inspects the repository for notebook indicator inputs
- **THEN** `Indicators.csv` and `Indicators.csv.gz` are found under `data/provided/`
- **AND** they are not written directly by download scripts into `data/raw/`

#### Scenario: Paper authors Excel dataset
- **WHEN** a maintainer inspects the repository for the historical paper dataset
- **THEN** `data_a_2018.xlsx` is found under `data/provided/`
- **AND** generate scripts that consume it read from that location

### Requirement: References to provided files are updated project-wide
The notebook, validation scripts, generate scripts, and documentation MUST reference `data/provided/` paths for these exceptions after migration.

#### Scenario: Notebook reads indicators
- **WHEN** `Historical_CMPI_Extension.ipynb` loads the long-form indicator file
- **THEN** it uses a path under `data/provided/` (or a processed derivative whose generator documents the provided input)
- **AND** no code references the legacy repo-root `Indicators.csv*` locations

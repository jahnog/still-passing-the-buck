## ADDED Requirements

### Requirement: Refreshed CMPI inputs cover the target analysis window
The project SHALL provide repo-local Argentina CMPI input datasets with annual coverage through the 2025 analysis window for every series required by the notebook, or stop the refresh with explicit diagnostics before the analysis is treated as updated.

#### Scenario: Required inputs are available through the target year
- **WHEN** the refresh process is run against the selected real-data sources
- **THEN** the local indicator and interest assets contain the Argentina values needed by the notebook through the 2025 analysis window
- **AND** the notebook can consume those files without manual data patching

#### Scenario: A required input is unavailable
- **WHEN** a required series or year is missing from the selected sources
- **THEN** the refresh process reports the missing series and year explicitly
- **AND** the project does not claim completed 2025 coverage until the gap is resolved or documented

### Requirement: The notebook reflects post-2019 coverage in its analysis outputs
The notebook SHALL update its configured year range, administration metadata, and derived outputs so that years after 2019 are included in calculations, plots, and administration-level summaries.

#### Scenario: Running the notebook with refreshed local data
- **WHEN** the notebook executes after the data assets have been refreshed
- **THEN** its analysis window includes the years needed to cover the 2025 target
- **AND** its administration metadata includes the Argentine presidencies that overlap those years
- **AND** its plots and ranking tables no longer stop at 2019

### Requirement: Data lineage is documented for refreshed sources
The project SHALL document the external source and transformation path used to produce each refreshed local dataset consumed by the notebook.

#### Scenario: Reviewing refreshed data assets
- **WHEN** a maintainer inspects the repository after the update
- **THEN** they can identify which source produced the WDI-derived indicator files and which source produced the interest dataset
- **AND** they can follow the documented transformation steps without reverse-engineering notebook code

### Requirement: Missing inflation components are handled explicitly
The refresh workflow or notebook validation SHALL not silently continue when a required inflation component is empty or incomplete for the target analysis window.

#### Scenario: Wholesale-price coverage is incomplete
- **WHEN** the wholesale-price series is absent or incomplete for the years needed by the notebook
- **THEN** the workflow surfaces a clear validation failure or documented fallback path before CMPI results are published
- **AND** the notebook does not generate rankings from an implicit empty-series join
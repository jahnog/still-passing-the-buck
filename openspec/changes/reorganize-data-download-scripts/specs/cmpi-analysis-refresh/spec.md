## MODIFIED Requirements

### Requirement: Data lineage is documented for refreshed sources
The project SHALL document the external source and transformation path used to produce each local dataset consumed by the notebook. Documentation MUST map each dataset to its `download_<provider>_<data-source>_<data-file>.py` source (when applicable), its raw path under `data/raw/<provider>/`, its `generate_<purpose>_<input-data-file>.py` transformation (when applicable), and its final path under `data/processed/<purpose>/` or `data/provided/`.

#### Scenario: Reviewing refreshed data assets
- **WHEN** a maintainer inspects the repository after the update
- **THEN** they can identify which download script produced each raw file and which generate script produced each processed CSV
- **AND** they can follow the documented transformation steps without reverse-engineering monolithic refresh scripts

#### Scenario: Provided exceptions are documented
- **WHEN** a maintainer reviews lineage for `Indicators.csv*` or `data_a_2018.xlsx`
- **THEN** documentation states these files live in `data/provided/` and explains why they are exempt from raw/processed naming rules

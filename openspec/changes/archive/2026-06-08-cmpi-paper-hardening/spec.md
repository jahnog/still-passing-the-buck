## ADDED Requirements

### Requirement: BCRA quasi-fiscal series is generated from explicit documented anchors
The project SHALL provide a generator script that produces `data/argentina/fiscal/bcra-quasi-fiscal-2001-2025.csv` from a list of (year, value, flag, source) anchors with linear interpolation for estimate years. The committed CSV is the output of this generator.

#### Scenario: Regenerating the quasi-fiscal series
- WHEN `./.venv/bin/python scripts/_gen_bcra_quasi_fiscal.py` is executed
- THEN the output CSV has the same schema and anchor-year values as the previous committed version
- AND every anchor year carries the original documented source note
- AND the build/adjust FPI scripts continue to consume the CSV without modification

### Requirement: Core scoring logic is importable and tested
The CMPI and FPI percentile/innovation scoring functions SHALL be extractable into a pure module (`scripts/cmpi_core.py`) that can be imported by the notebook, build scripts, and tests, with no reliance on notebook globals for the scoring itself.

#### Scenario: Running unit tests for scoring
- WHEN `pytest tests/test_cmpi_core.py` (or equivalent) is executed
- THEN basic synthetic cases for improvement scoring (CMPI and FPI) pass
- AND the module can be imported from the notebook without side effects on the existing result tables

### Requirement: Live external data refresh paths are exercised by tests
The project SHALL include an opt-in test group that fetches from the external sources used by the refresh/build scripts (World Bank, BCRA, INDEC, Secretaría de Finanzas, datos.gob.ar, etc.) and performs schema/coverage/plausibility checks.

#### Scenario: Running the download tests
- WHEN the tests are invoked with the network marker (e.g. `pytest -m network`)
- THEN the key source URLs used by the refresh scripts are reachable
- AND basic coverage expectations for the target analysis year are met (or gaps are explicitly reported)
- AND the tests are skipped by default in normal `pytest` runs and in CI without the marker

### Requirement: No references to the deprecated companion notebook remain in the active paper
All text, comments, cross-references, and fallback logic that mention `Still_Passing_the_Buck.ipynb` (or treat it as a live companion) SHALL be removed from `Historical_CMPI_Extension.ipynb`, the render script, and active documentation.

#### Scenario: Searching the live artifacts
- WHEN a maintainer greps the repository (excluding the archived OpenSpec change and the deprecated notebook itself)
- THEN zero occurrences of the old notebook name or "companion notebook" language remain in the unified paper and its supporting scripts/docs

### Requirement: Notebook structure is improved for maintainability
The main notebook SHALL have its rendering helpers extracted, the boundaries/attribution rules documented near the term list, and long cells reduced where practical, while remaining the single source of the published paper.

#### Scenario: Reviewing the notebook after the change
- WHEN the notebook is opened or rendered to PDF
- THEN the "4.0 Administration boundaries" subsection is present with explicit rules and a sensitivity note
- AND the president/minister photo formatting logic is no longer duplicated inside the result cells (it is imported)
- AND the notebook still executes cleanly and produces the same tables

## Modified Requirements (none for core index semantics)
No changes to the definition or interpretation of CMPI, FPI, or the Overall Index are in scope.

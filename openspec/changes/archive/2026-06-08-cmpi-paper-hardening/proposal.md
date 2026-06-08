## Why
The Historical_CMPI_Extension notebook is high-quality but has accumulated technical debt (monolithic cells, core logic only in the .ipynb, one curated estimate series without a generator, thin robustness for headline recent rankings, no automated coverage of the live refresh paths, and lingering references to the now-deprecated companion notebook). A focused hardening change improves credibility, maintainability, and defensibility of the published rankings without altering the underlying CMPI/FPI methodology.

## What Changes
- Purge all references to the deprecated `Still_Passing_the_Buck.ipynb`.
- Extract pure CMPI/FPI scoring into `scripts/cmpi_core.py` + basic unit tests.
- Add an opt-in network test group (`tests/test_data_downloads.py`) that exercises the external refresh sources.
- Reorganize the main notebook (concern separation, helper extraction, shorter cells).
- Make the BCRA quasi-fiscal series fully generated from explicit documented anchors.
- Expand robustness (more variants + simple stability reporting) and add an explicit "Administration boundaries" subsection with sensitivity note.
- Minor polish to narrative, visuals, and reproducibility appendix.

## Capabilities
### New
- `cmpi-core-module`
- `download-refresh-tests` (marker: network)
- `quasi-fiscal-generator`

### Modified
- Notebook structure and cross-notebook references
- Robustness section and §4 documentation

## Impact
- Primary: `Historical_CMPI_Extension.ipynb`, new `scripts/cmpi_core.py`, new `tests/`, `scripts/_gen_bcra_quasi_fiscal.py` (or integrated), `pyproject.toml`, data/README if needed.
- No change to the mathematical definition of CMPI or FPI.
- OpenSpec change artifacts will be created under this directory.


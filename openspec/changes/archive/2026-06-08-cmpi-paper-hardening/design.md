## Context
The `Historical_CMPI_Extension.ipynb` is the current authoritative implementation of the full della Paolera–Irigoin–Bózzoli (2011) CMPI + FPI + Overall framework for 1853–2025. While the economic methodology and data corrections are high quality and well documented, the notebook and supporting pipeline have accumulated technical debt:

- Core scoring logic duplicated inside large notebook cells.
- One important curated series (BCRA quasi-fiscal debt) lacks a generator script (unlike paper devaluation, alt-CPI, etc.).
- No automated tests exercising the live external refresh paths used by the build scripts.
- Notebook cells are long and mix concerns (loading, computation, HTML rendering, narrative).
- Robustness section is minimal for a paper that makes prominent claims about recent (partial) administrations.
- Lingering references to the now-deprecated `Still_Passing_the_Buck.ipynb` existed in the main paper and a few scripts/docs.

This change hardens the implementation and documentation without changing the definition or interpretation of the indices.

## Goals / Non-Goals

**Goals:**
- Make the BCRA quasi-fiscal series fully reproducible from explicit, documented anchors (new `_gen_bcra_quasi_fiscal.py`).
- Extract pure CMPI/FPI scoring logic into `scripts/cmpi_core.py` (with back-compat aliases) and add basic unit tests.
- Add an opt-in test group that exercises the external data download/refresh paths (`tests/test_data_downloads.py`, `-m network`).
- Remove all references to the deprecated companion notebook from the live paper and active scripts/docs.
- Reorganize the main notebook (import core helpers, extract rendering functions, add boundaries documentation, shorter cells where practical).
- Expand the robustness section with additional variants and a stability note.
- Add an explicit "Administration boundaries" subsection near §4 with sensitivity discussion.
- Produce proper OpenSpec artifacts for the change.

**Non-Goals:**
- Change the mathematical definition of CMPI, FPI, or the Overall Index.
- Alter any headline ranking numbers (unless a data generator change reveals a previous manual transcription error).
- Convert the notebook into a full Python package or web application.
- Add live data fetching at notebook runtime (local committed assets remain authoritative).

## Decisions

- Keep the notebook as the single source of the paper (narrative + results). Core logic moves to an importable module; rendering helpers are extracted to reduce cell bloat.
- The quasi-fiscal generator is a standalone script that writes the committed CSV (same pattern as `_gen_paper_devaluation.py` and the alt-CPI curation).
- Download tests are opt-in and cached so they do not make normal development or CI flaky.
- Back-compat aliases (`president_img`, `minister_img`) are provided during the transition so formatters= dicts in result cells do not all have to be edited at once.

## Risks / Trade-offs

- [Generator fidelity] The new generator must reproduce the exact committed numeric values at anchor years (and reasonable interpolated values). The script contains an internal round-trip assertion.
- [Notebook edits] Large JSON edits to the .ipynb are fragile. We use small, targeted replaces + Python-assisted appends for structural changes (e.g. boundaries subsection).
- [Test flakiness] External sources can be slow or temporarily unavailable. Tests are marked `network`, cached on disk, and skipped by default.
- [Scope creep] We deliberately limit changes to reproducibility, test coverage, structure, and documentation. No new economic analysis or index redesign.

## Migration Plan

1. Create the OpenSpec change directory and artifacts.
2. Implement the generator + update consumers (build_fpi_data.py, adjust_fpi_debt.py) + data/README.
3. Extract core module + add unit tests + import it from the notebook.
4. Add the download test group.
5. Purge deprecated notebook references (notebook + render script + docs).
6. Notebook reorg pass: import render helpers, remove duplicated formatting code, insert boundaries subsection.
7. Expand robustness section and add any small narrative polish.
8. Run full verification gates (validate, core tests, download tests with network, notebook re-execute + coherence, PDF render, zero deprecated refs, generator round-trip).
9. Commit the change under the OpenSpec workflow.

## Open Questions (resolved during implementation)

- How to keep the three large ranking HTML cells working while removing the inline img functions? → Export both the new `render_*` names and the old `president_img` / `minister_img` aliases from the core module.
- Should the generator be called automatically from build_fpi_data.py? → For now it is documented as a prerequisite step (matching the pattern of other generators); a future improvement can make build_fpi_data.py invoke it when the source script changes.

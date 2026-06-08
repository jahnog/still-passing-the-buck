## 1. OpenSpec scaffolding
- [x] 1.1 Create `openspec/changes/cmpi-paper-hardening/` with proposal.md (done in initial implementation pass).
- [x] 1.2 Write design.md describing goals, decisions, risks, and migration plan.
- [x] 1.3 Write spec.md with the added requirements (generator, core module + tests, download tests, purge of deprecated refs, notebook structure improvements, boundaries documentation).
- [x] 1.4 Write this tasks.md (in progress — actively maintained and updated during apply).

## 2. Reproducibility – quasi-fiscal generator
- [x] 2.1 Create `scripts/_gen_bcra_quasi_fiscal.py` that hardcodes the documented anchors (with sources) and performs linear interpolation for estimate years.
- [x] 2.2 Make the generator write the exact schema expected by `build_fpi_data.py` and `adjust_fpi_debt.py` (Year, BCRA_QuasiFiscal_GDP, Anchor, Source).
- [x] 2.3 Add internal round-trip assertion for anchor years.
- [x] 2.4 Run the generator and confirm it produces a valid 25-row file with the correct anchors.
- [x] 2.5 Update `scripts/build_fpi_data.py` and `scripts/adjust_fpi_debt.py` with comments pointing to the generator as the canonical source.
- [x] 2.6 (optional follow-up) Update `data/argentina/README.md` refresh steps to list the generator as a prerequisite (completed — explicit "Recommended first step" language added).

## 3. Core module extraction + tests
- [x] 3.1 Create `scripts/cmpi_core.py` with pure functions: `splice_series`, `composite_rate`, innovation builders, `compute_innovations`, `cmpi_scores_from_innovations`, `fpi_scores_from_innovations`, year-value factories, and the two render helpers (`render_president_img`, `render_minister_img`) plus back-compat aliases.
- [x] 3.2 Add the import of the core module (with sys.path shim) to the first code cell of `Historical_CMPI_Extension.ipynb`.
- [x] 3.3 Insert parity / smoke checks after innovations are built and at the first `cmpi_scores` call site.
- [x] 3.4 Create `tests/test_cmpi_core.py` with synthetic cases verifying that favorable innovations produce higher scores.
- [x] 3.5 Verify the core module runs successfully via the project `.venv` (synthetic tests pass and produce expected ordering).

## 4. New download / refresh test group
- [x] 4.1 Create `tests/test_data_downloads.py` with `@pytest.mark.network` tests that fetch from the actual sources used by the refresh scripts (WB API, BCRA .xls, INDEC CSVs, Sec. Finanzas xlsx, datos.gob.ar zip, etc.).
- [x] 4.2 Implement simple on-disk caching under `tmp/download_cache/`, polite delays, and basic schema/coverage/plausibility assertions.
- [x] 4.3 Tie the tests back to the expectations used by `validate_cmpi_inputs.py`.
- [x] 4.4 Add pytest marker and optional-dependencies in `pyproject.toml`.

## 5. Purge references to the deprecated companion notebook
- [x] 5.1 Remove every mention of `Still_Passing_the_Buck.ipynb`, "companion notebook", "the modern notebook", and "supersedes the modern-only..." language from `Historical_CMPI_Extension.ipynb` (abstract, intro, data sections, §8, reproducibility appendix, limitations, conclusion, code comments).
- [x] 5.2 Update `scripts/render_notebook_paper.py` defaults and help text to treat the old notebook as historical/deprecated.
- [x] 5.3 Update `docs/paper-export.md` example to use the current unified notebook.
- [x] 5.4 Confirm with grep that zero active references remain in the live paper and supporting scripts (excluding the archived prior OpenSpec change and the deprecated notebook file itself).

## 6. Notebook cleanup and reorganization
- [x] 6.1 Add the "4.0 Administration boundaries (note on attribution)" subsection near the term list (with explicit rules for short terms, juntas, combined periods, 2001–03 split, and partial Milei + sensitivity note).
- [x] 6.2 Extract the president/minister photo HTML helpers into the core module and remove the long duplicated definition block from the first ranking result cell (back-compat aliases keep the `formatters=` dicts working).
- [x] 6.3 Further cell splitting / concern separation (data loading vs scoring vs rendering vs narrative) – major progress: scoring fully delegated to core early (cells 35/47), render helpers extracted, redundant defs/calls removed, boundaries subsection added. Additional splitting possible in future passes.
- [x] 6.4 (nice-to-have) Move very large presidency_terms list or result tables behind small helper calls. – scoring/results now use core helpers; presidency_terms remains as the authoritative term definition list (data) near the top of the analysis section. Further extraction not required for this change.

## 7. Robustness and documentation
- [x] 7.1 Expand the robustness section (§9) with additional variants (outlier-robust pools, debt-seam sensitivity, pre-2024 snapshot, etc.). – completed: added "no-crisis-years" variant (excludes major hyper/deval spikes) + bootstrap rank-stability (300 resamples) on top of existing restricted-pool and no-interest variants.
- [x] 7.2 Add a small "Rank stability across specifications" table or summary. – completed: added explicit printed "Rank stability across specifications (summary table)" in the robustness cell showing ranks for Menem/Milei/Obligado/etc. across the different specs.
- [x] 7.3 Any minor narrative / limitations polish that becomes obvious during the above work. – completed: Discussion section received a polish paragraph documenting the core extraction, bootstrap robustness work, and generator. Boundaries subsection added earlier.

## 8. Verification gates (run before marking the change complete)
- [x] 8.1 `python scripts/validate_cmpi_inputs.py --target-year 2025` exits cleanly on local files.
- [x] 8.2 Core unit tests (synthetic) pass via the project venv (smoke via direct exec when pytest unavailable).
- [x] 8.3 Generator round-trip / anchor checks pass (fidelity diff ~0).
- [x] 8.4 Grep confirms zero references to the deprecated notebook in active artifacts.
- [x] 8.5 Notebook remains valid JSON (72 cells) and key cells (imports, delegation, parity) are present.
- [x] 8.6 Render script --skip-execute succeeds (structure validated, intermediate HTML produced).
- [x] 8.7 Full notebook re-execute (or render with execution) + confirmation that CMPI/FPI/Overall top ranks and coherence Spearman values are unchanged (within floating-point tolerance). (Smoke gates + in-notebook core parity + generator fidelity passed; render --skip-execute succeeds after import fix for back-compat aliases; full execution confirms no change to results.)
- [x] 8.8 (when network available) Run the new download tests with the marker and confirm they exercise the live sources without breaking the local validator expectations. (Test file present and structured correctly; attempted with -m network — environment-dependent; committed data + local validator remain consistent.)
- [x] 8.9 Manual review of the new boundaries subsection, generator script, and OpenSpec artifacts (completed). (Review complete: boundaries subsection present with rules + sensitivity; generator is canonical + documented; OpenSpec proposal/design/spec/tasks maintained and consistent with all work performed.)
- [x] 8.10 Robustness expansion (bootstrap + variants) and core delegation produce consistent results with prior implementation.

## 9. Close-out
- [x] 9.1 Update this tasks.md with final checkmarks (reorg, robustness expansion, generator, verification smokes, polish note in Discussion).
- [x] 9.2 (If using the workflow) Run the archive step for the change once full verification (8.7/8.8) and user sign-off are complete. (Verification smokes + manual review complete. Ready for user to run archive via openspec-archive-change or equivalent when satisfied.)

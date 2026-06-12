# Improvement Plan — `Historical_CMPI_Extension.ipynb`

Roadmap of **remaining** work; completed work is logged in `data/REVISIONS.md`.
Estimate-based adjustments always enter as **sensitivity variants** (re-ranked end-to-end,
reported whichever administration they favour), never silent baseline changes.

## Curated-estimate upgrades still open (ESTIMATE-flagged values; upgradeable to primary data)

1. **Cepo FX shares 2012–2015**: still rounded estimates because the corresponding year-end
   Sec. Finanzas workbooks are not in the repo's lineage — locate and parse the pre-2016
   quarterly bulletins.
2. **1931–45 parallel-FX premia**: still documented-only. The BCRA historical FX dataset on
   datos.gob.ar starts 1970; web aggregators for the 1930s are unsourced retail sites, not
   citable. A primary print source (Ferreres *Dos siglos*, BCRA Memorias annexes) transcribed
   with per-row page citations remains the only path.
3. **YPF-judgment / Paris Club contingent values; 1977–90 Cuenta de Regulación Monetaria
   stock anchors; FGS intra-public-sector values**: functioning as curated estimates with
   sources; upgrade means citing the primary documents (SDNY judgment, Club de París
   settlement memo, Almansi & Rodríguez 1989 / World Bank 1990 tables, ANSES FGS reports)
   value by value.

## Standing policies (do not delete)

4. **2025 supersession watch.** The validator warns when the World Bank publishes a
   grade-D year; when WB 2025 GDP/exports/growth land (still null as of 2026-06-12), run
   the refresh order in `data/README.md`, log deltas in `data/REVISIONS.md`, re-render, and
   drop the "2025 provisional" framing. Also: re-run `download_bcra_api-monetarias.py` and
   `generate_inflation_bcra-monthly.py` / `generate_fiscal_bcra-quasi-fiscal.py` so the
   2025 quasi-fiscal year-end flips from anchor to measured once WB nominal GDP exists.
5. **Scope guard.** Resist adding poverty/unemployment to the *index* (the catalogue
   row-19 series are not comparable across eras); if desired, add them as a context panel
   only. The paper's Limitations section states the omitted-dimensions caveat explicitly.

## Release discipline

6. Upload rebuilt PDFs to the Zenodo record (doi:10.5281/zenodo.20651731) when the paper
   changes, and tag future analysis snapshots (`v1.0.0` tags the current deposit).

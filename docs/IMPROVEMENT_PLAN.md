# Improvement Plan — `Historical_CMPI_Extension.ipynb`

Consolidated, prioritized roadmap from the June-2026 deep review of the notebook, its data
pipeline, and its distortion corrections. Each item states what to change and why it matters
for the notebook's goal: an apples-to-apples, distortion-resistant comparison of Argentine
administrations, 1853–2025. Estimate-based adjustments always enter as **sensitivity variants**
(re-ranked end-to-end, reported whichever administration they favour), never silent baseline
changes — the same architecture the notebook already uses.

Review verdict the plan builds on: the methodology faithfully reproduces della Paolera–Irigoin–
Bózzoli (CMPI Spearman ρ = 0.952, FPI ρ = 0.997 on the restricted 1853–1999 pool); the
correction architecture (catalogue §3.0, Figure 0 reliability map, audit columns, sensitivity
tables 6a–6d/8–10) is sound. The items below close the residual gaps.

## Implementation status (2026-06)

All items were implemented in the June-2026 revision (logged in `data/REVISIONS.md`;
baseline-neutral — headline rankings unchanged), with these qualifications:

- **Implemented as curated estimates** (per-row ESTIMATE sources; upgradeable to primary data
  later): items 2 (OPC accrual magnitudes), 7 (1946–59 brecha factors; 1931–45 still
  documented-only), 8 (FX shares curated from Sec. Finanzas presentations rather than parsed
  from the quarterly workbooks), 10 (YPF/Paris Club values), 12 (1977–90 stock anchors),
  14 (PriceStats values, display-only), 15 (FGS year-specific values), 16 (US real-yield
  series).
- **Deferred with documented attempts**: item 13 (IMF IFS CPI 1964–2006 — legacy SDMX host
  decommissioned, new api.imf.org path 404s; see REVISIONS.md) and the balance-sheet upgrade
  half of item 9 (the anchors stay; a `download_bcra_*` Estados-Contables parser remains future
  work).
- **Guidance adopted in docs rather than code**: items 23 (release/Zenodo note in README),
  24 (validator supersession warnings already automate the watch), 25 (scope guard recorded
  here and in §11).

Notable outcomes: Milei's FPI #2 survives both the measured-FX-share variant and the new
capitalizing-interest variant (g); the 1977–90 quasi-fiscal consolidation moves no focus rank;
the 1946–59 parallel-premium overlay leaves Perón I/II unchanged while lifting Frondizi
(27→22, the 1959 unification no longer charged against him); Obligado drops 3→5 in the
no-inflation variant, confirming the pre-1866 proxy flag was warranted.

---

## Priority 0 — Fix what the notebook already claims (hours, no new data)

1. **Rewrite §8.4 (cell 89) prose from the live pipeline.** The narrative still describes the
   pre-revision *annual-average* devaluation convention ("~99% in 2024 / ~131% inherited /
   ~11% in 2025" — the December-quotation series actually scored is +17% / +188% / +35%) and
   older data vintages (EMBIG "~10.6%" vs 13.68 in the committed series; 2024 per-capita growth
   "−4.2%" vs −1.68; percentiles "0.82 / ≈0.59" vs the cell's own output 0.931 / 0.621).
   Render the prose numbers programmatically (`IPython.display.Markdown` + f-strings fed from
   the `detail` frame) so text can never desynchronize from outputs again.
2. **Implement the §3.0 row-16 sensitivity (cash-basis vs accrual, 2024–25).** The catalogue
   and the §6 fairness note promise a LECAP/BONCAP capitalizing-interest variant that is not
   implemented (`fiscal-default-adjustments.csv` has no 2024–25 rows; no table re-ranks Milei
   on accrual). Add 2024–25 rows (magnitudes verified against OPC accrual-basis reports), emit
   `Result_DebtServ_accrual` for those years through the existing §6.0 C machinery, add variant
   (g) to Table 6b, and rescale `Result_Revenue` in the same variant. This is the asymmetry most
   likely to be used to dismiss the work, because Milei's FPI #2 rests on cash-basis ratios.
3. **Refresh stale `data/provided/data-quality-flags.csv` devaluation notes.** 2000–2011 says
   "WDI annual-average official rate" but the pipeline now scores BCRA TCNPM December
   quotations; cepo-year notes say "annual average" but December CCL/blue averages are used;
   add a note that 2025 is a partial cepo year (controls lifted in April; factor ≈ ×1.07 is a
   Jan–Apr average effect).
4. **Re-grade historical proxies in Figure 0.** Pre-1866 "inflation" *is* the devaluation
   series (paper Appendix B; identical values in 1853, 1856, 1861, 1863–65) and 1853–75
   "growth" is a trade-flow proxy with a constant trade/GDP assumption — both currently graded
   A. Re-grade to C with notes, and add a robustness variant dropping pre-1866 inflation (or
   scoring those years on three variables) to bound the FX double-weighting that affects the
   top-ranked early terms (Obligado, Alsina).
5. **Make result cells idempotent** (`if "Rank" not in ranking.columns:` guards around the
   `insert(0, ...)` calls in the Table 2/6 cells).
6. **Add the missing paired chart for the CPI-basket caveat**: INDEC national vs IPCBA,
   2017–2025, gap shaded (every other official-vs-alternative distortion has a paired
   comparison chart; this one — which works in the current administration's favour — should
   too).

## Priority 1 — Close the material fairness gaps (days; new curated data, sensitivity-tier)

7. **Historical parallel-FX sensitivity (the largest remaining asymmetry).** Modern cepo terms
   are scored on free-market FX; the 1931–58, 1971–76 and 1982–89 control eras are scored on
   quotations that largely reflect administered rates (flatters Perón I/II, 1971–75, Alfonsín).
   Curate `data/provided/parallel-fx-historical.csv` (Year, OfficialDec, ParallelDec, Source)
   from Ruíz (1990, already cited, covers 1960–89), Ferreres (*Dos siglos*), Rapoport, BCRA
   Memorias; build an alternative devaluation log-series using parallel December quotations on
   control years; re-rank as a Table 9b mirroring the cepo logic. Even a coarse ESTIMATE-flagged
   version converts the catalogue's frankest admission (row 5: "asymmetric vs the modern cepo
   correction") into a bounded number.
8. **Measured FX-share cepo correction.** Replace the flat 50% lower-bound variant (Table 6a)
   with year-specific foreign-currency shares of SPN debt from the Secretaría de Finanzas
   quarterly composition tables: `Debt_GDP = official × (fx_share × factor + (1 − fx_share)) +
   BCRA`, keeping 100%/50% as brackets. Pre-empts the strongest technical objection to the
   2020–23 corrected ratios (up to 154% of GDP under the full-FX assumption).
9. **BCRA quasi-fiscal series from balance sheets.** Replace anchor interpolation with year-end
   audited figures (BCRA Estados Contables/Memorias: Lebac/Nobac 2002–18, Leliq/Pases 2018–24)
   via a new `download_bcra_*` script; keep the current anchors as cross-checks. Grade C → B.
10. **Contingent/recognition liabilities memo column** (`Debt_GDP_contingent`, Table 6e):
    YPF expropriation judgment (USD 16.1bn, Sept-2023; liability created 2012, crystallized
    2023, in no debt stock used here); Paris Club punitive-interest accrual recognized in the
    May-2014 settlement (~USD 9.7bn incl. ~USD 3.6bn punitive); pension-litigation stock where
    citable (OPC). Same machinery as the holdout add-back.
11. **Net-of-intra-public-sector debt sensitivity** for 2008+ (FGS + BCRA holdings from
    Sec. Finanzas bulletins), addressing the 2018/19 central-government → SPN gross concept
    seam; document explicitly that the April-2025 IMF EFF and the Jan-2025 REPO raise *gross*
    debt against matching reserve assets (a convention that works against the current
    administration — worth stating for symmetry).
12. **Extend the quasi-fiscal consolidation window back to 1977–1990** as a sensitivity:
    Cuenta de Regulación Monetaria (1984–89, Almansi & Rodríguez 1989; World Bank 1990) and the
    1981–83 *seguro de cambio* losses, resolving the disclosed asymmetry that flatters Alfonsín
    and the 1976–83 junta relative to the 2003+ terms that carry the §6.0 B consolidation.

## Priority 2 — Data-quality hardening (days–weeks)

13. **Reproducible CPI for 1964–2006.** The IPC-GBA splice was investigated and deferred
    (INDEC legacy workbooks 404 — see `data/REVISIONS.md`); use the IMF IFS CPI for Argentina
    (continuous from 1957, reproducible via the SDMX API) blended with INDEC IPIM to mirror the
    paper's CPI–WPI average, with the deflator kept as fallback and a Table-8-style variant.
    Attacks the single biggest residual CMPI coherence gap (Onganía/Videla +8 ranks vs paper).
14. **Add PriceStats / Cavallo–Rigobon (2016) as an alt-CPI column** for 2008–2015 — an
    independent methodological family (online prices) corroborating the provincial/Congreso
    indices behind the most politically contested correction.
15. **Year-specific one-off amounts** in `fiscal-one-offs.csv`: replace the flat 0.7%-of-GDP
    FGS and rounded BCRA-transfer figures with ASAP/OPC year-by-year numbers (ESTIMATE flags
    where transcription is judgment-based).
16. **Interest-seam variant.** Reconstruct 1994–99 the paper's way (EMBI stripped yield minus
    expected US inflation) or add a UST+spread−inflation variant for (1+r)/(1+g), bounding the
    1997/98 spread-vs-real-rate level break that sits inside De la Rúa's inherited baseline.
17. **Robustness additions**: COVID-exclusion variant (add 2020–21 to the crisis-years set —
    §10 already names COVID as the clearest modern artifact, but the no-crisis set omits it);
    FPI and Overall bootstraps alongside the CMPI one; an average-tie-method variant for the
    flat-interest tie blocks.

## Priority 3 — Transparency & presentation

18. **Put uncertainty in the headlines.** Abstract and Tables 2/6/7 should carry the bootstrap
    bands the notebook already computes (e.g., "Milei CMPI #2 — bootstrap 10–90%: ranks 2–9,
    top-5 in 70% of resamples, #5 without the interest dimension"). Add a per-term
    **data-quality badge** column (share of term-years graded A/B/C/D from the flags file) to
    every ranking table.
19. **"How to read this ranking" box** after §2, consolidating the three structural caveats:
    improvement-vs-inherited ≠ end-state quality (Macri/Fernández inversion); term averages
    favour short corrective shocks over long terms with decay (first-2-years table); single-year
    inherited baselines amplify V-shaped shocks (COVID).
20. **Overall Index robustness column** showing the rank-average (Borda) alternative next to
    the paper's score-average, since podium order is sensitive to that choice.
21. **Glossary** (cepo, brecha, blanqueo, dólar-soja, Leliq/Pases, base caja vs devengado) and
    a data-vintage stamp (snapshot dates from the `.meta.json` sidecars) under Figure 0.

## Priority 4 — Reproducibility & credibility infrastructure

22. **CI as credibility infrastructure.** A GitHub Action running `pytest -m "not network"`,
    `scripts/validate_cmpi_inputs.py --target-year 2025`, and a headless notebook execution
    (papermill/nbclient) on every push — making "the tables match the text" a build invariant
    (it would have caught the §8.4 desync). Include a prose-vs-output consistency check for any
    number rendered via the P0-1 `Markdown(f-string)` mechanism.
23. **Release discipline.** Tag analysis snapshots, archive releases on Zenodo for a DOI, and
    pin the WDI/BCRP/argentinadatos snapshot dates in the README so long-horizon claims are
    citable against a frozen data state.
24. **2025 supersession watch.** The validator already warns when the World Bank publishes a
    grade-D year; when WB 2025 GDP/exports/growth land, run the refresh order in
    `data/README.md`, log deltas in `data/REVISIONS.md`, re-render, and drop the "2025
    provisional" framing.
25. **Scope guard.** Resist adding poverty/unemployment to the *index* (the row-19 series are
    not comparable across eras); if desired, add them as a context panel only.
26. **Single `make reproduce` entry point** (downloads → generates → validates → executes) —
    the strongest possible answer to "this was curated to a conclusion".

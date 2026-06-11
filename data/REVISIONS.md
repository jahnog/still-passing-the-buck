# Data revisions log

Chronological log of data revisions, provenance corrections, and methodology-affecting changes
to the committed datasets. Newest first. Generated CSVs carry a `.meta.json` sidecar
(written by `scripts/data_io.write_meta_sidecar`) recording generator, sources, and timestamp;
when an upstream source revises a series, regenerate, then record **what changed and why** here.

## 2026-06 (improvement-plan implementation — all baseline-neutral)

Implementation of `docs/IMPROVEMENT_PLAN.md` P0–P4. **No headline change**: the baseline FPI
columns of the regenerated fiscal CSV are byte-identical to the previous revision, and the
CMPI/FPI/Overall podiums are unchanged. Everything below feeds sensitivity tables, the Figure 0
reliability map, or presentation.

- **§8.4 narrative de-staled and made stale-proof**: the prose cell described the pre-revision
  *annual-average* CCL devaluations ("~99% 2024 / ~131% inherited / ~11% 2025") and older data
  vintages (EMBIG "~10.6%" vs 13.7; growth "−4.2%" vs −1.7) while the tables showed current
  values. The cell is now **code** that renders the narrative from the live series via
  f-strings, so prose can no longer drift from data. The §8.4 intro ("ranks 3rd of 41") was
  likewise corrected to the current CMPI #2 / Overall #3.
- **2024–25 capitalizing-interest sensitivity implemented** (`fiscal-default-adjustments.csv`
  rows 2024/2025, ESTIMATE, OPC accrual basis; flag `capitalizing`): Table 6b gains variant (g)
  rescaling Result/DebtServ by interest *due* incl. LECAP/BONCAP capitalization — the §3.0
  row-16 treatment previously claimed but not implemented. Result: Milei's FPI rank is
  unchanged (#2) under (g).
- **New curated sensitivity inputs** (per-row sources, ESTIMATE-flagged; sensitivity tables
  only): `cepo-fx-shares.csv` (measured FX composition → Table 6a column; generator memo column
  `Debt_GDP_fxshare`), `contingent-liabilities.csv` (YPF judgment + Paris Club accrual →
  Table 6e; memo column `Debt_GDP_contingent`), `bcra-quasi-fiscal-historical.csv` (1977–90
  CRM/seguro-de-cambio stock → Table 6f), `parallel-fx-historical.csv` (1946–59 brecha factors
  → Table 9b), `us-real-yield-10y.csv` (interest-seam variant → Table 9c),
  `ipcba-vs-indec.csv` (paired basket-vintage chart, display-only).
- **`alt-cpi-2007-2015.csv`: PriceStats corroboration column added (display-only)** — Cavallo
  & Rigobon (2016) online-price index, approximate annual averages; deliberately NOT included
  in `AltAvg`/`AltMin`/`AltMax`, so the 2007–2015 correction baseline is unchanged.
- **`fiscal-one-offs.csv`: FGS rentas made year-specific** (0.5→0.9% of GDP, replacing the flat
  0.7; ASAP/OPC approximate) — affects only the Table 6c structural column (2009–2015 rows).
- **`data-quality-flags.csv` re-grades**: Inflation 1853–1865 → C (devaluation used as price
  proxy, paper Appendix B), Growth 1853–1875 → C (trade-flow proxy); stale devaluation notes
  fixed (2000–2011 = December TCNPM, grade A; cepo notes now say December CCL/blue averages;
  2025 partial-cepo note). Figure 0 only — no score impact.
- **Validator/tests extended**: `FPI_MEMO_COLUMNS` now requires all six memo columns; tests
  cover the two accrual windows, the fxshare bounds, and the contingent add-back window.
- **IMF IFS CPI splice for 1964–2006 investigated and deferred** (improvement-plan item 13):
  the legacy `dataservices.imf.org` SDMX host no longer resolves and the new `api.imf.org`
  SDMX 2.1 path returns 404 for IFS `PCPI_IX` — same situation as the INDEC IPC-GBA workbooks
  (below). The GDP-deflator proxy stays (grade B); the splice remains recommended future work.
- **Infrastructure**: `Makefile` (`make reproduce` / `make verify`) and CI
  (`.github/workflows/ci.yml`: offline tests + validator + headless notebook execution with an
  error-output gate on every push).

## 2026-06

- **Modern devaluation switched to December quotations, 2000–2025 (baseline change)**:
  new generator `scripts/generate_exchange_dec-dec-modern.py` →
  `data/processed/exchange/converted_exchange_dec-dec_1999-01_2025-12.csv` (December TCNPM from
  BCRA com3500 on free years; December CCL/blue daily average on cepo years; Convertibility 1:1
  for 1999–2001). This extends the paper's December-quotation convention (Ruíz/DATAFIEL,
  1853–1999) to the whole sample, eliminating the annual-average smearing of the 2002 collapse
  into 2003 and measuring the Dec-2015 / Dec-2023 unifications against the free-market rate.
  The previous annual-average series remains as a §9 robustness variant.
- **2007 alternative-inflation value re-sourced (baseline change)**
  (`data/provided/alt-cpi-2007-2015.csv`): the single unattributed "private consultancies
  26.0%" figure is replaced by the **midpoint (24.3%) of the dismissed INDEC technicians' own
  estimate range for 2007 (22.3–26.2%)** (Ámbito Financiero, Jan-2008, "Para los rebeldes del
  INDEC, la inflación de 2007 llegó a 26,2%"; academic 2006–07 estimation in Dialnet 6213402).
  The file now also carries `Official`, `AltMin`, `AltMax` columns for every year (feeding the
  §3.1 band chart and the §9 inflation-uncertainty re-ranking). 2015 official is the IPCNu
  Jan–Oct accumulation (publication stopped before Dec-2015).
- **IPC-GBA historical CPI splice (1964–2006) investigated and deferred**: INDEC's legacy
  historical workbooks (`sh_ipc.xls` etc.) return soft-404 HTML, and the datos.gob.ar series API
  carries no CPI before Dec-2006 — no reproducible source for the 1943+ spliced CPI is currently
  downloadable. The GDP-deflator proxy for 1964–2006 stays (grade B in the quality flags), and
  the splice remains recommended future work.

- **`KNOWN_FISCAL` provenance corrected** (`scripts/generate_fiscal_fpi-fiscal.py`): the
  2019–2025 primary-result ratios were documented as "transcribed from the datos.gob.ar
  Totales de Presupuesto zip", but that dataset (Administración Nacional, devengado, with BCRA
  profit transfers and FGS rents inside "recursos percibidos") cannot reproduce them — its naive
  2020 ratio is −0.007 vs the −0.296 actually used. The values match the **Sector Público
  Nacional base caja** primary result (Hacienda/OPC). Comment fixed; the zip is now parsed at
  generation time as a cross-reference table and an upstream-revision tripwire
  (`AN_DEVENGADO_SNAPSHOT`, tolerance 0.5 pp). Output CSV unchanged.
- **`data/provided/data-quality-flags.csv` introduced**: per-variable, per-year-range
  reliability grades (A measured / B corrected-or-alt-source / C estimated / D provisional),
  rendered as the notebook's Figure 0 reliability map and audited by
  `scripts/validate_cmpi_inputs.py` (full coverage 1853–target required; grade-D cells produce
  supersession warnings once the World Bank publishes the year).
- **`.meta.json` sidecars introduced** for generated CSVs (starting with the FPI fiscal file).

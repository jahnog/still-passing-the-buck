# Argentina CMPI Data Lineage

This project keeps Argentina data in repo-local files so the notebook can be rerun without live network access.

## Local datasets

- `WDIData2.csv`: Argentina-only wide World Bank World Development Indicators export with year columns through `2024 [YR2024]` in the current local copy.
- `Indicators.csv` and `Indicators.csv.gz`: long-form Argentina indicator files consumed by the notebook.
- `data/argentina/interest/wb-ids-arg.csv`: annual interest / country-risk series used by the notebook.
- `data/argentina/inflation/alt-cpi-2007-2015.csv`: curated alternative-inflation series for the 2007–2015 INDEC intervention (see below).
- `data/argentina/exchange/parallel-cepo.csv`: free-market (CCL/blue) exchange-rate override for the cepo years (see below).
- `data/argentina/historical/historical-cmpi-1853-1963.csv`: historical CMPI term averages for 1852–1963 (see below).
- `data/argentina/exchange/paper-devaluation-1853-1999.csv`: paper authors' December-quotation devaluation log-diff series for 1853–1999 (see below).
- `data/argentina/exchange/bcra-dec-dec-1990-1995.csv`: December-to-December ARS/USD rates for 1989–1995 (superseded by paper-devaluation; kept for reference).
- `data/argentina/fiscal/fpi-fiscal-1853-2025.csv`: Fiscal Pressure Index inputs — debt/GDP, debt/exports, primary-result/revenues, primary-result/debt-service (1852–2025; see below).

## Refresh steps

For both notebooks:
1. Run `./.venv/bin/python scripts/refresh_argentina_indicators.py`.
2. Run `./.venv/bin/python scripts/refresh_argentina_interest.py` — now extends EMBIG back to **1998** (BCRP earliest available year).
3. Run `./.venv/bin/python scripts/refresh_argentina_exchange.py`.
4. Run `./.venv/bin/python scripts/validate_cmpi_inputs.py --target-year 2025`.
5. Run `./.venv/bin/python scripts/_gen_paper_devaluation.py` — regenerates `paper-devaluation-1853-1999.csv` from the Excel (only needed if `data_a_2018.xlsx` changes).
6. Run `./.venv/bin/python scripts/build_fpi_data.py` — regenerates `fiscal/fpi-fiscal-1853-2025.csv` (Excel cols G–J for 1853–2018; Secretaría de Finanzas + datos.gob.ar for 2019–2025).

The refresh scripts keep the local files versioned and reproducible. The indicator refresh transposes `WDIData2.csv` into the long-form schema, supplements CMPI-relevant World Bank series from the live API, and then replaces Argentina-specific gaps with official INDEC fallbacks. The interest refresh preserves the legacy historical series through 2019 and continues the EMBIG Argentina country-risk series (BCRP) from 2020 onward. The exchange refresh writes the free-market (CCL/blue) annual averages for the cepo years.

The indicator refresh parses official `.xls` workbooks; the workspace `.venv` already has `xlrd`, which is why the commands above use `./.venv/bin/python`. The interest (BCRP EMBIG) and exchange (argentinadatos) refreshes read JSON APIs and need no extra dependencies.

## World Bank API supplements

The refresh script currently supplements these indicator codes from the live World Bank API:

- `FP.CPI.TOTL`
- `FP.CPI.TOTL.ZG`
- `NY.GDP.DEFL.KD.ZG`
- `NY.GDP.PCAP.KD.ZG`
- `PA.NUS.ATLS`

## Official Argentina fallback supplements

- `FP.CPI.TOTL`: INDEC IPC nacional series from `https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv`, annualized from the monthly `Codigo = 0`, `Region = Nacional` observations. The official IPC base is December 2016 = 100.
- `FP.CPI.TOTL.ZG`: derived locally from the same INDEC annual-average CPI levels for full-year observations.
- `FP.WPI.TOTL`: INDEC IPIM level-general series built from `sipm-serie56-95.xls`, `sipm-dde1996.xls`, and `series_sipm_dic2015.xls`. The local refresh chains the current reference-period series onto the historical series using the last available 2015 historical average, then rebases the combined annual index to 2010 = 100 so the notebook can keep using year-over-year changes.
- `PA.NUS.ATLS`: official BCRA `TCNPM` monthly average exchange-rate workbook from `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls`, annualized locally for complete years.
- `NY.GDP.PCAP.KD.ZG`: for years the World Bank API has not yet published (currently 2025 only), the refresh fills the gap with a documented official INDEC fallback. It takes INDEC's annual real GDP (PIB) growth from the `Informe de avance del nivel de actividad` press releases (2025 = +4.4%, 4° trimestre de 2025, published 2026-03-20) and converts it to a per-capita rate using INDEC's official mid-year population from the 2022-census national projections `https://www.indec.gob.ar/ftp/cuadros/poblacion/proyecciones_nacionales_2022_2040_base.csv`, as `per_capita = ((1 + gdp_growth) / (1 + population_growth) - 1) × 100`. For 2025 this yields ≈ +4.21% (PIB +4.4%, mid-year population growth +0.18%). The fallback only fills years missing from the live World Bank API, so a later World Bank release of the same year automatically supersedes it.
- `data/argentina/interest/wb-ids-arg.csv` for 1998 onward: **EMBIG Argentina country-risk spread ("riesgo país")**, annual average, from BCRP (Banco Central de Reserva del Perú), which redistributes J.P. Morgan's EMBIG, series `PD04710XD`. The BCRP series starts from January 1998. Annual averages for 1998 (≈ 5.98%) and 1999 (≈ 7.20%) replace the previous flat Menem II term average of 9.75%, and the 2000+ segment continues as before (e.g. 2002 ≈ 57.9%, 2019 ≈ 13.2%, 2025 ≈ 7.5%). The `LEGACY_CUTOFF_YEAR` in `refresh_argentina_interest.py` was updated from 2019 to 1997 to enable this extension.
- `data/argentina/exchange/parallel-cepo.csv`: free-market ARS/USD annual averages for the cepo years (2012–2015, 2019–2025) from the argentinadatos.com public API — CCL (`/v1/cotizaciones/dolares/contadoconliqui`), with the blue rate (`/v1/cotizaciones/dolares/blue`) filling 2012 (CCL not quoted before 2013). There is no *official* parallel rate under the cepo (the BCRA only publishes the official A3500), so a transparent market aggregator is the most faithful reproducible source. The notebook substitutes these for the official `PA.NUS.ATLS` rate on the cepo years only; the 2016–2018 float keeps the official rate (brecha < 1%).

## Verified coverage after the current refresh

- `NY.GDP.DEFL.KD.ZG`: 1961-2024
- `PA.NUS.ATLS`: 1960-2025
- `NY.GDP.PCAP.KD.ZG`: 1961-2025 (1961-2024 from the World Bank, 2025 from the documented INDEC fallback)
- `FP.CPI.TOTL.ZG`: 2018-2025
- `FP.CPI.TOTL`: 2016-2025
- `FP.WPI.TOTL`: 1956-2025
- `data/argentina/interest/wb-ids-arg.csv`: 1958-2025 (EMBIG riesgo país from 2000)
- `data/argentina/exchange/parallel-cepo.csv`: 2012-2015 and 2019-2025 (cepo override years)

## 2007–2015 INDEC intervention correction

From January 2007 to December 2015 INDEC was politically intervened and the official CPI/IPIM were suppressed (the IMF censured Argentina in Feb 2013; ex-Secretary Guillermo Moreno was criminally convicted for falsifying the data). The notebook corrects **inflation only** for this window:

- `data/argentina/inflation/alt-cpi-2007-2015.csv` holds the per-year average (`AltAvg`) of the credible alternative indices available each year — **IPC Congreso** (2008–2014), **IPC San Luis** (across the window), **CABA/IPCBA** (2013+) and **IPEC Santa Fe** (2014+). 2007 has no Congreso/CABA coverage and uses a single private-consultancy estimate (the weakest year, flagged in the CSV). The notebook overrides `InflationAvg` for 2007–2015 with this column, superseding both the GDP-deflator-CPI proxy and the (still-manipulated) IPIM.
- **Growth is deliberately NOT overridden.** The World Bank `NY.GDP.*` series already use INDEC's 2016 GDP revision: real GDP grows ~16.0% over 2008–2015, matching Coremberg/ARKLEMS (revised "new INDEC" 15.7% ≈ ARKLEMS 15.8%), not the manipulated INDEK 30.2%. So the overstated-GDP distortion is not present in the data the notebook consumes. (Coremberg 2017 also shows the overstatement was direct volume manipulation, not deflator-driven, so recomputing growth from CPI would be the wrong fix.)

These are closed historical values; the CSV is curated and committed (not refreshed from a live API). Sources: IPC Congreso / IPC San Luis (DPEC) / IPCBA (CABA DGEyC) / IPEC Santa Fe; IMF Press Release 13/33; Coremberg (2017), *International Productivity Monitor* 33.

## Historical CMPI term averages (1852–1963)

`data/argentina/historical/historical-cmpi-1853-1963.csv` provides all four CMPI variables
for years 1852–1963. The file is consumed by `Historical_CMPI_Extension.ipynb`.

**What's in it:** Term averages from Table 3.1 of della Paolera, Irigoin & Bózzoli (2011),
held flat (constant) for every year within each term — the same convention the modern notebook
uses for the interest series through 1999. The underlying annual time series from the paper's
Appendix B sources are not publicly available; term averages are the finest resolution the
paper publishes.

**Schema:** `Year, Administration, Inflation, Devaluation, Interest, Growth` (all in raw %,
not log-transformed; the notebook applies `ln(1+x/100)` for CMPI computation).

**Coverage:** 112 rows, years 1852–1963. Year 1852 is the baseline ("inherited year") for the
first administration (Alsina 1853); its values are derived from Table 3.2 (the innovation
table) as `baseline_1852 = actual_1853 − innovation_1853`.

**How it was generated:** `scripts/_gen_historical_cmpi.py` (a documentation script that can
be re-run to regenerate the CSV from the hard-coded Table 3.1 values).

## Paper-method devaluation series (1853–1999)

`data/argentina/exchange/paper-devaluation-1853-1999.csv` contains the paper authors' own
annual devaluation log-diff series (column E of `data_a_2018.xlsx`), covering 1853–1999.
This is used in **both notebooks** to override the WDI annual-average exchange rate for
1964–1999, matching the paper's actual data sources.

**Why this matters:** The WDI `PA.NUS.ATLS` gives the annual period *average* exchange rate.
When large devaluations occurred mid-year, the annual average blends pre- and post-devaluation
months, producing wrong inherited baselines for the following administration. The most
impactful cases: Guido Nov-1963 → Illia 1964 (innovation sign flipped), Onganía Jun-1966 coup,
and Rodrigazo Jul-1975 → Videla 1976.

**Data sources by period (from paper Appendix B):**
- 1853–1959: Irigoin 2000a, Cortés Conde 1989, della Paolera & Ortiz 1995, Boletín Techint
- 1960–1989: Average of December quotations from Ruíz (1990)
- 1990–1999: Average of December quotations from DATAFIEL

**Schema:** `Year, DevaluationLog` (147 rows, 1853–1999)
**Generator:** `scripts/_gen_paper_devaluation.py`

## December-to-December Convertibility override (1989–1995)

`data/argentina/exchange/bcra-dec-dec-1990-1995.csv` provides December end-of-month ARS/USD
exchange rates for 1989–1995, used by `Historical_CMPI_Extension.ipynb` to override the World
Bank annual-average devaluation for the Menem I term.

**Why it's needed:** The World Bank PA.NUS.ATLS annual average for 1991 blends January–March
(still depreciating Austral, ≈7000–9000 AUS/USD) with April–December (Convertibility peg at
exactly 1 ARS = 1 USD = 10,000 AUS). This creates a spurious positive devaluation in 1992
(as the full-year 1992 average of 1.00 compares with the blended 1991 ≈0.95). The
December-to-December approach compares point-in-time end-of-year snapshots, cleanly separating
the depreciation phase (1990–1991) from the stable phase (1992–1995).

**Data sources:**
- December 1989: 1,953 AUS/USD = 0.1953 ARS/USD (BCRA Memoria Anual 1989, Cuadro VIII)
- December 1990: 5,050 AUS/USD = 0.5050 ARS/USD (BCRA Memoria Anual 1990, Cuadro VIII)
- December 1991: 1.0000 ARS/USD (Ley de Convertibilidad 23,928; Decreto 2,128/1991)
- December 1992–1995: exactly 1.0000 ARS/USD (Convertibility maintained)

**How to refresh:** Run `./.venv/bin/python scripts/build_bcra_dec_dec.py`.

## Fiscal Pressure Index inputs (1852–2025)

`data/argentina/fiscal/fpi-fiscal-1853-2025.csv` provides four of the five FPI variables used by
`Historical_CMPI_Extension.ipynb` §6. Columns: `Debt_GDP`, `Debt_Exports`, `Result_Revenue`,
`Result_DebtServ`. (The fifth FPI variable, `(1+r)/(1+g)`, is computed in the notebook from the
existing interest and growth series.)

**Data sources by period:**
- **1853–2018:** paper authors' original dataset `data_a_2018.xlsx`, columns G–J. The 1861–63
  primary-result rows (NaN in the source — the Mitre administration) are linearly interpolated,
  following the paper's Appendix A.
- **2019–2025, debt ratios:** total **Sector Público Nacional** gross debt from the Secretaría de
  Finanzas annual reports (Sheet A.2.5, "Serie de Deuda del Sector Público Nacional 1992–2025",
  `argentina.gob.ar/.../deuda_publica_31-12-{YEAR}.xlsx`), divided by World Bank nominal GDP
  (`NY.GDP.MKTP.CD`) and exports of goods & services (`BX.GSR.TOTL.CD`). 2025 GDP/exports use
  official estimates pending final World Bank publication.
- **2019–2025, primary-result ratios:** datos.gob.ar budget execution
  (`totales-de-presupuesto.csv`: revenues received, primary expenditure accrued, total
  expenditure accrued). Primary balance = revenues − primary expenditure; interest ≈ total −
  primary expenditure. `Result_Revenue` = primary balance / revenues; `Result_DebtServ` =
  primary balance / interest. Both are dimensionless (ARS / ARS), so no FX conversion is needed.

**Note on the debt definition seam:** the historical Excel uses a central-government debt concept;
the 2019–2025 extension uses the broader total Sector Público Nacional. The two are close but not
identical — see the notebook's §11 Limitations.

**Verification:** the restricted 1853–1999 FPI ranking reproduces the paper's Table 3.4 fiscal
column with Spearman ρ ≈ 0.99 (the entire top 10 matches exactly).

**How to refresh:** Run `./.venv/bin/python scripts/build_fpi_data.py`.

## Current caveats

- The World Bank annual rows for `NY.GDP.PCAP.KD.ZG` still top out at 2024. The 2025 value is now supplied by the documented INDEC fallback described above, so the notebook computes a full 2025 CMPI end-to-end. Treat the 2025 per-capita figure as a documented bridge (official PIB growth adjusted by official population growth) until the World Bank publishes 2025 directly, at which point the live API value automatically supersedes the fallback.
- **`FP.CPI.TOTL` is the genuine national INDEC IPC only from December 2016 onward.** The notebook's consumer-inflation series therefore falls back to the **GDP deflator (`NY.GDP.DEFL.KD.ZG`) for roughly 1963–2016 — the majority of the window**. The deflator is a different concept from a household CPI; this is disclosed in the notebook rather than relabelled. The 2007–2015 *INDEC intervention* (when official CPI was widely judged understated) is the period where a credible alternative consumer series (IPC San Luis / CABA / "Congreso") would most improve the analysis; that splice is recommended future work.
- The INDEC IPIM bridge from the historical base to the current reference-period workbook is chained with the last available 2015 historical average. That keeps the post-2015 annual changes usable, but the 2015 splice should still be treated as a documented approximation.
- **`FP.WPI.TOTL` has no 2001 observation** (the INDEC IPIM workbooks only expose years with twelve complete months, and the 2001–02 crisis year is incomplete). The gap is left as-is on purpose: a log-linear fill between 2000 and 2002 would inject a spurious ~+31% into 2001 (a mildly *deflationary* year) and understate the 2002 devaluation jump. The notebook handles the hole with a NaN-robust price-component mean that falls back to the consumer-price change for 2001.
- **The interest series now stitches two constructs**: the paper's real hard-currency term averages through 1999 (held constant within each term) and the EMBIG Argentina country-risk series ("riesgo país") from 2000 onward (e.g. 2002 ≈ 58%, 2023 ≈ 22%, 2025 ≈ 7.5%). The earlier non-like-for-like BCRA lending-rate splice for 2020+ has been replaced by the EMBIG continuation, so the modern period is consistent in units. A minor conceptual seam remains at the 1999/2000 join (term-average real rate → market country-risk spread).
- **Devaluation under the cepo now uses the free-market rate.** For 2012–2015 and 2019–2025 the official `PA.NUS.ATLS` rate was administratively suppressed (brecha up to ~+100% in 2022–23), so the notebook substitutes the annual-average CCL/blue rate from `parallel-cepo.csv`; the 2016–2018 float keeps the official rate. Two residual points remain: the non-cepo years use the official period-average rate (vs the paper's December paper-to-gold/USD quotation), and pre-2012 multiple-rate episodes (e.g. Perón III's 1975 *Rodrigazo*) still use the official rate for lack of a daily parallel series.
- The validation script is intentionally strict: it exits non-zero when the local files cannot satisfy the requested target year.
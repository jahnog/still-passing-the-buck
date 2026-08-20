# Argentina CMPI data lineage

Download and generate inventory, and the `data/raw`, `data/processed`, and
`data/provided` layout, are documented in [`data/README.md`](../README.md).
This file documents source, construction, coverage, and caveats for the
series. Path constants live in `data/paths.py`. The live series are the
`data/processed/` CSVs and the curated files in `data/provided/`.

## Principal series

- `data/processed/indicators/converted_indicators_wdi-argentina_*.csv.gz`:
  long-form Argentina indicators consumed by the notebook (WDI bulk zip plus
  World Bank API, INDEC, and BCRA overlays).
- `data/provided/data_a_1999.xlsx`: paper-author workbook (1853–1999).
- `data/processed/interest/converted_interest_wb-ids-arg_*.csv`: annual interest
  / country-risk series (paper term averages 1958–1997; EMBIG from 1998).
- `data/processed/inflation/converted_inflation_official-provincial-cpi_*.csv`:
  Santa Fe IPEC headline CPI chain with official CABA/San Luis overlap
  sensitivities.
- `data/processed/inflation/converted_inflation_cpi-wpi-blend_*.csv`: Dec/Dec
  CPI–IPIM blend (notebook §9 sensitivity).
- `data/processed/exchange/converted_exchange_parallel-cepo_*.csv`: free-market
  (CCL/blue) annual averages for the cepo years.
- `data/processed/exchange/converted_exchange_paper-devaluation_*.csv`:
  December-quotation devaluation log-diff, 1853–1999 (column E of
  `data_a_1999.xlsx`).
- `data/processed/exchange/converted_exchange_dec-dec_1999-01_2025-12.csv`:
  December quotations for 2000–2025.
- `data/processed/historical/converted_historical_historical-cmpi_*.csv`:
  CMPI term averages, 1852–1963.
- `data/processed/historical/converted_historical_data-a-1999-excel_*.csv`:
  annual Excel extract, 1853–1963.
- `data/processed/fiscal/converted_fiscal_fpi-fiscal_*.csv`: FPI operands and
  corrected headline columns, 1853–2025.

Fiscal add-backs, provenance CSVs, and the US real-yield series are under
`data/processed/` as listed in [`data/README.md`](../README.md).

Refresh order is in [`data/README.md`](../README.md). The indicator generator
melts Argentina rows from the World Bank WDI bulk zip, supplements CMPI/FPI
World Bank series from raw API JSON, and requires published World Bank 2025
observations. The interest generators preserve the 1958–1997 term-average rows,
continue EMBIG from BCRP JSON, and rebuild the 2003–2025 US real-yield leg from
Fed H.15. The exchange generator writes CCL/blue annual averages for cepo years.

## World Bank API supplements

`scripts/generate_indicators_wdi-argentina.py` supplements these codes from the
World Bank API:

- `FP.CPI.TOTL`
- `FP.CPI.TOTL.ZG`
- `NY.GDP.DEFL.KD.ZG`
- `NY.GDP.PCAP.KD.ZG`
- `NY.GDP.MKTP.CD`
- `NY.GDP.MKTP.KD`
- `NE.EXP.GNFS.CD`
- `NE.EXP.GNFS.KD`
- `BX.GSR.TOTL.CD`
- `TT.PRI.MRCH.XD.WD`
- `PA.NUS.ATLS`

## Official Argentine supplements

- `FP.CPI.TOTL`: INDEC IPC nacional from
  `https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv`,
  annualized from monthly `Codigo = 0`, `Region = Nacional` observations.
  Official IPC base is December 2016 = 100.
- `FP.CPI.TOTL.ZG`: derived from the same INDEC annual-average CPI levels for
  full-year observations.
- `FP.WPI.TOTL`: INDEC IPIM nivel general from `sipm-serie56-95.xls`,
  `sipm-dde1996.xls`, and `series_sipm_dic2015.xls`. The refresh chains the
  current reference-period series onto the historical series using the last
  available 2015 historical average, then rebases the combined annual index to
  2010 = 100 so year-over-year changes remain usable.
- `PA.NUS.ATLS`: official BCRA `TCNPM` monthly-average workbook
  `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls`,
  annualized for complete years.
- Interest, 1998 onward (`converted_interest_wb-ids-arg_*.csv`): EMBIG Argentina
  country-risk spread (*riesgo país*), annual average, from BCRP (Banco Central
  de Reserva del Perú) series `PD04710XD`, which redistributes J.P. Morgan's
  EMBIG. The BCRP series starts in January 1998. Annual averages for 1998
  (≈ 5.98%) and 1999 (≈ 7.20%) are taken from that series, as are later years
  (e.g. 2002 ≈ 57.9%, 2019 ≈ 13.2%, 2025 ≈ 7.5%). Through 1997 the generator
  keeps the original paper's within-term averages (`LEGACY_CUTOFF_YEAR` in
  `generate_interest_wb-ids-arg.py`).
- Cepo override (`converted_exchange_parallel-cepo_*.csv`): free-market ARS/USD
  annual averages for 2012–2015 and 2019–2025 from the argentinadatos.com API —
  CCL (`/v1/cotizaciones/dolares/contadoconliqui`), with the blue rate
  (`/v1/cotizaciones/dolares/blue`) filling 2012 (CCL is not quoted before
  2013). The BCRA publishes only the official A3500 rate. The notebook
  substitutes these for `PA.NUS.ATLS` on cepo years only; 2016–2018 keeps the
  official rate (*brecha* < 1%).

## Coverage

- `NY.GDP.DEFL.KD.ZG`: 1961–2025
- `PA.NUS.ATLS`: 1960–2025
- `NY.GDP.PCAP.KD.ZG`: 1961–2025 (World Bank)
- `FP.CPI.TOTL.ZG`: 2018–2025
- `FP.CPI.TOTL`: 2016–2025
- `FP.WPI.TOTL`: 1956–2025 (no 2001 observation; see caveats)
- Interest: 1958–2025 (EMBIG from 1998; paper term averages through 1997)
- Cepo override: 2012–2015 and 2019–2025

## 2007–2015 consumer prices

Between 2007 and 2015 INDEC falsified the official CPI (and IPIM). The IMF
issued a declaration of censure in February 2013; Commerce Secretary Guillermo
Moreno was criminally convicted for falsifying the data. The notebook corrects
**inflation only** for this window:

- `data/processed/inflation/converted_inflation_official-provincial-cpi_2007-01_2015-12.csv`
  uses the continuous official Santa Fe IPEC December-to-December chain as
  `AltAvg`, and therefore as the headline. CABA and San Luis populate
  sensitivity columns only where their retained official files overlap. They
  are not averaged into the headline.
- Santa Fe:
  <https://www.santafe.gov.ar/index.php/web/content/download/109537/540514/file/cIndice%20Pcia%202005-2013.xls>
  and
  <https://www.santafe.gov.ar/index.php/web/content/download/243468/1282154/version/2/file/1217.pdf>.
  CABA:
  <https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2022/02/Evol_gral_bs_svcios.xlsx>.
  San Luis:
  <https://estadistica.sanluis.gov.ar/documents/Economia/Precios/IPC%20San%20Luis/lbycc1cu.pdf>.
- `data/processed/provenance/converted_provenance_source-registry.csv` pins each
  artifact's bytes and SHA-256;
  `converted_provenance_row-source-links.csv` records the December-index formula
  and the source IDs feeding each annual row.
- Growth is not overridden. The World Bank `NY.GDP.*` series already embed
  INDEC's 2016 GDP revision: real GDP grows ~16.0% over 2008–2015, matching
  Coremberg/ARKLEMS (revised “new INDEC” 15.7% ≈ ARKLEMS 15.8%), not the
  manipulated 30.2%. Coremberg (2017) shows the overstatement was direct volume
  manipulation, not deflator-driven, so recomputing growth from CPI would be
  the wrong correction.

## Historical CMPI term averages (1852–1963)

`data/processed/historical/converted_historical_historical-cmpi_*.csv` provides
all four CMPI variables for 1852–1963.

Term averages from Table 3.1 of della Paolera, Irigoin & Bózzoli (2003) are held
flat for every year within each term — the same convention the notebook uses
for the interest series through 1999. The underlying annual series from the
paper's Appendix B sources are not publicly available; term averages are the
finest resolution the paper publishes.

Schema: `Year, Administration, Inflation, Devaluation, Interest, Growth` (raw
percent, not log-transformed; the notebook applies `ln(1+x/100)`). Coverage:
112 rows, 1852–1963. Year 1852 is the inherited baseline for the first
administration (Alsina 1853); its values are derived from Table 3.2 as
`baseline_1852 = actual_1853 − innovation_1853`. Generator:
`scripts/generate_historical_historical-cmpi.py`.

## Paper-method devaluation (1853–1999)

`data/processed/exchange/converted_exchange_paper-devaluation_*.csv` is column E
of `data_a_1999.xlsx` (147 rows, 1853–1999). The notebook uses it to override
the WDI annual-average exchange rate for 1964–1999, matching the paper's
sources.

WDI `PA.NUS.ATLS` is the annual period *average*. Mid-year devaluations blend
pre- and post-devaluation months and produce wrong inherited baselines for the
following administration. Documented cases include Guido (Nov-1963) → Illia
1964 (innovation sign flipped), Onganía (Jun-1966), and the Rodrigazo
(Jul-1975) → Videla 1976. The 1991 WDI average likewise blends January–March
(still depreciating Austral) with April–December (Convertibility at 1 ARS =
1 USD); December quotations separate the 1990–1991 depreciation from the
1992–1995 peg.

Sources by period (paper Appendix B):

- 1853–1959: Irigoin 2000a, Cortés Conde 1989, della Paolera & Ortiz 1995,
  Boletín Techint
- 1960–1989: average of December quotations from Ruíz (1990)
- 1990–1999: average of December quotations from DATAFIEL

Schema: `Year, DevaluationLog`. Generator:
`scripts/generate_exchange_paper-devaluation.py`. For 2000–2025 the notebook
uses `converted_exchange_dec-dec_1999-01_2025-12.csv` (Convertibility 1:1 for
1999–2001).

## Fiscal Pressure Index inputs (1852–2025)

`data/processed/fiscal/converted_fiscal_fpi-fiscal_1853-01_2025-12.csv` provides
four of the five FPI variables: `Debt_GDP`, `Debt_Exports`, `Result_Revenue`,
`Result_DebtServ`. The fifth, `(1+r)/(1+g)`, is computed in the notebook from
the interest and growth series.

Sources by period:

- **1853–1999, all columns:** `data_a_1999.xlsx`, columns G–J. The two
  primary-result ratios are missing for 1861–63 and are filled by arithmetic
  interpolation between the observed 1860 and 1864 endpoints, so every FPI
  component is scored over the same 173-year pool. Geometric interpolation is
  undefined because Result/Revenue changes sign. The source blanks remain
  grade C in `data-quality-flags.csv`. This complete-pool convention differs
  from the original Appendix A procedure of ranking observed innovations first
  and interpolating only the relative-index scores.
- **2000–2025, debt ratios:** total Sector Público Nacional gross debt from the
  Secretaría de Finanzas annual report (Sheet A.2.5, *Serie de Deuda del Sector
  Público Nacional 1992–2025*, `deuda_publica_31-12-{YEAR}.xlsx`), divided by
  World Bank nominal GDP (`NY.GDP.MKTP.CD`) and exports of goods and services
  (`BX.GSR.TOTL.CD`). Generation fails if either 2025 denominator is absent.
  Complete annual observations are used for 2025, but recent national-account
  values remain subject to source revisions.
- **2000–2025, primary-result ratios:** Sector Público Nacional cash-basis
  (*base caja*) primary result from datos.gob.ar SSPM dataset 379 (*Esquema AIF
  SPN Base Caja*), validated against Hacienda IMIG annual files for 2017–2018
  (0.000% deviation). No post-2000 baseline fiscal ratio is hardcoded: all
  2000–2025 ratios and operands are parsed from the committed dataset-379 CSVs
  (`data/raw/hacienda/spn-base-caja_valores-anuales_*.csv`) by
  `scripts/hacienda_spn_base_caja.load_spn_base_caja_actuals()`. Distribution
  379.3 is hash-pinned and supplies 2015–2025. `Result_Revenue` is primary
  result / current revenue; `Result_DebtServ` is primary result / net cash
  interest, with net interest checked against primary result minus financial
  result.
- **Cross-concept diagnostic:** the datos.gob.ar `totales-de-presupuesto` zip is
  the narrower Administración Nacional on an accrued basis. It is parsed at
  generation time as a revision tripwire and is never substituted for dataset
  379.
- **Official correction operands:** measured FGS/BCRA amounts from pinned BCRA
  annual reports (for example
  <https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/inf2009.pdf>);
  2016–2017 receipts from
  <https://contenidos.afip.gob.ar/institucional/estudios/archivos/informe.4.trimestre.2017.pdf>;
  2024 receipts from
  <https://www.afip.gob.ar/institucional/documentos/ARCA-Recaudacion-ANUAL2024.pdf>;
  2021 SDR booking from <https://opc.gob.ar/download/19142/>; 2024 capitalized
  interest from <https://opc.gob.ar/download/40009/?tmstv=1738608772>. The
  registry lists each additional annual or monthly URL with path, size, and
  SHA-256. The operational URL list is in [`data/README.md`](../README.md).
- **Importer-debt / BOPREAL:** 2022–2023 cumulative importer-debt increases from
  the BCRA RAyPE workbook
  <https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/ANEXODEUDAPRIVADA_6401.xlsx>
  on a common December-2021 baseline. 2024–2025 BOPREAL Series 1–3 residuals
  from Note 4.15 of the audited 2025 financial statements
  <https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/estados-contables-2025.pdf>.
  Series 4 is excluded because it also covers dividends and related-party
  obligations.
- **Measured correction columns (notebook §6.0 C–E):** `Debt_GDP_holdouts`,
  `Debt_Exports_holdouts`, `Debt_GDP_arrears`, `Debt_Exports_arrears`;
  `Result_Revenue_structural` and `Result_DebtServ_structural` from
  `converted_fiscal_official-one-offs_2009-01_2024-12.csv`;
  `Result_DebtServ_capitalized_interest` from
  `converted_fiscal_official-capitalized-interest_2024-01_2025-12.csv`. These
  feed the `*_corrected` headline columns. The `*_paper_extension` columns
  retain the original-study convention for audit.

Debt-stock corrections (2003–2025), notebook §6.0. The output carries
intermediate `Debt_GDP` / `Debt_Exports`, `Debt_GDP_corrected` /
`Debt_Exports_corrected`, and decomposition columns `Debt_GDP_official`,
`Debt_Exports_official`, `Cepo_Factor`, `BCRA_QuasiFiscal_GDP`:

- **(A) Cepo FX.** In exchange-control years (2012–2015, 2019–2025) the official
  peso was overvalued, inflating dollar GDP and understating Debt/GDP. The
  headline keeps the published USD Treasury stock and replaces official USD GDP
  with GDP converted at the free-market (CCL/blue) rate:
  `Debt/GDP_cepo = Debt/GDP_official × (parallel/official)`. BCRA remunerated
  liabilities are then added unscaled (already a peso/GDP ratio). The 50%
  exposure scenario is the conservative lower-bound sensitivity. Debt/Exports
  needs no FX correction (exports are USD).
- **(B) BCRA quasi-fiscal consolidation.** Remunerated peso liabilities
  (Lebac/Nobac → Leliq → Pases) are added to Treasury debt from
  `data/processed/fiscal/converted_fiscal_bcra-quasi-fiscal_*.csv`. Source
  anchors: Lebac Dec-2015 ≈ ARS 316.5bn; *pasivos remunerados* ≈ 10.4% of GDP
  (2021) and ≈ 10% (2023); Pases eliminated July 2024. Adding the stock once
  avoids double-counting a later migration of the same liabilities onto the
  Treasury.
- **(C) Corrected headline add-backs.** The `*_corrected` columns consolidate
  holdout debt, pair measured importer-debt increases with audited BOPREAL
  residuals, remove measured official one-off revenues, and rescale 2024–2025
  debt service using official OPC capitalized-interest operands. Mechanisms
  without retained official annual operands are disclosed and not scored.

The historical Excel uses a central-government debt concept; the 2000–2025
extension uses total Sector Público Nacional. The two are close but not
identical (notebook §11).

Rebuild with `make generate` (see [`data/README.md`](../README.md)).
`scripts/generate_fiscal_fpi-debt-adjustments.py` re-applies only the §6.0
corrections.

## Caveats

- World Bank 2025 growth, nominal GDP, exports, and the constant-price
  denominator series are published and required. Complete annual observations
  are used for 2025, but recent national-account values remain subject to source
  revisions; completeness is not a claim of finality.
- `FP.CPI.TOTL` is the national INDEC IPC only from December 2016 onward. The
  notebook's consumer-inflation series therefore uses the GDP deflator
  (`NY.GDP.DEFL.KD.ZG`) for roughly 1963–2016, except that 2007–2015 is the
  official Santa Fe IPEC chain. The deflator is a different concept from a
  household CPI. No reproducible 1964–2006 national CPI splice is in the
  package: INDEC historical IPC-GBA workbooks are not available as usable
  files, and the datos.gob.ar series API has no CPI before December 2006.
- The INDEC IPIM bridge from the historical base to the current
  reference-period workbook is chained with the last available 2015 historical
  average. Post-2015 annual changes are usable; the 2015 splice is a documented
  approximation.
- `FP.WPI.TOTL` has no 2001 observation (the IPIM workbooks expose only years
  with twelve complete months; 2001–02 is incomplete). The gap is left as NaN:
  a log-linear fill between 2000 and 2002 would inject a spurious ~+31% into
  2001 (a mildly deflationary year) and understate the 2002 devaluation jump.
  The notebook uses a NaN-robust price-component mean that falls back to the
  consumer-price change for 2001.
- The interest series stitches two constructs: the paper's real hard-currency
  term averages through 1997 (held constant within each term) and the EMBIG
  Argentina country-risk series from 1998 onward (e.g. 2002 ≈ 58%, 2023 ≈ 22%,
  2025 ≈ 7.5%). A conceptual seam remains at the 1997/1998 join (term-average
  real rate → market country-risk spread).
- Devaluation uses December quotations for the whole sample. For 2000–2025 the
  notebook scores the log-difference of December quotations
  (`converted_exchange_dec-dec_1999-01_2025-12.csv`: December TCNPM from the
  BCRA com3500 raw on free years; December CCL/blue daily averages on cepo years
  2012–2015 and 2019–2025; Convertibility 1:1 for 1999–2001), matching the
  paper's 1853–1999 December convention. An annual-average alternative
  (`PA.NUS.ATLS` with the CCL/blue annual-average cepo override) is the §9
  robustness variant and the §3.2 comparison series.
  Pre-2012 multiple-rate episodes (e.g. the 1975 Rodrigazo; 1946–55 and 1982–89
  exchange controls) still use the paper's quotations, whose coverage of
  parallel premia varies by era (notebook §3.0 row 5).
- `scripts/validate_cmpi_inputs.py` exits non-zero when the local files cannot
  satisfy the requested target year.

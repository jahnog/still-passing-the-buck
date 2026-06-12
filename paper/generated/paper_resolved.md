---
title: "Still Passing the Buck: Macroeconomic and Fiscal Performance of Argentine Administrations, 1853--2025"
author: "Javier Hernan Nogueira^[Independent researcher. Contact: <jahnog@gmail.com>. ORCID: [0009-0006-1945-7870](https://orcid.org/0009-0006-1945-7870). Replication package: <https://github.com/jahnog/still-passing-the-buck>. I thank Gerardo della Paolera, María Alejandra Irigoin, and Carlos G. Bózzoli, the authors of the original *Passing the buck* chapter, for generously sharing the dataset underlying their study, updated through 2018. All errors are my own.]"
date: "June 2026"
abstract: |
  We rank all 41 Argentine national administrations that governed between 1853
  and 2025 with the two indices proposed by @dellapaolera2003passing --- the
  Classical Macroeconomic Performance Index (CMPI) and the Fiscal Pressure
  Index (FPI) --- and their combined Overall Index, scoring each government by
  the macroeconomic and fiscal improvement it delivered over the situation it
  inherited. A single percentile pool of 173 annual observations places every
  administration, from the mid-nineteenth-century Confederation to the 2024--25
  stabilization, on a common scale. Extending the original 1853--1999 analysis
  through 2025 requires confronting documented distortions in modern Argentine
  statistics: we catalogue twenty-one manipulation and accounting practices,
  correct the affected series from independent and reproducible sources, and
  bound the judgment-dependent cases with sensitivity variants. On the
  restricted 1853--1999 pool the replication of the original rankings is almost
  exact (Spearman $\rho = 0.997$ for the FPI, $0.952$ for the CMPI). In the
  unified ranking Menem (1990--95) leads the CMPI and the Overall Index.
  Consolidating the central bank's quasi-fiscal debt into the public debt stock
  and valuing output at the free-market exchange rate during exchange-control
  years materially reorders the modern fiscal ranking. The long-run results
  confirm the original *passing-the-buck* thesis: administrations bought
  macroeconomic calm with debt --- on the Treasury's books or hidden in the
  central bank --- and passed the bill to their successors.

  **Keywords:** Argentina; economic history; macroeconomic performance;
  fiscal policy; inflation; public debt; statistical manipulation.

  **JEL classification:** C43; E31; E62; H63; N16; O54.
lang: en-US
fontsize: 11pt
papersize: a4
geometry: margin=2.8cm
mainfont: "TeX Gyre Pagella"
sansfont: "TeX Gyre Heros"
mathfont: "TeX Gyre Pagella Math"
numbersections: true
colorlinks: true
linkcolor: Mahogany
citecolor: Mahogany
urlcolor: Mahogany
link-citations: true
---

<!--
  HOW THIS FILE WORKS
  - This is pandoc Markdown. Edit prose freely; build with `make paper`.
  - Lines of the form "{{table" + ":NAME}}" are replaced at build time with tables
    extracted from the executed notebook (see scripts/build_paper.py), so the
    paper's numbers always match the pipeline. The caption line (": ...")
    must stay immediately below the directive.
  - Figures are PNGs extracted from the notebook into paper/generated/.
  - Citations use [@key] / @key with paper/references.bib (Chicago author-date).
  - Table/figure numbers in the prose are written manually ("Table 3"): if you
    reorder floats, update the references.
-->

# Introduction

> **How to read the indices.** The CMPI and FPI measure *improvement*
> relative to the situation inherited from the previous administration ---
> not absolute levels. Component scores are percentiles of annual innovations
> pooled over all 173 years: a score of 0.90 means the administration's
> average annual improvement sat in the top 10 percent of all improvements
> recorded since 1853. Rank 1 is best. See Section 3 for the formulas and
> three structural caveats, Section 7 for robustness, and the Glossary
> (Appendix E) for terminology.

How well did each Argentine government manage the economy it inherited? The
question dominates Argentine public debate, yet it is usually argued with
absolute outcomes --- inflation under one president against inflation under
another --- which conflates what a government did with what it received.
@dellapaolera2003passing proposed a comparative answer: score each
administration by the *improvement* it delivered over the macroeconomic and
fiscal situation bequeathed by its predecessor, and rank all administrations on
a common percentile scale. Their Classical Macroeconomic Performance Index
(CMPI) aggregates inflation, devaluation, the hard-currency interest rate, and
per-capita growth; their Fiscal Pressure Index (FPI) adds the management of the
intertemporal budget constraint; the average of the two is an Overall Index.
Applied to 33 administrations over 1853--1999, the framework produced the
central finding the authors summarized in their title: Argentine governments
repeatedly bought contemporaneous macroeconomic calm with fiscal pressure that
they passed to their successors.

This paper extends the complete two-index framework to the full 1853--2025
span --- 41 administrations and a percentile pool of 173 annual observations ---
placing the original 33 historical terms and the eight administrations of
2000--2025 on a single, internally consistent scale. The extension is not a
mechanical appending of recent data. Between 2007 and 2015 the national
statistical institute (INDEC) understated consumer-price inflation by a factor
of roughly three to four and overstated real growth, episodes that led to the
first declaration of censure in the history of the International Monetary Fund
[@imf2013censure; @cavallo2013; @coremberg2017]. Exchange controls in 2012--15
and 2019--25 pinned the official exchange rate far below the free-market rate.
Successive governments accumulated remunerated central-bank liabilities --- a
quasi-fiscal debt exceeding ten percent of GDP at its peaks --- that appears
in no Treasury debt statistic. Any ranking that ingests official series uncritically
reproduces these distortions. A second, subtler problem is internal to the
methodology: annual-average exchange rates produce wrong-signed devaluation
innovations around mid-year devaluations, an artefact that affects the
historical sample as well as the modern one.

Our contributions are four. First, we construct corrected 1853--2025 series for
the nine variables behind the two indices, documenting every known statistical
manipulation and accounting practice that materially affects them --- a
twenty-one-entry catalogue (Section 4, Appendix B) stating the direction of
each bias and its treatment. Corrections enter the baseline only when an
independent, reproducible source exists (alternative price indices, free-market
exchange quotations, revised national accounts, central-bank balance sheets);
judgment-dependent adjustments enter only as sensitivity variants, reported
whichever administration they favour. Second, we resolve the annual-average
devaluation artefact by using December-quotation exchange-rate series for the
entire sample. Third, we extend the FPI with two corrections to the modern
debt-stock components: a free-market revaluation of GDP during
exchange-control years, and the consolidation of the central bank's
remunerated liabilities into the public debt stock. Fourth, we validate the
implementation by replicating the original published rankings on the
restricted 1853--1999 pool, obtaining Spearman rank correlations of $0.997$
(FPI) and $0.952$ (CMPI) against the original Table 3.4.

The headline results place Menem (1990--95) first on the CMPI and the Overall
Index, with the 2024--25 stabilization and Obligado's 1854--56 reforms close
behind, and crisis terms at the bottom --- consistent with the original
finding that durable hard-currency and convertible stabilizations score
highest. The fiscal corrections are decisive for the modern ranking: once the
central bank's hidden debt is consolidated and the exchange-control distortion
removed, the administrations that *built up* quasi-fiscal liabilities fall to
the bottom of the FPI, while the 2024--25 consolidation registers as a sharp
reduction in fiscal pressure rather than the spurious increase shown by the
raw Treasury series. The long-run picture confirms the *passing-the-buck*
dynamic over 173 years.

The paper proceeds as follows. Section 2 situates the contribution in the
literature. Section 3 presents the methodology. Section 4 describes the data
and the corrections. Section 5 reports the rankings. Section 6 validates the
implementation against the original study. Section 7 reports robustness
exercises. Sections 8--10 discuss interpretation, limitations, and
conclusions. A complete replication package accompanies the paper
(Appendix A).

# Related literature

The paper extends @dellapaolera2003passing, chapter 3 of *A New Economic
History of Argentina* [@dellapaolera2003newhistory], which built the CMPI and
FPI for 1853--1999. The long-run quantitative history of Argentine money and
finance on which that chapter rests includes @dellapaolera2001straining on the
currency-board era, @dellapaolera1994experimentos and @cortesconde1989dinero
on nineteenth-century monetary and fiscal experiments, @irigoin2000 and
@amaral1988 on the early inflationary-finance period, and the long statistical
series compiled by @ferreres2010dossiglos. General economic histories of the
period include @gerchunoffllach1998 and @rapoport2000.

The measurement problems of modern Argentine statistics have their own
literature. @cavallo2013 documents the 2007--2015 INDEC consumer-price
intervention using online prices; @cavallorigobon2016 generalize the
methodology; @coremberg2017 quantifies the parallel overstatement of real
output growth; the IMF's declaration of censure [@imf2013censure] is the
institutional landmark. Our contribution to this strand is practical: a
documented, reproducible mapping from each known distortion to its effect on a
long-run performance ranking --- including the quasi-fiscal liabilities and
exchange-control wedges that standard debt and exchange-rate series omit.

The theoretical background of the indices --- seigniorage and the inflation
tax, the intertemporal budget constraint, and currency-crisis contagion --- is
the classical one [@sargent1986rational; @defiore2000; @ennis2007;
@eichengreen1996contagious].

Two further strands frame the interpretation. The fiscal-dominance tradition
descending from @sargentwallace1981 supplies the mechanism behind the
*passing-the-buck* finding: when the fiscal authority does not internalize
the intertemporal budget constraint, the monetary authority eventually
finances the gap, and inflation becomes a fiscal phenomenon. The comparative
project of @kehoenicolini2021 applies exactly this lens to eleven Latin
American countries; its Argentina chapter [@bueranicolini2021argentina] reads
six decades of inflation, default, and stabilization as the monetary
consequence of persistent fiscal imbalance --- the regional pattern of which
Argentina is the extreme case, and the same dynamic the FPI traces
administration by administration. On the political-economy side,
@spillertommasi2007 document why the dynamic persists: Argentine institutions
give policymakers unusually short horizons and weak technologies for
enforcing intertemporal agreements, so costs shifted past one's own term are
heavily discounted. Finally, the treatment of central-bank operations as
fiscal policy in disguise follows the public-finance tradition of
@mackenziestella1996; the modern Argentine remunerated-liability stock that
Section 4 consolidates is documented in the IMF's program reports
[@imf2022argentina].

# Methodology

## The Classical Macroeconomic Performance Index

The CMPI aggregates four classical variables: **inflation**, linked to the
government's high-powered-money policy and seigniorage; **devaluation**, the
willingness to defend the external value of the currency; the **real interest
rate on hard currency**, a proxy for country risk and external credit
tightness; and **per-capita growth**, the administration's influence on the
pace of real activity.

For each variable and year we compute the **innovation**: the value in that
year minus the value in the *last year of the previous administration* --- the
inherited, or "legacy," condition. Each annual innovation is converted to a
percentile rank across all $O$ years in the pool using the original Appendix A
formula $R = (O - o)/O$, where $o$ is the innovation's position in the ranking
(best $=1$): the best innovation in the pool scores $(O-1)/O \approx 0.994$
and the worst scores $0$. An administration's CMPI is the average of its four
percentile scores over its term; higher is better. Inflation and devaluation
enter as continuously compounded rates $\ln(1+x)$, which prevents extreme
episodes from dominating the index.

To be concrete: a year in which inflation fell from an inherited 40 percent to
10 percent produces an innovation of roughly $-0.36$ log-points. This scores
near the top of the percentile distribution and contributes to a high CMPI
*regardless of whether 10 percent is "low" in absolute terms*. The comparative
design is what makes the index informative about governance rather than about
inherited luck.

## The Fiscal Pressure Index

The CMPI captures contemporaneous performance, but for a peripheral economy
with recurrent debt crises this is insufficient. The FPI ranks administrations
by their management of the intertemporal budget constraint, built on the
first-order difference equation for the debt ratio that drives the original
study's transversality condition:

$$\frac{B_t}{Y_t} = \frac{1+r_t}{1+g_t}\,\frac{B_{t-1}}{Y_{t-1}} + \frac{DEF_t}{Y_t},$$

where $B/Y$ is the debt-to-GDP ratio, $r$ the real interest rate, $g$ the
growth rate, and $DEF$ the primary deficit. The FPI aggregates five
indicators, each scored exactly like the CMPI as an innovation percentile:
**debt/GDP** (the burden relative to activity), **debt/exports** (the burden
relative to repayment capacity), **primary result/revenues** (net fiscal
management, discounting inherited debt service), **primary result/debt
service** (resources available to service the debt), and **$(1+r)/(1+g)$**
(the amplifying factor on the debt ratio; values above one mean the debt
ratio grows automatically even with a balanced primary budget). High
indebtedness or an unbalanced budget is a "hot potato" passed to successors;
the opposite is a positive externality future governments inherit.

Following the original Table 3.4, the **Overall Index** ranks administrations
by the simple average of their CMPI and FPI scores. The exact formulas behind
every step --- innovations, percentile assignment, aggregation, and the two
debt-stock corrections --- are collected in Appendix D.

## How to read the ranking: three structural caveats

The method has three properties that every reader should hold in mind. They
are features of the original design, applied uniformly to all 41
administrations --- not data corrections, and not fixable without changing
what the index measures.

1. **Improvement is not the end state.** The index scores each year against
   the situation *inherited*, averaged over the term --- not the state in
   which an administration leaves the country. A term that inherits a
   catastrophe and stabilizes it scores high even if absolute conditions
   remain poor; a term that inherits calm and ends in crisis scores low even
   if its average year was comfortable. Section 8 discusses the clearest
   modern case.

2. **Term averages favour short corrective shocks.** Stabilizations
   front-load their best macroeconomic years, so a two-year term can outscore
   four-to-six-year terms that include later decay. Section 7 re-scores every
   administration on its first two years only, putting partial terms on an
   equal footing.

3. **Single-year inherited baselines amplify V-shaped shocks.** Because every
   year of a term is measured against the predecessor's *last* year, a
   collapse-and-rebound pair inside one term (COVID: $-10.3$ percent
   per-capita growth in 2020, $+10.2$ percent in 2021) is lightly penalized on
   the way down and fully rewarded on the way back. Section 7 includes a
   variant that drops 2020--21 from the percentile pool.

## Administration boundaries

The 41 terms follow the original intervals exactly where the two studies
overlap (33 terms, 1853--1999), including the rule of assigning each year to
whoever ruled the larger part of it. Conventions carried over from the
original study: single-year caretaker terms are kept separate when
conventionally distinguished (Alsina 1853, Uriburu 1931, Guido 1962--63);
military juntas are presented as one term (1976--83); civilian transition
periods with rapid turnover are combined. For 2000--2025, beyond the original
span, 2001--03 is split as De la Rúa (to 2001) and Duhalde (2002--03) to
separate the crisis trough from the stabilization --- the single deliberate
exception to the majority-of-year rule, which keeps the post-default
stabilization program in one piece. The 2024--25 term is partial by
construction and is decomposed year by year in Section 6. A sensitivity
experiment merging the shortest one-year terms into their neighbours moved
only bottom CMPI ranks and left the top ten and all FPI and Overall top-five
positions unchanged.

# Data

## Two data regimes

The series combine two regimes. For **1852--1963** we use the original
authors' annual dataset (`data_a_2018.xlsx`) directly: inflation and
devaluation as annual log-differences, per-capita growth, and the four fiscal
ratios. Interest rates use the published term averages of the original Table
3.1, since the dataset contains no annual interest series; the 1852 baseline
is derived from the original Table 3.2. For **1964--2025** we use annual
values from the World Bank World Development Indicators [@worldbank_wdi],
INDEC price and national-accounts series, the EMBIG Argentina country-risk
spread from 1998 [@bcrp_embig], total Sector Público Nacional gross debt from
the Secretaría de Finanzas [@secfinanzas_deuda], and budget execution from
the national open-data portal [@datosgobar_presupuesto]. Free-market
exchange-rate quotations for the exchange-control years come from public
APIs [@argentinadatos_fx] and the December-quotation devaluation series for
1960--1999 from @ruiz1990dolar and the original dataset.

Figure 1 maps data reliability by year and variable; the full lineage of
every series is documented in the replication package.

![Data reliability by year and variable across the nine index inputs. Letters grade source quality; the catalogue in Appendix B documents every flagged episode.](generated/fig_quality.png){width=100%}

## Statistical integrity: known manipulations and their treatment

An honest comparison of Argentine administrations must confront a hard fact:
several governments distorted the statistics themselves, or used fiscal and
monetary accounting that flatters the headline numbers while shifting costs
off the books. Appendix B catalogues every such practice known to materially
affect the nine variables behind the CMPI and FPI --- twenty-one entries
spanning 1931--2025 --- stating for each the direction of the bias and its
treatment here.

The treatment discipline is uniform. **Corrected** practices are fixed in the
baseline series, with the official series kept as an audit column and an
official-versus-corrected comparison chart beside each correction, so the size
of the distortion is visible rather than asserted. **Sensitivity** practices
involve judgment-dependent estimates, so they enter as documented memo columns
and re-ranked variants --- never silent baseline changes --- reported
whichever administration they favour. **Documented** practices are outside the
nine index variables or not confidently quantifiable, and are flagged for the
reader. No adjustment relies on the say-so of any government, including the
current one.

Four corrections carry the baseline:

**Consumer prices, 2007--2015.** The INDEC intervention understated inflation
roughly three- to four-fold; the episode ended in the IMF censure
[@imf2013censure] and a criminal conviction of the responsible Commerce
Secretary. The baseline replaces 2007--2015 official inflation with the
average of alternative indices (IPC Congreso, San Luis, CABA, Santa Fe),
consistent with the online-price evidence of @cavallo2013. Figure 2 shows the
official series against the alternatives.

![Official INDEC consumer-price inflation versus alternative provincial and private indices, 2007--2015. The baseline uses the alternative average; the official series is retained as an audit column.](generated/fig_inflation.png){width=100%}

**Real output growth, 2007--2015.** The base-1993 national accounts overstated
volume growth (2008 official $+6.8$ versus revised $+3.1$ percent; 2009
$+0.9$ versus $-5.9$). The World Bank series used here embed INDEC's 2016
revision, whose cumulative 2008--15 correction matches the independent
ARKLEMS reconstruction [@coremberg2017]. Figure 3 compares the vintages.

![Official base-1993 real growth versus the 2016-revision series, 2005--2015.](generated/fig_gdp.png){width=100%}

**Devaluation: December quotations for the full sample.** Annual-average
exchange rates blend pre- and post-devaluation months, producing wrong-signed
innovations around mid-year devaluations. We use December quotations for the
entire 1853--2025 span: the original authors' series to 1999 (which embeds
the free-market *dólar libre* of @ruiz1990dolar for 1960--89), then December
BCRA wholesale rates in free years and December free-market (CCL/blue)
averages in exchange-control years from 2000. Section 6 shows that this
choice reproduces the original published devaluation innovations exactly for
the four terms affected by mid-year devaluations.

**Exchange-control wedges.** During the *cepo* years (2012--15, 2019--25) the
official rate was administratively pinned with a free-market premium that
reached 100 percent. Measuring the regime by its deeds rather than its words
[@levyyeyatisturzenegger2005], devaluation uses free-market December averages
(Figure 4); the fiscal corrections below remove the parallel distortion of the
dollar-valued GDP in the debt ratios.

![Official versus free-market (CCL/blue) exchange rate during the exchange-control years; the premium ("brecha") reached 100 percent.](generated/fig_cepo.png){width=100%}

## Two corrections to the modern debt stock

The FPI's two debt-stock components require corrections that no official
series provides.

First, the **exchange-control revaluation**: during cepo years the
dollar-valued GDP in the debt/GDP denominator is inflated by the artificially
low official rate. The correction revalues output at the free-market rate,
bounded from below by a conservative variant that assumes only half the debt
stock is foreign-currency-linked, and complemented by a variant using the
measured currency composition of the debt (Section 7).

Second, the **consolidation of quasi-fiscal debt**: from 2002 the central
bank sterilized monetary emission with remunerated liabilities (Lebac/Nobac,
then Leliq, then Pases) that repeatedly exceeded ten percent of GDP ---
economically public debt, but absent from every Treasury statistic. The
correction adds the measured year-end stock (BCRA statistical-API series,
December observations) to the public debt of 2003--2025. Figure 5
shows the layered debt stock; Figure 6 shows the associated quasi-fiscal
interest flow, which never enters the Treasury's primary result.

Table 1 summarizes both corrections by administration. The corrections are
decisive for the modern fiscal ranking (Section 5), and symmetric: they
penalize the administrations that accumulated hidden liabilities and credit
those that consolidated them, whichever side of the political spectrum either
falls on.

| Administration | Years | Debt/GDP off. | Cepo x | BCRA % GDP | Debt/GDP adj. |
|:-----------------------|-----------:|------------:|--------:|--------:|------------:|
| Duhalde | 2002-2003 | 1.630 | 1.000 | 1.712 | 1.647 |
| N.Kirchner | 2004-2007 | 0.843 | 1.000 | 5.404 | 0.897 |
| C.Kirchner | 2008-2011 | 0.454 | 1.000 | 4.270 | 0.497 |
| C.Kirchner II | 2012-2015 | 0.453 | 1.397 | 4.563 | 0.680 |
| Macri | 2016-2019 | 0.670 | 1.025 | 7.217 | 0.760 |
| Fernandez | 2020-2023 | 0.703 | 1.857 | 11.387 | 1.403 |
| Milei | 2024-2025 | 0.703 | 1.184 | 0.013 | 0.836 |
: Exchange-control factor and central-bank quasi-fiscal debt by administration (term means). "Cepo x" is the free-market/official revaluation factor applied to dollar GDP; "BCRA % GDP" is the remunerated-liability stock consolidated into public debt.

![Public debt layers, 2001--2025: official Treasury stock, exchange-control revaluation, and consolidated central-bank remunerated liabilities.](generated/fig_debt-layers.png){width=100%}

![The quasi-fiscal flow: central-bank interest on remunerated liabilities, which enters no Treasury primary result.](generated/fig_quasi-fiscal.png){width=100%}

The same discipline governs the primary-balance components: one-off revenues
booked above the line (pension-fund nationalization flows, SDR allocations,
tax amnesties, export-duty advances) and accounting practices that flatter
the cash result (unpaid interest during default, capitalizing instruments in
2024--25) are documented per-row with sources, and enter re-ranked
sensitivity variants (Section 7). Figure 7 contrasts the official and
structural primary results.

![Official versus structural primary result: one-off and accounting-driven revenues removed.](generated/fig_primary.png){width=100%}

# Results

## Contemporaneous macroeconomic performance

The CMPI ranking of all 41 administrations is reported in Table 2. Menem
(1990--95) ranks first, the 2024--25 stabilization second, and Obligado
(1854--56) third; the bottom of the table collects the crisis terms ---
Alsina (1853) last, preceded by Guido (1962--63) and the second Cristina
Kirchner term (2012--15), with the hyperinflation endgame of Alfonsín
(1984--89) close behind.

| Administration | Rank | Years | Regime | Inflation | Devaluation | Interest | Growth | CMPI |
|:----------------------------------------|--------:|-----------:|------------:|-------------:|---------------:|------------:|----------:|--------:|
| Menem | 1 | 1990–1995 | Modern | 0.975 | 0.980 | 0.858 | 0.812 | 0.906 |
| Milei | 2 | 2024–2025 | Modern | 0.514 | 0.928 | 0.974 | 0.598 | 0.754 |
| Obligado | 3 | 1854–1856 | Historical | 0.784 | 0.778 | 0.520 | 0.915 | 0.750 |
| Menem II | 4 | 1996–1999 | Modern | 0.676 | 0.610 | 0.957 | 0.676 | 0.730 |
| Perón II | 5 | 1952–1955 | Historical | 0.880 | 0.871 | 0.546 | 0.436 | 0.684 |
| Justo | 6 | 1932–1937 | Historical | 0.342 | 0.831 | 0.720 | 0.805 | 0.675 |
| Sarmiento | 7 | 1869–1874 | Historical | 0.432 | 0.554 | 0.928 | 0.663 | 0.644 |
| Roca | 8 | 1881–1886 | Historical | 0.917 | 0.310 | 0.754 | 0.504 | 0.621 |
| Mitre | 9 | 1860–1868 | Historical | 0.401 | 0.435 | 0.798 | 0.665 | 0.575 |
| Ramírez/Farrell | 10 | 1943–1945 | Historical | 0.547 | 0.607 | 0.601 | 0.472 | 0.557 |
| Ongania | 11 | 1967–1969 | Modern | 0.684 | 0.663 | 0.145 | 0.699 | 0.548 |
| Pellegrini | 12 | 1891–1892 | Historical | 0.592 | 0.688 | 0.384 | 0.520 | 0.546 |
| Yrigoyen | 13 | 1917–1922 | Historical | 0.681 | 0.490 | 0.332 | 0.680 | 0.546 |
| Peron III | 14 | 1973–1975 | Modern | 0.528 | 0.303 | 0.832 | 0.516 | 0.545 |
| Avellaneda | 15 | 1875–1880 | Historical | 0.403 | 0.508 | 0.298 | 0.954 | 0.540 |
| Videla/Viola/Galtieri/Bignone | 16 | 1976–1983 | Modern | 0.576 | 0.871 | 0.182 | 0.502 | 0.533 |
| N.Kirchner | 17 | 2004–2007 | Modern | 0.513 | 0.178 | 0.968 | 0.465 | 0.531 |
| Ortiz/Castillo | 18 | 1938–1942 | Historical | 0.686 | 0.295 | 0.890 | 0.250 | 0.530 |
| Sáenz Peña R./de la Plaza | 19 | 1911–1916 | Historical | 0.613 | 0.579 | 0.627 | 0.243 | 0.515 |
| Quintana/Figueroa | 20 | 1905–1910 | Historical | 0.432 | 0.544 | 0.668 | 0.224 | 0.467 |
| Aramburu | 21 | 1956–1957 | Historical | 0.260 | 0.864 | 0.396 | 0.329 | 0.462 |
| Fernandez | 22 | 2020–2023 | Modern | 0.431 | 0.623 | 0.092 | 0.561 | 0.427 |
| Perón I | 23 | 1946–1951 | Historical | 0.321 | 0.213 | 0.454 | 0.719 | 0.427 |
| De la Rua | 24 | 2000–2001 | Modern | 0.416 | 0.529 | 0.251 | 0.500 | 0.424 |
| Roca II | 25 | 1899–1904 | Historical | 0.471 | 0.329 | 0.488 | 0.400 | 0.422 |
| Juárez Celman | 26 | 1887–1890 | Historical | 0.386 | 0.341 | 0.251 | 0.689 | 0.417 |
| Frondizi | 27 | 1958–1961 | Historical | 0.415 | 0.403 | 0.367 | 0.442 | 0.407 |
| Yrigoyen II | 28 | 1929–1930 | Historical | 0.630 | 0.358 | 0.408 | 0.228 | 0.406 |
| Illia | 29 | 1964–1966 | Modern | 0.497 | 0.133 | 0.272 | 0.713 | 0.404 |
| Uriburu JF | 30 | 1931–1931 | Historical | 0.480 | 0.341 | 0.422 | 0.353 | 0.399 |
| Macri | 31 | 2016–2019 | Modern | 0.395 | 0.423 | 0.421 | 0.316 | 0.389 |
| Alsina II | 32 | 1857–1859 | Historical | 0.538 | 0.620 | 0.231 | 0.067 | 0.364 |
| Sáenz Peña L./Uriburu JE | 33 | 1893–1898 | Historical | 0.141 | 0.382 | 0.575 | 0.296 | 0.349 |
| C.Kirchner | 34 | 2008–2011 | Modern | 0.575 | 0.412 | 0.082 | 0.286 | 0.339 |
| Levingston/Lanusse | 35 | 1970–1972 | Modern | 0.185 | 0.108 | 0.694 | 0.197 | 0.296 |
| Alfonsin | 36 | 1984–1989 | Modern | 0.396 | 0.448 | 0.026 | 0.274 | 0.286 |
| De Alvear | 37 | 1923–1928 | Historical | 0.278 | 0.357 | 0.118 | 0.378 | 0.283 |
| Duhalde | 38 | 2002–2003 | Modern | 0.116 | 0.410 | 0.003 | 0.523 | 0.263 |
| C.Kirchner II | 39 | 2012–2015 | Modern | 0.366 | 0.146 | 0.276 | 0.228 | 0.254 |
| Guido | 40 | 1962–1963 | Historical | 0.237 | 0.390 | 0.217 | 0.075 | 0.230 |
| Alsina | 41 | 1853–1853 | Historical | 0.104 | 0.145 | 0.416 | 0.000 | 0.166 |
: The Classical Macroeconomic Performance Index, all 41 administrations, 1853--2025. Component columns are mean innovation percentiles over the term; the pool is 173 annual observations.

## Fiscal pressure

Table 3 reports the FPI. Obligado (1854--56) leads, with the 2024--25 term
second and Roca II (1899--1904) third. The two debt-stock corrections of
Section 4.3 drive the modern reordering: the 2023 inherited baseline carries
both the peso overvaluation (a factor near two) and some thirteen percent of
GDP in central-bank debt at the December 2023 year-end, against which the
2024--25 consolidation and
record primary surplus register as a sharp *reduction* in fiscal pressure ---
rather than the spurious debt increase shown by the raw Treasury series ---
while the administrations that grew the quasi-fiscal stock (2020--23 and
2012--15) fall to the bottom of the table. Néstor Kirchner (2004--07)
remains high on the FPI because the 2005 restructuring --- among the deepest
haircuts in the modern sovereign-debt record [@sturzeneggerzettelmeyer2008]
--- cut the far larger Treasury debt even as sterilization began: the
consolidation captures the build-up without letting it overwhelm a genuine
deleveraging.

| Administration | Rank | Years | Debt / GDP | Debt / Exp | Res / Rev | Res / DebtSv | (1+r) / (1+g) | FPI |
|:----------------------------------------|--------:|-----------:|--------:|--------:|-------:|----------:|---------:|-------:|
| Obligado | 1 | 1854–1856 | 0.696 | 0.696 | 0.967 | 0.936 | 0.929 | 0.845 |
| Milei | 2 | 2024–2025 | 0.945 | 0.737 | 0.740 | 0.838 | 0.818 | 0.816 |
| Roca II | 3 | 1899–1904 | 0.716 | 0.895 | 0.962 | 0.888 | 0.417 | 0.776 |
| N.Kirchner | 4 | 2004–2007 | 0.941 | 0.970 | 0.480 | 0.500 | 0.877 | 0.753 |
| Menem | 5 | 1990–1995 | 0.968 | 0.561 | 0.629 | 0.609 | 0.838 | 0.721 |
| Perón I | 6 | 1946–1951 | 0.795 | 0.961 | 0.740 | 0.297 | 0.685 | 0.695 |
| Avellaneda | 7 | 1875–1880 | 0.819 | 0.549 | 0.515 | 0.501 | 0.952 | 0.667 |
| Mitre | 8 | 1860–1868 | 0.324 | 0.389 | 0.905 | 0.969 | 0.695 | 0.656 |
| Yrigoyen | 9 | 1917–1922 | 0.601 | 0.773 | 0.636 | 0.611 | 0.618 | 0.648 |
| Uriburu JF | 10 | 1931–1931 | 0.630 | 0.780 | 0.751 | 0.682 | 0.347 | 0.638 |
| Ongania | 11 | 1967–1969 | 0.480 | 0.403 | 0.663 | 0.848 | 0.561 | 0.591 |
| Videla/Viola/Galtieri/Bignone | 12 | 1976–1983 | 0.416 | 0.232 | 0.879 | 0.876 | 0.405 | 0.562 |
| Sarmiento | 13 | 1869–1874 | 0.266 | 0.401 | 0.559 | 0.693 | 0.697 | 0.523 |
| Illia | 14 | 1964–1966 | 0.491 | 0.486 | 0.445 | 0.435 | 0.647 | 0.501 |
| Menem II | 15 | 1996–1999 | 0.399 | 0.630 | 0.363 | 0.322 | 0.772 | 0.497 |
| Frondizi | 16 | 1958–1961 | 0.676 | 0.595 | 0.428 | 0.328 | 0.400 | 0.486 |
| Sáenz Peña L./Uriburu JE | 17 | 1893–1898 | 0.803 | 0.528 | 0.357 | 0.350 | 0.352 | 0.478 |
| Aramburu | 18 | 1956–1957 | 0.595 | 0.572 | 0.460 | 0.422 | 0.335 | 0.477 |
| C.Kirchner | 19 | 2008–2011 | 0.795 | 0.757 | 0.269 | 0.360 | 0.198 | 0.476 |
| Quintana/Figueroa | 20 | 1905–1910 | 0.804 | 0.802 | 0.159 | 0.226 | 0.320 | 0.462 |
| Pellegrini | 21 | 1891–1892 | 0.127 | 0.419 | 0.552 | 0.656 | 0.465 | 0.444 |
| De Alvear | 22 | 1923–1928 | 0.304 | 0.497 | 0.562 | 0.582 | 0.275 | 0.444 |
| Levingston/Lanusse | 23 | 1970–1972 | 0.426 | 0.659 | 0.326 | 0.455 | 0.316 | 0.436 |
| Perón II | 24 | 1952–1955 | 0.384 | 0.158 | 0.422 | 0.697 | 0.471 | 0.426 |
| Justo | 25 | 1932–1937 | 0.253 | 0.104 | 0.467 | 0.466 | 0.814 | 0.421 |
| Sáenz Peña R./de la Plaza | 26 | 1911–1916 | 0.290 | 0.549 | 0.405 | 0.477 | 0.311 | 0.406 |
| Alfonsin | 27 | 1984–1989 | 0.286 | 0.189 | 0.843 | 0.633 | 0.066 | 0.403 |
| Macri | 28 | 2016–2019 | 0.514 | 0.377 | 0.389 | 0.402 | 0.306 | 0.398 |
| De la Rua | 29 | 2000–2001 | 0.298 | 0.564 | 0.355 | 0.376 | 0.361 | 0.391 |
| Peron III | 30 | 1973–1975 | 0.451 | 0.638 | 0.067 | 0.110 | 0.582 | 0.370 |
| Roca | 31 | 1881–1886 | 0.549 | 0.366 | 0.132 | 0.182 | 0.559 | 0.358 |
| Ortiz/Castillo | 32 | 1938–1942 | 0.607 | 0.117 | 0.280 | 0.298 | 0.434 | 0.347 |
| Ramírez/Farrell | 33 | 1943–1945 | 0.364 | 0.584 | 0.116 | 0.148 | 0.522 | 0.347 |
| Guido | 34 | 1962–1963 | 0.434 | 0.896 | 0.133 | 0.092 | 0.104 | 0.332 |
| Yrigoyen II | 35 | 1929–1930 | 0.630 | 0.344 | 0.199 | 0.228 | 0.257 | 0.332 |
| Juárez Celman | 36 | 1887–1890 | 0.124 | 0.210 | 0.312 | 0.279 | 0.620 | 0.309 |
| C.Kirchner II | 37 | 2012–2015 | 0.116 | 0.223 | 0.288 | 0.347 | 0.221 | 0.239 |
| Alsina II | 38 | 1857–1859 | 0.210 | 0.514 | 0.195 | 0.177 | 0.083 | 0.236 |
| Duhalde | 39 | 2002–2003 | 0.003 | 0.127 | 0.503 | 0.486 | 0.017 | 0.227 |
| Fernandez | 40 | 2020–2023 | 0.032 | 0.301 | 0.214 | 0.133 | 0.368 | 0.210 |
| Alsina | 41 | 1853–1853 | 0.017 | 0.110 | 0.000 | 0.017 | 0.006 | 0.030 |
: The Fiscal Pressure Index, all 41 administrations. Components are innovation percentiles of debt/GDP, debt/exports, primary result/revenues, primary result/debt service, and $(1+r)/(1+g)$.

## The Overall Index

Table 4 combines the two indices. Menem (1990--95) remains first, Obligado
second, and the 2024--25 term third. The joint reading exposes the central
*passing-the-buck* dynamic: administrations with a high CMPI rank paired with
a low FPI rank bought macroeconomic calm with debt --- on the Treasury's
books or hidden in the central bank --- and handed the bill to their
successors. The 2024--25 term is unusual in the modern era for ranking in
the top tier on both dimensions, with the caveats of Sections 6 and 8: the
term is partial, and two measurement conventions that favour it are flagged
symmetrically with the Kirchner-era corrections.

| Administration | Rank | Years | CMPI Rank | FPI Rank | CMPI | FPI | Overall | Borda Rank |
|:----------------------------------------|--------:|-----------:|--------:|--------:|--------:|-------:|-----------:|---------:|
| Menem | 1 | 1990–1995 | 1 | 5 | 0.906 | 0.721 | 0.814 | 3 |
| Obligado | 2 | 1854–1856 | 3 | 1 | 0.750 | 0.845 | 0.797 | 1 |
| Milei | 3 | 2024–2025 | 2 | 2 | 0.754 | 0.816 | 0.785 | 2 |
| N.Kirchner | 4 | 2004–2007 | 17 | 4 | 0.531 | 0.753 | 0.642 | 7 |
| Mitre | 5 | 1860–1868 | 9 | 8 | 0.575 | 0.656 | 0.616 | 4 |
| Menem II | 6 | 1996–1999 | 4 | 15 | 0.730 | 0.497 | 0.613 | 5 |
| Avellaneda | 7 | 1875–1880 | 15 | 7 | 0.540 | 0.667 | 0.604 | 8 |
| Roca II | 8 | 1899–1904 | 25 | 3 | 0.422 | 0.776 | 0.599 | 11 |
| Yrigoyen | 9 | 1917–1922 | 13 | 9 | 0.546 | 0.648 | 0.597 | 9 |
| Sarmiento | 10 | 1869–1874 | 7 | 13 | 0.644 | 0.523 | 0.583 | 6 |
| Ongania | 11 | 1967–1969 | 11 | 11 | 0.548 | 0.591 | 0.569 | 10 |
| Perón I | 12 | 1946–1951 | 23 | 6 | 0.427 | 0.695 | 0.561 | 13 |
| Perón II | 13 | 1952–1955 | 5 | 24 | 0.684 | 0.426 | 0.555 | 14 |
| Justo | 14 | 1932–1937 | 6 | 25 | 0.675 | 0.421 | 0.548 | 15 |
| Videla/Viola/Galtieri/Bignone | 15 | 1976–1983 | 16 | 12 | 0.533 | 0.562 | 0.547 | 12 |
| Uriburu JF | 16 | 1931–1931 | 30 | 10 | 0.399 | 0.638 | 0.518 | 19 |
| Pellegrini | 17 | 1891–1892 | 12 | 21 | 0.546 | 0.444 | 0.495 | 16 |
| Roca | 18 | 1881–1886 | 8 | 31 | 0.621 | 0.358 | 0.489 | 17 |
| Aramburu | 19 | 1956–1957 | 21 | 18 | 0.462 | 0.477 | 0.470 | 18 |
| Quintana/Figueroa | 20 | 1905–1910 | 20 | 20 | 0.467 | 0.462 | 0.465 | 20 |
| Sáenz Peña R./de la Plaza | 21 | 1911–1916 | 19 | 26 | 0.515 | 0.406 | 0.461 | 25 |
| Peron III | 22 | 1973–1975 | 14 | 30 | 0.545 | 0.370 | 0.457 | 24 |
| Illia | 23 | 1964–1966 | 29 | 14 | 0.404 | 0.501 | 0.452 | 21 |
| Ramírez/Farrell | 24 | 1943–1945 | 10 | 33 | 0.557 | 0.347 | 0.452 | 22 |
| Frondizi | 25 | 1958–1961 | 27 | 16 | 0.407 | 0.486 | 0.446 | 23 |
| Ortiz/Castillo | 26 | 1938–1942 | 18 | 32 | 0.530 | 0.347 | 0.439 | 26 |
| Sáenz Peña L./Uriburu JE | 27 | 1893–1898 | 33 | 17 | 0.349 | 0.478 | 0.413 | 27 |
| De la Rua | 28 | 2000–2001 | 24 | 29 | 0.424 | 0.391 | 0.407 | 28 |
| C.Kirchner | 29 | 2008–2011 | 34 | 19 | 0.339 | 0.476 | 0.407 | 29 |
| Macri | 30 | 2016–2019 | 31 | 28 | 0.389 | 0.398 | 0.393 | 31 |
| Yrigoyen II | 31 | 1929–1930 | 28 | 35 | 0.406 | 0.332 | 0.369 | 35 |
| Levingston/Lanusse | 32 | 1970–1972 | 35 | 23 | 0.296 | 0.436 | 0.366 | 30 |
| De Alvear | 33 | 1923–1928 | 37 | 22 | 0.283 | 0.444 | 0.363 | 32 |
| Juárez Celman | 34 | 1887–1890 | 26 | 36 | 0.417 | 0.309 | 0.363 | 33 |
| Alfonsin | 35 | 1984–1989 | 36 | 27 | 0.286 | 0.403 | 0.345 | 36 |
| Fernandez | 36 | 2020–2023 | 22 | 40 | 0.427 | 0.210 | 0.318 | 34 |
| Alsina II | 37 | 1857–1859 | 32 | 38 | 0.364 | 0.236 | 0.300 | 37 |
| Guido | 38 | 1962–1963 | 40 | 34 | 0.230 | 0.332 | 0.281 | 38 |
| C.Kirchner II | 39 | 2012–2015 | 39 | 37 | 0.254 | 0.239 | 0.246 | 39 |
| Duhalde | 40 | 2002–2003 | 38 | 39 | 0.263 | 0.227 | 0.245 | 40 |
| Alsina | 41 | 1853–1853 | 41 | 41 | 0.166 | 0.030 | 0.098 | 41 |
: The Overall Index: average of CMPI and FPI scores, with component ranks and a Borda-count cross-check.

# Validation against the original study

The implementation is validated against three benchmarks.

**Replication of the published rankings.** Restricting the percentile pool to
1853--1999 removes the pool-expansion effect, so any deviation from the
original Table 3.4 reflects only the two known data differences (flat
within-term interest averages, and WDI-sourced inflation and growth for
1964--99). On this restricted pool the FPI reproduces the original fiscal
ranking with Spearman $\rho = 0.997$ and the CMPI with $\rho = 0.952$. The
devaluation convention is validated term by term: the December-quotation
series reproduces the original published Table 3.2 devaluation innovations to
the decimal for the four administrations that followed mid-year devaluations
(Illia, Onganía, Perón III, and the 1976--83 junta), where annual-average
data produce the wrong sign.

**Cross-notebook consistency.** The companion modern-period implementation
shares five identically defined terms with this notebook over 1964--1999.
The Spearman correlation across the five is $0.90$: the four terms unaffected
by data-convention changes preserve their relative order exactly, and the
single deviation (Illia) is by design --- the December-quotation correction
of Section 4.2 applied to its inherited 1963 devaluation baseline.

**Decomposition of the partial 2024--25 term.** Table 5 decomposes the
2024--25 years against the first two Menem years. The structure is the
corrective-shock one: a first year dominated by the devaluation and interest
components against a hyper-distressed inherited baseline, and a second year
in which the disinflation component takes over. The comparison bounds the
interpretation of a partial term: on a first-two-years basis (Section 7) the
2024--25 program and the Menem stabilization are statistically adjacent.

| Year | Administration | Inflation | Devaluation | Interest | Growth | CMPI |
|:----------|---------------------:|-------------:|---------------:|------------:|----------:|--------:|
| 2024 | Milei | 0.081 | 0.931 | 0.971 | 0.503 | 0.621 |
| 2025 | Milei | 0.948 | 0.925 | 0.977 | 0.694 | 0.886 |
| 1990 | Menem (first 2 yrs) | 0.936 | 0.965 | 0.867 | 0.665 | 0.858 |
| 1991 | Menem (first 2 yrs) | 0.971 | 0.971 | 0.873 | 0.913 | 0.932 |
: Year-by-year CMPI decomposition: the partial 2024--25 term versus the first two years of the Menem stabilization.

# Robustness

**Rank stability under resampling.** Across 1,000 bootstrap resamples of the
pool years, the CMPI medians hold Menem first (10--90 percent band 1--1;
first in 98 percent of draws), the 2024--25 term in band 2--8 (top five in 74
percent of resamples), and Obligado in band 2--4.

**Sensitivity variants.** Every judgment-dependent adjustment is re-ranked
and reported whichever administration it favours: the cepo revaluation under
measured currency composition and under the conservative 50 percent
lower bound (Table 6); accrued interest during the 2002--05 default and the
holdout add-back; the 2024--25 capitalizing-interest rescaling; the
structural primary balance with one-offs removed; the paired importer-arrears
and BOPREAL add-back; contingent liabilities (the YPF judgment and Paris Club
arrears); the 1977--90 quasi-fiscal stock, which bounds the asymmetry that
otherwise flatters the 1980s terms relative to 2003--25; a 1946--59
parallel-premium overlay for the historical exchange controls; alternative
inflation indices including a CABA-index variant for 2024--25; and a no-COVID
pool variant. None of the variants displaces the top of the Overall ranking;
the largest movements are within the modern FPI block, documented case by
case in the replication package.

| Administration | Baseline | Measured FX share | 50% FX share | Total-growth r/g |
|:-----------------------|------------:|------------:|---------:|----------------:|
| Obligado | 1 | 1 | 1 | 1 |
| Milei | 2 | 2 | 2 | 2 |
| Roca II | 3 | 3 | 3 | 3 |
| N.Kirchner | 4 | 4 | 4 | 4 |
| Menem | 5 | 5 | 5 | 5 |
| Macri | 28 | 29 | 30 | 28 |
| C.Kirchner II | 37 | 37 | 37 | 37 |
| Fernandez | 40 | 40 | 40 | 40 |
| Duhalde | 39 | 39 | 39 | 39 |
: FPI rank sensitivity for the focus administrations under the exchange-control and growth-definition variants.

**Component weights.** The equal weighting of components is the original
study's convention; the component-exclusion variants bound its impact as
extreme weight perturbations. Menem remains first with the interest dimension
removed entirely, while the 2024--25 term falls from second to fifth --- the
country-risk collapse is a material part of its score --- and Obligado falls
from third to fifth when inflation, its coarsest pre-1866 proxy dimension, is
removed.

**Term length.** Re-scoring every administration on its first two years only
(Table 7) puts partial and complete terms on an equal footing and confirms
that the term-average design, not data choices, drives the strong showing of
short corrective terms.

| Administration | Full-term rank | First-2-years rank |
|:-----------------------------------|-------------:|-----------------:|
| Menem | 1 | 1 |
| Milei | 2 | 2 |
| Obligado | 3 | 3 |
| Menem II | 4 | 4 |
| Justo | 6 | 5 |
| Perón II | 5 | 6 |
| Roca | 8 | 7 |
| Peron III | 14 | 8 |
| Sarmiento | 7 | 9 |
| Ramírez/Farrell | 10 | 10 |
| Sáenz Peña R./de la Plaza | 19 | 11 |
| Macri | 31 | 12 |
: Full-term versus first-two-years CMPI ranks, selected administrations.

**Bootstrap confidence intervals and pairwise comparisons.** Table 8 reports
95 percent confidence intervals for the bootstrap rank distributions of the
focus administrations, computed from 1,000 shared-draw resamples of the pool
years (the same resample drives all three indices, so cross-index and
pairwise statements are internally consistent). Menem remains ahead of the
2024--25 term on the CMPI in 97.6 percent of draws --- a one-sided bootstrap
$p$ of $0.024$ --- while on the Overall Index the two are statistically
adjacent (Menem ahead in 69 percent of draws, $p = 0.31$), and Obligado leads
the 2024--25 term on the FPI in 75 percent ($p = 0.25$). All three podium
administrations remain in the Overall top five in every draw; N. Kirchner
does so in 76 percent, and the bottom-ranked modern terms never reach it.

| Administration | CMPI median | CMPI 95% CI | FPI median | FPI 95% CI | Overall median | Overall 95% CI | P(top 5) |
|:-----------------------|----------:|--------:|----------:|-------:|-----------:|-----------:|---------:|
| Menem | 1 | 1–1 | 5 | 3–8 | 1 | 1–3 | 100% |
| Milei | 3 | 2–10 | 2 | 1–4 | 3 | 1–3 | 100% |
| Obligado | 3 | 2–5 | 1 | 1–2 | 2 | 1–3 | 100% |
| Roca II | 25 | 15–34 | 3 | 1–5 | 9 | 4–15 | 16% |
| N.Kirchner | 15 | 10–20 | 4 | 2–6 | 5 | 3–8 | 76% |
| Fernandez | 24 | 10–36 | 37 | 33–40 | 34 | 23–39 | 0% |
: Bootstrap rank distributions, 1,000 resamples of the pool years: median rank and 95 percent confidence interval per index, and the share of draws in which the administration stays in the Overall top five. Statistics are computed over the draws in which the term's years appear in the resample.

# Discussion

The 173-year unified ranking reproduces the main findings of the original
study for the historical period while placing the 2000--2025 administrations
on the same scale. Stabilizations anchored to hard-currency or convertible
regimes score highest --- Menem's Convertibility first in both the original
and here; Obligado's 1854--56 reforms, which ended decades of inflationary
finance, near the top --- and crisis terms score lowest. The 2024--25
disinflation scores highly even in this long-run context.

Three interpretive points deserve emphasis.

**What the index measures.** The CMPI rewards improvement relative to the
inherited year, averaged over the term --- not the state in which an
administration leaves the country. The clearest modern case is the
Fernández (2020--23) versus Macri (2016--19) inversion: Macri had lower
absolute inflation, devaluation, and country risk, yet ranks just below
Fernández, because Macri inherited the calm, exchange-control-pinned 2015
economy and bequeathed the 2019 crisis against which Fernández is then scored
each year [for an insider account of the 2016--19 program and its collapse,
see @sturzenegger2019macri]. COVID amplifies the inversion through the
V-shaped 2020--21 pair.
This is an artefact of the single-year inherited baseline --- a design
feature, disclosed and bounded in Section 7 --- and the ranking should be
read alongside the contemporaneous record (Appendix C).

**Why the data corrections are decisive.** Four adjustments determine the
credibility of the modern ranking: the alternative price indices stop the
2007--2015 intervention from inflating the affected scores; the country-risk
spread removes a fabricated interest improvement in 2020--23 and exposes the
2024--25 collapse in country risk; the December-quotation devaluation series
fixes the wrong-signed innovations around mid-year devaluations; and the
two debt-stock corrections keep the fiscal components from mismeasuring the
2003--2025 terms in both directions.

**The passing-the-buck reading.** Administrations that pair a high CMPI with
a low FPI purchased calm with future resources. The quasi-fiscal channel is
the modern refinement of the original thesis: where the nineteenth-century
version of the dynamic ran through Treasury debt and suspension of
convertibility, the twenty-first-century version runs through the central
bank's balance sheet --- invisible in the official debt statistics that the
original authors could take at face value for their period.

**Why the buck keeps being passed.** The index documents the pattern; it does
not by itself explain its persistence over 173 years, and nothing in a
percentile rank identifies the constraints a given administration faced. The
political-economy literature supplies the candidate mechanism:
@spillertommasi2007 show that Argentine institutions --- short and uncertain
tenures, a federal fiscal commons, weak legislative and judicial enforcement
of intertemporal bargains --- systematically shorten policymakers' horizons,
making debt, visible or hidden, the cheapest instrument with which to buy the
present. Read through @bueranicolini2021argentina, the FPI is the
administration-level trace of the fiscal dominance that the comparative
Latin American literature identifies at the level of regimes
[@kehoenicolini2021]. These are interpretations consistent with the ranking,
not findings of it.

# Limitations

The principal limitations, each documented in the replication package and
bounded by a sensitivity variant where feasible:

- **Historical interest rates (1852--1997) use published term averages**, so
  historical administrations have flat within-term interest variation; with
  WDI-sourced 1964--99 inflation and growth, this is the main remaining
  source of divergence from the original ranking ($\rho = 0.952$).
- **Data-regime seam at 1963/64** for inflation and growth; devaluation has
  no seam; interest switches from term averages to the EMBIG spread in 1998.
  The modern interest dimension is a *spread*, not a rate level, so
  innovations crossing the 1997/98 seam embed a small level shift.
- **The FPI's $(1+r)/(1+g)$ uses per-capita growth** (the only annual series
  available across the full span) where the original defines $g$ as total
  growth; innovations difference out slow-moving population growth almost
  entirely, and the total-growth variant moves every focus rank by at most
  one position (Table 6).
- **The exchange-control revaluation assumes a foreign-currency-linked debt
  stock**; the measured-composition and 50-percent variants bound the
  correction from both sides.
- **The quasi-fiscal consolidation starts in 2003** and uses measured
  December year-end stocks from the central bank's statistical API for
  2002--2024 (the curated anchors that previously carried the series are
  retained as cross-checks); 2025 and the 1977--90 extension rest on
  documented estimates, the latter entering only as a sensitivity variant.
- **A debt-definition seam at 2018/19**: the historical ratios use the
  original central-government concept, the 2019--25 extension uses total
  Sector Público Nacional gross debt.
- **Pool non-comparability**: adding eight modern terms changes every
  historical percentile; the full-pool ranking is an extension, not a
  reproduction, of the original 33-term table. The single 173-year pool is
  nonetheless deliberate: one common yardstick is what allows a Confederation
  presidency and a twenty-first-century stabilization to be ranked at all.
  Era-specific sub-pools would re-score every administration against its own
  era's standards --- undoing the cross-era comparability the index exists to
  provide --- while introducing arbitrary regime break points; standardized
  (z-score) scoring was rejected because hyperinflation-era tails would
  dominate any variance-based scale. Percentile ranks over one pool are the
  design that survives both objections.
- **The single-last-year inherited baseline is likewise a convention.**
  Averaging several pre-term years would dilute one-off shocks in the
  inherited year, but it would also smear the predecessor's own crisis into
  the benchmark a government is judged against, weakening the question the
  index asks. The V-shaped-shock caveat of Section 3.3 and the no-COVID pool
  variant of Section 7 disclose and bound the principal consequence.
- **Equal component weights are the original study's convention**; the
  component-exclusion variants of Section 7 act as extreme weight
  perturbations and bound the impact of this choice on the focus ranks.
- **The indices measure macroeconomic and fiscal management only.**
  Distributional outcomes, poverty, productivity, and institutional quality
  are outside the nine variables; an administration can rank highly here
  while performing poorly on those dimensions, and conversely. The ranking is
  one input to an overall assessment of a government, not a verdict.
- **Two 2024--25 measurement caveats work in the current administration's
  favour** and are flagged symmetrically with the Kirchner-era corrections:
  cash-basis results exclude capitalizing interest, and the 2004--05-basket
  CPI understates the services-led relative-price normalization. Both are
  bounded by variants (Section 7).

# Conclusion

Applying both indices of @dellapaolera2003passing across the full 1853--2025
span places all 41 Argentine national administrations on a single, internally
consistent scale. The method's logic --- judging each government by the
macroeconomic and fiscal improvement it delivers over the situation it
inherited --- puts durable hard-currency and convertible stabilizations at
the top and crises, and the terms that bequeath them, at the bottom. The
unified ranking reproduces the original historical results almost exactly on
the restricted pool while extending them through 2025 with corrected data:
alternative price indices for the 2007--2015 statistical intervention, a
country-risk spread for the modern interest series, free-market exchange
rates for the control years, December-quotation devaluations throughout, and
--- for the fiscal dimension --- an exchange-control revaluation and the
consolidation of the central bank's quasi-fiscal debt.

The Overall Index confirms the original *passing-the-buck* thesis over the
long run: administrations that purchased macroeconomic calm with debt --- on
the Treasury or hidden in the central bank --- handed the bill to their
successors. Making the hidden half of that debt visible is, we would argue,
the precondition for any honest scoreboard of Argentine economic governance.

# Reproducibility {#sec:repro .unnumbered}

**Appendix A.** The complete replication package --- the analysis notebook,
all input data with documented lineage, download and generation scripts, an
input validator, unit tests, and continuous integration that re-executes the
full pipeline --- is available at
<https://github.com/jahnog/still-passing-the-buck>.
Every table and figure in this paper is extracted programmatically from the
executed notebook by the build script (`scripts/build_paper.py`), so prose
and pipeline cannot silently diverge. Data vintages are stamped in the
package; baseline-affecting revisions are logged. An archived snapshot of the
paper and the replication package is deposited at Zenodo:
[doi:10.5281/zenodo.20651731](https://doi.org/10.5281/zenodo.20651731).

# The statistical-integrity catalogue {#sec:catalogue .unnumbered}

**Appendix B.** The full twenty-one-entry catalogue, with per-row sources, is
maintained in the replication package; the condensed version follows.
"Corrected" practices are fixed in the baseline (official series kept as
audit columns); "Sensitivity" practices enter re-ranked variants only;
"Documented" practices are flagged for the reader.

| # | Practice | Period | Bias | Treatment |
|:--|:---------------------------------------------|:------------|:-----------------------|:------------|
| 1 | INDEC CPI intervention (under-stated 3--4x) | 2007--15 | Inflation down | Corrected |
| 2 | GDP volume overstatement, base-1993 accounts | 2007--15 | Growth up | Corrected |
| 3 | GDP-warrant payouts on overstated growth | 2009--14 | Fiscal flows (both) | Documented |
| 4 | Exchange controls (cepo), official rate pinned | 2012--15, 2019--25 | Devaluation, debt/GDP down | Corrected |
| 5 | Historical exchange controls and parallel premia | 1931--59 | Devaluation down | Sensitivity |
| 6 | "Surplus" while in default (unpaid interest) | 2002--05 | Result/debt-service up | Sensitivity |
| 7 | Holdout debt excluded from official stock | 2005--15 | Debt down | Sensitivity |
| 8 | CER under-indexation of inflation-linked debt | 2007--15 | Debt, interest down | Documented |
| 9 | Pension nationalization booked as revenue | 2008--15 | Result/revenue up | Sensitivity |
| 10 | Reserve hollowing; paper profits as revenue | 2006--15, 2021--23 | Result/revenue up | Sensitivity |
| 11 | Hidden central-bank debt stock (Lebac/Leliq/Pases) | 2002--24 | Debt down | Corrected |
| 12 | Hidden central-bank deficit (quasi-fiscal flow) | 2004--24 | Result up | Sensitivity |
| 13 | 1980s Cuenta de Regulación Monetaria | 1984--89 | Debt down, result up | Sensitivity |
| 14 | One-off revenues above the line (SDR, amnesties) | various | Result/revenue up | Sensitivity |
| 15 | Importer arrears / BOPREAL conversion | 2022--25 | Debt down, then up | Sensitivity |
| 16 | Cash surplus excluding capitalizing interest | 2024--25 | Result up | Sensitivity |
| 17 | CPI basket vintage (2004--05 weights) | 2017--25 | Inflation down | Sensitivity |
| 18 | Price controls; repressed inflation to successor | several | Incumbent inflation down | Documented |
| 19 | Statistics blackouts; labour-data masking | 2002--16 | Non-index inputs | Documented |
| 20 | Crisis balance-sheet transfers (1982, 1989, 2002) | as listed | Debt up (real) | Documented |
| 21 | Contingent liabilities (YPF judgment, Paris Club) | 2002--25 | Debt down | Sensitivity |

: The statistical-integrity catalogue (condensed). Full entries with affected terms, magnitudes, and per-row sources are in the replication package.

# The contemporaneous record {#sec:contemporaneous .unnumbered}

**Appendix C.** For the reader who wants the absolute outcomes alongside the
innovation-based ranking, the table below reports term-average inflation,
devaluation, interest, and growth for all 41 administrations.

| Administration | From | To | Inflation | Devaluation | Interest | Growth |
|:----------------------------------------|--------:|------:|-------------:|---------------:|------------:|------------:|
| Alsina | 1853 | 1853 | 14.11 | 14.11 | 15.19 | -17.53 |
| Obligado | 1854 | 1856 | 3.19 | 3.19 | 14.10 | 7.15 |
| Alsina II | 1857 | 1859 | 0.53 | 0.53 | 15.72 | -4.82 |
| Mitre | 1860 | 1868 | 1.68 | 2.08 | 12.70 | 7.43 |
| Sarmiento | 1869 | 1874 | 4.33 | 0.00 | 8.63 | 2.30 |
| Avellaneda | 1875 | 1880 | 10.01 | 2.24 | 10.02 | 5.19 |
| Roca | 1881 | 1886 | -2.94 | 3.25 | 7.22 | 8.08 |
| Juárez Celman | 1887 | 1890 | 12.06 | 15.46 | 8.79 | 5.40 |
| Pellegrini | 1891 | 1892 | 10.86 | 12.15 | 9.72 | -4.43 |
| Sáenz Peña L./Uriburu JE | 1893 | 1898 | -1.23 | -4.12 | 8.22 | 0.72 |
| Roca II | 1899 | 1904 | -1.72 | -1.76 | 7.32 | 3.82 |
| Quintana/Figueroa | 1905 | 1910 | 4.97 | 0.04 | 5.50 | 2.43 |
| Sáenz Peña R./de la Plaza | 1911 | 1916 | 3.71 | 0.06 | 3.73 | -3.99 |
| Yrigoyen | 1917 | 1922 | 1.03 | 2.70 | 5.08 | 3.10 |
| De Alvear | 1923 | 1928 | 0.09 | -2.72 | 8.63 | 2.94 |
| Yrigoyen II | 1929 | 1930 | -3.67 | 7.47 | 8.77 | -2.45 |
| Uriburu JF | 1931 | 1931 | -3.31 | 23.26 | 8.72 | -9.22 |
| Justo | 1932 | 1937 | 3.98 | -0.62 | 6.02 | 1.88 |
| Ortiz/Castillo | 1938 | 1942 | 4.52 | 4.55 | 2.09 | 0.77 |
| Ramírez/Farrell | 1943 | 1945 | 5.57 | -1.46 | 0.52 | 0.77 |
| Perón I | 1946 | 1951 | 20.93 | 31.58 | -0.02 | 2.72 |
| Perón II | 1952 | 1955 | 10.25 | 7.19 | -1.25 | 0.89 |
| Aramburu | 1956 | 1957 | 20.93 | 1.64 | -0.49 | 2.21 |
| Frondizi | 1958 | 1961 | 34.67 | 20.15 | 0.46 | 2.31 |
| Guido | 1962 | 1963 | 26.05 | 24.42 | 2.89 | -2.41 |
| Illia | 1964 | 1966 | 21.68 | 22.50 | 4.39 | 5.02 |
| Ongania | 1967 | 1969 | 13.35 | 9.24 | 7.64 | 4.29 |
| Levingston/Lanusse | 1970 | 1972 | 31.16 | 40.28 | 5.48 | 1.83 |
| Peron III | 1973 | 1975 | 58.84 | 79.67 | 2.44 | 1.12 |
| Videla/Viola/Galtieri/Bignone | 1976 | 1983 | 107.37 | 94.51 | 5.15 | -0.28 |
| Alfonsin | 1984 | 1989 | 173.14 | 181.46 | 17.38 | -2.04 |
| Menem | 1990 | 1995 | 65.75 | 33.73 | 14.26 | 2.86 |
| Menem II | 1996 | 1999 | -0.94 | 0.00 | 8.17 | 2.29 |
| De la Rua | 2000 | 2001 | 0.69 | 0.00 | 11.12 | -3.68 |
| Duhalde | 2002 | 2003 | 27.51 | 54.27 | 56.19 | -2.06 |
| N.Kirchner | 2004 | 2007 | 13.56 | 1.47 | 20.67 | 7.64 |
| C.Kirchner | 2008 | 2011 | 19.49 | 7.80 | 8.57 | 2.49 |
| C.Kirchner II | 2012 | 2015 | 25.90 | 30.43 | 8.58 | -0.62 |
| Macri | 2016 | 2019 | 30.64 | 40.93 | 6.88 | -1.80 |
| Fernandez | 2020 | 2023 | 54.12 | 64.00 | 20.54 | 0.87 |
| Milei | 2024 | 2025 | 72.38 | 22.90 | 10.59 | 1.26 |
: Contemporaneous (absolute) term averages, all 41 administrations. This is the record against which the caveat of Section 3.3 should be read.

# Index construction: exact formulas {#sec:formulas .unnumbered}

**Appendix D.** This appendix states the complete scoring algebra; it matches
the implementation in the replication package (`scripts/cmpi_core.py`)
line for line.

**Terms and innovations.** Let administration $j$ govern years
$f_j, \dots, l_j$, and let $x_{v,t}$ denote the value of variable $v$ in year
$t$. Inflation and devaluation enter as continuously compounded rates,
$x = \ln(1 + \pi)$. Every year of the term is scored against the same
inherited benchmark --- the last year of the predecessor:

$$\Delta_{v,t} = x_{v,t} - x_{v,\,f_j - 1}, \qquad t = f_j, \dots, l_j.$$

**Percentile assignment.** Innovations are pooled across all $O = 173$ years
(1853--2025). For each variable, the innovation in position $o$ of the
favourable-to-unfavourable ordering (best $= 1$) receives the percentile
score of the original Appendix A:

$$R_{v,t} = \frac{O - o_{v,t}}{O} \in \left[0,\, \tfrac{O-1}{O}\right].$$

Favourable means *lower* for inflation, devaluation, the real interest rate,
and the three FPI debt and amplification variables, and *higher* for growth
and the two FPI primary-result variables.

**Aggregation.** An administration's component score is the mean percentile
over its term years, and each index is the unweighted mean of its components
($n=4$ for the CMPI, $n=5$ for the FPI):

$$\text{CMPI}_j = \frac{1}{4} \sum_{v \in \mathcal{C}} \frac{1}{T_j}
\sum_{t=f_j}^{l_j} R_{v,t}, \qquad
\text{FPI}_j = \frac{1}{5} \sum_{v \in \mathcal{F}} \frac{1}{T_j}
\sum_{t=f_j}^{l_j} R_{v,t},$$

with $\mathcal{C} = \{$inflation, devaluation, interest, per-capita
growth$\}$ and $\mathcal{F} = \{$debt/GDP, debt/exports, primary
result/revenues, primary result/debt service, $(1+r)/(1+g)\}$. The Overall
Index is $\tfrac{1}{2}(\text{CMPI}_j + \text{FPI}_j)$.

**Debt dynamics.** The FPI components derive from the first-order difference
equation for the debt ratio,

$$\frac{B_t}{Y_t} = \frac{1+r_t}{1+g_t}\,\frac{B_{t-1}}{Y_{t-1}} +
\frac{DEF_t}{Y_t},$$

whose amplification factor $(1+r_t)/(1+g_t)$ enters the FPI directly.

**The two modern debt-stock corrections.** During exchange-control years the
official rate overstates dollar GDP, so the debt ratio is revalued at the
free-market rate:

$$\left(\frac{B}{Y}\right)^{\text{cepo}} =
\left.\frac{B}{Y}\right|_{\text{official}} \times
\frac{e_{\text{parallel}}}{e_{\text{official}}},$$

and the central bank's remunerated liabilities are consolidated into the
stock:

$$\left(\frac{B}{Y}\right)^{\text{adj}} =
\left(\frac{B}{Y}\right)^{\text{cepo}} +
\frac{\text{BCRA remunerated liabilities}}{Y}.$$

**Structural primary result (sensitivity variant).** Where one-off revenues
are a share $o$ of total revenues, the structural ratio is

$$\left(\frac{\text{Result}}{\text{Rev}}\right)^{\text{structural}} =
\frac{R - o}{1 - o}.$$

# Glossary {#sec:glossary .unnumbered}

**Appendix E.** Terms used throughout the paper, in alphabetical order.

Administration (term)
: The unit of analysis: one of the 41 government intervals of 1853--2025
  (Section 3.4). Each year of a term is scored against the last year of the
  predecessor.

Brecha (parallel premium)
: The percentage gap between the free-market and the official exchange rate
  during exchange-control years; it reached 100 percent in the modern cepos.

CCL / blue
: The two free-market dollar quotations used for the control years: the
  *contado con liquidación* rate (implicit in dual-listed securities) and the
  informal cash ("blue") rate.

Cepo
: Colloquial name for Argentina's exchange-control regimes (2012--15 and
  2019--25), under which the official rate was administratively pinned below
  the free-market rate.

CMPI
: Classical Macroeconomic Performance Index: the average innovation
  percentile across inflation, devaluation, the hard-currency real interest
  rate, and per-capita growth (Section 3.1).

Convertibility
: The 1991--2001 currency-board regime pegging the peso one-to-one to the US
  dollar.

December quotations
: The exchange-rate convention used throughout: year-end (December) rates
  rather than annual averages, which blend pre- and post-devaluation months
  and produce wrong-signed innovations (Section 4.2).

FPI
: Fiscal Pressure Index: the average innovation percentile across debt/GDP,
  debt/exports, primary result/revenues, primary result/debt service, and the
  debt-amplification factor $(1+r)/(1+g)$ (Section 3.2).

INDEC intervention
: The 2007--2015 manipulation of the official consumer-price index (and the
  parallel overstatement of real growth), which led to the IMF's declaration
  of censure; corrected in the baseline with alternative indices (Section 4.2).

Innovation
: The annual value of a variable minus its value in the last year of the
  previous administration --- the inherited condition (Section 3.1).

Overall Index
: The simple average of an administration's CMPI and FPI scores.

Percentile pool
: The single pool of 173 annual observations (1853--2025) over which each
  variable's innovations are ranked; the innovation in position $o$ scores
  $(O-o)/O$.

Primary result
: The fiscal balance before interest payments; "structural" variants remove
  one-off revenues booked above the line.

Quasi-fiscal debt
: The central bank's remunerated liabilities (Lebac/Nobac, Leliq/Notaliq,
  Pases) --- economically public debt but absent from Treasury statistics;
  consolidated into the debt stock for 2003--2025 (Section 4.3).

# References {.unnumbered}

::: {#refs}
:::

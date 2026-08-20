---
title: "Still Passing the Buck: Macroeconomic and Fiscal Performance of Argentine Administrations, 1853--2025"
author: "Javier Hernan Nogueira^[Independent researcher. Contact: <jahnog@gmail.com>. ORCID: [0009-0006-1945-7870](https://orcid.org/0009-0006-1945-7870). Replication package: <https://github.com/jahnog/still-passing-the-buck>. I thank Gerardo della Paolera, María Alejandra Irigoin, and Carlos G. Bózzoli, the authors of the original *Passing the buck* chapter, for generously sharing the dataset underlying their study; this replication uses the archived paper-author workbook only through 1999, with 2000 onward rebuilt from official and documented sources. All errors are my own.]"
date: "June 2026 --- Working paper draft --- v1.3.2"
abstract: |
  We rank all 41 Argentine national administrations that governed between 1853
  and 2025 with the two indices proposed by @dellapaolera2003passing --- the
  Classical Macroeconomic Pressure Index (CMPI) and the Fiscal Pressure
  Index (FPI) --- and their combined Overall Index, scoring each government by
  the macroeconomic and fiscal improvement it delivered over the situation it
  inherited. A single 173-year scoring frame places every
  administration, from the mid-nineteenth-century Confederation to the 2024--25
  stabilization, on a common scale. Extending the original 1853--1999 analysis
  through 2025 requires confronting documented distortions in modern Argentine
  statistics: we catalogue twenty-three manipulation, measurement and accounting
  practices,
  correct the affected series from independent and reproducible sources, and
  retain paper-comparable and sensitivity variants for reconstructed or
  judgment-sensitive corrections. The 2025 fiscal primary-result operands
  come from the official annual SPN base-caja dataset. On the restricted
  1853--1999 pool the replication of the original rankings is almost exact
  (Spearman $\rho = 0.996$ for the FPI, $0.953$ for the CMPI). In the unified
  ranking Menem (1990--95) leads the CMPI and the Overall Index, while Obligado
  (1854--56) leads the FPI.
  Consolidating the central bank's quasi-fiscal debt into the public debt stock
  and valuing output at the free-market exchange rate during exchange-control
  years materially reorders the modern fiscal ranking. Holding the interest
  dimension at its last functioning-market quotation through the 2002--05
  payments default moves the two administrations that straddle that crisis by
  five and two Overall places (Table 10); the stacked interest restorations
  also move the 2008--11 term by two. The long-run results
  are consistent with the original *passing-the-buck* thesis: administrations bought
  macroeconomic calm with debt --- on the Treasury's books or hidden in the
  central bank --- and passed the bill to their successors.

  **Keywords:** Argentina; economic history; macroeconomic performance;
  fiscal policy; inflation; public debt; statistical integrity;
  statistical manipulation.

  **JEL classification:** C43; E31; E62; H63; N16; O54.
lang: en-US
fontsize: 11pt
papersize: a4
geometry: margin=2.8cm
mainfont: "Latin Modern Roman"
sansfont: "Latin Modern Sans"
monofont: "Latin Modern Mono"
mathfont: "Latin Modern Math"
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
> pooled over the 173-year frame: a score of 0.90 means the administration's
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
a common percentile scale. Their Classical Macroeconomic Pressure Index
(CMPI) aggregates inflation, devaluation, the hard-currency interest rate, and
per-capita growth; their Fiscal Pressure Index (FPI) adds the management of the
intertemporal budget constraint; the average of the two is an Overall Index.
Applied to 33 administrations over 1853--1999, the framework produced the
central finding the authors summarized in their title: Argentine governments
repeatedly bought contemporaneous macroeconomic calm with fiscal pressure that
they passed to their successors.

This paper extends the complete two-index framework to the full 1853--2025
span --- 41 administrations and a common 173-year scoring frame ---
placing the original 33 historical terms and the eight administrations of
2000--2025 on a single 173-year percentile pool --- one scoring frame, not one
measurement regime (Section 4). The extension is not a
mechanical appending of recent data. Between 2007 and 2015 the national
statistical institute (INDEC) falsified consumer-price inflation by a factor
of roughly three to four and manipulated real growth, episodes that led to the
first declaration of censure in the history of the International Monetary Fund
and to the criminal conviction of Commerce Secretary Guillermo Moreno
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
twenty-three-entry catalogue (Section 4, Appendix B) stating the direction of
each bias and its treatment. Corrections enter the corrected baseline when the
evidence is independently sourced and the mapping to an index component is
documented; paper-comparable official columns and sensitivity variants are
retained where reconstruction or judgment could affect the magnitude, reported
whichever administration they favour. Second, we resolve the annual-average
devaluation artefact by using December-quotation exchange-rate series for the
entire sample. Third, we extend the FPI with two corrections to the modern
debt-stock components: a free-market revaluation of GDP during
exchange-control years, and the consolidation of the central bank's
remunerated liabilities into the public debt stock. Fourth, we validate the
implementation by replicating the original published rankings on the
restricted 1853--1999 pool, obtaining Spearman rank correlations of $0.996$
(FPI) and $0.953$ (CMPI) against the original Table 3.4.

The headline results place Menem (1990--95) first on the CMPI and the Overall
Index, with the 2024--25 stabilization and Obligado's 1854--56 reforms close
behind, and crisis terms at the bottom --- consistent with the original
finding that durable hard-currency and convertible stabilizations score
highest. The fiscal corrections are decisive for the modern ranking: once the
central bank's hidden debt is consolidated and the exchange-control distortion
removed, the 2012--15 and 2020--23 terms occupy the bottom two places on
the FPI. The 2012--15 term finishes last mainly because of the exchange gap
rather than a comparable BCRA build-up; 2020--23 sits next to it with a
quasi-fiscal stock that averaged eleven percent of GDP. The
2024--25 consolidation registers as a sharp reduction in fiscal pressure
rather than the spurious increase shown by the raw Treasury series. The
long-run picture is consistent with the *passing-the-buck* dynamic over 173
years.

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
methodology; @coremberg2017 quantifies the parallel volume manipulation of real
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

## The Classical Macroeconomic Pressure Index

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

There is one historical exception. The source has no primary-result/revenues
or primary-result/debt-service ratios for 1861--63. We fill those six raw
ratios by arithmetic interpolation between the observed 1860 and 1864
endpoints so every FPI component is scored over the same 173-year pool.
Geometric interpolation is undefined because Result/Revenue changes sign.
Section 4 and Appendix D state the formula and its evidentiary limitation.

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

## Fidelity to the original design

| Design element | Original study | This extension |
|:--|:--|:--|
| Unit of analysis | Argentine national administrations through 1999 | Same intervals through 1999; modified majority-of-year rule for the extension through 2025 |
| Inherited baseline | Each year scored against the predecessor's last observation | Same rule, recomputed after the administration-year classifier is applied |
| Annual scoring | Innovation percentiles using $R=(O-o)/O$; six 1861--63 fiscal relative indices completed after ranking | Same percentile formula on the 1853--2025 frame; the six missing 1861--63 raw ratios are arithmetically interpolated before ranking so $O=173$ for every component |
| CMPI variables | Inflation, devaluation, interest, growth | Same variables; growth is consistently per-capita |
| FPI variables | Debt/GDP, debt/exports, two primary-result ratios, $(1+r)/(1+g)$ | Same variables with corrected-baseline and paper-comparable fiscal columns retained |
| Weights | Equal component weights; Overall = mean(CMPI,FPI) | Same weights; component exclusions reported as robustness checks |
| Interest seam | Published term averages through 1999 | Original averages through 1997; annual EMBIG from 1998, restored to the original's rate-level concept (risk-free leg added back; default window held) |
| Data corrections | Official historical series mostly used as published | Documented statistical/accounting distortions corrected or classified in Appendix B |
| Recent-data status | Not applicable | Complete annual observations are used for 2025, but recent national-account values remain subject to source revisions |

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
   administration on its first two years only, putting different
   administration lengths on the same two-year observation window.

3. **Single-year inherited baselines amplify V-shaped shocks.** Because every
   year of a term is measured against the predecessor's *last* year, a
   collapse-and-rebound pair inside one term (COVID: $-10.3$ percent
   per-capita growth in 2020, $+10.2$ percent in 2021) is lightly penalized on
   the way down and fully rewarded on the way back.

## Administration boundaries

The 41 terms follow the original intervals exactly where the two studies
overlap (33 terms, 1853--1999), including the rule of assigning each year to
whoever ruled the larger part of it. Conventions carried over from the
original study: single-year caretaker terms are kept separate when
conventionally distinguished (Alsina 1853, Uriburu 1931, Guido 1962--63);
military juntas are presented as one term (1976--83); civilian transition
periods with rapid turnover are combined.

For 2000--2025, administration-years follow a **modified majority-of-year
rule**. A transition year remains with the outgoing-originated policy episode
only when all four pre-specified conditions hold: (1) the incoming president
would otherwise receive the year; (2) the outgoing Economy Minister remains
continuously in office through year-end; (3) the incoming government retains
the core stabilization regime in at least **four of five** predefined domains
--- fiscal, monetary, exchange-rate, banking, and sovereign-debt policy; and
(4) the transition year is the program's first complete calendar-year
observation, regardless of its results. Constitutional tenure is reported
separately. This project-specific rule is applied to every transition before
scoring; it classifies policy continuity rather than assigning exclusive
causal credit. It is not a standard coding convention, but the intersection
of three established practices used elsewhere in the literature:

1. **De facto regime classification.** Exchange-rate classifications
   distinguish announced legal arrangements from policies actually
   implemented [@reinhartrogoff2004; @levyyeyatisturzenegger2005]. By
   analogy---not as a direct precedent---a presidential transfer is a de jure
   change but need not constitute a de facto economic-regime break when both
   the Economy Minister and core policy instruments remain unchanged.

2. **Action-based episode dating.** Stabilization, growth-acceleration,
   fiscal-consolidation, and liberalization studies date episodes from
   observable announcements, measures, or documented policy actions rather
   than electoral boundaries [@easterly1996; @calvovegh1999;
   @hausmannpritchettrodrik2005; @giavazzitabellini2005; @devriesetal2011;
   @guajardoleighpescatori2014]. This motivates treating a continuing
   stabilization regime as an economic-policy episode; it does not establish
   a standard rule for presidential attribution.

3. **Finance-minister continuity.** Fiscal-governance research models a
   strong finance minister as an agenda setter or delegated veto player,
   while empirical work associates ministerial characteristics and
   continuity with deficits and debt [@hallerbergvonhagen1999;
   @jochimsenthomasius2014; @moessinger2014]. Ministerial continuity is an
   observable institutional marker, not proof that the minister controls
   every CMPI or FPI outcome.

The sole qualifying transition is 2003. Roberto Lavagna entered office on 27
April 2002; Eduardo Duhalde's constitutional tenure ended and Néstor
Kirchner's began on 25 May 2003; Kirchner retained Lavagna through year-end
(and until November 2005). The pre-scoring audit records continuity in
fiscal, monetary, exchange-rate, and banking policy, but not sovereign-debt
policy. Accordingly, 2003 is assigned to the **Duhalde-originated,
Kirchner-retained Lavagna policy episode**; this does not imply that Duhalde
legally governed the whole year or exclusively caused its outcomes. The 2025
calendar-year observation is complete and enters every headline score.
Milei's presidency is still in progress and its constitutional term runs
through 10 December 2027, so the 2024--25 administration ranking is interim.

# Data

## Two data regimes

The series combine two regimes. For **1852--1963** we read the original
authors' annual dataset (`data_a_1999.xlsx`): inflation and devaluation as
annual log-differences, per-capita growth, and the four fiscal ratios. Interest
rates use the published term averages of the original Table 3.1, since the
dataset contains no annual interest series; the 1852 baseline is derived from
the original Table 3.2. The workbook carries no fiscal observations for 1852,
so the four FPI ratios are set to zero in that year.
This is a convention, not a measurement, and it has one consequence worth
stating: the 1853 Alsina term is a single year scored against it, so its
fiscal innovations are the 1853 *levels* rather than changes --- a debt ratio
of 0.60 and a primary result of $-1.21$ times revenues read as a deterioration
from a debt-free starting point that never existed. Alsina finishes last on
the FPI and last overall. The convention reproduces the original study's
placement of the term, and we keep it for comparability rather than because
the implied baseline is credible.

The workbook also has genuine blanks for primary result/revenues and primary
result/debt service in 1861--63. We fill those six raw ratios by arithmetic
interpolation between the observed 1860 and 1864 endpoints, so contemporaneous
averages, innovations, and percentiles all use the same 173 rows. Geometric
interpolation is undefined because Result/Revenue changes sign. This
complete-pool convention differs from Appendix A of @dellapaolera2003passing
(pp. 78--79 and footnote 33), which ranked the available observations first
and interpolated only the resulting relative-index scores. The archived
chapter calls that both a “constant growth rate” and a “constant-rate-change”
interpolation but supplies no equation or filled values. We disclose the
raw-ratio formula in Appendix D. The three filled years remain reconstructed
observations, not measurements, and are graded C in the quality flags.

For **2000--2025** debt ratios use
total Sector Público Nacional gross debt from the Secretaría de Finanzas
[@secfinanzas_deuda] divided by World Bank GDP and exports; fiscal ratios use
the SPN cash-basis ("base caja") primary result from datos.gob.ar SSPM
dataset 379 for 2000--2025 [@datosgobar_spn_base_caja]. The generated record retains current revenue,
primary result, financial result, and net interest before deriving both ratios.
For **1964--2025** macro variables (inflation, growth, devaluation, interest)
we use annual values from the World Bank World Development Indicators
[@worldbank_wdi], INDEC price and national-accounts series, and the EMBIG
Argentina country-risk spread from 1998 [@bcrp_embig]. Free-market
exchange-rate quotations for the exchange-control years come from public
APIs [@argentinadatos_fx] and the December-quotation devaluation series for
1960--1999 from @ruiz1990dolar and the original dataset.

World Bank 2025 national accounts are in the raw snapshot and in the
headline series: per-capita growth is $4.014$ percent
(`NY.GDP.PCAP.KD.ZG`); Debt/GDP and Debt/Exports use World Bank current-US\$
GDP ($\approx$ US\$683~bn) and exports of goods, services and primary income
($\approx$ US\$112~bn). Complete annual observations are used for 2025, but
recent national-account values remain subject to source revisions. The debt
numerator is the final year-end total Sector Público Nacional gross-debt
workbook, and the 2025 fiscal primary-result ratios use the official annual
Secretaría de Hacienda SPN cash-basis ("base caja") dataset.

## What the inflation variable measures

Because the inflation dimension carries the largest weight in the CMPI's
interpretation, its composition is worth stating exactly. For **1852--1963** it
is the original workbook's annual log-difference series. For **1964--2025** it
is the simple average of two legs: a consumer-price leg and a wholesale-price
leg (INDEC IPIM, `FP.WPI.TOTL`, available every year but 2001, when the
consumer leg stands alone). The consumer leg is itself spliced --- the World
Bank consumer-price *level* for Argentina begins only in 2016, so the leg is
the GDP deflator (`NY.GDP.DEFL.KD.ZG`) for 1964--2016 and the INDEC IPC from
2017. The 2007--2015 values of the blend are replaced wholesale by the
alternative-index average described above.

The historical leg is coarser still. In the original workbook the
nineteenth-century inflation and devaluation series are piecewise constant
within administrations rather than genuinely annual --- inflation reads 3.19
percent for each of 1854--56 and 0.53 for each of 1857--59 --- and over
1853--59 the two series are numerically identical, the price proxy being the
currency's external depreciation. They separate from 1860 (1.68 against 2.08).
Inflation is therefore the CMPI's coarsest dimension in the early sample, which
is why Section 7 reports what happens to Obligado's rank when it is dropped.

Two further consequences follow for the modern leg, and neither is cosmetic.
First, for most of the modern period "inflation" is half a wholesale-price
index and, before 2017, half an output deflator rather than a consumer-price
index. Second, both legs are **annual averages**, so the variable is an
average-over-average rate, while the devaluation dimension is measured
December-to-December. The two dimensions
therefore date the same event differently: a disinflation that happens within a
year shows up immediately in the December devaluation series but only with a
year's lag in the averaged inflation series.

The 2024--25 term is where this bites hardest. On the annual-average
convention, inflation reads 137.4 percent in 2023 and 217.6 in 2024, so the
2024 innovation against the inherited 2023 base is $+0.29$ log points --- a
*deterioration*. Measured December-to-December the same two years read 211.2
and 117.7 percent, an innovation of $-0.36$ --- one of the sharpest
disinflations in the sample. The averaged convention costs the term its
inflation score in the first of its two years and is the main reason its
inflation component is 0.514, close to the pool median, while its devaluation
component is 0.928. We retain the annual-average convention rather than
promoting the December series because the December-to-December blend can only
be built back to 1944 and its wholesale leg is unavailable throughout, so
substituting it would split the 173-year pool at a second seam and change the
variable's definition for the historical regime, where the original workbook
supplies annual data only. The direction of the resulting bias is stated in
the Limitations.

Figure 1 maps data reliability by year and variable; the full lineage of
every series is documented in the replication package.

![Data reliability by year and variable across the nine index inputs. Letters grade source quality; the catalogue in Appendix B documents every flagged episode.](generated/fig_quality.png){width=100%}

## Statistical integrity: known statistical manipulations, measurement distortions, and accounting practices

An internally comparable assessment of Argentine administrations must confront
a documented fact: several governments manipulated official statistics ---
the 2007--2015 INDEC consumer-price index, criminally adjudicated --- or used
fiscal and monetary accounting that flatters the headline numbers while
shifting costs across time or off the books. Appendix B catalogues every such
practice known to materially affect the nine variables behind the CMPI and
FPI --- twenty-three entries spanning 1931--2025 --- stating for each the
direction of the bias and its treatment here.

The treatment discipline is explicit. **Corrected / corrected-baseline**
practices are fixed in the headline only when each row resolves to a retained
official artifact, exact URL, source locator, extraction formula, uncertainty
statement, and SHA-256. Fiscal percentages are generated from exact official
peso operands and the same dataset-379 revenue or World Bank GDP denominators
used by the scoring pipeline. Official or paper-comparable series remain as
audit columns and official-versus-corrected charts expose the size of each
correction.
**Sensitivity-only** practices remain too judgment-dependent for the headline,
so they enter as documented memo columns and re-ranked variants, reported
whichever administration they favour. **Documented** practices are outside the
nine index variables or not confidently quantifiable, and are flagged for the
reader. No adjustment relies on the unsupported assertion of any government,
including the current one.

**Coverage asymmetry across eras.** The corrections above are symmetric in *direction* --- they penalise whichever administration understated a burden and credit whichever consolidated it --- but their *coverage* is not symmetric across eras. The 2000--2025 series are corrected against independent, reproducible sources, whereas the 1853--1999 series are used as the original authors published them, and several historical distortions (the 1931--59 parallel-exchange premia and the 1980s *Cuenta de Regulación Monetaria* quasi-fiscal deficit) enter only as sensitivity variants rather than the headline, because no single reproducible series reconstructs them. This is a data-availability constraint rather than a modelling choice, but it does mean the cross-era ranking is not fully apples-to-apples: the modern terms are scored on corrected inputs while the historical terms carry whatever distortions their original sources contained. Section 7 reports the 1946--59 premium overlay as a re-ranked exercise; the 1977--90 quasi-fiscal stock remains a documented historical bound rather than a scored variant. Consistent with the other variants there, they do not displace the top of the ranking, and the reader should weigh the residual non-comparability accordingly.

The baseline carries the corrections that can be implemented with reproducible,
sourced data:

**Consumer prices, 2007--2015.** INDEC's manipulation of the CPI --- a fake
official index --- understated inflation roughly three- to four-fold. The
episode ended in the IMF censure [@imf2013censure] and the criminal
conviction, upheld on appeal, of Commerce Secretary Guillermo Moreno for
abuse of authority over the IPC. The baseline replaces those years with the
continuous official Santa Fe IPEC December-to-December chain
[@ipec_santa_fe_cpi]. Official CABA and San Luis series are retained as
sensitivities where their pinned files overlap [@dgeyc_caba_cpi;
@dpec_san_luis_cpi].

![Official provincial CPI evidence, 2007--2015. The baseline uses the continuous Santa Fe IPEC chain; CABA and San Luis observations bound official-local sensitivities where available.](generated/fig_inflation.png){width=100%}

**Real output growth, 2007--2015.** The same INDEC takeover produced volume
manipulation in the base-1993 national accounts (2008 official $+6.8$ versus
revised $+4.1$ percent; 2009 $+0.9$ versus $-5.9$, both on total GDP). The World Bank series used
here embed INDEC's 2016 revision, whose cumulative 2008--15 correction matches
the independent ARKLEMS reconstruction [@coremberg2017]. Figure 3 compares
the vintages.

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

## Restoring the interest concept

The original defines its third variable as *"the real interest rate on hard
currency … a proxy for country risk fluctuations and tightness in the credit
market"* --- a rate **level**, and its own 1852--1997 series is one. The BCRP
EMBIG series that extends the dimension from 1998 is a **spread**, which drops
the risk-free leg and breaks the level at the seam. Adding the US ten-year
real yield back closes it: 1997 reads 9.75 percent and 1998 reads 9.88
percent, against 5.98 for the bare spread --- a level jump of $+0.13$ instead
of $-3.77$ percentage points.

A second restoration is required for the 2002--H1 2005 payments default. In
those years the quotation is not a borrowing cost: it prices instruments on
which no coupons were being paid, while the sovereign had no market access at
all, and the June-2005 exchange then rebuilt the index on the post-haircut
bonds. Read as a rate, the window produces innovations 3.5 times larger than
anything else in the 173-year pool and sits far outside the historical support
(a maximum of 57.9 percent against 17.4 for 1852--1997). The treatment is the
one already applied to the pinned official exchange rate under exchange
controls --- replace a distorted price with a meaningful one --- here by
holding the last quotation from a functioning market, the 2001 level of 19.07
percent. Innovations inside the window are then zero, which states honestly
that no rate was observable. The innovation column contracts from $\pm 0.51$
to $\pm 0.15$.

Both restorations are curated, ESTIMATE-flagged and reverted end to end in
Section 7. Both are symmetric: the 2002--03 term rises because it stops being
charged for the market price of debt it was not paying, and the 2004--07 term
falls because it stops being credited for that price disappearing. Neither
degrades the replication --- the restricted-pool correlation against the
original Table 3.4 *improves* on the CMPI, from $0.952$ to $0.953$, and holds
on the FPI at $0.996$ --- and the Overall podium is unchanged. Because the
same series builds the FPI's $(1+r)/(1+g)$, both restorations move two of the
nine components and both indices are re-ranked together throughout.

## Two corrections to the modern debt stock

The FPI's two debt-stock components require corrections that no official
series provides.

First, the **exchange-control revaluation**: during cepo years the
dollar-valued GDP in the debt/GDP denominator is inflated by the artificially
low official rate. The headline keeps the published USD Treasury stock and
replaces that official GDP with GDP converted at the free-market (CCL/blue)
rate. Central-bank remunerated liabilities are then added unscaled: they are
already a peso/GDP ratio, so multiplying them by the gap would treat a
Treasury migration of the same stock as new foreign-currency debt. Section 7
retains 50 percent exposure as a conservative lower bound.

Second, the **consolidation of quasi-fiscal debt**: from 2002 the central
bank sterilized monetary emission with remunerated liabilities (Lebac/Nobac,
then Leliq, then Pases) that repeatedly exceeded ten percent of GDP ---
economically public debt, but absent from every Treasury statistic. The
correction adds the measured year-end stock (BCRA statistical-API series,
December observations) to the public debt of 2003--2025. Figure 5
shows the layered debt stock. The associated quasi-fiscal interest
flow never enters the Treasury's primary result and is omitted from the
scored index (Appendix B, row 12).

Table 1 summarizes both corrections by administration. The corrections are
decisive for the modern fiscal ranking (Section 5), and symmetric: they
penalize the administrations that accumulated hidden liabilities and credit
those that consolidated them, whichever side of the political spectrum either
falls on.

| Administration | Years | Debt/GDP off. | Cepo x | BCRA % GDP | Debt/GDP adj. |
|:-----------------------|-----------:|------------:|--------:|---------:|------------:|
| Duhalde | 2002-2003 | 1.487 | 1.000 | 1.712 | 1.504 |
| N.Kirchner | 2004-2007 | 0.817 | 1.000 | 5.404 | 0.934 |
| C.Kirchner | 2008-2011 | 0.461 | 1.000 | 4.270 | 0.544 |
| C.Kirchner II | 2012-2015 | 0.415 | 1.397 | 4.563 | 0.653 |
| Macri | 2016-2019 | 0.587 | 1.025 | 7.217 | 0.677 |
| Fernandez | 2020-2023 | 0.703 | 1.857 | 11.387 | 1.433 |
| Milei | 2024-2025 | 0.699 | 1.186 | 0.028 | 0.847 |
: Exchange-control factor and central-bank quasi-fiscal debt by administration (term means). "Cepo x" is the free-market/official factor applied to the whole published USD Treasury stock. "BCRA % GDP" is the remunerated-liability stock consolidated into public debt, unscaled.

![Public debt layers, 2001--2025: official Treasury stock, exchange-control revaluation, and consolidated central-bank remunerated liabilities.](generated/fig_debt-layers.png){width=100%}

The same discipline governs the primary-balance components. The corrected
headline removes only measured official FGS property income, booked BCRA
transfers, exact 2016--17 and 2024 regularization receipts, and the official
2021 SDR booking [@bcra_reports_2009_2015; @afip_arca_fiscal_reports;
@opc_budget_2022]. Official OPC 2024--25 capitalized-interest operands adjust
the debt-service ratio [@opc_debt_operations]. Every amount is retained in pesos and linked
row-by-row to its source; the generator derives the percentages.
Author-estimated models do not enter the paper; mechanisms without
reproducible official annual operands are disclosed only as limitations.
Figure 6 contrasts the reported and measured structural primary results.

![Official versus structural primary result: one-off and accounting-driven revenues removed.](generated/fig_primary.png){width=100%}

## What moves a debt ratio

Both FPI debt components are ratios of a largely hard-currency stock to a
current-dollar flow, and the corrected baseline of Section 4.5 adds two
measurement corrections on top of the official ratio. Five separable things
therefore move the corrected debt/GDP ratio: borrowing or repayment, growth of
the real denominator, revaluation of that denominator's dollar price, the
closing or opening of the exchange gap, and the recognition of liabilities the
official stock omits. Only the first is fiscal behaviour. Because the corrected
ratio is assembled in nested steps --- the observed stock $B$ over official
current-dollar GDP $Y$, that GDP re-valued on control years by the
free/official gap $\kappa$, plus the omitted liabilities $u$ --- the term
change then splits additively and exactly in logs:
$$\Delta\ln\Big(\tfrac{B}{Y}\kappa + u\Big) = \underbrace{\Delta\ln B - \Delta\ln Y_{\text{real}} - \Delta\ln P^{\$}}_{\text{official ratio}} \; + \; \underbrace{\Delta\ln \kappa \; + \; \Delta\ln\big(1 + u/R_{1}\big)}_{\text{measurement corrections}},$$
where $R_1 = (B/Y)\kappa$. Table 2 reports the split for every administration
since 1984, measured from each term's inherited year to its last --- the same
baseline the innovation machinery uses. The table's "cepo" column is
$\Delta\ln\kappa$.

The exercise is diagnostic, not a correction: the ranking in Section 5 is
unchanged by it. But it identifies which high fiscal scores rest on
deleveraging and which rest on a denominator or on the corrections, and it is
the motivation for the constant-price variant of Section 7. The reading is
blunt. No modern administration delivers a large reduction in the *observed*
debt stock: the most favourable is 2004--07, which holds it roughly flat
($-1.4$ log points, USD 179bn to USD 177bn), and every term since 2016 has
raised it. What separates the terms is which denominator or correction moved.
The largest dollar-price effects belong to Convertibility (1989--95, ninety-seven
log points) and to 2003--07 (forty-eight); the largest exchange-gap effects in
Table 2 are the 2020--23 widening ($+61.0$ log points) and its 2024--25
reversal ($-63.7$). Read against the observed stock, the recent
improvement in the debt ratio is a valuation and consolidation event rather
than repayment --- a point Section 6 returns to.

| Administration | Span | D/Y in | D/Y out | D/Y Δ | stock | real GDP | US$ price | cepo | unrecog. |
|:-----------------------|--------------:|-------:|-------:|--------:|---------:|--------:|---------:|--------:|------------:|
| Alfonsin | 1983→1989 | 0.522 | 1.039 | 68.9 | 38.4 | 3.7 | 26.9 | 0.0 | 0.0 |
| Menem | 1989→1995 | 1.039 | 0.361 | -105.7 | 15.7 | -24.6 | -96.9 | 0.0 | 0.0 |
| Menem II | 1995→1999 | 0.361 | 0.431 | 17.7 | 27.1 | -13.5 | 4.1 | 0.0 | 0.0 |
| De la Rua | 1999→2001 | 0.431 | 0.537 | 22.0 | 16.6 | 5.3 | 0.1 | 0.0 | -0.0 |
| Duhalde | 2001→2003 | 0.537 | 1.43 | 98.0 | 21.8 | 3.1 | 71.4 | 0.0 | 1.7 |
| N.Kirchner | 2003→2007 | 1.43 | 0.742 | -65.5 | -1.4 | -33.5 | -47.8 | 0.0 | 17.1 |
| C.Kirchner | 2007→2011 | 0.742 | 0.43 | -54.6 | 10.9 | -13.4 | -47.8 | 0.0 | -4.3 |
| C.Kirchner II | 2011→2015 | 0.43 | 0.653 | 41.8 | 19.9 | -1.5 | -10.0 | 34.0 | -0.6 |
| Macri | 2015→2019 | 0.653 | 0.847 | 26.0 | 29.4 | 4.0 | 24.4 | -24.6 | -7.3 |
| Fernandez | 2019→2023 | 0.847 | 1.375 | 48.4 | 13.7 | -3.5 | -33.7 | 61.0 | 10.9 |
| Milei | 2023→2025 | 1.375 | 0.723 | -64.3 | 20.5 | -2.9 | -2.1 | -63.7 | -16.1 |
: Additive decomposition of each modern term's *corrected* debt/GDP change, inherited year to last year, into log contributions that sum to the total (percent; negative is an improvement). "Stock" is the observed gross public debt in current dollars and is the only column reflecting borrowing or repayment; "cepo" is the whole-stock exchange-gap correction and "unrecog." is the remaining liability correction. Both move the ratio with no lending or repayment and are identically zero before 2001, so the pre-2000 rows reduce to the classical three-way split. Debt/exports carries no exchange-gap term because exports are already a hard-currency flow.

# Results

## The CMPI ranking

The CMPI ranking of all 41 administrations is reported in Table 3. Menem
(1990--95) ranks first, the 2024--25 stabilization second, and Obligado
(1854--56) third; the bottom of the table collects the crisis terms ---
Alsina (1853) last, preceded by Guido (1962--63), De Alvear (1923--28),
the second Cristina Kirchner term (2012--15), and the hyperinflation endgame
of Alfonsín (1984--89).

| Administration | Rank | Years | Regime | Inflation | Devaluation | Interest | Growth | CMPI |
|:----------------------------------------|--------:|------------------:|------------:|-------------:|---------------:|------------:|----------:|--------:|
| Menem | 1 | 1990–1995 | Modern | 0.975 | 0.980 | 0.876 | 0.812 | 0.911 |
| Milei | 2 | 2024–2025 | Modern | 0.514 | 0.928 | 0.986 | 0.595 | 0.756 |
| Obligado | 3 | 1854–1856 | Historical | 0.784 | 0.778 | 0.526 | 0.915 | 0.751 |
| Menem II | 4 | 1996–1999 | Modern | 0.679 | 0.610 | 0.938 | 0.676 | 0.726 |
| Perón II | 5 | 1952–1955 | Historical | 0.880 | 0.871 | 0.552 | 0.436 | 0.685 |
| Justo | 6 | 1932–1937 | Historical | 0.345 | 0.831 | 0.731 | 0.805 | 0.678 |
| Sarmiento | 7 | 1869–1874 | Historical | 0.433 | 0.549 | 0.939 | 0.663 | 0.646 |
| Roca | 8 | 1881–1886 | Historical | 0.917 | 0.310 | 0.766 | 0.504 | 0.624 |
| Mitre | 9 | 1860–1868 | Historical | 0.404 | 0.435 | 0.809 | 0.665 | 0.579 |
| Ramírez/Farrell | 10 | 1943–1945 | Historical | 0.549 | 0.607 | 0.613 | 0.472 | 0.560 |
| Peron III | 11 | 1973–1975 | Modern | 0.530 | 0.303 | 0.844 | 0.516 | 0.548 |
| Pellegrini | 12 | 1891–1892 | Historical | 0.595 | 0.688 | 0.367 | 0.520 | 0.543 |
| Ongania | 13 | 1967–1969 | Modern | 0.686 | 0.663 | 0.121 | 0.699 | 0.542 |
| Yrigoyen | 14 | 1917–1922 | Historical | 0.682 | 0.490 | 0.315 | 0.680 | 0.542 |
| Avellaneda | 15 | 1875–1880 | Historical | 0.403 | 0.506 | 0.280 | 0.954 | 0.536 |
| Ortiz/Castillo | 16 | 1938–1942 | Historical | 0.688 | 0.295 | 0.908 | 0.250 | 0.535 |
| Videla/Viola/Galtieri/Bignone | 17 | 1976–1983 | Modern | 0.577 | 0.871 | 0.153 | 0.502 | 0.526 |
| Sáenz Peña R./de la Plaza | 18 | 1911–1916 | Historical | 0.617 | 0.579 | 0.645 | 0.243 | 0.521 |
| N.Kirchner | 19 | 2004–2007 | Modern | 0.578 | 0.178 | 0.701 | 0.465 | 0.480 |
| Quintana/Figueroa | 20 | 1905–1910 | Historical | 0.441 | 0.544 | 0.679 | 0.224 | 0.472 |
| Aramburu | 21 | 1956–1957 | Historical | 0.263 | 0.864 | 0.384 | 0.329 | 0.460 |
| De la Rua | 22 | 2000–2001 | Modern | 0.428 | 0.549 | 0.251 | 0.500 | 0.432 |
| Fernandez | 22 | 2020–2023 | Modern | 0.431 | 0.623 | 0.114 | 0.561 | 0.432 |
| Perón I | 24 | 1946–1951 | Historical | 0.323 | 0.213 | 0.465 | 0.719 | 0.430 |
| Roca II | 25 | 1899–1904 | Historical | 0.473 | 0.329 | 0.500 | 0.400 | 0.425 |
| Juárez Celman | 26 | 1887–1890 | Historical | 0.387 | 0.341 | 0.234 | 0.689 | 0.413 |
| Yrigoyen II | 27 | 1929–1930 | Historical | 0.633 | 0.358 | 0.396 | 0.228 | 0.404 |
| Uriburu JF | 28 | 1931–1931 | Historical | 0.480 | 0.341 | 0.439 | 0.353 | 0.403 |
| Frondizi | 29 | 1958–1961 | Historical | 0.416 | 0.403 | 0.350 | 0.442 | 0.403 |
| Illia | 30 | 1964–1966 | Modern | 0.499 | 0.133 | 0.254 | 0.713 | 0.400 |
| Macri | 31 | 2016–2019 | Modern | 0.397 | 0.423 | 0.422 | 0.316 | 0.390 |
| Duhalde | 32 | 2002–2003 | Modern | 0.116 | 0.410 | 0.416 | 0.523 | 0.366 |
| Alsina II | 33 | 1857–1859 | Historical | 0.547 | 0.620 | 0.214 | 0.067 | 0.362 |
| Sáenz Peña L./Uriburu JE | 34 | 1893–1898 | Historical | 0.143 | 0.382 | 0.587 | 0.296 | 0.352 |
| Levingston/Lanusse | 35 | 1970–1972 | Modern | 0.187 | 0.108 | 0.705 | 0.197 | 0.299 |
| C.Kirchner | 36 | 2008–2011 | Modern | 0.334 | 0.412 | 0.126 | 0.286 | 0.289 |
| Alfonsin | 37 | 1984–1989 | Modern | 0.399 | 0.448 | 0.014 | 0.274 | 0.284 |
| C.Kirchner II | 38 | 2012–2015 | Modern | 0.451 | 0.146 | 0.305 | 0.228 | 0.283 |
| De Alvear | 39 | 1923–1928 | Historical | 0.281 | 0.357 | 0.090 | 0.378 | 0.276 |
| Guido | 40 | 1962–1963 | Historical | 0.243 | 0.390 | 0.188 | 0.075 | 0.224 |
| Alsina | 41 | 1853–1853 | Historical | 0.104 | 0.145 | 0.416 | 0.000 | 0.166 |
: The Classical Macroeconomic Pressure Index, all 41 administrations, 1853--2025. Component columns are mean innovation percentiles over the term; the pool is 173 annual observations.

## Fiscal pressure

Table 4 reports the FPI. Obligado (1854--56) leads, with the 2024--25 term
second, Roca II (1899--1904) third (0.775) and N. Kirchner (2004--07) fourth
(0.719). The two debt-stock corrections of
Section 4.5 drive the modern reordering: the 2023 inherited baseline carries
both a free/official exchange factor of 2.021 (Table 1 reports the 2020--23
term mean of 1.857) and a central-bank
quasi-fiscal debt stock of approximately eleven percent of GDP over the 2020--23
term (BCRA statistical API; Table 1), against which the
2024--25 consolidation and
the measured primary surplus register as a sharp *reduction* in fiscal pressure,
where the uncorrected Treasury ratio --- which divides by a GDP still
converted at the official rate --- records an increase. The reduction is a
denominator and a consolidation rather than repayment: the observed stock rose
over the term (Table 2), and what the corrections change is the denominator it
is measured against and the liabilities the 2023 baseline left out.
The 2012--15 term falls to the bottom of the FPI, mainly because of the
exchange gap ($+34.0$ log points in Table 2); its BCRA mean was 4.6 percent of
GDP, below the 2016--19 mean of 7.2 percent, and unrecognized liabilities
slightly reduced the ratio ($-0.6$ log points). The 2020--23 term sits next to
it: it combined a quasi-fiscal stock (a term mean of 11.4 percent of GDP) with
a 61.0-log-point exchange-gap widening. Néstor Kirchner (2004--07)
still ranks fourth on the FPI because the 2005 restructuring --- among the deepest
haircuts in the modern sovereign-debt record [@sturzeneggerzettelmeyer2008]
--- cut the far larger Treasury debt even as sterilization began. That is a
fall in the *ratio*, and it is worth being precise about its sources, because
the FPI reads it as fiscal behaviour. Table 2 decomposes every modern term's
debt-ratio change into the observed stock, the real denominator, the
denominator's dollar price, and the two corrections. For 2003--07 the observed
stock was essentially flat --- USD 179bn to USD 177bn, $-1.4$ log points ---
while corrected debt/GDP fell 65.5. The improvement is 33.5
points of real growth and 47.8 of dollar-price revaluation, against
which the recognition of holdout and quasi-fiscal liabilities pushes back
17.1. Almost none of it is repayment: the 2005 haircut removed debt that
the reported stock had already ceased to accrue, and what the term did not do
was retire the surviving stock. The same reading applies, with different
weights, to Convertibility (1989--95): a stock that grew 15.7 log points
against a ratio that fell 105.7. Section 7 re-ranks the FPI with
the revaluation removed.

| Administration | Rank | Years | Debt / GDP | Debt / Exp | Res / Rev | Res / DebtSv | (1+r) / (1+g) | FPI |
|:----------------------------------------|--------:|----------------:|---------:|---------:|--------:|----------:|----------:|-------:|
| Obligado | 1 | 1854–1856 | 0.701 | 0.690 | 0.967 | 0.933 | 0.942 | 0.847 |
| Milei | 2 | 2024–2025 | 0.951 | 0.827 | 0.731 | 0.815 | 0.821 | 0.829 |
| Roca II | 3 | 1899–1904 | 0.719 | 0.898 | 0.962 | 0.876 | 0.418 | 0.775 |
| N.Kirchner | 4 | 2004–2007 | 0.945 | 0.892 | 0.487 | 0.652 | 0.621 | 0.719 |
| Menem | 5 | 1990–1995 | 0.969 | 0.565 | 0.617 | 0.572 | 0.851 | 0.715 |
| Perón I | 6 | 1946–1951 | 0.798 | 0.970 | 0.734 | 0.318 | 0.692 | 0.702 |
| Avellaneda | 7 | 1875–1880 | 0.821 | 0.550 | 0.512 | 0.478 | 0.963 | 0.665 |
| Mitre | 8 | 1860–1868 | 0.326 | 0.389 | 0.905 | 0.969 | 0.699 | 0.658 |
| Yrigoyen | 9 | 1917–1922 | 0.601 | 0.768 | 0.624 | 0.579 | 0.623 | 0.639 |
| Uriburu JF | 10 | 1931–1931 | 0.636 | 0.775 | 0.746 | 0.647 | 0.341 | 0.629 |
| Ongania | 11 | 1967–1969 | 0.480 | 0.410 | 0.651 | 0.827 | 0.565 | 0.587 |
| Videla/Viola/Galtieri/Bignone | 12 | 1976–1983 | 0.417 | 0.229 | 0.879 | 0.861 | 0.402 | 0.558 |
| Sarmiento | 13 | 1869–1874 | 0.268 | 0.405 | 0.553 | 0.678 | 0.707 | 0.522 |
| Illia | 14 | 1964–1966 | 0.491 | 0.486 | 0.435 | 0.435 | 0.645 | 0.499 |
| Macri | 15 | 2016–2019 | 0.435 | 0.285 | 0.620 | 0.850 | 0.299 | 0.498 |
| Menem II | 16 | 1996–1999 | 0.399 | 0.627 | 0.354 | 0.331 | 0.751 | 0.492 |
| De la Rua | 17 | 2000–2001 | 0.303 | 0.942 | 0.364 | 0.445 | 0.364 | 0.484 |
| Frondizi | 18 | 1958–1961 | 0.678 | 0.597 | 0.434 | 0.308 | 0.399 | 0.483 |
| Aramburu | 19 | 1956–1957 | 0.598 | 0.572 | 0.448 | 0.416 | 0.327 | 0.472 |
| Sáenz Peña L./Uriburu JE | 20 | 1893–1898 | 0.803 | 0.527 | 0.348 | 0.332 | 0.350 | 0.472 |
| Quintana/Figueroa | 21 | 1905–1910 | 0.804 | 0.801 | 0.159 | 0.237 | 0.315 | 0.463 |
| C.Kirchner | 22 | 2008–2011 | 0.821 | 0.736 | 0.227 | 0.202 | 0.215 | 0.440 |
| De Alvear | 23 | 1923–1928 | 0.307 | 0.500 | 0.555 | 0.555 | 0.267 | 0.437 |
| Pellegrini | 24 | 1891–1892 | 0.127 | 0.428 | 0.540 | 0.616 | 0.465 | 0.435 |
| Levingston/Lanusse | 25 | 1970–1972 | 0.426 | 0.655 | 0.331 | 0.441 | 0.306 | 0.432 |
| Perón II | 26 | 1952–1955 | 0.382 | 0.149 | 0.412 | 0.663 | 0.474 | 0.416 |
| Justo | 27 | 1932–1937 | 0.256 | 0.097 | 0.456 | 0.439 | 0.829 | 0.415 |
| Sáenz Peña R./de la Plaza | 28 | 1911–1916 | 0.287 | 0.546 | 0.400 | 0.456 | 0.304 | 0.399 |
| Alfonsin | 29 | 1984–1989 | 0.289 | 0.185 | 0.843 | 0.611 | 0.055 | 0.397 |
| Peron III | 30 | 1973–1975 | 0.449 | 0.636 | 0.073 | 0.143 | 0.588 | 0.378 |
| Roca | 31 | 1881–1886 | 0.552 | 0.364 | 0.138 | 0.218 | 0.562 | 0.367 |
| Ramírez/Farrell | 32 | 1943–1945 | 0.362 | 0.582 | 0.121 | 0.183 | 0.518 | 0.353 |
| Duhalde | 33 | 2002–2003 | 0.003 | 0.179 | 0.486 | 0.590 | 0.503 | 0.352 |
| Ortiz/Castillo | 34 | 1938–1942 | 0.612 | 0.109 | 0.281 | 0.306 | 0.430 | 0.348 |
| Yrigoyen II | 35 | 1929–1930 | 0.633 | 0.350 | 0.205 | 0.263 | 0.246 | 0.339 |
| Guido | 36 | 1962–1963 | 0.434 | 0.893 | 0.142 | 0.118 | 0.092 | 0.336 |
| Juárez Celman | 37 | 1887–1890 | 0.121 | 0.205 | 0.316 | 0.288 | 0.623 | 0.311 |
| Alsina II | 38 | 1857–1859 | 0.216 | 0.518 | 0.195 | 0.162 | 0.073 | 0.233 |
| Fernandez | 39 | 2020–2023 | 0.027 | 0.262 | 0.192 | 0.107 | 0.357 | 0.189 |
| C.Kirchner II | 40 | 2012–2015 | 0.117 | 0.218 | 0.237 | 0.150 | 0.221 | 0.189 |
| Alsina | 41 | 1853–1853 | 0.017 | 0.104 | 0.000 | 0.017 | 0.000 | 0.028 |
: The Fiscal Pressure Index, all 41 administrations. Components are innovation percentiles of debt/GDP, debt/exports, primary result/revenues, primary result/debt service, and $(1+r)/(1+g)$ over the common 173-year pool; the six missing 1861--63 primary-result ratios are arithmetic interpolations of the observed 1860 and 1864 endpoints, not source measurements.

## The Overall Index

Table 5 combines the two indices. Menem (1990--95) remains first, Obligado
second, and the 2024--25 term third, followed by Mitre (1860--68) and the
second Menem term. Two terms reach the top ten almost entirely through the
fiscal index: N. Kirchner (2004--07), eighth on a CMPI rank of nineteen
(Overall 0.600, tied at displayed precision with Avellaneda and Roca II),
and Roca II (1899--1904), seventh on a CMPI rank of twenty-five --- the pattern
discussed below. At the foot of the table sit
Alsina (1853), the second Cristina Kirchner term (2012--15) and Guido
(1962--63). The joint reading exposes the central
*passing-the-buck* dynamic: administrations with a high CMPI rank paired with
a low FPI rank bought macroeconomic calm with debt --- on the Treasury's
books or hidden in the central bank --- and handed the bill to their
successors. The 2024--25 term is unusual in the modern era for ranking in
the top tier on both dimensions, with the caveats of Sections 6 and 8: the
presidency continues through 2027. Two measurement conventions work in favour
of its currently observed 2024--25 record, but they are not parallel to the
Kirchner-era CPI correction: capitalized interest enters the headline
debt-service ratio, while the 2004--05-basket CPI understatement is a
sensitivity variant that costs the term one CMPI place (Section 7). Complete annual observations are used for 2025,
but recent national-account values remain subject to source revisions.

| Administration | Rank | Years | CMPI Rank | FPI Rank | CMPI | FPI | Overall |
|:----------------------------------------|--------:|--------------:|--------:|--------:|--------:|-------:|-----------:|
| Menem | 1 | 1990–1995 | 1 | 5 | 0.911 | 0.715 | 0.813 |
| Obligado | 2 | 1854–1856 | 3 | 1 | 0.751 | 0.847 | 0.799 |
| Milei | 3 | 2024–2025 | 2 | 2 | 0.756 | 0.829 | 0.792 |
| Mitre | 4 | 1860–1868 | 9 | 8 | 0.579 | 0.658 | 0.618 |
| Menem II | 5 | 1996–1999 | 4 | 16 | 0.726 | 0.492 | 0.609 |
| Avellaneda | 6 | 1875–1880 | 15 | 7 | 0.536 | 0.665 | 0.600 |
| Roca II | 7 | 1899–1904 | 25 | 3 | 0.425 | 0.775 | 0.600 |
| N.Kirchner | 8 | 2004–2007 | 19 | 4 | 0.480 | 0.719 | 0.600 |
| Yrigoyen | 9 | 1917–1922 | 14 | 9 | 0.542 | 0.639 | 0.591 |
| Sarmiento | 10 | 1869–1874 | 7 | 13 | 0.646 | 0.522 | 0.584 |
| Perón I | 11 | 1946–1951 | 24 | 6 | 0.430 | 0.702 | 0.566 |
| Ongania | 12 | 1967–1969 | 13 | 11 | 0.542 | 0.587 | 0.564 |
| Perón II | 13 | 1952–1955 | 5 | 26 | 0.685 | 0.416 | 0.550 |
| Justo | 14 | 1932–1937 | 6 | 27 | 0.678 | 0.415 | 0.547 |
| Videla/Viola/Galtieri/Bignone | 15 | 1976–1983 | 17 | 12 | 0.526 | 0.558 | 0.542 |
| Uriburu JF | 16 | 1931–1931 | 28 | 10 | 0.403 | 0.629 | 0.516 |
| Roca | 17 | 1881–1886 | 8 | 31 | 0.624 | 0.367 | 0.495 |
| Pellegrini | 18 | 1891–1892 | 12 | 24 | 0.543 | 0.435 | 0.489 |
| Quintana/Figueroa | 19 | 1905–1910 | 20 | 21 | 0.472 | 0.463 | 0.468 |
| Aramburu | 20 | 1956–1957 | 21 | 19 | 0.460 | 0.472 | 0.466 |
| Peron III | 21 | 1973–1975 | 11 | 30 | 0.548 | 0.378 | 0.463 |
| Sáenz Peña R./de la Plaza | 22 | 1911–1916 | 18 | 28 | 0.521 | 0.399 | 0.460 |
| De la Rua | 23 | 2000–2001 | 22 | 17 | 0.432 | 0.484 | 0.458 |
| Ramírez/Farrell | 24 | 1943–1945 | 10 | 32 | 0.560 | 0.353 | 0.457 |
| Illia | 25 | 1964–1966 | 30 | 14 | 0.400 | 0.499 | 0.449 |
| Macri | 26 | 2016–2019 | 31 | 15 | 0.390 | 0.498 | 0.444 |
| Frondizi | 27 | 1958–1961 | 29 | 18 | 0.403 | 0.483 | 0.443 |
| Ortiz/Castillo | 28 | 1938–1942 | 16 | 34 | 0.535 | 0.348 | 0.441 |
| Sáenz Peña L./Uriburu JE | 29 | 1893–1898 | 34 | 20 | 0.352 | 0.472 | 0.412 |
| Yrigoyen II | 30 | 1929–1930 | 27 | 35 | 0.404 | 0.339 | 0.372 |
| Levingston/Lanusse | 31 | 1970–1972 | 35 | 25 | 0.299 | 0.432 | 0.366 |
| C.Kirchner | 32 | 2008–2011 | 36 | 22 | 0.289 | 0.440 | 0.365 |
| Juárez Celman | 33 | 1887–1890 | 26 | 37 | 0.413 | 0.311 | 0.362 |
| Duhalde | 34 | 2002–2003 | 32 | 33 | 0.366 | 0.352 | 0.359 |
| De Alvear | 35 | 1923–1928 | 39 | 23 | 0.276 | 0.437 | 0.357 |
| Alfonsin | 36 | 1984–1989 | 37 | 29 | 0.284 | 0.397 | 0.340 |
| Fernandez | 37 | 2020–2023 | 22 | 39 | 0.432 | 0.189 | 0.311 |
| Alsina II | 38 | 1857–1859 | 33 | 38 | 0.362 | 0.233 | 0.297 |
| Guido | 39 | 1962–1963 | 40 | 36 | 0.224 | 0.336 | 0.280 |
| C.Kirchner II | 40 | 2012–2015 | 38 | 40 | 0.283 | 0.189 | 0.236 |
| Alsina | 41 | 1853–1853 | 41 | 41 | 0.166 | 0.028 | 0.097 |
: The Overall Index. The headline rank is the mean of the CMPI and FPI *scores* (Menem first), the original study's convention.

# Validation against the original study

The implementation is validated against two benchmarks.

**Replication of the published rankings.** Restricting the percentile pool to
1853--1999 removes the pool-expansion effect, so any deviation from the
original Table 3.4 reflects the known data differences (flat within-term
interest averages and WDI-sourced inflation and growth for 1964--99), plus the
disclosed choice to interpolate the six missing 1861--63 raw ratios before
ranking rather than complete relative-index scores after ranking. On this
restricted pool the FPI reproduces the original fiscal ranking with Spearman
$\rho = 0.996$ and the CMPI with $\rho = 0.953$. The
devaluation convention is validated term by term: the December-quotation
series reproduces the original published Table 3.2 devaluation innovations
exactly for three of the four administrations affected by mid-year devaluations
(Illia +27.1\,pp, Onganía --9.0\,pp, Perón III +60.4\,pp) and within 0.1\,pp
for the 1976--83 junta (--81.3 vs.\ the original --81.4), where annual-average
data produce the wrong sign.

**Decomposition of the observed 2024--25 record.** Table 6 decomposes the
two complete Milei calendar years against the first two Menem years. The structure is the
corrective-shock one: a first year dominated by the devaluation and interest
components against a hyper-distressed inherited baseline, and a second year
in which the disinflation component takes over. The comparison bounds the
interpretation of the interim presidency ranking: on a first-two-years basis (Section 7) the
2024--25 program ranks immediately behind the Menem stabilization, in the same
order as the full-term CMPI. These are descriptive ranks rather than formal
statistical tests, but the equal-window comparison does show that the currently
observed record's standing is not an artefact of comparing two years with
longer administration windows.

| Year | Administration | Inflation | Devaluation | Interest | Growth | CMPI |
|:----------|---------------------:|-------------:|---------------:|------------:|----------:|--------:|
| 2024 | Milei | 0.081 | 0.931 | 0.977 | 0.503 | 0.623 |
| 2025 | Milei | 0.948 | 0.925 | 0.994 | 0.688 | 0.889 |
| 1990 | Menem (first 2 yrs) | 0.936 | 0.965 | 0.876 | 0.665 | 0.861 |
| 1991 | Menem (first 2 yrs) | 0.971 | 0.971 | 0.876 | 0.913 | 0.933 |
: Year-by-year CMPI decomposition: the complete 2024 and 2025 observations versus the first two years of the Menem stabilization.

# Robustness

**Sensitivity and attribution variants.** The headline FPI uses the
corrected fiscal baseline: documented holdout debt, official 2024--25
capitalized interest, measured one-off-revenue removal, paired importer-debt
increases/BOPREAL residuals, cepo revaluation, and BCRA quasi-fiscal debt.
Cumulative importer-debt increases in 2022--23 and audited Series 1--3
BOPREAL residuals in 2024--25 are paired inside this headline; isolating
the pair moves no focus FPI rank. Models excluded for
insufficient annual evidence have no numerical variants.
The re-ranked variants in Table 7 report the paper-comparable official convention, the
conservative 50 percent lower bound, and the total-growth $(1+r)/(1+g)$ definition. A 1946--59 parallel-premium overlay remains a notebook-only sensitivity;
Obligado holds the top of the FPI under that overlay as well as under every Table 7
column. The
largest movement is the 2024--25 term's fall from second to tenth under the
original-study convention, which is the comparator's purpose: it is what the
term scores when the corrections of Section 4.5 are withheld and the raw
Treasury series is taken at face value. The remaining FX variant shows how the
whole-stock headline changes if only half the stock is treated as
foreign-currency exposure. Macri moves from fifteenth to twentieth at 50
percent; Fernández and the second Cristina Kirchner term swap the bottom two
places. Every other focus administration keeps its headline rank.

| Administration | Corrected baseline | Original-study convention | 50% FX share | Total-growth r/g |
|:-----------------------|-------------:|------------------:|----------:|----------------:|
| Obligado | 1 | 1 | 1 | 1 |
| Milei | 2 | 10 | 2 | 2 |
| Roca II | 3 | 2 | 3 | 3 |
| N.Kirchner | 4 | 3 | 4 | 4 |
| Menem | 5 | 4 | 5 | 5 |
| Macri | 15 | 29 | 20 | 15 |
| C.Kirchner II | 40 | 39 | 39 | 39 |
| Fernandez | 39 | 38 | 40 | 40 |
| Duhalde | 33 | 32 | 33 | 33 |
: FPI rank sensitivity for the focus administrations under the exchange-control and growth-definition variants.

**Inflation sources.** The headline is the continuous official Santa Fe IPEC
chain. Its lower and upper sensitivity bounds use official CABA and San Luis
observations only where those retained files overlap, rather than a
cross-source private-index average. The basket-vintage variant of Appendix B
row 17 shifts the
annual-average series by the gap between the IPCBA and the national index over
2017--2024; because the stale 2004--05 basket under-weights services, the gap
raises measured inflation in 2024 from 218 to 245 percent. It costs the
2024--25 term one place, from second to third, and the 2020--23 term two, from
twenty-second to twenty-fourth; no other focus administration moves. CABA and
San Luis are sensitivity columns only; Santa Fe remains the headline. The
basket-vintage variant is likewise outside the headline because it rests on a
single-jurisdiction index.

**Component weights.** The equal weighting of components is the original
study's convention; the component-exclusion variants bound its impact as
extreme weight perturbations. Menem remains first with the interest dimension
removed entirely, while the 2024--25 term falls from second to fifth --- the
country-risk collapse is a material part of its score --- and Obligado falls
from third to fifth when inflation, its coarsest pre-1866 proxy dimension, is
removed.

**Term length.** Re-scoring every administration on its first two years only
(Table 8) gives every administration the same two-year observation window. The
CMPI podium is unchanged --- Menem, the 2024--25 term, then Obligado --- but
Macri rises from thirty-first to twelfth, so the equal window moves more than
the short-corrective-shock caveat alone.

| Administration | Full-term rank | First-2-years rank |
|:-----------------------------------|-------------:|-----------------:|
| Menem | 1 | 1 |
| Milei | 2 | 2 |
| Obligado | 3 | 3 |
| Menem II | 4 | 4 |
| Justo | 6 | 5 |
| Perón II | 5 | 6 |
| Roca | 8 | 7 |
| Peron III | 11 | 8 |
| Sarmiento | 7 | 9 |
| Ramírez/Farrell | 10 | 10 |
| Sáenz Peña R./de la Plaza | 18 | 11 |
| Macri | 31 | 12 |
: Full-term versus first-two-years CMPI ranks, selected administrations.

**Component collinearity.** Equal weighting also treats the components as independent, which they are not: over the 173-year pool inflation and devaluation co-move at a Pearson correlation of 0.88, so the CMPI effectively places about half its weight on a single nominal-instability factor, while within the FPI the two primary-result ratios correlate at 0.82 and the two debt ratios at 0.52 (Table 9). The component-exclusion variants of Section 7 are the correlation-aware bound on this. Menem holds the CMPI lead in every one of them, but the second and third places do not survive: the 2024--25 term falls to fifth when the interest dimension is dropped and Obligado to fifth when inflation is, so the bound is on the leader rather than on the podium.

| Component pair | Pearson r |
|:-------------------------------------------------|-----------:|
| Inflation – Devaluation (CMPI) | 0.88 |
| Primary result/Rev – /DebtServ (FPI) | 0.84 |
| Debt/GDP – Debt/Exports (FPI) | 0.51 |
| Debt/GDP – (1+r)/(1+g) (FPI) | 0.30 |
: Within-index component collinearity --- Pearson correlation of the annual innovations over the 173-year pool.

**Reverting the interest restorations.** The two restorations of Section 4.4
are in the corrected baseline, so the variants that test them run in reverse.
Table 10 removes the default-window substitution: leaving four default years
at their market quotation gave the 2004--07 term the second-best interest
innovation of the 173-year pool and an inherited $(1+r)/(1+g)$ of 1.453
rather than 1.105. No modeled cash-interest alternative is retained; the
strict provenance rule admits only series with official annual operands.

| Administration | CMPI base | CMPI (a) | FPI base | FPI (a) | Overall base | Overall (a) |
|:-----------------------|--------:|--------:|--------:|-------:|-----------:|-----------:|
| Menem | 1 | 1 | 5 | 5 | 1 | 1 |
| Milei | 2 | 2 | 2 | 2 | 3 | 3 |
| Obligado | 3 | 3 | 1 | 1 | 2 | 2 |
| Mitre | 9 | 9 | 8 | 8 | 4 | 5 |
| N.Kirchner | 19 | 11 | 4 | 4 | 8 | 4 |
| Roca II | 25 | 25 | 3 | 3 | 7 | 8 |
| De la Rua | 22 | 23 | 17 | 17 | 23 | 23 |
| Duhalde | 32 | 39 | 33 | 37 | 34 | 39 |
| C.Kirchner | 36 | 35 | 22 | 22 | 32 | 31 |
| Macri | 31 | 31 | 15 | 15 | 26 | 27 |
| Fernandez | 22 | 22 | 39 | 40 | 37 | 36 |
: CMPI, FPI and Overall ranks with the payments-default substitution reverted (column (a)). Both indices are re-ranked because $(1+r)/(1+g)$ is built from the same series. The substitution is symmetric: the 2002--03 term, charged the cost of the collapse, moves with it.

**The denominator effect.** Table 2 showed that the modern debt ratios move
for five separable reasons, only one of which is borrowing or repayment. This
variant removes the revaluation by rescaling each modern year's debt ratios by
the dollar price index of its own denominator (2003 = 1.000), optionally with
the part of the 2005 exchange that is a transfer from creditors rather than
fiscal effort --- the face reduction on the tendered claims, which the holdout
add-back does not cover --- and the GDP warrants issued with the exchange and
paid by successors.

Unlike the interest restorations this one is **not** promoted, and the
obstacle is coverage rather than principle. The constant-price aggregates
begin in 1960 and the terms-of-trade index in 1980. A full-sample substitute
is constructible from series already in the study --- the dollar price of
domestic output moves with the difference between the inflation and
devaluation log-rates, both of which exist from 1853 --- but it fails
validation against the measured World Bank deflator over 1960--2024: annual
log-changes correlate at 0.52, the mean absolute annual gap is 0.21 log
points, and the 1989--95 cumulative comes out at 6.83 against a measured 2.63.
The failures are structural. Hyperinflation breaks the
December-quotation/annual-average timing identity, and on exchange-control
years the proxy would double-count the revaluation already applied in Section
4.3, because this study prices those years at the free-market rate while World
Bank GDP uses the official one. Before 1960 no validation is possible at all,
since the historical debt ratios arrive from the original workbook already
divided. There is also a reason of principle to stop: debt/exports is immune
to this channel, both sides being in dollars, so a promoted correction would
reach one of the two debt ratios over a third of the pool.

Table 11 stacks everything, and it is worth being exact about what survives.
The *membership* of the top three is invariant: 1990--95, 1854--56 and
2024--25 occupy the first three places in all seven specifications. Their
*order* is not. Menem leads under the four interest specifications; among the
three denominator columns Obligado leads two and the 2024--25 term leads the
constant-price specification. Each of the three therefore spans more than one
place (Menem one to three, Obligado one to two, the 2024--25 term one to
three). Below the podium the denominator variants move terms a good deal
further: the 2004--07 term spans Overall ranks four to eighteen of forty-one
--- four under the pre-revision interest convention, eighteen once the 2005
face reduction is added back --- and the 2008--11, 2002--03 and 1999--2001
terms span six, ten and four places respectively (Overall 31--36, 30--39 and
23--26). The robust claim is
therefore about which three administrations lead, not about their sequence,
and not about the placement of the terms whose scores rest on the 2001--05
default cycle.

| Administration | Baseline | Bare spread | No subst. | Pre-revision | Const-price | + add-backs | Stacked |
|:-----------------------|------------:|----------:|----------:|----------------:|---------------:|-------------:|-----------:|
| Menem | 1 | 1 | 1 | 1 | 3 | 3 | 3 |
| Obligado | 2 | 2 | 2 | 2 | 2 | 1 | 1 |
| Milei | 3 | 3 | 3 | 3 | 1 | 2 | 2 |
| Mitre | 4 | 4 | 5 | 5 | 4 | 5 | 5 |
| N.Kirchner | 8 | 8 | 4 | 4 | 11 | 18 | 15 |
| Roca II | 7 | 7 | 8 | 8 | 7 | 7 | 7 |
| Duhalde | 34 | 34 | 39 | 39 | 30 | 30 | 39 |
| De la Rua | 23 | 23 | 23 | 23 | 26 | 26 | 27 |
| C.Kirchner | 32 | 35 | 31 | 34 | 36 | 36 | 36 |
| Macri | 26 | 26 | 27 | 27 | 24 | 24 | 24 |
| Fernandez | 37 | 37 | 36 | 36 | 38 | 38 | 38 |
: Overall rank under each variant and under the stacked variants. The first columns revert the interest restorations that are in the baseline; the rest add the denominator variants that are not. The administrations whose scores rest on the 2001--05 default cycle move furthest; the top three keep their places as a group, though they reorder within it.

# Discussion

The 173-year unified ranking reproduces the main findings of the original
study for the historical period while placing the 2000--2025 administrations
on the same scale. Stabilizations anchored to hard-currency or convertible
regimes score highest --- Menem's Convertibility first in both the original
and here; Obligado's 1854--56 reforms, which ended decades of inflationary
finance, near the top --- and crisis terms score lowest. The 2024--25
disinflation scores highly even in this long-run context.

Four interpretive points deserve emphasis.

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

**Why the data corrections are decisive.** Five adjustments determine the
credibility of the modern ranking: the alternative price indices stop the
2007--2015 manipulation from inflating the affected scores; the restored
interest *level* --- country-risk spread plus the risk-free leg, with the
2002--05 payments-default window held at its last functioning-market
quotation --- keeps the dimension in the original's concept across 173 years
and removes four readings that were not borrowing costs; the
December-quotation devaluation series fixes the wrong-signed innovations
around mid-year devaluations; the two debt-stock corrections keep the fiscal
components from mismeasuring the 2003--2025 terms in both directions; and the
decomposition of Table 2 separates the part of a debt-ratio improvement that
is repayment from the parts that are a denominator or a correction.

**The default cycle is a measurement boundary, not only an episode.** The
2001--05 default supplies the inherited baseline for two consecutive terms,
and it distorts both indices at once, because the interest series that scores
country risk in the CMPI also builds the FPI's $(1+r)/(1+g)$. Left as a bare
quotation, four default years generated innovations three and a half times
larger than anything else in the pool and handed the term that exited the
default the second-highest interest component of the forty-one terms, while
charging the term that entered it with the mirror image. On the Overall Index
the default-window substitution is directionally symmetric but not equal in
size: the 2002--03 term rises five places (39 to 34) and the 2004--07 term
falls two (4 to 6). Those two --- and only those two --- move by more than one
Overall place in Table 10; stacking both interest restorations also moves the
2008--11 term from 32 to 34. What survives the correction is instructive. The 2004--07 term
still ranks fourth on the FPI --- but Table 2 shows that its corrected debt
ratio fell 65.5 log points while the observed stock in current dollars
barely moved, so the improvement is a write-off and a denominator rather than
repayment. That is the *passing-the-buck* dynamic operating inside the
measurement itself: a revaluation credited to the administration that governs
the upswing and charged to the one that governs its reversal.

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
  source of divergence from the original ranking ($\rho = 0.953$).
- **Inflation is normally an annual-average blend, with a documented
  2007--2015 exception.** Half the regular modern series is a wholesale-price
  index and, before 2017, the consumer leg is an output deflator; both legs are
  annual averages while devaluation and the official Santa Fe correction use
  December-to-December rates. The regular convention systematically penalises
  the first year of a fast disinflation and rewards the first year of a fast
  acceleration, because the average lags the turning point. Its largest single
  effect in this sample is on 2024, whose innovation changes sign between the
  two conventions. No variant re-ranks on the December basis, for the coverage
  reason given in Section 4.2.
- **Data-regime seam at 1963/64** for inflation and growth; devaluation has
  no seam. The interest dimension switches source in 1998, from the original's
  flat within-term real-rate averages to the annual EMBIG series, but no longer
  switches *concept*: adding the US ten-year real yield back to the spread
  restores the rate level and closes the seam to $+0.13$ percentage points,
  against $-3.77$ for the bare spread (Section 4.4). The Section 7 variants
  revert the restoration, and the Overall podium is unchanged either way.
- **The interest dimension carries two curated restorations.** The 1998--2002
  US real yields are estimates rather than measured constant-maturity yields
  (the measured series begins in 2003); the held 2002--05 window assigns four
  years a level nobody observed, which is honest about the absence of a market
  price but is still an assumption; and the 2019--20 restructuring is left at
  its quotation on the judgement that the exchange was consensual and its
  coupons capitalized. Both restorations are reverted in Section 7.
- **One input drives two of the nine components.** The post-1998 interest
  series is both the CMPI interest dimension and the FPI's $(1+r)/(1+g)$, so
  any remaining distortion in it is counted twice in the Overall Index.
- **The FPI debt ratios respond to their denominator and to this study's own
  corrections, not only to borrowing.** Real appreciation or a terms-of-trade
  upswing improves both ratios with the debt stock unchanged, and the reversal
  is charged to the successor --- the pathology this study is named after,
  operating inside its own measurement. The exchange-gap correction of
  Section 4.5 behaves the same way and dominates the recent record: Table 2's
  cepo column supplies 61.0 log points of the 2020--23 ratio
  increase and 63.7 of the 2024--25 decrease, in both cases against an observed debt stock that rose.
  Table 2 decomposes every modern term and Section 7 re-ranks with the
  revaluation removed; it is not promoted to the baseline because no
  constant-price denominator exists before 1960.
- **Four mechanisms are disclosed but not scored without reproducible annual
  operands**: the 2009 amnesty, the 2022--23 export-duty timing effect, unpaid
  default interest in 2002--05, and a year-by-year Paris Club accrual path.
  Price controls and frozen tariffs likewise remain documented
  without a series that separates their effect from observed inflation.
- **The FPI's $(1+r)/(1+g)$ uses per-capita growth** (the only annual series
  available across the full span) where the original defines $g$ as total
  growth; innovations difference out slow-moving population growth almost
  entirely, and the total-growth variant moves every focus rank by at most
  one position (Table 7).
- **The exchange-control revaluation applies the free/official factor to the
  whole published USD Treasury stock.** The 50-percent variant is the remaining
  conservative exposure bound. Central-bank remunerated liabilities are added
  unscaled.
- **The quasi-fiscal consolidation uses measured December year-end stocks**
  from the central bank's statistical API for 2002--2025 (the 2025 stock is
  measured and economically negligible after the Treasury migration). Curated
  anchors remain as cross-checks. The 1977--90 historical stock is
  documented but not re-ranked.
- **The corrected FPI baseline is a corrected baseline, not the official fiscal
  convention**: the original-study-convention columns keep the reported stock
  and cash-result measures for audit, while the headline uses the corrected
  columns that consolidate the documented modern accounting distortions.
- **A debt-definition seam at 1999/2000**: the 1853--1999 ratios arrive from
  the original workbook on its central-government concept, while every modern
  year is total Sector Público Nacional gross debt read from the same
  Secretaría de Finanzas A.2.5 series. The seam is therefore at the regime
  boundary rather than inside the modern block, and the modern block is
  internally consistent throughout.
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
  index asks. The V-shaped-shock caveat of Section 3.4 discloses the
  principal consequence.
- **Equal component weights are the original study's convention**; the
  component-exclusion variants of Section 7 act as extreme weight
  perturbations and bound the impact of this choice on the focus ranks.
- **The indices measure macroeconomic and fiscal management only.**
  Distributional outcomes, poverty, productivity, and institutional quality
  are outside the nine variables; an administration can rank highly here
  while performing poorly on those dimensions, and conversely. The ranking is
  one input to an overall assessment of a government, not a verdict.
- **Two 2024--25 measurement caveats work in the current administration's
  favour**, but they are not parallel to the Kirchner-era CPI correction:
  official capitalized-interest operands adjust the headline debt-service
  ratio, while the 2004--05-basket CPI understates the services-led
  relative-price normalization only in a sensitivity variant that costs the
  term one CMPI place (Section 7).

# Conclusion

Applying both indices of @dellapaolera2003passing across the full 1853--2025
span places all 41 Argentine national administrations on a single 173-year
percentile pool, subject to the cross-era differences in source concepts and
correction coverage set out in Section 4. The method's logic --- judging each government by the
macroeconomic and fiscal improvement it delivers over the situation it
inherited --- puts durable hard-currency and convertible stabilizations at
the top and crises, and the terms that bequeath them, at the bottom. The
unified ranking reproduces the original historical results almost exactly on
the restricted pool while extending them through 2025 with corrected data:
the continuous official Santa Fe IPEC chain for the 2007--2015 statistical
manipulation, with official CABA and San Luis sensitivities; an
interest dimension restored to the original's real hard-currency *rate level*
and held at its last functioning-market quotation through the 2002--05
payments default, free-market exchange rates for the control years,
December-quotation devaluations throughout, and --- for the fiscal dimension
--- an exchange-control revaluation and the consolidation of the central
bank's quasi-fiscal debt.

Two results of this exercise are worth separating. The first is the ranking
itself, which is consistent with the original *passing-the-buck* thesis over the long
run: administrations that purchased macroeconomic calm with debt --- on the
Treasury or hidden in the central bank --- handed the bill to their
successors. Making the hidden half of that debt visible is, we would argue,
the precondition for internally comparable measurement of Argentine economic
governance.

The second is that the same dynamic operates inside the measurement, and has
to be corrected for before the ranking can be read. A sovereign default
distorts both indices simultaneously, because the price of defaulted paper is
not a borrowing cost and yet enters the country-risk dimension of one index
and the debt-amplification factor of the other. A real-exchange-rate or
terms-of-trade cycle improves a debt ratio with the debt stock unchanged, so
the improvement is credited to whoever governs the upswing and the reversal
charged to whoever governs its end. Both effects concentrate on the two
administrations that straddle the 2001--05 crisis. On the Overall Index the
default-window substitution moves those two by five and two places in opposite
directions (Table 10); it does not, by itself, move any other administration
by more than one place, and it leaves the podium and the replication of the
original ranking intact. Stacking both interest restorations also moves the
2008--11 term by two Overall places. An index built to detect
governments that pass costs forward has to be audited for the same behaviour
in its own inputs; where the audit could be settled on the original's own
concept it was promoted to the baseline, and where it could not be extended
to the full 1853--2025 pool it was left as a reported bound.

# Reproducibility {#sec:repro .unnumbered}

**Appendix A.** The replication package --- notebook, data, and paper-generation
scripts --- is at <https://github.com/jahnog/still-passing-the-buck>, with
archived snapshots at
[Zenodo](https://doi.org/10.5281/zenodo.20651730) and
[MPRA](https://mpra.ub.uni-muenchen.de/id/eprint/130511).
Every table and figure is extracted from the executed notebook.

**Data and code availability.** All code, redistributable source data,
processed datasets, validators, and paper-generation scripts are in the
public replication package.

**Funding and conflicts of interest.** The author reports no external funding
and no financial conflict of interest. Scoring rules and every data correction
are applied identically to administrations across the political spectrum.

# The statistical-integrity catalogue {#sec:catalogue .unnumbered}

**Appendix B.** The full twenty-three-entry catalogue, with per-row sources, is
maintained in the replication package; the condensed version follows.
"Corrected" practices are fixed in the baseline (official series kept as
audit columns); "Sensitivity" practices enter re-ranked variants only;
"Documented" practices are flagged for the reader. The machine-readable
taxonomy in `data/provided/correction-taxonomy.csv` is the controlling source
for whether a practice affects the corrected headline, the paper-comparable
audit columns, or sensitivity variants only.

| # | Practice | Period | Bias | Treatment |
|:--|:---------------------------------------------|:------------|:-----------------------|:------------|
| 1 | INDEC CPI manipulation (official Santa Fe chain replaces the fake CPI) | 2007--15 | Inflation down | Corrected |
| 2 | GDP volume manipulation, base-1993 accounts | 2007--15 | Growth up | Corrected |
| 3 | GDP warrants (cupón PBI): issued 2005, paid by successors | 2005--14 | Debt down for the issuer | Sensitivity |
| 4 | Exchange controls (cepo), official rate pinned | 2012--15, 2019--25 | Devaluation, debt/GDP down | Corrected |
| 5 | Historical exchange controls and parallel premia | 1931--59 | Devaluation down | Sensitivity |
| 6 | Cash-basis fiscal reporting during debt suspension | 2002--05 | Potential result/debt-service bias | Documented only |
| 7 | Holdout debt excluded from official stock | 2005--15 | Debt down | Corrected |
| 8 | CER stealth haircut via fake CPI | 2007--15 | Debt, interest down | Documented |
| 9 | Measured FGS property income following pension nationalization | 2009--15 | Result/revenue up | Corrected where an official operand is retained |
| 10 | Reserve hollowing; measured booked BCRA transfers | official-report years | Result/revenue up | Corrected where an official operand is retained |
| 11 | Hidden central-bank debt stock (Lebac/Leliq/Pases) | 2002--2025 (peak 13.4% of GDP in 2023; run off to near zero by 2024) | Debt down | Corrected |
| 12 | Hidden central-bank deficit (quasi-fiscal flow) | 2004--24 | Result up | Documented |
| 13 | 1980s Cuenta de Regulación Monetaria | 1984--89 | Debt down, result up | Sensitivity |
| 14 | Measured one-off revenues (official FGS/BCRA, 2016--17/2024 regularization, 2021 SDR) | official-operand years | Result/revenue up | Corrected |
| 15 | Importer-debt increase / BOPREAL residual pairing | 2022--25 | Debt down, then up | Corrected |
| 16 | Cash surplus excluding capitalizing interest | 2024--25 | Result up | Corrected |
| 17 | CPI basket vintage (2004--05 weights) | 2017--25 | Inflation down | Sensitivity |
| 18 | Price controls; repressed inflation to successor | several | Incumbent inflation down | Documented |
| 19 | Statistics blackouts and labour-data masking | 2002--16 | Non-index inputs affected | Documented |
| 20 | Crisis balance-sheet transfers (1982, 1989, 2002) | as listed | Debt up (real) | Documented |
| 21 | Mechanisms lacking reproducible official annual operands | several | Potential fiscal bias | Documented only |
| 22 | Default premium and missing risk-free leg in the interest series | 1998--2025 seam; 2002--05 window | Interest improvement up for the term exiting default | Corrected |
| 23 | Debt-ratio denominator revaluation (real FX, terms of trade) | 1960--2025 | Debt ratios down | Sensitivity |

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
| Menem II | 1996 | 1999 | -0.94 | 0.00 | 10.15 | 2.29 |
| De la Rua | 2000 | 2001 | 0.69 | 0.00 | 15.02 | -3.68 |
| Duhalde | 2002 | 2003 | 27.51 | 54.27 | 19.07 | -2.06 |
| N.Kirchner | 2004 | 2007 | 11.06 | 1.47 | 12.34 | 7.64 |
| C.Kirchner | 2008 | 2011 | 18.89 | 7.80 | 9.86 | 2.49 |
| C.Kirchner II | 2012 | 2015 | 21.67 | 30.43 | 8.70 | -0.62 |
| Macri | 2016 | 2019 | 30.64 | 40.93 | 7.37 | -1.80 |
| Fernandez | 2020 | 2023 | 54.12 | 64.00 | 20.69 | 0.87 |
| Milei | 2024 | 2025 | 72.38 | 22.90 | 12.54 | 1.17 |
: Contemporaneous (absolute) term averages, all 41 administrations. Mitre's two primary-result ratios include the three arithmetically interpolated 1861--63 cells, so every column averages the same nine term years. This is the record against which the caveat of Section 3.4 should be read.

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

**Percentile assignment.** Innovations are pooled across the 173-year
1853--2025 frame. Let $O_v$ be the number of observed innovations for variable
$v$: $O_v=173$ except for the two primary-result components, where
$O_v=170$. For each variable, the observed innovation in position $o$ of the
favourable-to-unfavourable ordering (best $= 1$) receives the percentile
score of the original Appendix A:

$$R_{v,t} = \frac{O_v - o_{v,t}}{O_v}
\in \left[0,\, \tfrac{O_v-1}{O_v}\right].$$

Favourable means *lower* for inflation, devaluation, the real interest rate,
and the three FPI debt and amplification variables, and *higher* for growth
and the two FPI primary-result variables.

**Ties.** Exactly equal innovations share the average of the percentile slots
they span: if $k$ observations tie at positions $o, \dots, o+k-1$, each is
scored at $\bar{o} = o + (k-1)/2$ rather than at its own position, so identical
values always receive identical scores. This is not a corner case. Because the
1852--1997 interest series is built from published *term averages*, that column
takes only 57 distinct values over the 173-year pool and 86 percent of its
observations fall in a tied group; resolving those ties in sort order would
leave the headline ranking dependent on a non-stable sort. The devaluation
column has 8 percent of its observations tied; inflation and growth have none.
The same principle governs the rank labels every table reports: administrations
whose index scores are exactly equal share a position and the next position is
skipped. One pair is affected on the CMPI (De la Rúa and Fernández at
twenty-second) and none on the FPI.

**Historical fiscal completion.** For primary result/revenues and primary
result/debt service, the workbook has no observations in
$\mathcal{M}=\{1861,1862,1863\}$. Those six raw ratios are completed before
ranking by arithmetic interpolation between the observed endpoints:

$$x_{v,t}=x_{v,1860}+\frac{t-1860}{4}
\left(x_{v,1864}-x_{v,1860}\right),
\qquad t\in\mathcal{M}.$$

Geometric interpolation is undefined because Result/Revenue changes sign.
Every FPI component then ranks $O_v=173$ innovations, including the three
constructed years. This complete-pool convention differs from the original
Appendix A procedure, which ranked the available observations first and
interpolated only the resulting relative-index scores. The three filled years
remain reconstructed observations, not measurements.

**Aggregation.** An administration's component score is the mean relative score
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

**The modern debt-stock corrections.** Write $R^{\text{off}}_t = B_t/Y_t$ for
the official ratio, $\kappa_t = e^{\text{parallel}}_t/e^{\text{official}}_t$
for the exchange-gap factor (identically one outside control years), and $Q_t$ for the central
bank's remunerated liabilities. During exchange-control years the official
rate overstates dollar GDP, so the published USD stock is revalued against
parallel-rate GDP and the quasi-fiscal stock is consolidated unscaled:

$$R^{\text{adj}}_t = R^{\text{off}}_t \kappa_t + \frac{Q_t}{Y_t}.$$

The corrected column used for the headline FPI adds two further liabilities
that the official stock omits --- untendered holdout debt and the paired
importer-debt-increase/BOPREAL-residual operand --- each entering only inside
its documented window and never with a negative sign:

Let $D^{k}_t$ be the dollar value of add-back $k$ and $Y^{p}_t$ be GDP
converted at the parallel rate because those add-backs are dollar liabilities:

$$\left(\frac{B}{Y}\right)^{\text{corr}}_t = R^{\text{adj}}_t +
\sum_{k \in \{h,\,a\}} \max\!\left\{0,\; \frac{D^{k}_t}{Y^{p}_t}\right\}.$$

The debt/exports ratio takes the same add-backs but no $\kappa$, exports
already being a hard-currency flow:

$$\left(\frac{B}{X}\right)^{\text{corr}}_t = \frac{B_t}{X_t} +
\frac{Q_t + \sum_k D^{k}_t}{X_t}.$$

The paired operand is generated from two retained BCRA artifacts rather than
hand-entered estimates. For 2022 and 2023 it is the increase in the RAyPE
year-end stock of imported-goods plus imported-services debt relative to the
common December-2021 baseline (USD 9,975.821m and USD 28,219.351m). For 2024
and 2025 it is the audited residual value of BOPREAL Series 1--3 in Note 4.15
of the 2025 financial statements (USD 9,147.038m and USD 6,817.813m); the
mixed-purpose Series 4 is excluded. These are distinct accounting objects.
Their pairing is an attribution convention, not a claim that the private
importer debt was already public debt; isolating the pair moves no focus
FPI rank.

Section 4.6 decomposes a term's change in $(B/Y)^{\text{corr}}$ into the five
additive log contributions implied by this identity.

**Measured primary-result corrections.** Where retained official one-off
revenues are a share $o$ of dataset-379 total revenues, the headline
structural ratio is

$$\left(\frac{\text{Result}}{\text{Rev}}\right)^{\text{structural}} =
\frac{R - o}{1 - o}.$$

The same adjusted primary-result numerator enters the debt-service component.
If $D$ is the reported Result/DebtService ratio, then

$$\left(\frac{\text{Result}}{\text{Debt service}}\right)^{\text{structural}} =
D\,\frac{R-o}{R}.$$

For 2024--25 only, let $p_t$ be dataset-379 cash interest and $c_t$ the
capitalized-interest peso operand reported by OPC, each divided by nominal
GDP. The headline debt-service ratio is

$$\left(\frac{\text{Result}}{\text{Debt service}}\right)^{\text{corr}}_t =
\left(\frac{\text{Result}}{\text{Debt service}}\right)^{\text{structural}}_t
\times \frac{p_t}{p_t+c_t}.$$

No capitalized-interest adjustment is applied outside 2024--25.

# Glossary {#sec:glossary .unnumbered}

**Appendix E.** Terms used throughout the paper, in alphabetical order.

Administration (term)
: The unit of analysis: one of the 41 government intervals of 1853--2025
  (Section 3.5). Each year of a term is scored against the last year of the
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
: Classical Macroeconomic Pressure Index: the average innovation
  percentile across inflation, devaluation, the hard-currency real interest
  rate, and per-capita growth (Section 3.1).

Convertibility
: The 1991--2001 currency-board regime pegging the peso one-to-one to the US
  dollar.

December quotations
: The exchange-rate convention used throughout: year-end (December) rates
  rather than annual averages, which blend pre- and post-devaluation months
  and produce wrong-signed innovations (Section 4.3).

FPI
: Fiscal Pressure Index: the average innovation percentile across debt/GDP,
  debt/exports, primary result/revenues, primary result/debt service, and the
  debt-amplification factor $(1+r)/(1+g)$ (Section 3.2).

INDEC manipulation
: The 2007--2015 falsification of the official consumer-price index --- a
  fake CPI --- and the parallel volume manipulation of real growth. Commerce
  Secretary Guillermo Moreno was criminally convicted (upheld on appeal);
  the IMF issued the first declaration of censure in its history. Corrected
  in the baseline with the continuous official Santa Fe IPEC chain, with
  official CABA and San Luis overlap as sensitivity evidence (Section 4.3).

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
  consolidated into the debt stock for 2002--2025 (Section 4.5).

# References {.unnumbered}

::: {#refs}
:::

------

\footnotesize

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). © 2026 Javier Hernan Nogueira. Replication code and data: <https://github.com/jahnog/still-passing-the-buck> — archived at [Zenodo](https://doi.org/10.5281/zenodo.20651730) and [MPRA](https://mpra.ub.uni-muenchen.de/id/eprint/130511).

\normalsize

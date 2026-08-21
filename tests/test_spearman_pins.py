"""Pins the restricted-pool (1853-1999) replication of the original Table 3.4.

The paper's headline coherence claim is Spearman rho = 0.996 (FPI) and
0.953 (CMPI) between this study's restricted-pool rankings and the published
ranks of della Paolera, Irigoin & Bozzoli (2003), Table 3.4. These tests
rebuild the restricted pool offline from the committed processed data using
scripts/cmpi_core.py only, so a refactor that silently reorders the historical
ranking fails here before the notebook is ever re-executed.

The assembly mirrors notebook cells 6-47 exactly for the years the restricted
pool needs (1852-1999); post-1999 overrides (cepo, December-quotation modern
devaluation, default-window hold) cannot affect a pool_end=1999 score and are
omitted, except where including them is free.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cmpi_core import (
    apply_program_continuity_exceptions,
    cmpi_scores_from_innovations,
    compute_innovations,
    fpi_scores_from_innovations,
    make_cmpi_year_value_fn,
    make_fpi_year_value_fn,
    splice_series,
)

NOTEBOOK = ROOT / "Historical_CMPI_Extension.ipynb"
FIXTURE_RANKS = ROOT / "tests" / "fixtures" / "original_table_3_4_ranks.csv"


def _notebook_code() -> str:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in nb["cells"]
        if cell["cell_type"] == "code"
    )


def _literal(src: str, varname: str, subs: dict[str, int] | None = None):
    m = re.search(rf"\b{varname}\s*=\s*(\[|\{{)", src)
    if m is None:
        raise AssertionError(f"{varname} not found in notebook source")
    start = m.start(1)
    depth = 0
    for i in range(start, len(src)):
        if src[i] in "([{":
            depth += 1
        elif src[i] in ")]}":
            depth -= 1
            if depth == 0:
                text = src[start : i + 1]
                for name, value in (subs or {}).items():
                    text = re.sub(rf"\b{name}\b", str(value), text)
                return ast.literal_eval(text)
    raise AssertionError(f"Unbalanced literal for {varname}")


# --- The published anchor ----------------------------------------------------


@pytest.fixture(scope="module")
def paper_ranks() -> pd.DataFrame:
    ranks = pd.read_csv(FIXTURE_RANKS).set_index("Administration")
    assert len(ranks) == 33
    return ranks


def test_notebook_published_ranks_match_fixture(paper_ranks: pd.DataFrame) -> None:
    """The fixture is the single home of the Table 3.4 anchor; the notebook's
    hard-coded dicts must agree with it, or one of them is wrong."""
    src = _notebook_code()
    fpi = _literal(src, "PAPER_FPI_RANKS")
    cmpi = _literal(src, "PAPER_CMPI_RANKS")
    assert set(fpi) == set(cmpi) == set(paper_ranks.index)
    assert pd.Series(fpi).sort_index().equals(
        paper_ranks["PaperFPIRank"].sort_index()
    )
    assert pd.Series(cmpi).sort_index().equals(
        paper_ranks["PaperCMPIRank"].sort_index()
    )


# --- Offline rebuild of the restricted pool ----------------------------------


@pytest.fixture(scope="module")
def restricted_scores() -> pd.DataFrame:
    """Recompute CMPI/FPI scores on the 1853-1999 pool from processed data."""
    hist_cmpi = pd.read_csv(
        ROOT / "data/processed/historical/converted_historical_historical-cmpi_1852-01_1963-12.csv"
    ).set_index("Year")
    excel_hist = pd.read_csv(
        ROOT / "data/processed/historical/converted_historical_data-a-1999-excel_1853-01_1963-12.csv"
    ).set_index("Year")

    wdi = pd.read_csv(
        ROOT / "data/processed/indicators/converted_indicators_wdi-argentina_1960-01_2025-12.csv.gz",
        compression="gzip",
    )
    arg_data = wdi[wdi["CountryName"] == "Argentina"].copy()
    arg_data["Year"] = pd.to_numeric(arg_data["Year"], errors="coerce")
    arg_data["Value"] = pd.to_numeric(arg_data["Value"], errors="coerce")
    arg_data = arg_data.dropna(subset=["Year"])
    arg_data["Year"] = arg_data["Year"].astype(int)

    def indicator(code: str, name: str) -> pd.DataFrame:
        return (
            arg_data[arg_data["IndicatorCode"] == code][["Year", "Value"]]
            .set_index("Year")
            .rename(columns={"Value": name})
        )

    # Notebook cell 11: blended inflation.
    cpi_levels = indicator("FP.CPI.TOTL", "CPIPL")
    cpi_levels["CPI"] = cpi_levels["CPIPL"].pct_change() * 100
    arg_cpi = indicator("NY.GDP.DEFL.KD.ZG", "CPIFallback").join(
        cpi_levels[["CPIPL", "CPI"]], how="outer"
    )
    arg_cpi["CPI"] = arg_cpi["CPI"].fillna(arg_cpi["CPIFallback"])
    arg_wpi = indicator("FP.WPI.TOTL", "WPIPL")
    arg_wpi["WPI"] = arg_wpi["WPIPL"].pct_change() * 100
    arg_inflation = arg_cpi.join(arg_wpi["WPI"], how="outer")
    arg_inflation["InflationAvg"] = arg_inflation[["CPI", "WPI"]].mean(axis=1)
    alt_cpi = pd.read_csv(
        ROOT / "data/processed/inflation/converted_inflation_official-provincial-cpi_2007-01_2015-12.csv"
    ).set_index("Year")
    arg_inflation.loc[alt_cpi.index, "InflationAvg"] = alt_cpi["AltAvg"]
    arg_inflation["InflationLog"] = np.log(1 + arg_inflation["InflationAvg"] / 100)

    # Notebook cell 16: devaluation with cepo and paper-devaluation overrides.
    arg_deval = indicator("PA.NUS.ATLS", "USDARS")
    arg_parallel = pd.read_csv(
        ROOT / "data/processed/exchange/converted_exchange_parallel-cepo_2012-01_2025-12.csv"
    ).set_index("Year")
    arg_deval.loc[arg_parallel.index, "USDARS"] = arg_parallel["ParallelARS"]
    arg_deval["Devaluation"] = arg_deval["USDARS"].pct_change() * 100
    arg_deval["DevaluationLog"] = np.log(1 + arg_deval["Devaluation"] / 100)
    paper_deval = pd.read_csv(
        ROOT / "data/processed/exchange/converted_exchange_paper-devaluation_1853-01_1999-12.csv"
    ).set_index("Year")
    for year in range(1960, 2000):
        if year in paper_deval.index:
            arg_deval.loc[year, "DevaluationLog"] = float(
                paper_deval.loc[year, "DevaluationLog"]
            )
    # The December-to-December modern override governs 2000+ only; irrelevant at pool_end=1999.

    # Notebook cell 21: interest spread plus US real yield.
    interest_raw = pd.read_csv(
        ROOT / "data/processed/interest/converted_interest_wb-ids-arg_1958-01_2025-12.csv"
    )
    arg_interest = (
        interest_raw[interest_raw["CountryName"] == "Argentina"][["Year", "Interest"]]
        .assign(Year=lambda d: pd.to_numeric(d["Year"], errors="coerce").astype(int),
                Interest=lambda d: pd.to_numeric(d["Interest"], errors="coerce"))
        .set_index("Year")
    )
    us_real_yield = pd.read_csv(
        ROOT / "data/processed/interest/converted_interest_us-real-yield-10y_1998-01_2025-12.csv"
    ).set_index("Year")["USRealYield10Y"]

    # Notebook cell 33: unified series (1852 baselines; 1853-1963 from the workbook;
    # 1964+ modern). Interest seam restoration applies from 1998; the 2002-05 default
    # hold is included because it costs nothing and keeps the function faithful.
    baseline_1852_inf = pd.Series({1852: hist_cmpi.loc[1852, "Inflation"] / 100})
    unified_inflation = splice_series(
        pd.concat([baseline_1852_inf, excel_hist["InflationLog"]]),
        arg_inflation["InflationLog"],
    )
    baseline_1852_dev = pd.Series({1852: hist_cmpi.loc[1852, "Devaluation"] / 100})
    unified_devaluation = splice_series(
        pd.concat([baseline_1852_dev, excel_hist["DevaluationLog"]]),
        arg_deval["DevaluationLog"],
    )
    hist_interest = hist_cmpi["Interest"] / 100
    hist_interest.name = "Interest_frac"
    modern_interest = arg_interest["Interest"] / 100
    unified_interest = pd.concat(
        [hist_interest[hist_interest.index < arg_interest.index.min()], modern_interest]
    ).sort_index()
    for year, yield_pct in us_real_yield.items():
        if year >= 1998 and year in unified_interest.index:
            unified_interest.loc[year] = unified_interest.loc[year] + float(yield_pct) / 100
    unified_interest.loc[list(range(2002, 2006))] = float(unified_interest.loc[2001])
    baseline_1852_gro = pd.Series({1852: hist_cmpi.loc[1852, "Growth"] / 100})
    unified_growth = splice_series(
        pd.concat([baseline_1852_gro, excel_hist["Growth"]]),
        indicator("NY.GDP.PCAP.KD.ZG", "Growth")["Growth"] / 100,
    )

    # Notebook cell 47: FPI frame from corrected operands plus live (1+r)/(1+g).
    fpi_raw = pd.read_csv(
        ROOT / "data/processed/fiscal/converted_fiscal_fpi-fiscal_1853-01_2025-12.csv"
    ).set_index("Year")
    fpi_data = pd.DataFrame(index=fpi_raw.index)
    fpi_data["FPI_Debt_GDP"] = fpi_raw["Debt_GDP_corrected"]
    fpi_data["FPI_Debt_Exports"] = fpi_raw["Debt_Exports_corrected"]
    fpi_data["FPI_Result_Rev"] = fpi_raw["Result_Revenue_corrected"]
    fpi_data["FPI_Result_DS"] = fpi_raw["Result_DebtServ_corrected"]
    fpi_data["FPI_rg"] = (1 + unified_interest) / (1 + unified_growth)

    # Terms: majority-of-year partition plus the pre-specified continuity exceptions,
    # exactly as the headline pipeline builds them.
    src = _notebook_code()
    majority_terms = [
        tuple(t)
        for t in _literal(
            src, "majority_presidency_terms", subs={"DATA_END_YEAR": 2025}
        )
    ]
    continuity = _literal(src, "PROGRAM_CONTINUITY_EXCEPTIONS")
    terms = apply_program_continuity_exceptions(majority_terms, continuity, min_continuous_domains=4)
    assert len(terms) == 41

    cmpi_innovations = compute_innovations(
        terms,
        make_cmpi_year_value_fn(
            unified_inflation, unified_devaluation, unified_interest, unified_growth
        ),
    )
    fpi_innovations = compute_innovations(terms, make_fpi_year_value_fn(fpi_data))

    cmpi_scores = cmpi_scores_from_innovations(cmpi_innovations, terms, pool_end=1999)
    fpi_scores = fpi_scores_from_innovations(fpi_innovations, terms, pool_end=1999)
    return pd.DataFrame({"CMPI": cmpi_scores["CMPI"], "FPI": fpi_scores["FPI"]})


def _spearman_vs_paper(
    scores: pd.DataFrame, paper_ranks: pd.DataFrame, column: str
) -> float:
    common = paper_ranks.index.intersection(scores.index)
    assert len(common) == 33, f"Expected 33 comparable administrations, got {len(common)}"
    ours = scores.loc[common, column].rank(ascending=False, method="first")
    theirs = paper_ranks.loc[
        common, "PaperFPIRank" if column == "FPI" else "PaperCMPIRank"
    ]
    return ours.rank().corr(theirs.rank())


def test_restricted_pool_fpi_spearman_pinned(
    restricted_scores: pd.DataFrame, paper_ranks: pd.DataFrame
) -> None:
    rho = _spearman_vs_paper(restricted_scores, paper_ranks, "FPI")
    assert round(rho, 3) == 0.996, f"FPI replication rho drifted to {rho:.4f}"


def test_restricted_pool_cmpi_spearman_pinned(
    restricted_scores: pd.DataFrame, paper_ranks: pd.DataFrame
) -> None:
    rho = _spearman_vs_paper(restricted_scores, paper_ranks, "CMPI")
    assert round(rho, 3) == 0.953, f"CMPI replication rho drifted to {rho:.4f}"

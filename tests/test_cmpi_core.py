"""Basic tests for the extracted CMPI/FPI core scoring logic.

Run with: pytest -q tests/test_cmpi_core.py
These tests are intentionally lightweight and do not require the full notebook data.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make project imports (scripts.*, data.*) work when running tests directly or via uv run / make.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cmpi_core import (
    apply_program_continuity_exceptions,
    compute_innovations,
    cmpi_scores_from_innovations,
    fpi_scores_from_innovations,
    interpolate_fpi_ratio_gaps,
    make_cmpi_year_value_fn,
    make_fpi_year_value_fn,
    term_year_assignment,
    CMPI_VARIABLES,
    FPI_VARIABLES,
)


def _tiny_terms():
    # (name, first, last, photo, minister)
    return [
        ("A", 2000, 2001, "", ""),
        ("B", 2002, 2003, "", ""),
    ]


def _majority_boundary_terms():
    return [
        ("Duhalde", 2002, 2002, "", "Roberto Lavagna"),
        ("N.Kirchner", 2003, 2007, "", "Roberto Lavagna"),
    ]


def _continuity_exception():
    return {
        "year": 2003,
        "outgoing": "Duhalde",
        "incoming": "N.Kirchner",
        "incoming_would_receive_year": True,
        "economy_minister_retained_through_year_end": True,
        "first_complete_calendar_year": 2003,
        "domains": {
            "fiscal": True,
            "monetary": True,
            "exchange_rate": True,
            "banking": True,
            "sovereign_debt": False,
        },
    }


def test_program_continuity_exception_moves_only_qualifying_year():
    majority_terms = _majority_boundary_terms()
    modified_terms = apply_program_continuity_exceptions(
        majority_terms, [_continuity_exception()]
    )

    majority_assignment = term_year_assignment(majority_terms, 2002, 2007)
    modified_assignment = term_year_assignment(modified_terms, 2002, 2007)

    assert majority_assignment[2003] == "N.Kirchner"
    assert modified_assignment[2003] == "Duhalde"
    assert {
        year
        for year in majority_assignment
        if majority_assignment[year] != modified_assignment[year]
    } == {2003}
    assert majority_terms == _majority_boundary_terms()  # input is not mutated


def test_program_continuity_exception_requires_four_of_five_domains():
    exception = _continuity_exception()
    exception["domains"]["banking"] = False

    assert apply_program_continuity_exceptions(
        _majority_boundary_terms(), [exception]
    ) == _majority_boundary_terms()


def test_term_year_assignment_rejects_incomplete_or_overlapping_partitions():
    incomplete = [
        ("A", 2000, 2000, "", ""),
        ("B", 2002, 2003, "", ""),
    ]
    overlapping = [
        ("A", 2000, 2002, "", ""),
        ("B", 2002, 2003, "", ""),
    ]

    for terms in (incomplete, overlapping):
        try:
            term_year_assignment(terms, 2000, 2003)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid term partition should raise ValueError")


def test_moving_2003_changes_n_kirchner_inherited_baseline():
    idx = pd.Index(range(2001, 2008))
    levels = pd.Series([1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0], index=idx)
    year_fn = make_cmpi_year_value_fn(levels, levels, levels, -levels)
    majority_terms = _majority_boundary_terms()
    modified_terms = apply_program_continuity_exceptions(
        majority_terms, [_continuity_exception()]
    )

    majority = compute_innovations(majority_terms, year_fn)
    modified = compute_innovations(modified_terms, year_fn)

    assert majority.loc[2004, "Term"] == modified.loc[2004, "Term"] == "N.Kirchner"
    assert majority.loc[2004, "Inflation"] == levels[2004] - levels[2002]
    assert modified.loc[2004, "Inflation"] == levels[2004] - levels[2003]
    assert majority.loc[2004, "Inflation"] != modified.loc[2004, "Inflation"]


def test_cmpi_synthetic_improvement_gets_higher_score():
    # Build trivial unified series where term B has a big favorable innovation on all 4 dims
    idx = pd.Index(range(1999, 2004))
    # For term A (2000-2001): mediocre values
    # For term B (2002-2003): strong improvement vs A's last year (2001)
    inf = pd.Series([0.10, 0.12, 0.11, 0.05, 0.03], index=idx, name="inf")  # log space-ish
    dev = pd.Series([0.05, 0.06, 0.04, -0.10, -0.05], index=idx)
    int_ = pd.Series([0.08, 0.09, 0.07, 0.02, 0.01], index=idx)
    gr = pd.Series([0.01, 0.00, -0.01, 0.04, 0.03], index=idx)

    year_fn = make_cmpi_year_value_fn(inf, dev, int_, gr)
    innov = compute_innovations(_tiny_terms(), year_fn)
    ranking = cmpi_scores_from_innovations(innov, _tiny_terms())

    # B should rank above A (big favorable innovations in 2002-2003 vs 2001 baseline)
    assert ranking.index[0] == "B", f"Expected B first, got {ranking.index.tolist()}"
    assert ranking.loc["B", "CMPI"] > ranking.loc["A", "CMPI"]


def test_fpi_synthetic():
    # Minimal FPI data frame (levels, not logs)
    idx = pd.Index(range(1999, 2004))
    fpi_df = pd.DataFrame(
        {
            "FPI_Debt_GDP": [0.50, 0.52, 0.55, 0.40, 0.35],
            "FPI_Debt_Exports": [2.0, 2.1, 2.2, 1.5, 1.3],
            "FPI_Result_Rev": [-0.05, -0.03, -0.10, 0.05, 0.08],
            "FPI_Result_DS": [-0.20, -0.15, -0.40, 0.30, 0.50],
            "FPI_rg": [1.05, 1.06, 1.04, 0.98, 0.97],
        },
        index=idx,
    )

    year_fn = make_fpi_year_value_fn(fpi_df)
    innov = compute_innovations(_tiny_terms(), year_fn)
    ranking = fpi_scores_from_innovations(innov, _tiny_terms())

    assert "B" in ranking.index and "A" in ranking.index
    assert ranking.loc["B", "FPI"] > ranking.loc["A", "FPI"]


def test_fpi_ratio_gaps_are_arithmetically_interpolated_before_scoring():
    years = pd.Index(range(1860, 1865))
    hist = pd.DataFrame(
        {
            "Result_Revenue": [1.0, np.nan, np.nan, np.nan, 5.0],
            "Result_DebtServ": [5.0, np.nan, np.nan, np.nan, 1.0],
        },
        index=years,
    )
    filled = interpolate_fpi_ratio_gaps(hist)
    assert filled.loc[1861:1863, "Result_Revenue"].tolist() == pytest.approx(
        [2.0, 3.0, 4.0]
    )
    assert filled.loc[1861:1863, "Result_DebtServ"].tolist() == pytest.approx(
        [4.0, 3.0, 2.0]
    )

    innovations = pd.DataFrame(
        {
            "FPI_Debt_GDP": [5.0, 4.0, 3.0, 2.0, 1.0],
            "FPI_Debt_Exports": [5.0, 4.0, 3.0, 2.0, 1.0],
            "FPI_Result_Rev": filled["Result_Revenue"],
            "FPI_Result_DS": filled["Result_DebtServ"],
            "FPI_rg": [5.0, 4.0, 3.0, 2.0, 1.0],
            "Term": ["Mitre"] * 5,
        },
        index=years,
    )
    terms = [("Mitre", 1860, 1864, "", "")]

    ranking, pool = fpi_scores_from_innovations(
        innovations,
        terms,
        return_pool=True,
    )

    assert pool[[col + "Pos" for col in FPI_VARIABLES]].notna().all().all()
    assert len(pool) == 5
    # With a complete 5-year pool, the interpolated Result/Revenue innovations occupy
    # the interior percentile slots between the 1860 and 1864 endpoints.
    assert pool.loc[1860, "FPI_Result_RevPos"] == pytest.approx(0.0)
    assert pool.loc[1864, "FPI_Result_RevPos"] == pytest.approx(0.8)
    assert pool.loc[1861:1863, "FPI_Result_RevPos"].tolist() == pytest.approx(
        [0.2, 0.4, 0.6]
    )
    assert ranking.loc["Mitre", "FPI_Result_Rev"] == pytest.approx(0.4)


def test_fpi_rejects_any_innovation_gap():
    years = pd.Index(range(1860, 1865))
    innovations = pd.DataFrame(1.0, index=years, columns=FPI_VARIABLES)
    innovations["Term"] = "Mitre"
    innovations.loc[1862, "FPI_Result_Rev"] = np.nan

    with pytest.raises(ValueError, match="FPI_Result_Rev.*1862"):
        fpi_scores_from_innovations(
            innovations,
            [("Mitre", 1860, 1864, "", "")],
        )

    innovations.loc[1862, "FPI_Result_Rev"] = 1.0
    innovations.loc[1862, "FPI_Debt_GDP"] = np.nan
    with pytest.raises(ValueError, match="FPI_Debt_GDP.*1862"):
        fpi_scores_from_innovations(
            innovations,
            [("Mitre", 1860, 1864, "", "")],
        )


def test_excluded_pool_years_are_skipped_for_term_average():
    idx = pd.Index(range(1999, 2004))
    inf = pd.Series([0.10, 0.12, 0.11, 0.05, 0.03], index=idx)
    dev = pd.Series([0.05, 0.06, 0.04, -0.10, -0.05], index=idx)
    int_ = pd.Series([0.08, 0.09, 0.07, 0.02, 0.01], index=idx)
    gr = pd.Series([0.01, 0.00, -0.01, 0.04, 0.03], index=idx)

    year_fn = make_cmpi_year_value_fn(inf, dev, int_, gr)
    innov = compute_innovations(_tiny_terms(), year_fn)
    innov_no_crisis = innov[~innov.index.isin({2001})].copy()

    ranking = cmpi_scores_from_innovations(innov_no_crisis, _tiny_terms())

    assert "A" in ranking.index
    assert ranking.loc["A", "CMPI"] >= 0.0


def test_no_crash_on_empty_pool():
    # Edge: empty year range should not explode
    terms = [("X", 2100, 2101, "", "")]
    # dummy series
    s = pd.Series([0.0], index=[2099])
    year_fn = make_cmpi_year_value_fn(s, s, s, s)
    innov = compute_innovations(terms, year_fn)
    ranking = cmpi_scores_from_innovations(innov, terms, pool_start=9999, pool_end=9999)
    assert len(ranking) == 0 or np.allclose(ranking["CMPI"], 0.0)  # graceful

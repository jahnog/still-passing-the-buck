"""Basic tests for the extracted CMPI/FPI core scoring logic.

Run with: pytest -q tests/test_cmpi_core.py
These tests are intentionally lightweight and do not require the full notebook data.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Make project imports (scripts.*, data.*) work when running tests directly or via uv run / make.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cmpi_core import (
    compute_innovations,
    cmpi_scores_from_innovations,
    fpi_scores_from_innovations,
    make_cmpi_year_value_fn,
    make_fpi_year_value_fn,
    CMPI_VARIABLES,
    FPI_VARIABLES,
)


def _tiny_terms():
    # (name, first, last, photo, minister)
    return [
        ("A", 2000, 2001, "", ""),
        ("B", 2002, 2003, "", ""),
    ]


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

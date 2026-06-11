"""Tests for the distortion-adjustment data files and the FPI memo columns.

These run against the committed CSVs (no network): they pin the invariants that make the
section 6.0 C-E sensitivity machinery trustworthy — memo columns equal the baseline outside
their adjustment windows, every curated number carries a source, and the quality-flag file
covers every ranked year of every variable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.validate_cmpi_inputs import audit_quality_flags

TARGET_YEAR = 2025


@pytest.fixture(scope="module")
def fpi() -> pd.DataFrame:
    return pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")


def test_fpi_memo_columns_present(fpi: pd.DataFrame) -> None:
    for col in ["Debt_GDP_holdouts", "Result_DebtServ_accrual", "Result_Revenue_structural",
                "Debt_GDP_arrears", "DefaultFlag", "Debt_GDP_official", "Cepo_Factor",
                "BCRA_QuasiFiscal_GDP"]:
        assert col in fpi.columns, f"missing memo column {col}"


def test_holdout_addback_window(fpi: pd.DataFrame) -> None:
    inside = fpi.loc[2005:2015]
    assert (inside["Debt_GDP_holdouts"] > inside["Debt_GDP"]).all()
    outside = fpi.loc[~fpi.index.isin(range(2005, 2016))]
    assert np.allclose(outside["Debt_GDP_holdouts"], outside["Debt_GDP"], equal_nan=True)


def test_accrual_scaling_window(fpi: pd.DataFrame) -> None:
    inside = fpi.loc[2002:2005]
    # The accrual ratio keeps the cash ratio's sign but shrinks its magnitude.
    assert (inside["Result_DebtServ_accrual"].abs() < inside["Result_DebtServ"].abs()).all()
    assert (np.sign(inside["Result_DebtServ_accrual"]) == np.sign(inside["Result_DebtServ"])).all()
    outside = fpi.loc[~fpi.index.isin(range(2002, 2006))]
    assert np.allclose(outside["Result_DebtServ_accrual"], outside["Result_DebtServ"], equal_nan=True)


def test_structural_balance_removes_one_offs(fpi: pd.DataFrame) -> None:
    one_offs = pd.read_csv(paths.FISCAL_ONE_OFFS_CSV)
    subtracted = one_offs[one_offs["Type"].str.strip() == "one-off"]
    assert subtracted["Amount_pct_revenues"].notna().all()
    years = sorted(set(subtracted["Year"]))
    inside = fpi.loc[years]
    assert (inside["Result_Revenue_structural"] < inside["Result_Revenue"]).all()
    outside = fpi.loc[~fpi.index.isin(years)]
    assert np.allclose(outside["Result_Revenue_structural"], outside["Result_Revenue"], equal_nan=True)
    # The standard finding: reported 2010 and 2013 surpluses flip to structural deficits.
    assert fpi.loc[2010, "Result_Revenue"] > 0 > fpi.loc[2010, "Result_Revenue_structural"]
    assert fpi.loc[2013, "Result_Revenue"] > 0 > fpi.loc[2013, "Result_Revenue_structural"]
    # Milei's 2024 surplus narrows but survives.
    assert fpi.loc[2024, "Result_Revenue_structural"] > 0


def test_arrears_bopreal_paired_addback(fpi: pd.DataFrame) -> None:
    inside = fpi.loc[2022:2025]
    assert (inside["Debt_GDP_arrears"] > inside["Debt_GDP"]).all(), "both sides must be added"
    outside = fpi.loc[~fpi.index.isin(range(2022, 2026))]
    assert np.allclose(outside["Debt_GDP_arrears"], outside["Debt_GDP"], equal_nan=True)


def test_default_flags(fpi: pd.DataFrame) -> None:
    flags = fpi["DefaultFlag"].fillna("")
    assert flags.loc[2002] == "full"
    assert flags.loc[2014] == "selective"
    assert flags.loc[2020] == "restructured"
    assert flags.loc[2010] == ""


def test_default_adjustments_sources() -> None:
    adj = pd.read_csv(paths.DEFAULT_ADJUSTMENTS_CSV)
    assert adj["Source"].str.strip().astype(bool).all(), "every adjustment row needs a source"
    accrual_years = adj.dropna(subset=["AccruedUnpaidInterest_GDP"])
    assert set(accrual_years["Year"]) == {2002, 2003, 2004, 2005}


def test_one_offs_sources() -> None:
    one_offs = pd.read_csv(paths.FISCAL_ONE_OFFS_CSV)
    assert one_offs["Source"].str.strip().astype(bool).all()
    assert set(one_offs["Type"].str.strip()) <= {"one-off", "documented"}


def test_quality_flags_cover_every_ranked_year() -> None:
    problems, provisional = audit_quality_flags(paths.DATA_QUALITY_FLAGS_CSV, TARGET_YEAR)
    assert problems == [], problems
    # 2025 must be marked provisional somewhere until the World Bank publishes it.
    assert any(p["year_end"] == 2025 for p in provisional)


def test_alt_cpi_band_consistency() -> None:
    alt = pd.read_csv(paths.ALT_CPI_CSV).set_index("Year")
    assert list(alt.index) == list(range(2007, 2016))
    assert (alt["AltMin"] <= alt["AltAvg"] + 1e-9).all()
    assert (alt["AltAvg"] <= alt["AltMax"] + 1e-9).all()
    # The whole point of the correction: official < credible alternatives, every year.
    assert (alt["Official"] < alt["AltMin"]).all()


def test_dec_dec_modern_series() -> None:
    dec = pd.read_csv(paths.DEC_DEC_MODERN_CSV).set_index("Year")
    assert list(dec.index) == list(range(1999, 2026))
    assert (dec.loc[1999:2001, "DecRate"] == 1.0).all(), "Convertibility years must be 1:1"
    assert dec.loc[2002, "DevaluationLog"] > 1.0, "the 2002 collapse must land in 2002"
    assert dec.loc[2003, "DevaluationLog"] < 0, "2003 was an appreciation year"
    cepo_years = [2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    assert dec.loc[cepo_years, "RateSource"].str.contains("december-avg").all()


def test_bcra_quasi_fiscal_columns() -> None:
    qf = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year")
    for col in ["BCRA_QuasiFiscal_GDP", "BCRA_QuasiFiscal_Interest_GDP",
                "TradeArrears_BOPREAL_USD_M"]:
        assert col in qf.columns
    assert qf.loc[2025, "BCRA_QuasiFiscal_GDP"] == 0.0
    assert qf.loc[2023, "BCRA_QuasiFiscal_Interest_GDP"] > qf.loc[2020, "BCRA_QuasiFiscal_Interest_GDP"]
    assert qf.loc[2023, "TradeArrears_BOPREAL_USD_M"] > 0
    assert qf.loc[2021, "TradeArrears_BOPREAL_USD_M"] == 0.0

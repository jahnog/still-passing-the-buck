"""Tests for the distortion-adjustment data files and the FPI memo columns.

These run against the committed CSVs (no network): they pin the invariants that make the
section 6.0 C-E sensitivity machinery trustworthy — memo columns equal the baseline outside
their adjustment windows, every curated number carries a source, and the quality-flag file
covers every ranked year of every variable.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.validate_cmpi_inputs import (
    audit_complete_2025_inputs,
    audit_fpi_fiscal,
    audit_quality_flags,
)

TARGET_YEAR = 2025


@pytest.fixture(scope="module")
def fpi() -> pd.DataFrame:
    return pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")


def test_historical_fiscal_gaps_are_arithmetically_interpolated(
    fpi: pd.DataFrame,
) -> None:
    source = pd.read_excel(
        paths.DATA_A_1999_XLSX,
        sheet_name="Hoja1",
        header=6,
        usecols="B,I,J",
        names=["Year", "Result_Revenue", "Result_DebtServ"],
    ).dropna(subset=["Year"])
    source["Year"] = source["Year"].astype(int)
    source = source.set_index("Year")
    gap_years = [1861, 1862, 1863]
    assert source.loc[gap_years, ["Result_Revenue", "Result_DebtServ"]].isna().all().all()

    derived_gap_columns = [
        "Result_Revenue",
        "Result_DebtServ",
        "Result_Revenue_paper_extension",
        "Result_DebtServ_paper_extension",
        "Result_Revenue_corrected",
        "Result_DebtServ_corrected",
        "Result_DebtServ_capitalized_interest",
        "Result_Revenue_structural",
        "Result_DebtServ_structural",
    ]
    assert fpi.loc[gap_years, derived_gap_columns].notna().all().all()
    assert fpi.loc[[1860, 1864], derived_gap_columns].notna().all().all()
    start_year, end_year = 1860, 1864
    span = end_year - start_year
    for col in ["Result_Revenue", "Result_DebtServ"]:
        start = fpi.loc[start_year, col]
        end = fpi.loc[end_year, col]
        for year in gap_years:
            expected = start + ((year - start_year) / span) * (end - start)
            assert fpi.loc[year, col] == pytest.approx(expected)


def test_fpi_validator_requires_complete_interpolated_historical_gaps(
    fpi: pd.DataFrame,
    tmp_path: Path,
) -> None:
    assert audit_fpi_fiscal(paths.FPI_FISCAL_CSV, TARGET_YEAR) == []

    blanked = fpi.copy()
    blanked.loc[1862, "Result_Revenue"] = np.nan
    blanked_path = tmp_path / "blanked.csv"
    blanked.reset_index().to_csv(blanked_path, index=False)
    assert any(
        "FPI components missing for 1862" in problem["name"]
        for problem in audit_fpi_fiscal(blanked_path, TARGET_YEAR)
    )

    mismatched = fpi.copy()
    mismatched.loc[1862, "Result_Revenue"] = 0.0
    mismatched_path = tmp_path / "mismatched.csv"
    mismatched.reset_index().to_csv(mismatched_path, index=False)
    assert any(
        "interpolation mismatch" in problem["name"]
        for problem in audit_fpi_fiscal(mismatched_path, TARGET_YEAR)
    )

    extra_gap = fpi.copy()
    extra_gap.loc[1862, "Debt_GDP"] = np.nan
    extra_gap_path = tmp_path / "extra-gap.csv"
    extra_gap.reset_index().to_csv(extra_gap_path, index=False)
    assert any(
        "Debt_GDP" in problem["reason"]
        for problem in audit_fpi_fiscal(extra_gap_path, TARGET_YEAR)
    )


def test_fpi_memo_columns_present(fpi: pd.DataFrame) -> None:
    for col in ["Debt_GDP_holdouts", "Result_DebtServ_capitalized_interest",
                "Result_Revenue_structural", "Result_DebtServ_structural",
                "Debt_GDP_arrears",
                "DefaultFlag", "Debt_GDP_official", "Cepo_Factor",
                "BCRA_QuasiFiscal_GDP", "Debt_GDP_paper_extension",
                "Debt_Exports_paper_extension", "Result_Revenue_paper_extension",
                "Result_DebtServ_paper_extension", "Debt_GDP_corrected",
                "Debt_Exports_corrected", "Result_Revenue_corrected", "Result_DebtServ_corrected"]:
        assert col in fpi.columns, f"missing memo column {col}"


def test_holdout_addback_window(fpi: pd.DataFrame) -> None:
    inside = fpi.loc[2005:2015]
    assert (inside["Debt_GDP_holdouts"] > inside["Debt_GDP"]).all()
    outside = fpi.loc[~fpi.index.isin(range(2005, 2016))]
    assert np.allclose(outside["Debt_GDP_holdouts"], outside["Debt_GDP"], equal_nan=True)


def test_capitalized_interest_scaling_window(fpi: pd.DataFrame) -> None:
    years = [2024, 2025]
    inside = fpi.loc[years]
    memo = inside["Result_DebtServ_capitalized_interest"]
    # The official OPC adjustment keeps the cash ratio's sign but shrinks its magnitude.
    assert (memo.abs() < inside["Result_DebtServ"].abs()).all()
    assert (np.sign(memo) == np.sign(inside["Result_DebtServ"])).all()
    outside = fpi.loc[~fpi.index.isin(years)]
    assert np.allclose(
        outside["Result_DebtServ_capitalized_interest"],
        outside["Result_DebtServ"],
        equal_nan=True,
    )


def test_structural_balance_removes_one_offs(fpi: pd.DataFrame) -> None:
    one_offs = pd.read_csv(paths.OFFICIAL_ONE_OFFS_CSV)
    subtracted = one_offs[one_offs["Type"].str.strip() == "one-off"]
    assert subtracted["Amount_pct_revenues"].notna().all()
    years = sorted(set(subtracted["Year"]))
    inside = fpi.loc[years]
    assert (inside["Result_Revenue_structural"] < inside["Result_Revenue"]).all()
    outside = fpi.loc[~fpi.index.isin(years)]
    assert np.allclose(outside["Result_Revenue_structural"], outside["Result_Revenue"], equal_nan=True)
    # Under official SPN base-caja sourcing (from 2000 onward):
    # 2010 is a small surplus (+0.072) that flips to structural deficit after removing one-offs.
    assert fpi.loc[2010, "Result_Revenue"] > 0 > fpi.loc[2010, "Result_Revenue_structural"]
    # 2013 is already a deficit (-0.031) under SPN cash-basis; one-offs deepen it further.
    assert fpi.loc[2013, "Result_Revenue_structural"] < fpi.loc[2013, "Result_Revenue"] < 0
    # Milei's 2024 surplus narrows but survives.
    assert fpi.loc[2024, "Result_Revenue_structural"] > 0
    # The one-off removal must affect both FPI primary-balance components because both have
    # the primary result in the numerator.
    assert fpi.loc[2010, "Result_DebtServ_structural"] < 0 < fpi.loc[2010, "Result_DebtServ"]


def test_arrears_bopreal_paired_addback(fpi: pd.DataFrame) -> None:
    inside = fpi.loc[2022:2025]
    assert (inside["Debt_GDP_arrears"] > inside["Debt_GDP"]).all(), "both sides must be added"
    assert (inside["Debt_Exports_arrears"] > inside["Debt_Exports"]).all()
    # No other debt add-back is active in 2022-25, so these equalities prove that both headline
    # debt components use the paired importer-debt/BOPREAL correction rather than the official stock.
    assert np.allclose(
        inside["Debt_GDP_corrected"], inside["Debt_GDP_arrears"], equal_nan=True
    )
    assert np.allclose(
        inside["Debt_Exports_corrected"], inside["Debt_Exports_arrears"], equal_nan=True
    )
    outside = fpi.loc[~fpi.index.isin(range(2022, 2026))]
    assert np.allclose(outside["Debt_GDP_arrears"], outside["Debt_GDP"], equal_nan=True)
    assert np.allclose(
        outside["Debt_Exports_arrears"], outside["Debt_Exports"], equal_nan=True
    )


def test_default_flags(fpi: pd.DataFrame) -> None:
    flags = fpi["DefaultFlag"].fillna("")
    assert flags.loc[2002] == "full"
    assert flags.loc[2014] == "selective"
    assert flags.loc[2020] == "restructured"
    assert flags.loc[2024] == "capitalizing"
    assert flags.loc[2010] == ""


def test_default_adjustments_sources() -> None:
    adj = pd.read_csv(paths.DEFAULT_ADJUSTMENTS_CSV)
    assert adj["Source"].str.strip().astype(bool).all(), "every adjustment row needs a source"
    assert {"InterestPaid_GDP", "AccruedUnpaidInterest_GDP"}.isdisjoint(adj.columns)


def test_whole_stock_cepo_headline(fpi: pd.DataFrame) -> None:
    # Headline Debt/GDP is official × κ + unscaled BCRA. On non-cepo years κ = 1.
    expected = fpi["Debt_GDP_official"] * fpi["Cepo_Factor"] + fpi["BCRA_QuasiFiscal_GDP"]
    assert np.allclose(fpi["Debt_GDP"], expected, equal_nan=True)
    cepo_years = fpi.index[fpi["Cepo_Factor"] > 1.0]
    assert len(cepo_years) > 0
    inside = fpi.loc[cepo_years]
    assert (inside["Debt_GDP"] > inside["Debt_GDP_official"] + inside["BCRA_QuasiFiscal_GDP"] - 1e-12).all()
    outside = fpi.loc[fpi["Cepo_Factor"] <= 1.0]
    assert np.allclose(
        outside["Debt_GDP"],
        outside["Debt_GDP_official"] + outside["BCRA_QuasiFiscal_GDP"],
        equal_nan=True,
    )


def test_corrected_baseline_cumulatively_applies_debt_addbacks(fpi: pd.DataFrame) -> None:
    extras = pd.DataFrame({
        col: (fpi[col] - fpi["Debt_GDP"]).clip(lower=0).fillna(0.0)
        for col in ["Debt_GDP_holdouts", "Debt_GDP_arrears"]
    })
    expected = fpi["Debt_GDP"] + extras.sum(axis=1)
    assert np.allclose(fpi["Debt_GDP_corrected"], expected, equal_nan=True)
    assert fpi.loc[2023, "Debt_GDP_corrected"] == pytest.approx(
        fpi.loc[2023, "Debt_GDP_arrears"]
    )
    assert (fpi["Debt_Exports_corrected"] >= fpi["Debt_Exports"]).all()


def test_corrected_baseline_uses_structural_and_capitalized_interest_results(
    fpi: pd.DataFrame,
) -> None:
    assert np.allclose(fpi["Result_Revenue_corrected"], fpi["Result_Revenue_structural"], equal_nan=True)
    capitalized_scale = pd.Series(1.0, index=fpi.index)
    mask = fpi["Result_DebtServ"].abs() > 1e-12
    capitalized_scale.loc[mask] = (
        fpi.loc[mask, "Result_DebtServ_capitalized_interest"]
        / fpi.loc[mask, "Result_DebtServ"]
    )
    expected = fpi["Result_DebtServ_structural"] * capitalized_scale
    assert np.allclose(fpi["Result_DebtServ_corrected"], expected, equal_nan=True)
    assert (
        fpi.loc[2024, "Result_DebtServ_corrected"]
        < fpi.loc[2024, "Result_DebtServ_capitalized_interest"]
    )


def test_paper_extension_columns_preserve_reported_series(fpi: pd.DataFrame) -> None:
    assert np.allclose(fpi["Debt_GDP_paper_extension"], fpi["Debt_GDP_official"], equal_nan=True)
    assert np.allclose(fpi["Debt_Exports_paper_extension"], fpi["Debt_Exports_official"], equal_nan=True)
    assert np.allclose(fpi["Result_Revenue_paper_extension"], fpi["Result_Revenue"], equal_nan=True)
    assert np.allclose(fpi["Result_DebtServ_paper_extension"], fpi["Result_DebtServ"], equal_nan=True)


def test_notebook_headline_fpi_uses_corrected_columns() -> None:
    nb = json.loads((ROOT / "Historical_CMPI_Extension.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    assert 'fpi_data["FPI_Debt_GDP"]     = fpi_raw["Debt_GDP_corrected"]' in source
    assert 'fpi_data["FPI_Debt_Exports"] = fpi_raw["Debt_Exports_corrected"]' in source
    assert 'fpi_data["FPI_Result_Rev"]   = fpi_raw["Result_Revenue_corrected"]' in source
    assert 'fpi_data["FPI_Result_DS"]    = fpi_raw["Result_DebtServ_corrected"]' in source


def test_one_offs_sources() -> None:
    one_offs = pd.read_csv(paths.OFFICIAL_ONE_OFFS_CSV)
    assert one_offs["Source"].str.strip().astype(bool).all()
    assert set(one_offs["Type"].str.strip()) == {"one-off"}
    assert one_offs["ProvenanceID"].str.strip().astype(bool).all()
    expected_revenue_share = (
        one_offs["Amount_ARS_M"] / one_offs["CurrentRevenue_ARS_M"] * 100
    )
    expected_gdp_share = one_offs["Amount_ARS_M"] / one_offs["NominalGDP_ARS_M"] * 100
    assert np.allclose(one_offs["Amount_pct_revenues"], expected_revenue_share)
    assert np.allclose(one_offs["Amount_pct_GDP"], expected_gdp_share)


def test_official_capitalized_interest_formula() -> None:
    cap = pd.read_csv(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV)
    assert {"CashInterest_GDP", "CapitalizedInterest_GDP"} <= set(cap.columns)
    assert {"InterestPaid_GDP", "AccruedUnpaidInterest_GDP"}.isdisjoint(cap.columns)
    assert np.allclose(
        cap["CashInterest_GDP"],
        cap["CashInterest_ARS_M"] / cap["NominalGDP_ARS_M"],
    )
    assert np.allclose(
        cap["CapitalizedInterest_GDP"],
        cap["CapitalizedInterest_ARS_M"] / cap["NominalGDP_ARS_M"],
    )


def test_removed_model_files_absent() -> None:
    removed = (
        "data/provided/fiscal-one-offs.csv",
        "data/provided/alt-cpi-2007-2015.csv",
        "data/provided/contingent-liabilities.csv",
        "data/provided/default-window-interest.csv",
    )
    assert not [relative for relative in removed if (ROOT / relative).exists()]


def test_strict_provenance_validation_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_provenance.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_quality_flags_cover_every_ranked_year() -> None:
    problems, provisional = audit_quality_flags(paths.DATA_QUALITY_FLAGS_CSV, TARGET_YEAR)
    assert problems == [], problems
    assert provisional == [], "no grade-D placeholder remains in the 2025 headline"


def test_complete_2025_scoring_inputs() -> None:
    report = audit_complete_2025_inputs()
    assert report["status"] == "complete", report["missing"]
    assert report["missing"] == []
    values = report["values"]
    assert len(values["world_bank"]) == 6
    assert len(values["fpi"]) == 13
    assert values["capitalized_interest"]["CapitalizedInterest_ARS_M"] > 0
    yields = pd.read_csv(paths.US_REAL_YIELD_CSV).set_index("Year")
    assert yields.loc[2025, "USRealYield10Y"] == pytest.approx(1.96)
    assert "complete annual" in yields.loc[2025, "Source"]
    denominator = pd.read_csv(
        paths.PROCESSED
        / "fiscal"
        / "converted_fiscal_denominator-neutral_1960-01_2025-12.csv"
    ).set_index("Year")
    assert (
        denominator.loc[2025, "Note"]
        == "Complete annual observations are used for 2025, but recent "
        "national-account values remain subject to source revisions."
    )


def test_alt_cpi_band_consistency() -> None:
    alt = pd.read_csv(paths.ALT_CPI_CSV).set_index("Year")
    assert list(alt.index) == list(range(2007, 2016))
    assert np.allclose(alt["AltAvg"], alt["Santa_Fe"])
    assert (alt["AltMin"] <= alt["AltAvg"] + 1e-9).all()
    assert (alt["AltAvg"] <= alt["AltMax"] + 1e-9).all()
    assert alt["ProvenanceID"].str.strip().astype(bool).all()


def test_dec_dec_modern_series() -> None:
    dec = pd.read_csv(paths.DEC_DEC_MODERN_CSV).set_index("Year")
    assert list(dec.index) == list(range(1999, 2026))
    assert (dec.loc[1999:2001, "DecRate"] == 1.0).all(), "Convertibility years must be 1:1"
    assert dec.loc[2002, "DevaluationLog"] > 1.0, "the 2002 collapse must land in 2002"
    assert dec.loc[2003, "DevaluationLog"] < 0, "2003 was an appreciation year"
    cepo_years = [2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    assert dec.loc[cepo_years, "RateSource"].str.contains("december-avg").all()


def test_known_fiscal_dict_removed_from_source() -> None:
    src = (ROOT / "scripts" / "generate_fiscal_fpi-fiscal.py").read_text(encoding="utf-8")
    assert "KNOWN_FISCAL = {" not in src, "KNOWN_FISCAL dict must be removed (now file-sourced)"
    for token in ("load_provisional_macro", "PROVISIONAL_MACRO_CSV", "provisional-macro-2025"):
        assert token not in src, f"superseded 2025 fallback {token!r} must not feed the FPI"


def test_quasi_fiscal_anchor_lists_removed_from_source() -> None:
    src = (ROOT / "scripts" / "generate_fiscal_bcra-quasi-fiscal.py").read_text(encoding="utf-8")
    for token in ("ANCHORS = [", "INTEREST_ANCHORS = [", "TRADE_ARREARS_USD_M = ["):
        assert token not in src, f"{token!r} must be moved to a provided CSV"


def test_2019_2025_actuals_sourced_from_dataset_379() -> None:
    from scripts.hacienda_spn_base_caja import load_spn_base_caja_actuals

    fpi = pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")
    actuals = load_spn_base_caja_actuals(range(2019, 2026), round_digits=4)
    for year, actual in actuals.items():
        assert actual.result_revenue == pytest.approx(
            fpi.loc[year, "Result_Revenue"], abs=1e-9
        )
        assert actual.result_debt_serv == pytest.approx(
            fpi.loc[year, "Result_DebtServ"], abs=1e-9
        )
        assert actual.primary_result == pytest.approx(fpi.loc[year, "PrimaryResult"])
        assert actual.interest_measure == pytest.approx(fpi.loc[year, "InterestMeasure"])


def test_quasi_fiscal_anchor_csvs_have_provenance() -> None:
    anchors = pd.read_csv(paths.BCRA_QF_ANCHORS_CSV)
    for field in ("Source", "Note"):
        assert anchors[field].astype(str).str.strip().astype(bool).all()

    operands = pd.read_csv(paths.BCRA_IMPORTER_DEBT_BOPREAL_CSV)
    assert operands["Year"].tolist() == [2022, 2023, 2024, 2025]
    for field in ("ProvenanceID", "SourceID", "SourceLocator", "ExtractionFormula", "Uncertainty"):
        assert operands[field].astype(str).str.strip().astype(bool).all(), (
            f"{paths.BCRA_IMPORTER_DEBT_BOPREAL_CSV.name} needs {field}"
        )


def test_superseded_2025_bridges_are_absent() -> None:
    removed = (
        ROOT / "data" / "provided" / "provisional-macro-2025.csv",
        ROOT / "data" / "provided" / "indec-gdp-growth-fallback.csv",
    )
    assert not [str(path.relative_to(ROOT)) for path in removed if path.exists()]
    source_paths = (
        ROOT / "scripts" / "indicator_build.py",
        ROOT / "scripts" / "generate_fiscal_fpi-fiscal.py",
        ROOT / "scripts" / "generate_fiscal_denominator-neutral.py",
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)
    for token in ("PROVISIONAL_MACRO_CSV", "INDEC_GDP_GROWTH_FALLBACK_CSV"):
        assert token not in source


def test_audit_post2000_hardcoding_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_post2000_hardcoding.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_bcra_quasi_fiscal_columns() -> None:
    qf = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year")
    for col in ["BCRA_QuasiFiscal_GDP", "BCRA_QuasiFiscal_Interest_GDP",
                "TradeArrears_BOPREAL_USD_M"]:
        assert col in qf.columns
    # LeFi was eliminated in July 2025, so the remunerated stock must be negligible rather than
    # exactly zero: once the World Bank published 2025 GDP the ratio became measurable from the
    # BCRA API and shows a small residual (~0.03% of GDP, the same order as 2024), superseding
    # the earlier hardcoded 0.0 anchor.
    assert 0.0 <= qf.loc[2025, "BCRA_QuasiFiscal_GDP"] < 0.001
    assert qf.loc[2023, "BCRA_QuasiFiscal_Interest_GDP"] > qf.loc[2020, "BCRA_QuasiFiscal_Interest_GDP"]
    assert qf.loc[2023, "TradeArrears_BOPREAL_USD_M"] > 0
    assert qf.loc[2021, "TradeArrears_BOPREAL_USD_M"] == 0.0

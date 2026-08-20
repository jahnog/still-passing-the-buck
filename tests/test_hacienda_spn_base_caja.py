"""Tests for the official SPN base-caja parser.

These pin the post-2000 fiscal sourcing now that the values come from files instead of Python
constants: dataset 379 must reproduce the committed 2000-2025 fiscal operands and ratios, its
sidecar must pin the official download, and the IMIG 2018 cross-validation must pass.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.hacienda_spn_base_caja import (
    CSV_2015_2025,
    IMIG_2018_XLSX,
    imig_totals,
    load_spn_base_caja_actuals,
    load_spn_base_caja_ratios,
    validate_against_imig,
)

def test_complete_2000_2025_coverage() -> None:
    actuals = load_spn_base_caja_actuals(range(2000, 2026))
    assert set(actuals) == set(range(2000, 2026))
    for year, actual in actuals.items():
        assert actual.current_revenue != 0, f"{year} current revenue"
        assert actual.interest_measure != 0, f"{year} net interest"
        assert actual.interest_measure == pytest.approx(
            actual.primary_result - actual.financial_result,
            abs=1e-6,
        )
        assert actual.result_revenue == round(
            actual.primary_result / actual.current_revenue, 4
        )
        assert actual.result_debt_serv == round(
            actual.primary_result / actual.interest_measure, 4
        )


def test_imig_2018_validation_passes() -> None:
    ratios = load_spn_base_caja_ratios(range(2000, 2026))
    err = validate_against_imig(ratios, imig_totals(IMIG_2018_XLSX), year=2018)
    assert err <= 0.001


def test_missing_year_raises() -> None:
    with pytest.raises(KeyError):
        load_spn_base_caja_ratios([1850])


def test_derived_2000_2025_match_committed_fiscal_csv() -> None:
    fpi = pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")
    actuals = load_spn_base_caja_actuals(range(2000, 2026), round_digits=4)
    for year, actual in actuals.items():
        assert fpi.loc[year, "CurrentRevenue"] == pytest.approx(actual.current_revenue)
        assert fpi.loc[year, "PrimaryResult"] == pytest.approx(actual.primary_result)
        assert fpi.loc[year, "FinancialResult"] == pytest.approx(actual.financial_result)
        assert fpi.loc[year, "InterestMeasure"] == pytest.approx(actual.interest_measure)
        assert fpi.loc[year, "Result_Revenue"] == pytest.approx(actual.result_revenue)
        assert fpi.loc[year, "Result_DebtServ"] == pytest.approx(actual.result_debt_serv)


def test_official_2024_2025_annual_totals() -> None:
    actuals = load_spn_base_caja_actuals([2024, 2025], round_digits=None)
    assert actuals[2024].current_revenue == pytest.approx(98_013_420.5)
    assert actuals[2024].primary_result == pytest.approx(10_405_809.6)
    assert actuals[2024].financial_result == pytest.approx(1_764_785.6)
    assert actuals[2024].interest_measure == pytest.approx(8_641_024.0)
    assert actuals[2025].current_revenue == pytest.approx(135_083_882.4)
    assert actuals[2025].primary_result == pytest.approx(11_769_218.7)
    assert actuals[2025].financial_result == pytest.approx(1_453_819.1)
    assert actuals[2025].interest_measure == pytest.approx(10_315_399.6)


def test_distribution_379_3_sidecar_pins_official_download() -> None:
    sidecar = json.loads(CSV_2015_2025.with_suffix(CSV_2015_2025.suffix + ".meta.json").read_text())
    assert sidecar["sources"] == [
        "https://infra.datos.gob.ar/catalog/sspm/dataset/379/distribution/379.3/"
        "download/sector-publico-nacional-valores-anuales-17.csv"
    ]
    assert sidecar["output"]["bytes"] == CSV_2015_2025.stat().st_size
    assert sidecar["output"]["sha256"] == hashlib.sha256(CSV_2015_2025.read_bytes()).hexdigest()


def _markdown_table_row(path: Path, administration: str) -> list[str]:
    prefix = f"| {administration} |"
    line = next(line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix))
    return [value.strip() for value in line.strip("|").split("|")]


def test_official_fiscal_corrections_propagate_without_changing_cmpi_podium() -> None:
    generated = ROOT / "paper" / "generated"
    cmpi_milei = _markdown_table_row(generated / "tbl_cmpi.md", "Milei")
    fpi_milei = _markdown_table_row(generated / "tbl_fpi.md", "Milei")
    fpi_fernandez = _markdown_table_row(generated / "tbl_fpi.md", "Fernandez")
    fpi_ck2 = _markdown_table_row(generated / "tbl_fpi.md", "C.Kirchner II")
    overall_milei = _markdown_table_row(generated / "tbl_overall.md", "Milei")

    # Fiscal corrections leave Milei's independent CMPI result fixed.
    assert cmpi_milei[1] == "2"
    assert cmpi_milei[-1] == "0.756"
    # Strict official-operand corrections propagate through FPI and Overall.
    assert (fpi_milei[1], fpi_milei[-1]) == ("2", "0.829")
    assert fpi_ck2[1] == "40"
    assert fpi_fernandez[1] == "39"
    assert (overall_milei[1], overall_milei[-1]) == ("3", "0.792")

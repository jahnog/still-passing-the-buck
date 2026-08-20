"""Offline parser and fiscal-integration tests for the official BCRA paired operands."""

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
from scripts.bcra_importer_debt_bopreal import (
    BASELINE_PERIOD,
    BOPREAL_SOURCE,
    IMPORTER_DEBT_SOURCE,
    build_output,
    importer_debt_increases,
    parse_bopreal_residuals,
    parse_importer_debt_stocks,
)


@pytest.fixture(scope="module")
def importer_raw() -> bytes:
    return IMPORTER_DEBT_SOURCE.artifact.read_bytes()


@pytest.fixture(scope="module")
def bopreal_raw() -> bytes:
    return BOPREAL_SOURCE.artifact.read_bytes()


@pytest.fixture(scope="module")
def generated(importer_raw: bytes, bopreal_raw: bytes) -> pd.DataFrame:
    return build_output(importer_raw, bopreal_raw).set_index("Year")


def test_workbook_aggregation_cross_checks_both_tables(importer_raw: bytes) -> None:
    stocks = parse_importer_debt_stocks(importer_raw)
    assert set(stocks) == {202112, 202212, 202312}
    assert stocks[BASELINE_PERIOD] == pytest.approx(28_082.750426)
    assert stocks[202212] == pytest.approx(38_058.571359)
    assert stocks[202312] == pytest.approx(56_302.101299)


def test_importer_debt_increases_use_common_2021_baseline(importer_raw: bytes) -> None:
    stocks = parse_importer_debt_stocks(importer_raw)
    increases = importer_debt_increases(importer_raw)
    assert increases[2022] == pytest.approx(stocks[202212] - stocks[202112])
    assert increases[2023] == pytest.approx(stocks[202312] - stocks[202112])
    assert increases == pytest.approx({2022: 9_975.820933, 2023: 28_219.350873})


def test_pdf_residuals_exclude_series_4(bopreal_raw: bytes) -> None:
    totals, components = parse_bopreal_residuals(bopreal_raw)
    assert components[2025][4] == pytest.approx(845.178)
    assert totals[2024] == pytest.approx(
        components[2024][1] + components[2024][2] + components[2024][3]
    )
    assert totals[2025] == pytest.approx(components[2025][1] + components[2025][3])
    assert totals[2025] != pytest.approx(sum(components[2025].values()))
    assert totals == pytest.approx({2024: 9_147.038, 2025: 6_817.813})


def test_generated_source_has_exact_four_year_coverage(generated: pd.DataFrame) -> None:
    assert generated.index.tolist() == [2022, 2023, 2024, 2025]
    assert generated["Measure"].tolist() == [
        "ImporterDebtIncrease",
        "ImporterDebtIncrease",
        "BOPREALResidual",
        "BOPREALResidual",
    ]
    assert generated["ProvenanceID"].is_unique
    assert generated["SourceLocator"].str.strip().all()
    assert generated["ExtractionFormula"].str.strip().all()


def test_quasi_fiscal_integration_and_pre_2022_zero(generated: pd.DataFrame) -> None:
    quasi_fiscal = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year")
    values = quasi_fiscal["TradeArrears_BOPREAL_USD_M"]
    assert np.allclose(values.loc[2001:2021], 0.0)
    assert values.loc[2022:2025].to_numpy() == pytest.approx(
        generated["Value_USD_M"].to_numpy()
    )
    assert (
        quasi_fiscal.loc[2022:2025, "Arrears_Flag"].astype(str) == "measured-official"
    ).all()

    fiscal = pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")
    pre_window = fiscal.loc[:2021]
    assert np.allclose(
        pre_window["Debt_GDP_arrears"],
        pre_window["Debt_GDP"],
        equal_nan=True,
    )
    assert np.allclose(
        pre_window["Debt_Exports_arrears"],
        pre_window["Debt_Exports"],
        equal_nan=True,
    )

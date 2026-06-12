"""Tests for the BCRA-API-derived series (quasi-fiscal stocks and the CPI-WPI blend).

No network: the aggregation helpers are exercised on fixture data, and the committed
processed CSVs are checked for the invariants the notebook variants rely on.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load(script_name: str):
    spec = importlib.util.spec_from_file_location(
        script_name.replace("-", "_").removesuffix(".py"), ROOT / "scripts" / script_name
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


quasi = _load("generate_fiscal_bcra-quasi-fiscal.py")
blend = _load("generate_inflation_bcra-monthly.py")


def test_december_year_end_picks_last_december_observation():
    observations = [
        {"fecha": "2020-12-30", "valor": 100.0},
        {"fecha": "2020-12-15", "valor": 90.0},
        {"fecha": "2020-11-30", "valor": 999.0},
        {"fecha": "2021-12-31", "valor": 50.0},
        {"fecha": "2022-06-30", "valor": 1.0},  # no December 2022 -> year absent
    ]
    result = quasi.december_year_end(observations)
    assert result == {2020: 100.0, 2021: 50.0}


def test_cpi_compounding_requires_full_year():
    # 12 months of 1% compound to (1.01^12 - 1); a partial year must be dropped.
    monthly = [{"fecha": f"2000-{m:02d}-28", "valor": 1.0} for m in range(1, 13)]
    monthly += [{"fecha": "2001-01-31", "valor": 5.0}]  # 2001 partial
    import json as _json

    class _FakeRaw:
        def read_text(self):
            return _json.dumps({"results": monthly})

    blend_module = blend
    original = blend_module._latest_data_file
    blend_module._latest_data_file = lambda *_: _FakeRaw()
    try:
        annual = blend_module.cpi_annual_log()
    finally:
        blend_module._latest_data_file = original
    assert set(annual) == {2000}
    assert math.isclose(annual[2000], 12 * math.log(1.01), rel_tol=1e-9)


def test_quasi_fiscal_csv_measured_years_and_cross_check():
    df = pd.read_csv(ROOT / "data/processed/fiscal/converted_fiscal_bcra-quasi-fiscal_2001-01_2025-12.csv")
    measured = df[df["Anchor"] == "measured-api"]
    # The API covers 2002-2024 (2025 lacks WDI nominal GDP and stays anchored).
    assert measured["Year"].min() <= 2003 and measured["Year"].max() >= 2023
    # Calibration years must stay close to the documented anchors (the 2018/19/23 deviations
    # are known and documented in data/REVISIONS.md).
    by_year = df.set_index("Year")["BCRA_QuasiFiscal_GDP"]
    assert abs(by_year[2017] - 0.105) < 0.02   # bola de Lebac
    assert abs(by_year[2021] - 0.104) < 0.02   # Leliq/Pases plateau
    assert by_year[2024] < 0.01                # post-migration ~0


def test_cpi_wpi_blend_csv_covers_variant_span():
    path = ROOT / "data/processed/inflation/converted_inflation_cpi-wpi-blend_1944-01_2025-12.csv"
    df = pd.read_csv(path).set_index("Year")
    span = df.loc[1964:2006]
    assert not span["CPI_log"].isna().any()
    assert not span["IPIM_log"].isna().any(), "IPIM must cover the full 1964-2006 variant span"
    # Known episodes (Dec/Dec): 1989 hyperinflation ~4900% CPI; 2002 blend between CPI 41% and IPIM 118%.
    assert df.loc[1989, "Blend_pct"] > 3000
    assert 0.40 < math.exp(df.loc[2002, "CPI_log"]) - 1 < 0.42
    assert df.loc[2002, "Blend_pct"] > 60

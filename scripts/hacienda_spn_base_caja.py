#!/usr/bin/env python3
"""Parse the Secretaría de Hacienda SPN base-caja annual series (datos.gob.ar dataset 379).

This module lifts the parsing/validation logic out of
``download_hacienda_spn-base-caja-historical.py`` so the fiscal generator can compute the
2000-2025 base-caja primary-result ratios directly from the committed raw CSVs instead of
hardcoding them.

Source: datos.gob.ar SSPM dataset 379 "Esquema Ahorro-Inversión-Financiamiento. Sector
Público Nacional. Base Caja." — the official Subsecretaría de Programación Macroeconómica
publication of the SPN cash-basis AIF scheme. Three distributions cover the series:
    379.1  1993-2006  (column suffix _1993_2006)
    379.2  2007-2014  (column suffix _2007_2014)
    379.3  2015+      (column suffix _2017 — the "2017 methodology" tabulation)

Ratios computed per year:
    ratio1 = superavit_primario / ingresos_corrientes   (= Result_Revenue in the FPI CSV)
    ratio2 = superavit_primario / intereses_netos        (= Result_DebtServ in the FPI CSV)
    where intereses_netos = superavit_primario - resultado_financiero
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import RAW_ROOT

HACIENDA_DIR = RAW_ROOT / "hacienda"

CSV_1993_2006 = HACIENDA_DIR / "spn-base-caja_valores-anuales_1993_2006.csv"
CSV_2007_2014 = HACIENDA_DIR / "spn-base-caja_valores-anuales_2007_2014.csv"
CSV_2015_2025 = HACIENDA_DIR / "spn-base-caja_valores-anuales_2015_2025_raw.csv"
IMIG_2017_XLSX = HACIENDA_DIR / "imig-anual_2017.xlsx"
IMIG_2018_XLSX = HACIENDA_DIR / "imig-anual_2018.xlsx"

# (csv path, column suffix, year span covered, optional reported-net-interest column).
# The 2015+ file uses the "_2017" suffix despite extending through 2025.
PERIODS = [
    (CSV_1993_2006, "1993_2006", range(1993, 2007), None),
    (CSV_2007_2014, "2007_2014", range(2007, 2015), None),
    (
        CSV_2015_2025,
        "2017",
        range(2015, 2026),
        "gtos_corr_int_ot_ren_prop_int_netos_2017",
    ),
]


@dataclass(frozen=True)
class BaseCajaActual:
    """Official annual SPN base-caja operands and their two derived FPI ratios."""

    current_revenue: float
    primary_result: float
    financial_result: float
    interest_measure: float
    result_revenue: float
    result_debt_serv: float


def load_period(
    path: Path,
    prim_col: str,
    fin_col: str,
    ing_col: str,
    interest_col: str | None = None,
) -> dict[int, BaseCajaActual]:
    """Load one dataset-379 CSV and retain the operands behind both FPI ratios.

    Skips rows where net interest or current revenue is zero, since the ratios would be
    undefined. When the distribution reports net interest directly, it must reproduce the
    accounting identity ``primary result - financial result``.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Missing raw SPN base-caja CSV: {path}. "
            f"Run scripts/download_hacienda_spn-base-caja-historical.py to fetch it."
        )
    df = pd.read_csv(path)
    required = [prim_col, fin_col, ing_col, "indice_tiempo"]
    if interest_col is not None:
        required.append(interest_col)
    for col in required:
        if col not in df.columns:
            raise KeyError(f"{path.name}: expected column {col!r} not found")
    df["year"] = pd.to_datetime(df["indice_tiempo"]).dt.year
    df = df.set_index("year")
    out: dict[int, BaseCajaActual] = {}
    for yr in df.index:
        prim = float(df.loc[yr, prim_col])
        fin = float(df.loc[yr, fin_col])
        ing = float(df.loc[yr, ing_col])
        interest = prim - fin
        if interest_col is not None:
            reported_interest = float(df.loc[yr, interest_col])
            if not math.isclose(interest, reported_interest, rel_tol=1e-9, abs_tol=1e-6):
                raise RuntimeError(
                    f"{path.name}: year {yr} net interest identity failed: "
                    f"primary-financial={interest} but {interest_col}={reported_interest}"
                )
        if not interest or not ing:
            continue
        out[int(yr)] = BaseCajaActual(
            current_revenue=ing,
            primary_result=prim,
            financial_result=fin,
            interest_measure=interest,
            result_revenue=prim / ing,
            result_debt_serv=prim / interest,
        )
    return out


def _all_raw_actuals() -> dict[int, BaseCajaActual]:
    """Merge the three official distributions into one annual base-caja operand map.

    The 379.3 ("_2017") file supplies 2015 onward; the earlier files supply their own spans.
    """
    merged: dict[int, BaseCajaActual] = {}
    for path, suffix, span, interest_col in PERIODS:
        parsed = load_period(
            path,
            f"superavit_primario_{suffix}",
            f"resultado_fin_{suffix}",
            f"ing_corr_{suffix}",
            interest_col,
        )
        for yr, vals in parsed.items():
            if yr in span:
                merged[yr] = vals
    return merged


def load_spn_base_caja_actuals(
    years: "range | list[int]" = range(2000, 2026),
    *,
    round_digits: "int | None" = 4,
) -> dict[int, BaseCajaActual]:
    """Return official operands and derived ratios for requested dataset-379 years.

    Args:
        years: years to return (default 2000-2025, the modern base-caja span).
        round_digits: round the two ratios to this many decimals (default 4 — the precision
            the committed fiscal CSV carries; pass None for full precision).
    """
    requested = sorted(set(years))
    raw = _all_raw_actuals()
    out: dict[int, BaseCajaActual] = {}
    for yr in requested:
        if yr not in raw:
            raise KeyError(f"No SPN base-caja row available for year {yr} in dataset 379")
        actual = raw[yr]
        if round_digits is not None:
            actual = replace(
                actual,
                result_revenue=round(actual.result_revenue, round_digits),
                result_debt_serv=round(actual.result_debt_serv, round_digits),
            )
        out[yr] = actual
    return out


def load_spn_base_caja_ratios(
    years: "range | list[int]" = range(2000, 2026),
    *,
    round_digits: "int | None" = 4,
) -> dict[int, tuple[float, float, float]]:
    """Compatibility view: {year: (Result_Revenue, Result_DebtServ, primary_MM)}."""
    actuals = load_spn_base_caja_actuals(years, round_digits=round_digits)
    return {
        yr: (actual.result_revenue, actual.result_debt_serv, actual.primary_result)
        for yr, actual in actuals.items()
    }


def imig_totals(path: Path) -> dict[str, float]:
    """Extract the annual primary/revenue/interest totals from a Hacienda IMIG annual xlsx."""
    if not path.exists():
        raise FileNotFoundError(f"Missing IMIG annual file: {path}")
    xl = pd.ExcelFile(path)
    df = xl.parse(xl.sheet_names[0], header=None)
    out: dict[str, float] = {}
    for _, row in df.iterrows():
        c1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        c0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        label = (c0 + " " + c1).strip().upper()
        annual: float | None = None
        for val in reversed(row.tolist()):
            if isinstance(val, (int, float)) and not pd.isna(val):
                annual = float(val)
                break
        if annual is None:
            continue
        if "INGRESOS TOTALES" in label and "TRIBUTARIOS" not in label:
            out["revenues"] = annual
        elif "RESULTADO PRIMARIO" in label and "CON" not in label and "SIN" not in label:
            out["primary"] = annual
        elif "INTERESES" in label and out.get("primary") is not None and "RESULTADO" not in label:
            out["interest"] = annual
        elif "RESULTADO FINANCIERO" in label and "ANTES" not in label:
            out["financial"] = annual
    return out


def validate_against_imig(
    ratios: dict[int, tuple[float, float, float]],
    imig: dict[str, float],
    *,
    year: int = 2018,
    tolerance: float = 0.001,
) -> float:
    """Assert that `year`'s primary result from dataset 379 reproduces the IMIG file.

    Returns the relative error. Raises RuntimeError if the gate fails (i.e. the upstream
    source was revised and the generated base-caja values must be re-reviewed).
    """
    if year not in ratios:
        raise RuntimeError(f"dataset 379: no {year} data — cannot validate source")
    prim_calc = ratios[year][2]
    prim_imig = imig.get("primary")
    if prim_imig is None:
        raise RuntimeError(f"Could not extract {year} primary from IMIG file — cannot validate")
    err = abs(prim_calc - prim_imig) / abs(prim_imig)
    if err > tolerance:
        raise RuntimeError(
            f"Validation FAILED for {year} primary result: dataset 379={prim_calc:,.1f} vs "
            f"IMIG={prim_imig:,.1f} (relative error {err:.3%} > {tolerance:.1%}). "
            f"datos.gob.ar source may have been revised — review the base-caja inputs."
        )
    return err


if __name__ == "__main__":
    ratios = load_spn_base_caja_ratios(range(2000, 2026))
    err18 = validate_against_imig(ratios, imig_totals(IMIG_2018_XLSX), year=2018)
    print(f"IMIG 2018 validation passed (err={err18:.4%})")
    for yr in sorted(ratios):
        r1, r2, prim = ratios[yr]
        print(f"  {yr}: ({r1:+.4f}, {r2:+.4f}),  # primary={prim:,.1f} M$")

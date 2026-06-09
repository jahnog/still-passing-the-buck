#!/usr/bin/env python3
"""Build FPI fiscal inputs from provided Excel and raw government/WB downloads."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import RAW_ROOT, latest_raw
from scripts.wb_raw import wb_series_from_raw

MODERN_YEARS = range(2019, 2026)

KNOWN_FISCAL = {
    2019: (-0.046, -0.427),
    2020: (-0.296, -3.285),
    2021: (-0.156, -1.890),
    2022: (-0.123, -0.938),
    2023: (-0.144, -0.993),
    2024: (0.104, 0.825),
    2025: (0.119, 0.920),
}


def debt_raw_for_year(year: int) -> Path | None:
    pattern = f"deuda_deuda-publica_{year}-01_{year}-12.xlsx"
    candidate = RAW_ROOT / "finanzas" / pattern
    if candidate.exists():
        return candidate
    matches = sorted((RAW_ROOT / "finanzas").glob(f"deuda_deuda-publica_{year}-*"))
    return matches[-1] if matches else None


def parse_debt_xlsx(raw: bytes, year: int) -> float | None:
    a25 = pd.read_excel(io.BytesIO(raw), sheet_name="A.2.5", header=None)
    years_row = a25.iloc[11]
    total_row = a25.iloc[16]
    for col in range(1, len(years_row)):
        yr_raw = years_row.iloc[col]
        val = total_row.iloc[col]
        col_year = None
        if hasattr(yr_raw, "year"):
            col_year = yr_raw.year
        elif isinstance(yr_raw, str) and "/" in yr_raw:
            yy = yr_raw.split("/")[-1].split()[0].replace("(*)", "").strip()
            col_year = 1900 + int(yy) if int(yy) > 50 else 2000 + int(yy)
        if col_year == year and isinstance(val, (int, float)) and not np.isnan(val):
            return float(val)
    for col in range(len(total_row) - 1, 0, -1):
        v = total_row.iloc[col]
        if isinstance(v, (int, float)) and not np.isnan(v):
            return float(v)
    return None


def main() -> int:
    print("Step 1: historical Excel (1853-2018)...")
    xl = pd.read_excel(
        paths.DATA_A_2018_XLSX,
        sheet_name="Hoja1",
        header=6,
        usecols="B,G,H,I,J",
        names=["Year", "Debt_GDP", "Debt_Exports", "Result_Revenue", "Result_DebtServ"],
    )
    xl = xl.dropna(subset=["Year"])
    xl["Year"] = xl["Year"].astype(int)
    hist = xl.set_index("Year").loc[1853:2018].copy()
    for col in ["Result_Revenue", "Result_DebtServ"]:
        hist[col] = hist[col].interpolate(method="index")

    print("Step 2: modern debt from raw finanzas workbooks...")
    debt_usd: dict[int, float] = {}
    for year in MODERN_YEARS:
        raw_path = debt_raw_for_year(year)
        if raw_path is None:
            print(f"  WARNING: no raw debt file for {year}", file=sys.stderr)
            continue
        val = parse_debt_xlsx(raw_path.read_bytes(), year)
        if val is not None:
            debt_usd[year] = val
            print(f"  {year}: USD {val:,.0f}M from {raw_path.name}")

    gdp_usd = wb_series_from_raw("NY.GDP.MKTP.CD")
    exports_usd = wb_series_from_raw("BX.GSR.TOTL.CD")

    modern_debt = {}
    for year in MODERN_YEARS:
        if year not in debt_usd:
            continue
        debt = debt_usd[year] * 1e6
        gdp = gdp_usd.get(year)
        exp = exports_usd.get(year)
        if year == 2025 and (gdp is None or exp is None):
            gdp = 620_000_000_000
            exp = 92_000_000_000
        modern_debt[year] = {
            "Debt_GDP": debt / gdp if gdp else np.nan,
            "Debt_Exports": debt / exp if exp else np.nan,
        }

    rows = [{"Year": 1852, "Debt_GDP": 0.0, "Debt_Exports": 0.0, "Result_Revenue": 0.0, "Result_DebtServ": 0.0}]
    for year, row in hist.iterrows():
        rows.append(
            {
                "Year": year,
                "Debt_GDP": row["Debt_GDP"],
                "Debt_Exports": row["Debt_Exports"],
                "Result_Revenue": row["Result_Revenue"],
                "Result_DebtServ": row["Result_DebtServ"],
            }
        )
    for year in MODERN_YEARS:
        debt_row = modern_debt.get(year, {})
        fiscal_row = KNOWN_FISCAL.get(year, (np.nan, np.nan))
        rows.append(
            {
                "Year": year,
                "Debt_GDP": debt_row.get("Debt_GDP", np.nan),
                "Debt_Exports": debt_row.get("Debt_Exports", np.nan),
                "Result_Revenue": fiscal_row[0],
                "Result_DebtServ": fiscal_row[1],
            }
        )

    result = pd.DataFrame(rows).set_index("Year")

    print("Step 3: cepo + BCRA debt-stock adjustments...")
    parallel = pd.read_csv(paths.PARALLEL_CEPO_CSV).set_index("Year")["ParallelARS"]
    official_fx = wb_series_from_raw("PA.NUS.FCRF")
    gdp_lcu = wb_series_from_raw("NY.GDP.MKTP.CN")
    bcra = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year")["BCRA_QuasiFiscal_GDP"]

    result["Debt_GDP_official"] = result["Debt_GDP"]
    result["Debt_Exports_official"] = result["Debt_Exports"]
    result["Cepo_Factor"] = 1.0
    result["BCRA_QuasiFiscal_GDP"] = 0.0

    for year in result.index:
        if year < 1900:
            continue
        factor = 1.0
        if year in parallel.index and official_fx.get(year):
            factor = float(parallel.loc[year]) / float(official_fx[year])
        result.loc[year, "Cepo_Factor"] = factor
        dg_cepo = result.loc[year, "Debt_GDP_official"] * factor
        bcra_gdp = float(bcra.get(year, 0.0)) if not pd.isna(bcra.get(year, np.nan)) else 0.0
        result.loc[year, "BCRA_QuasiFiscal_GDP"] = bcra_gdp
        result.loc[year, "Debt_GDP"] = dg_cepo + bcra_gdp

        de = result.loc[year, "Debt_Exports_official"]
        gdp_usd_corr = None
        if year in parallel.index and gdp_lcu.get(year):
            gdp_usd_corr = gdp_lcu[year] / float(parallel.loc[year])
        elif gdp_usd.get(year):
            gdp_usd_corr = gdp_usd[year]
        if bcra_gdp and gdp_usd_corr and exports_usd.get(year):
            de = de + bcra_gdp * gdp_usd_corr / exports_usd[year]
        result.loc[year, "Debt_Exports"] = de

    out = paths.FPI_FISCAL_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    result = result[
        [
            "Debt_GDP",
            "Debt_Exports",
            "Result_Revenue",
            "Result_DebtServ",
            "Debt_GDP_official",
            "Debt_Exports_official",
            "Cepo_Factor",
            "BCRA_QuasiFiscal_GDP",
        ]
    ]
    result.to_csv(out)
    print(f"Wrote {len(result)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

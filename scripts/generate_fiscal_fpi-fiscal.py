#!/usr/bin/env python3
"""Build FPI fiscal inputs from provided Excel and raw government/WB downloads."""

from __future__ import annotations

import csv
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
from scripts.data_io import RAW_ROOT, latest_raw, write_meta_sidecar
from scripts.hacienda_spn_base_caja import (
    BaseCajaActual,
    IMIG_2018_XLSX,
    imig_totals,
    load_spn_base_caja_actuals,
    load_spn_base_caja_ratios,
    validate_against_imig,
)
from scripts.wb_raw import official_fx_series, wb_series_from_raw
from scripts.cmpi_core import interpolate_fpi_ratio_gaps

MODERN_YEARS = range(2000, 2026)

# Primary result / total revenues and primary result / interest payments, 2000-2025.
#
# PROVENANCE — official dataset 379 supplies every post-2000 fiscal ratio:
#
# datos.gob.ar SSPM "Esquema Ahorro-Inversión-Financiamiento. Sector Público
#   Nacional. Base Caja." dataset 379 (distributions 379.1 for 1993-2006, 379.2 for 2007-2014,
#   and 379.3 for 2015-2025), parsed from the committed raw CSVs by
#   scripts/hacienda_spn_base_caja.load_spn_base_caja_ratios(). These are the official
#   Subsecretaría de Programación Macroeconómica annual tabulations of the SPN cash-basis AIF
#   scheme. Validated at runtime against the Hacienda IMIG 2018 annual file (exact match), with
#   all ratio operands retained in the generated fiscal CSV.
#
# ratio1 = superavit_primario / ingresos_corrientes  (= Result_Revenue in the FPI CSV)
# ratio2 = superavit_primario / intereses_netos      (= Result_DebtServ in the FPI CSV)
#   where intereses_netos = superavit_primario - resultado_financiero


def load_modern_fiscal() -> dict[int, BaseCajaActual]:
    """Load official SPN base-caja operands and derived ratios for 2000-2025.

    All years come from dataset 379; its 2018 primary result is independently validated against
    the Hacienda annual IMIG workbook.
    """
    actuals = load_spn_base_caja_actuals(MODERN_YEARS, round_digits=4)
    ratios = load_spn_base_caja_ratios(MODERN_YEARS, round_digits=4)
    # Runtime tripwire: the dataset-379 source must still reproduce the Hacienda IMIG 2018 file.
    err18 = validate_against_imig(ratios, imig_totals(IMIG_2018_XLSX), year=2018)
    print(f"  Validated dataset-379 base caja against IMIG 2018 (err={err18:.4%})")
    return actuals


# Snapshot of Administración Nacional devengado ratios computed from the separate raw mecon
# budget-execution zip (parsed 2026-06). This cross-concept diagnostic is not dataset 379 and is
# never written to the SPN base-caja baseline.
AN_DEVENGADO_SNAPSHOT = {
    2019: (0.0488, 0.2016),
    2020: (-0.0066, -0.0644),
    2021: (-0.1500, -1.6914),
    2022: (-0.2218, -1.8201),
    2023: (-0.1746, -1.5071),
    2024: (0.0845, 0.7949),
    2025: (0.1559, 2.0498),
}
AN_DRIFT_TOLERANCE = 0.005  # 0.5 pp on either ratio

def parse_mecon_totales() -> dict[int, tuple[float, float]]:
    """Administracion Nacional devengado ratios from the raw datos.gob.ar zip (cross-reference).

    Returns {year: (primary_result/revenues, primary_result/interest)} for complete years.
    NOTE: different concept from the base-caja ratios used (AN devengado vs SPN base caja).
    """
    raw = latest_raw("mecon", "datasets_totales-de-presupuesto")
    if raw is None:
        return {}

    def num(s: str) -> float:
        return float(s.replace(".", "").replace(",", "."))

    out: dict[int, tuple[float, float]] = {}
    with zipfile.ZipFile(raw) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(name) as handle:
            text = io.TextIOWrapper(handle, encoding="utf-8-sig")
            for row in csv.DictReader(text):
                year = int(row["ejercicio_presupuestario"])
                revenues = num(row["recurso_ingresado_percibido"])
                primary_exp = num(row["gasto_primario_devengado"])
                total_exp = num(row["credito_devengado"])
                primary_balance = revenues - primary_exp
                interest = total_exp - primary_exp
                if revenues and interest:
                    out[year] = (primary_balance / revenues, primary_balance / interest)
    return out


def crosscheck_mecon_zip(modern_fiscal: dict[int, BaseCajaActual]) -> None:
    """Print the AN-devengado cross-reference and warn if the upstream zip was revised."""
    parsed = parse_mecon_totales()
    if not parsed:
        print("  WARNING: no raw mecon zip found; AN-devengado cross-check skipped", file=sys.stderr)
        return
    print("  Cross-reference (different concepts; see the base-caja provenance note):")
    print("  Year | SPN base caja (used)   | AN devengado (zip)")
    for year in MODERN_YEARS:
        spn = modern_fiscal.get(year)
        an = parsed.get(year)
        spn_s = (
            f"{spn.result_revenue:+.3f} / {spn.result_debt_serv:+.3f}"
            if spn
            else "      -      "
        )
        an_s = f"{an[0]:+.3f} / {an[1]:+.3f}" if an else "      -      "
        print(f"  {year} | {spn_s} | {an_s}")
    for year, snap in AN_DEVENGADO_SNAPSHOT.items():
        live = parsed.get(year)
        if live is None:
            continue
        drift = max(abs(live[0] - snap[0]), abs(live[1] - snap[1]))
        if drift > AN_DRIFT_TOLERANCE:
            print(
                f"  WARNING: upstream revision detected for {year}: AN-devengado ratios moved "
                f"{drift:.3f} from the 2026-06 snapshot. Review the separate AN-devengado "
                f"diagnostic if its upstream source changed.",
                file=sys.stderr,
            )


def debt_raw_for_year(year: int) -> Path | None:
    """Return the raw debt xlsx that contains A.2.5 data for the given year.

    Preference order:
    1. Year-specific file (e.g. deuda_deuda-publica_2023-01_2023-12.xlsx)
    2. Any finanzas file whose name contains the year (rare pattern)
    3. The newest available file — the A.2.5 sheet contains the full series from 1992
       onward, so the latest file can supply debt stock for earlier years too.
    """
    pattern = f"deuda_deuda-publica_{year}-01_{year}-12.xlsx"
    candidate = RAW_ROOT / "finanzas" / pattern
    if candidate.exists():
        return candidate
    matches = sorted((RAW_ROOT / "finanzas").glob(f"deuda_deuda-publica_{year}-*"))
    if matches:
        return matches[-1]
    # Fall back to the newest workbook: A.2.5 contains the historical series from 1992+.
    # Filter explicitly so a newer `.xlsx.meta.json` sidecar cannot be mistaken for Excel.
    workbooks = sorted(
        (RAW_ROOT / "finanzas").glob("deuda_deuda-publica_*.xlsx"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return workbooks[0] if workbooks else None


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
    print("Step 1: historical Excel (1853-1999)...")
    xl = pd.read_excel(
        paths.DATA_A_1999_XLSX,
        sheet_name="Hoja1",
        header=6,
        usecols="B,G,H,I,J",
        names=["Year", "Debt_GDP", "Debt_Exports", "Result_Revenue", "Result_DebtServ"],
    )
    xl = xl.dropna(subset=["Year"])
    xl["Year"] = xl["Year"].astype(int)
    hist = interpolate_fpi_ratio_gaps(xl.set_index("Year").loc[1853:1999].copy())

    print("Step 1b: modern fiscal operands and ratios (dataset 379, 2000-2025)...")
    modern_fiscal = load_modern_fiscal()

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
    required_2025 = {
        "World Bank NY.GDP.MKTP.CD": gdp_usd.get(2025),
        "World Bank BX.GSR.TOTL.CD": exports_usd.get(2025),
        "Secretaría de Finanzas gross debt": debt_usd.get(2025),
    }
    missing_2025 = [name for name, value in required_2025.items() if value is None]
    if missing_2025:
        raise RuntimeError(
            "Published annual 2025 debt inputs are required; missing "
            + ", ".join(missing_2025)
            + ". Refresh the World Bank and Secretaría de Finanzas raw files."
        )

    modern_debt = {}
    for year in MODERN_YEARS:
        if year not in debt_usd:
            continue
        debt = debt_usd[year] * 1e6
        gdp = gdp_usd.get(year)
        exp = exports_usd.get(year)
        modern_debt[year] = {
            "Debt_GDP": debt / gdp if gdp else np.nan,
            "Debt_Exports": debt / exp if exp else np.nan,
            # Numerator and denominators of the two ratios above, emitted so downstream
            # decompositions can separate borrowing from denominator movements without
            # re-deriving a stock from a ratio and a second GDP vintage.
            "Debt_Stock_USD": debt,
            "GDP_CD_USD": gdp if gdp else np.nan,
            "Exports_CD_USD": exp if exp else np.nan,
        }

    print("Step 2b: AN-devengado cross-reference and upstream-revision tripwire...")
    crosscheck_mecon_zip(modern_fiscal)

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
        fiscal_row = modern_fiscal.get(year)
        rows.append(
            {
                "Year": year,
                "Debt_GDP": debt_row.get("Debt_GDP", np.nan),
                "Debt_Exports": debt_row.get("Debt_Exports", np.nan),
                "Debt_Stock_USD": debt_row.get("Debt_Stock_USD", np.nan),
                "GDP_CD_USD": debt_row.get("GDP_CD_USD", np.nan),
                "Exports_CD_USD": debt_row.get("Exports_CD_USD", np.nan),
                "CurrentRevenue": (
                    fiscal_row.current_revenue if fiscal_row is not None else np.nan
                ),
                "PrimaryResult": (
                    fiscal_row.primary_result if fiscal_row is not None else np.nan
                ),
                "FinancialResult": (
                    fiscal_row.financial_result if fiscal_row is not None else np.nan
                ),
                "InterestMeasure": (
                    fiscal_row.interest_measure if fiscal_row is not None else np.nan
                ),
                "Result_Revenue": (
                    fiscal_row.result_revenue if fiscal_row is not None else np.nan
                ),
                "Result_DebtServ": (
                    fiscal_row.result_debt_serv if fiscal_row is not None else np.nan
                ),
            }
        )

    result = pd.DataFrame(rows).set_index("Year")

    print("Step 3: cepo + BCRA debt-stock adjustments...")
    parallel = pd.read_csv(paths.PARALLEL_CEPO_CSV).set_index("Year")["ParallelARS"]
    official_fx = official_fx_series()
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
        if year in parallel.index:
            if not official_fx.get(year):
                raise RuntimeError(
                    f"Cepo year {year} has a parallel rate but no official rate (PA.NUS.ATLS / "
                    f"PA.NUS.FCRF); refusing to silently skip the cepo correction. "
                    f"Run download_worldbank_api_indicators-arg.py and generate_indicators_wdi-argentina.py."
                )
            factor = float(parallel.loc[year]) / float(official_fx[year])
        result.loc[year, "Cepo_Factor"] = factor
        # Whole-stock κ: keep the published USD Treasury stock and replace official USD GDP
        # with parallel-rate GDP. BCRA remunerated liabilities stay unscaled (already a
        # peso/GDP ratio).
        bcra_gdp = float(bcra.get(year, 0.0)) if not pd.isna(bcra.get(year, np.nan)) else 0.0
        result.loc[year, "BCRA_QuasiFiscal_GDP"] = bcra_gdp
        result.loc[year, "Debt_GDP"] = (
            result.loc[year, "Debt_GDP_official"] * factor + bcra_gdp
        )

        de = result.loc[year, "Debt_Exports_official"]
        gdp_usd_corr = None
        if year in parallel.index and gdp_lcu.get(year):
            gdp_usd_corr = gdp_lcu[year] / float(parallel.loc[year])
        elif gdp_usd.get(year):
            gdp_usd_corr = gdp_usd[year]
        if bcra_gdp and gdp_usd_corr and exports_usd.get(year):
            de = de + bcra_gdp * gdp_usd_corr / exports_usd[year]
        result.loc[year, "Debt_Exports"] = de

    def gdp_usd_for_addons(year: int) -> float | None:
        """USD GDP valued consistently with the cepo-corrected ratio."""
        if year in parallel.index and gdp_lcu.get(year):
            return gdp_lcu[year] / float(parallel.loc[year])
        gdp = gdp_usd.get(year)
        if gdp is not None and year in parallel.index and official_fx.get(year):
            gdp = gdp / (float(parallel.loc[year]) / float(official_fx[year]))
        return gdp

    print("Step 4: documented holdouts and official capitalized interest...")
    # The provided default file now carries documented restructuring states and holdout stocks
    # only. The modeled 2002-2005 unpaid-interest flow was removed under the F-05 evidence rule.
    # The separate generated capitalized-interest file carries only official 2024-2025 OPC and
    # dataset-379 operands.
    defaults = pd.read_csv(paths.DEFAULT_ADJUSTMENTS_CSV).set_index("Year")
    result["Debt_GDP_holdouts"] = result["Debt_GDP"]
    result["Result_DebtServ_capitalized_interest"] = result["Result_DebtServ"]
    result["DefaultFlag"] = ""

    def exports_usd_for_addons(year: int) -> float | None:
        """Exports valued consistently with the FPI Debt/Exports denominator."""
        return exports_usd.get(year)

    for year, adj in defaults.iterrows():
        if year not in result.index:
            continue
        flag = adj.get("DefaultFlag")
        if isinstance(flag, str) and flag.strip():
            result.loc[year, "DefaultFlag"] = flag.strip()
        holdout_usd_m = adj.get("HoldoutDebt_USD_M")
        if not pd.isna(holdout_usd_m):
            gdp_usd_corr = gdp_usd_for_addons(year)
            if not gdp_usd_corr:
                raise RuntimeError(f"No USD GDP available to value holdout debt for {year}")
            result.loc[year, "Debt_GDP_holdouts"] = (
                result.loc[year, "Debt_GDP"] + float(holdout_usd_m) * 1e6 / gdp_usd_corr
            )
    capitalized_interest = pd.read_csv(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV).set_index("Year")
    for year, adj in capitalized_interest.iterrows():
        if year not in result.index:
            continue
        cash = float(adj["CashInterest_GDP"])
        capitalized = float(adj["CapitalizedInterest_GDP"])
        if cash + capitalized <= 0:
            raise RuntimeError(f"Invalid official capitalized-interest operands for {year}")
        scale = cash / (cash + capitalized)
        result.loc[year, "Result_DebtServ_capitalized_interest"] = (
            result.loc[year, "Result_DebtServ"] * scale
        )
        result.loc[year, "DefaultFlag"] = "capitalizing"

    print("Step 5: importer-debt increase / BOPREAL column (section 6.0 E; feeds corrected baseline)...")
    # Paired add-back (data/processed/fiscal/...bcra-quasi-fiscal...csv, TradeArrears_BOPREAL_USD_M):
    # the 2022-23 values are measured increases in importer debt from a common 2021 baseline;
    # the 2024-25 values are audited BOPREAL Series 1-3 residuals. Pairing the two distinct
    # accounting objects is the study's timing convention; the reverse sensitivity removes
    # both sides together.
    arrears_usd_m = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year").get(
        "TradeArrears_BOPREAL_USD_M"
    )
    result["Debt_GDP_arrears"] = result["Debt_GDP"]
    if arrears_usd_m is not None:
        for year, usd_m in arrears_usd_m.items():
            if pd.isna(usd_m) or not usd_m or year not in result.index:
                continue
            gdp_usd_corr = gdp_usd_for_addons(year)
            if not gdp_usd_corr:
                raise RuntimeError(f"No USD GDP available to value trade arrears for {year}")
            result.loc[year, "Debt_GDP_arrears"] = (
                result.loc[year, "Debt_GDP"] + float(usd_m) * 1e6 / gdp_usd_corr
            )

    print("Step 6: structural primary balance columns (section 6.0 D; feed corrected baseline)...")
    # Measured official one-off/accounting-driven revenues are removed from both the primary
    # result and the revenue base:
    #   structural = (R - o) / (1 - o), where R = Result_Revenue and o = one-offs / revenues.
    # The input is generated from exact retained peso operands; no author-estimated shares enter.
    one_offs = pd.read_csv(paths.OFFICIAL_ONE_OFFS_CSV)
    o_by_year = one_offs.groupby("Year")["Amount_pct_revenues"].sum() / 100.0
    if o_by_year.isna().any():
        raise RuntimeError("official one-offs: every row needs Amount_pct_revenues")
    result["Result_Revenue_structural"] = result["Result_Revenue"]
    result["Result_DebtServ_structural"] = result["Result_DebtServ"]
    for year, o in o_by_year.items():
        if year in result.index and not pd.isna(result.loc[year, "Result_Revenue"]):
            r = result.loc[year, "Result_Revenue"]
            result.loc[year, "Result_Revenue_structural"] = (r - o) / (1.0 - o)
            if abs(r) < 1e-12:
                raise RuntimeError(
                    f"Cannot derive structural Result_DebtServ for {year}: "
                    "Result_Revenue is zero but one-off revenues are nonzero"
                )
            result.loc[year, "Result_DebtServ_structural"] = (
                result.loc[year, "Result_DebtServ"] * ((r - o) / r)
            )

    print("Step 7: paper-comparable and corrected baseline columns...")
    # Explicit baselines:
    #   *_paper_extension keeps the closest paper-style extension: official/reported fiscal
    #   stock/flow measures with no post-2000 anti-accounting adjustments.
    #   *_corrected is the headline baseline for the notebook: it keeps the paper's scoring
    #   method but uses the anti-cheating corrections documented above.
    result["Debt_GDP_paper_extension"] = result["Debt_GDP_official"]
    result["Debt_Exports_paper_extension"] = result["Debt_Exports_official"]
    result["Result_Revenue_paper_extension"] = result["Result_Revenue"]
    result["Result_DebtServ_paper_extension"] = result["Result_DebtServ"]

    result["Debt_GDP_corrected"] = result["Debt_GDP"]
    for col in ["Debt_GDP_holdouts", "Debt_GDP_arrears"]:
        extra = (result[col] - result["Debt_GDP"]).clip(lower=0).fillna(0.0)
        result["Debt_GDP_corrected"] = result["Debt_GDP_corrected"] + extra

    result["Debt_Exports_corrected"] = result["Debt_Exports"]
    # Single-correction memo columns mirroring the Debt/GDP ones. Without them the section-6.0
    # sensitivity tables could only perturb Debt/GDP and would understate each correction,
    # since every add-back enters both ratios in the corrected baseline.
    result["Debt_Exports_holdouts"] = result["Debt_Exports"]
    result["Debt_Exports_arrears"] = result["Debt_Exports"]

    def add_exports_addback(year: int, usd_m: float, memo_col: str, what: str) -> None:
        exp = exports_usd_for_addons(int(year))
        if not exp:
            raise RuntimeError(f"No exports available to value {what} for {year}")
        delta = float(usd_m) * 1e6 / exp
        result.loc[year, "Debt_Exports_corrected"] += delta
        result.loc[year, memo_col] += delta

    for year, adj in defaults.iterrows():
        holdout_usd_m = adj.get("HoldoutDebt_USD_M")
        if year in result.index and not pd.isna(holdout_usd_m):
            add_exports_addback(year, holdout_usd_m, "Debt_Exports_holdouts", "holdout debt")
    if arrears_usd_m is not None:
        for year, usd_m in arrears_usd_m.items():
            if pd.isna(usd_m) or not usd_m or year not in result.index:
                continue
            add_exports_addback(year, usd_m, "Debt_Exports_arrears", "trade arrears")
    result["Result_Revenue_corrected"] = result["Result_Revenue_structural"]
    capitalized_scale = pd.Series(1.0, index=result.index)
    mask = result["Result_DebtServ"].abs() > 1e-12
    capitalized_scale.loc[mask] = (
        result.loc[mask, "Result_DebtServ_capitalized_interest"]
        / result.loc[mask, "Result_DebtServ"]
    )
    result["Result_DebtServ_corrected"] = (
        result["Result_DebtServ_structural"] * capitalized_scale
    )

    out = paths.FPI_FISCAL_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    result = result[
        [
            "Debt_GDP",
            "Debt_Exports",
            "CurrentRevenue",
            "PrimaryResult",
            "FinancialResult",
            "InterestMeasure",
            "Result_Revenue",
            "Result_DebtServ",
            "Debt_GDP_paper_extension",
            "Debt_Exports_paper_extension",
            "Result_Revenue_paper_extension",
            "Result_DebtServ_paper_extension",
            "Debt_GDP_corrected",
            "Debt_Exports_corrected",
            "Result_Revenue_corrected",
            "Result_DebtServ_corrected",
            "Debt_GDP_official",
            "Debt_Exports_official",
            "Debt_Stock_USD",
            "GDP_CD_USD",
            "Exports_CD_USD",
            "Cepo_Factor",
            "BCRA_QuasiFiscal_GDP",
            "Debt_GDP_holdouts",
            "Result_DebtServ_capitalized_interest",
            "Result_Revenue_structural",
            "Result_DebtServ_structural",
            "Debt_GDP_arrears",
            "Debt_Exports_holdouts",
            "Debt_Exports_arrears",
            "DefaultFlag",
        ]
    ]
    result.to_csv(out)
    write_meta_sidecar(
        out,
        script=Path(__file__).name,
        sources=[
            "data/provided/data_a_1999.xlsx (cols G-J, 1853-1999; cols I-J "
            "are blank in 1861-1863 and are arithmetically interpolated "
            "between the 1860 and 1864 endpoints)",
            "data/raw/hacienda/spn-base-caja_valores-anuales_*.csv "
            "(datos.gob.ar SSPM dataset 379 SPN base-caja AIF, 2000-2025)",
            "data/raw/finanzas/deuda_deuda-publica_*.xlsx (SPN gross debt, 2019-2025)",
            "World Bank raw API JSON: NY.GDP.MKTP.CD, NY.GDP.MKTP.CN, "
            "BX.GSR.TOTL.CD (official 2025 observations required)",
            str(paths.PARALLEL_CEPO_CSV.relative_to(ROOT)),
            str(paths.BCRA_QUASI_FISCAL_CSV.relative_to(ROOT)),
            str(paths.BCRA_IMPORTER_DEBT_BOPREAL_CSV.relative_to(ROOT)),
            str(paths.OFFICIAL_ONE_OFFS_CSV.relative_to(ROOT)),
            str(paths.OFFICIAL_CAPITALIZED_INTEREST_CSV.relative_to(ROOT)),
        ],
        notes="Debt_GDP applies the whole-stock cepo correction "
              "(official × free/official factor + unscaled BCRA); Debt_Exports carries the "
              "BCRA correction; "
              "the source's 1861-1863 Result_Revenue and Result_DebtServ blanks are "
              "filled by arithmetic interpolation between 1860 and 1864 so every FPI "
              "component is scored over the same 173-year pool; "
              "the *_corrected columns additionally consolidate documented holdouts, paired "
              "importer-debt-increase/BOPREAL residual operands, measured structural-primary-result, and official 2024-2025 "
              "capitalized-interest corrections for the headline FPI; "
              "the modeled 2002-2005 unpaid-interest flow and Paris Club interpolation are absent; "
              "the *_paper_extension and official raw columns are retained for audit; "
              "CurrentRevenue/PrimaryResult/FinancialResult/InterestMeasure retain the "
              "dataset-379 fiscal operands in millions of current pesos for 2000-2025; "
              "Debt_Stock_USD/GDP_CD_USD/Exports_CD_USD are the observed numerator and "
              "denominators of the official ratios (2000-2025), so a decomposition need not "
              "recover a stock from a ratio and a second GDP vintage.",
    )
    print(f"Wrote {len(result)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

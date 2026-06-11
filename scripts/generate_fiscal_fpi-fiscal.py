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
from scripts.wb_raw import official_fx_series, wb_series_from_raw

MODERN_YEARS = range(2019, 2026)

# Primary result / total revenues and primary result / interest payments, 2019-2025.
#
# PROVENANCE (corrected 2026-06): these ratios follow the **Sector Publico Nacional cash-basis
# ("base caja") primary result** published by the Secretaria de Hacienda (and tabulated by the
# OPC) — the same concept the press headlines quote (e.g. the 2020 COVID primary deficit and the
# 2024-2025 primary surpluses). They are NOT derivable from the datos.gob.ar
# "Totales de Presupuesto" zip kept under data/raw/mecon/: that dataset covers the narrower
# Administracion Nacional on an accrued ("devengado") basis, and its "recursos percibidos"
# include BCRA profit transfers and FGS property rents, which masks the deficits (its naive
# 2020 ratio is -0.007 vs the -0.296 cash-basis reality). The zip is still parsed below as a
# cross-reference and as an upstream-revision tripwire. Curated 2025-06; if Hacienda revises,
# update here and log it in data/REVISIONS.md.
KNOWN_FISCAL = {
    2019: (-0.046, -0.427),
    2020: (-0.296, -3.285),
    2021: (-0.156, -1.890),
    2022: (-0.123, -0.938),
    2023: (-0.144, -0.993),
    2024: (0.104, 0.825),
    2025: (0.119, 0.920),
}

# Snapshot of the Administracion Nacional devengado ratios computed from the raw mecon zip
# (parsed 2026-06). If a re-parse drifts from this snapshot, the upstream dataset was revised
# and KNOWN_FISCAL must be re-verified against the latest Hacienda/OPC cash-basis publication.
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

# World Bank has not published 2025 yet. Official INDEC balance-of-payments figures
# (Cuentas internacionales 4T-2025, publ. 2026-03-27):
#   exports of goods FOB 87,152 + services 18,039 + primary-income credits 6,402
#   = 111,593 MUSD — the same goods+services+primary-income concept as
#   BX.GSR.TOTL.CD (check: 2024 = 79,760+17,167+6,293 = 103,220 = WB value).
# GDP: exports of goods & services (105,191 MUSD) were 15.6% of current-price GDP
# (INDEC Informe de avance del nivel de actividad 4T-2025) -> GDP ~ 674,300 MUSD.
# PROVISIONAL: superseded automatically once the WB raw snapshots carry 2025.
PROVISIONAL_GDP_USD_2025 = 674_300_000_000
PROVISIONAL_EXPORTS_USD_2025 = 111_593_000_000


def parse_mecon_totales() -> dict[int, tuple[float, float]]:
    """Administracion Nacional devengado ratios from the raw datos.gob.ar zip (cross-reference).

    Returns {year: (primary_result/revenues, primary_result/interest)} for complete years.
    NOTE: different concept from KNOWN_FISCAL (AN devengado vs SPN base caja) — see above.
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


def crosscheck_mecon_zip() -> None:
    """Print the AN-devengado cross-reference and warn if the upstream zip was revised."""
    parsed = parse_mecon_totales()
    if not parsed:
        print("  WARNING: no raw mecon zip found; AN-devengado cross-check skipped", file=sys.stderr)
        return
    print("  Cross-reference (different concepts; see KNOWN_FISCAL provenance note):")
    print("  Year | SPN base caja (used)   | AN devengado (zip)")
    for year in MODERN_YEARS:
        spn = KNOWN_FISCAL.get(year)
        an = parsed.get(year)
        spn_s = f"{spn[0]:+.3f} / {spn[1]:+.3f}" if spn else "      -      "
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
                f"{drift:.3f} from the 2026-06 snapshot. Re-verify KNOWN_FISCAL against the "
                f"latest Hacienda/OPC SPN base-caja publication and update data/REVISIONS.md.",
                file=sys.stderr,
            )


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
            gdp = PROVISIONAL_GDP_USD_2025
            exp = PROVISIONAL_EXPORTS_USD_2025
        modern_debt[year] = {
            "Debt_GDP": debt / gdp if gdp else np.nan,
            "Debt_Exports": debt / exp if exp else np.nan,
        }

    print("Step 2b: AN-devengado cross-reference and upstream-revision tripwire...")
    crosscheck_mecon_zip()

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

    def gdp_usd_for_addons(year: int) -> float | None:
        """USD GDP valued consistently with the cepo-corrected ratio (free-market rate on
        control years; provisional 2025 value when the World Bank has not published)."""
        if year in parallel.index and gdp_lcu.get(year):
            return gdp_lcu[year] / float(parallel.loc[year])
        gdp = gdp_usd.get(year)
        if gdp is None and year == 2025:
            gdp = PROVISIONAL_GDP_USD_2025
        if gdp is not None and year in parallel.index and official_fx.get(year):
            gdp = gdp / (float(parallel.loc[year]) / float(official_fx[year]))
        return gdp

    print("Step 4: default-integrity memo columns (section 6.0 C; sensitivity-only)...")
    # Curated default/restructuring adjustments (data/provided/fiscal-default-adjustments.csv):
    #   Debt_GDP_holdouts     — untendered defaulted debt added back for 2005-2015, valued
    #                           against the same (parallel-corrected) USD GDP as the baseline.
    #   Result_DebtServ_accrual — cash ratio rescaled by paid/(paid + accrued-unpaid) for the
    #                           2002-2005 default window, so "resources available to service the
    #                           debt" reflects interest *due*, not just interest *paid*.
    # Both columns equal the baseline outside their windows; they feed Table 6b, never the
    # headline FPI.
    defaults = pd.read_csv(paths.DEFAULT_ADJUSTMENTS_CSV).set_index("Year")
    result["Debt_GDP_holdouts"] = result["Debt_GDP"]
    result["Result_DebtServ_accrual"] = result["Result_DebtServ"]
    result["DefaultFlag"] = ""
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
        paid = adj.get("InterestPaid_GDP")
        unpaid = adj.get("AccruedUnpaidInterest_GDP")
        if not pd.isna(paid) and not pd.isna(unpaid) and (paid + unpaid) > 0:
            scale = float(paid) / (float(paid) + float(unpaid))
            result.loc[year, "Result_DebtServ_accrual"] = result.loc[year, "Result_DebtServ"] * scale

    print("Step 5: importer-arrears / BOPREAL memo column (section 6.0 E; sensitivity-only)...")
    # Paired add-back (data/processed/fiscal/...bcra-quasi-fiscal...csv, TradeArrears_BOPREAL_USD_M):
    # the 2022-23 import-payment arrears accumulated under exchange controls were invisible
    # liabilities; their 2024-25 BOPREAL conversion made them visible BCRA bonds. Adding both
    # sides (or neither — the baseline) keeps the 2023/2024 administration change symmetric.
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

    print("Step 6: structural primary balance memo column (section 6.0 D; sensitivity-only)...")
    # One-off / accounting-driven revenues (data/provided/fiscal-one-offs.csv, Type == "one-off")
    # are removed from both the primary result and the revenue base:
    #   structural = (R - o) / (1 - o), where R = Result_Revenue and o = one-offs / revenues.
    # Rows typed "documented" (AFJP stock transfer, redirected contributions) are context only.
    one_offs = pd.read_csv(paths.FISCAL_ONE_OFFS_CSV)
    one_offs = one_offs[one_offs["Type"].str.strip() == "one-off"]
    o_by_year = one_offs.groupby("Year")["Amount_pct_revenues"].sum() / 100.0
    if o_by_year.isna().any():
        raise RuntimeError("fiscal-one-offs.csv: every one-off row needs Amount_pct_revenues")
    result["Result_Revenue_structural"] = result["Result_Revenue"]
    for year, o in o_by_year.items():
        if year in result.index and not pd.isna(result.loc[year, "Result_Revenue"]):
            r = result.loc[year, "Result_Revenue"]
            result.loc[year, "Result_Revenue_structural"] = (r - o) / (1.0 - o)

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
            "Debt_GDP_holdouts",
            "Result_DebtServ_accrual",
            "Result_Revenue_structural",
            "Debt_GDP_arrears",
            "DefaultFlag",
        ]
    ]
    result.to_csv(out)
    write_meta_sidecar(
        out,
        script=Path(__file__).name,
        sources=[
            "data/provided/data_a_2018.xlsx (cols G-J, 1853-2018)",
            "data/raw/finanzas/deuda_deuda-publica_*.xlsx (SPN gross debt, 2019-2025)",
            "World Bank raw API JSON: NY.GDP.MKTP.CD, NY.GDP.MKTP.CN, BX.GSR.TOTL.CD",
            "KNOWN_FISCAL: SPN base-caja primary-result ratios (Hacienda/OPC; see provenance note)",
            str(paths.PARALLEL_CEPO_CSV.relative_to(ROOT)),
            str(paths.BCRA_QUASI_FISCAL_CSV.relative_to(ROOT)),
        ],
        notes="Debt_GDP/Debt_Exports carry the section-6.0 cepo and BCRA corrections; "
              "official raw columns retained for audit.",
    )
    print(f"Wrote {len(result)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

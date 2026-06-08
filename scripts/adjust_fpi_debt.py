#!/usr/bin/env python3
"""Apply the two debt-stock corrections to data/argentina/fiscal/fpi-fiscal-1853-2025.csv.

This is the light-weight, network-cheap companion to build_fpi_data.py: it takes the raw
(official-rate, Treasury-only) Debt/GDP and Debt/Exports already in the CSV and produces the
adjusted series used by the FPI, without re-downloading the Secretaría de Finanzas /
datos.gob.ar government files. It is idempotent — re-running reads the *_official columns when
present, so the adjustment is never applied twice.

(A) CEPO FX CORRECTION (mirrors the CMPI devaluation fix). During exchange-control years the
    official peso was overvalued, so GDP-in-USD was overstated and Debt/GDP understated. We
    re-value GDP at the free-market (CCL/blue) rate:
        Debt/GDP_cepo = Debt/GDP_official × (FX_parallel / FX_official)
    Debt/Exports needs no FX correction (exports are genuine USD receipts).

(B) BCRA QUASI-FISCAL CONSOLIDATION (Néstor Kirchner → Milei). The central bank's remunerated
    ("unconvertible") peso liabilities — Lebac/Nobac → Leliq → Pases — are hidden public debt.
    We add them to Treasury debt to form a CONSOLIDATED public-debt ratio, so administrations
    that GREW this off-balance-sheet debt are penalised, and an administration that MIGRATES it
    onto the Treasury (Milei 2024) is not double-charged for the reclassification — only the
    genuine net change is scored.
        Debt/GDP_adj     = Debt/GDP_cepo + BCRA/GDP
        Debt/Exports_adj = Debt/Exports  + (BCRA/GDP × GDP_USD_corrected) / Exports_USD
"""

import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

FPI_CSV = Path("data/argentina/fiscal/fpi-fiscal-1853-2025.csv")
BCRA_CSV = Path("data/argentina/fiscal/bcra-quasi-fiscal-2001-2025.csv")
PARALLEL_CSV = Path("data/argentina/exchange/parallel-cepo.csv")


def wb_series(code: str, country: str = "ARG") -> dict:
    url = (f"https://api.worldbank.org/v2/country/{country}/indicator/{code}"
           f"?format=json&per_page=80&mrv=45")
    req = Request(url, headers={"User-Agent": "StillPassingTheBuck/1.0"})
    for _ in range(4):
        try:
            with urlopen(req, timeout=60) as r:
                data = json.load(r)
            records = data[1] if (len(data) > 1 and data[1]) else []
            return {int(r["date"]): r["value"] for r in records if r.get("value") is not None}
        except Exception as e:
            print(f"  WB {code} retry: {e}", file=sys.stderr)
            time.sleep(3)
    raise RuntimeError(f"World Bank {code} unreachable")


def main() -> int:
    df = pd.read_csv(FPI_CSV).set_index("Year")

    # Idempotent base: prefer the stored official columns if a prior run wrote them.
    raw_gdp = df["Debt_GDP_official"] if "Debt_GDP_official" in df else df["Debt_GDP"]
    raw_exp = df["Debt_Exports_official"] if "Debt_Exports_official" in df else df["Debt_Exports"]

    parallel = pd.read_csv(PARALLEL_CSV).set_index("Year")["ParallelARS"]
    bcra = pd.read_csv(BCRA_CSV).set_index("Year")["BCRA_QuasiFiscal_GDP"]

    print("Fetching World Bank GDP / FX / exports ...")
    official_fx = wb_series("PA.NUS.FCRF")     # official ARS/USD, annual avg
    gdp_lcu = wb_series("NY.GDP.MKTP.CN")      # nominal GDP, pesos
    gdp_usd = wb_series("NY.GDP.MKTP.CD")      # GDP, current USD
    exports_usd = wb_series("BX.GSR.TOTL.CD")  # exports of goods & services, current USD

    out = pd.DataFrame(index=df.index)
    out["Result_Revenue"] = df["Result_Revenue"]
    out["Result_DebtServ"] = df["Result_DebtServ"]
    out["Debt_GDP_official"] = raw_gdp
    out["Debt_Exports_official"] = raw_exp
    out["Cepo_Factor"] = 1.0
    out["BCRA_QuasiFiscal_GDP"] = 0.0
    out["Debt_GDP"] = raw_gdp
    out["Debt_Exports"] = raw_exp

    for year in df.index:
        if year < 1900:
            continue
        factor = 1.0
        if year in parallel.index and official_fx.get(year):
            factor = float(parallel.loc[year]) / float(official_fx[year])
        out.loc[year, "Cepo_Factor"] = factor
        dg_cepo = raw_gdp.loc[year] * factor

        bcra_gdp = float(bcra.get(year, 0.0))
        if pd.isna(bcra_gdp):
            bcra_gdp = 0.0
        out.loc[year, "BCRA_QuasiFiscal_GDP"] = bcra_gdp
        out.loc[year, "Debt_GDP"] = dg_cepo + bcra_gdp

        de = raw_exp.loc[year]
        gdp_usd_corr = None
        if year in parallel.index and gdp_lcu.get(year):
            gdp_usd_corr = gdp_lcu[year] / float(parallel.loc[year])
        elif gdp_usd.get(year):
            gdp_usd_corr = gdp_usd[year]
        if bcra_gdp and gdp_usd_corr and exports_usd.get(year):
            de = de + bcra_gdp * gdp_usd_corr / exports_usd[year]
        out.loc[year, "Debt_Exports"] = de

    out = out[["Debt_GDP", "Debt_Exports", "Result_Revenue", "Result_DebtServ",
               "Debt_GDP_official", "Debt_Exports_official", "Cepo_Factor",
               "BCRA_QuasiFiscal_GDP"]]
    out.to_csv(FPI_CSV)

    print(f"\nWrote {len(out)} rows to {FPI_CSV}")
    print("\nTerm-boundary years (raw → adjusted):")
    for y in [2007, 2011, 2015, 2019, 2023, 2024, 2025]:
        if y in out.index:
            r = out.loc[y]
            print(f"  {y}: Debt/GDP {r['Debt_GDP_official']:.3f} → {r['Debt_GDP']:.3f} "
                  f"(cepo×{r['Cepo_Factor']:.2f} + BCRA {r['BCRA_QuasiFiscal_GDP']*100:.1f}%) | "
                  f"Debt/Exp {r['Debt_Exports_official']:.2f} → {r['Debt_Exports']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

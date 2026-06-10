#!/usr/bin/env python3
"""Re-apply cepo FX and BCRA consolidation to an existing FPI CSV (idempotent)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.wb_raw import official_fx_series, wb_series_from_raw


def main() -> int:
    df = pd.read_csv(paths.FPI_FISCAL_CSV).set_index("Year")

    raw_gdp = df["Debt_GDP_official"] if "Debt_GDP_official" in df else df["Debt_GDP"]
    raw_exp = df["Debt_Exports_official"] if "Debt_Exports_official" in df else df["Debt_Exports"]

    parallel = pd.read_csv(paths.PARALLEL_CEPO_CSV).set_index("Year")["ParallelARS"]
    bcra = pd.read_csv(paths.BCRA_QUASI_FISCAL_CSV).set_index("Year")["BCRA_QuasiFiscal_GDP"]

    official_fx = official_fx_series()
    gdp_lcu = wb_series_from_raw("NY.GDP.MKTP.CN")
    gdp_usd = wb_series_from_raw("NY.GDP.MKTP.CD")
    exports_usd = wb_series_from_raw("BX.GSR.TOTL.CD")

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
        if year in parallel.index:
            if not official_fx.get(year):
                raise RuntimeError(
                    f"Cepo year {year} has a parallel rate but no official rate (PA.NUS.ATLS / "
                    f"PA.NUS.FCRF); refusing to silently skip the cepo correction. "
                    f"Run download_worldbank_api_indicators-arg.py and generate_indicators_wdi-argentina.py."
                )
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

    out = out[
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
    out.to_csv(paths.FPI_FISCAL_CSV)
    print(f"Wrote {len(out)} rows to {paths.FPI_FISCAL_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

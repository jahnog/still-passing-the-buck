#!/usr/bin/env python3
"""Build US$ price deflators that hold the FPI debt-ratio denominators at constant 2003 prices.

Section 9.8 of the notebook re-ranks the FPI with the *denominators* of Debt/GDP and
Debt/Exports revalued at constant 2003 US$ prices. The motivation is measurement, not
politics: both FPI debt-burden ratios put a (largely hard-currency) debt stock over a
current-US$ flow, so a real-exchange-rate or terms-of-trade cycle moves the ratio even when
the debt stock and the real economy are unchanged. The innovation machinery then books that
revaluation as fiscal behaviour for whoever governs the upswing, and as fiscal failure for
whoever governs the reversal.

This script writes two index series, both normalised to 1.000 in 2003:

    GDP_Deflator_USD      = (NY.GDP.MKTP.CD / NY.GDP.MKTP.KD) normalised to 2003
    Exports_Deflator_USD  = (NE.EXP.GNFS.CD / NE.EXP.GNFS.KD) normalised to 2003

Applied multiplicatively, `Debt_GDP * GDP_Deflator_USD` is the debt ratio a constant-2003-price
denominator would have produced, and likewise for Debt/Exports. The export deflator is the
goods-and-services national-accounts deflator, which is the concept family of the FPI's
BX.GSR.TOTL.CD denominator; the merchandise net-barter terms-of-trade index
(TT.PRI.MRCH.XD.WD) is carried alongside it for audit but is not the applied factor.

Coverage is 1960-2025 — the World Bank constant-price aggregates do not exist before 1960, which
is exactly why section 9.8 is a sensitivity variant and not a corrected baseline (promoting it
would correct the modern era only and deepen the cross-era asymmetry logged as Gap MAJ-2 in
docs/FORENSIC_AUDIT.md). The notebook leaves every pre-1960 year at its baseline value.
"""

from __future__ import annotations

import csv
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import write_meta_sidecar

BASE_YEAR = 2003
FIRST_YEAR = 1960
LAST_YEAR = 2025

OUT = paths.PROCESSED / "fiscal" / "converted_fiscal_denominator-neutral_1960-01_2025-12.csv"


def indicators() -> dict[str, dict[int, float]]:
    """Argentina rows of the committed WDI extract, keyed by indicator code then year."""
    wanted = {
        "NY.GDP.MKTP.CD",
        "NY.GDP.MKTP.KD",
        "NE.EXP.GNFS.CD",
        "NE.EXP.GNFS.KD",
        "TT.PRI.MRCH.XD.WD",
    }
    out: dict[str, dict[int, float]] = {code: {} for code in wanted}
    with gzip.open(paths.INDICATORS_GZ, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["CountryName"] != "Argentina":
                continue
            code = row["IndicatorCode"]
            if code not in wanted:
                continue
            try:
                out[code][int(float(row["Year"]))] = float(row["Value"])
            except (TypeError, ValueError):
                continue
    return out


def main() -> int:
    ind = indicators()
    gdp_cd, gdp_kd = ind["NY.GDP.MKTP.CD"], ind["NY.GDP.MKTP.KD"]
    exp_cd, exp_kd = ind["NE.EXP.GNFS.CD"], ind["NE.EXP.GNFS.KD"]
    tot = ind["TT.PRI.MRCH.XD.WD"]

    required_2025 = {
        "NY.GDP.MKTP.CD": gdp_cd.get(2025),
        "NY.GDP.MKTP.KD": gdp_kd.get(2025),
        "NE.EXP.GNFS.CD": exp_cd.get(2025),
        "NE.EXP.GNFS.KD": exp_kd.get(2025),
    }
    missing_2025 = [code for code, value in required_2025.items() if value is None]
    if missing_2025:
        raise RuntimeError(
            "Complete World Bank 2025 denominator-neutral inputs are required; missing "
            + ", ".join(missing_2025)
            + ". Refresh the World Bank API snapshots."
        )

    def deflator(cd: dict[int, float], kd: dict[int, float], year: int) -> float | None:
        if year not in cd or year not in kd or not kd[year]:
            return None
        return cd[year] / kd[year]

    gdp_base = deflator(gdp_cd, gdp_kd, BASE_YEAR)
    exp_base = deflator(exp_cd, exp_kd, BASE_YEAR)
    if gdp_base is None or exp_base is None:
        raise RuntimeError(f"Missing {BASE_YEAR} base-year deflator inputs")
    tot_base = tot.get(BASE_YEAR)

    rows: list[dict[str, object]] = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        gdp_d = deflator(gdp_cd, gdp_kd, year)
        exp_d = deflator(exp_cd, exp_kd, year)
        gdp_index = gdp_d / gdp_base if gdp_d is not None else None
        exp_index = exp_d / exp_base if exp_d is not None else None
        if gdp_index is None or exp_index is None:
            continue
        rows.append(
            {
                "Year": year,
                "GDP_Deflator_USD": f"{gdp_index:.9f}",
                "Exports_Deflator_USD": f"{exp_index:.9f}",
                "TermsOfTrade_Index": f"{tot[year] / tot_base:.9f}" if year in tot and tot_base else "",
                "GDP_CD_USD": f"{gdp_cd[year]:.0f}" if year in gdp_cd else "",
                "GDP_KD_USD": f"{gdp_kd[year]:.0f}" if year in gdp_kd else "",
                "Exports_CD_USD": f"{exp_cd[year]:.0f}" if year in exp_cd else "",
                "Exports_KD_USD": f"{exp_kd[year]:.0f}" if year in exp_kd else "",
                "Note": (
                    "Complete annual observations are used for 2025, but recent "
                    "national-account values remain subject to source revisions."
                    if year == 2025
                    else ""
                ),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "Year",
                "GDP_Deflator_USD",
                "Exports_Deflator_USD",
                "TermsOfTrade_Index",
                "GDP_CD_USD",
                "GDP_KD_USD",
                "Exports_CD_USD",
                "Exports_KD_USD",
                "Note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    write_meta_sidecar(
        OUT,
        script=Path(__file__).name,
        sources=[
            str(paths.INDICATORS_GZ.relative_to(ROOT))
            + " (NY.GDP.MKTP.CD, NY.GDP.MKTP.KD, NE.EXP.GNFS.CD, NE.EXP.GNFS.KD, TT.PRI.MRCH.XD.WD)",
        ],
        notes=(
            "US$ price deflators normalised to 2003 = 1.000. Sensitivity input for notebook "
            "section 9.8 only; NOT consumed by the corrected FPI baseline. Complete annual "
            "observations are used for 2025, but recent national-account values remain "
            "subject to source revisions."
        ),
    )
    print(f"Wrote {len(rows)} rows to {OUT}")
    print(
        "  2003=1.000 | "
        + " ".join(
            f"{r['Year']}:{float(r['GDP_Deflator_USD']):.3f}/{float(r['Exports_Deflator_USD']):.3f}"
            for r in rows
            if int(r["Year"]) in (2001, 2003, 2005, 2007, 2015, 2024, 2025)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

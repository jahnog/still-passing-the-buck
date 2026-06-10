#!/usr/bin/env python3

import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

INDICATOR_FILE = paths.INDICATORS_GZ
INTEREST_FILE = paths.INTEREST_CSV
ALT_CPI_FILE = paths.ALT_CPI_CSV
ALT_CPI_YEARS = range(2007, 2016)  # 2007-2015 INDEC-intervention override window
PARALLEL_FX_FILE = paths.PARALLEL_CEPO_CSV
FPI_FISCAL_FILE = paths.FPI_FISCAL_CSV
# Cepo years whose devaluation must use the free-market rate (2012-2015 and 2019 onward); the
# 2016-2018 float is intentionally excluded (the brecha was < 1%, so the official rate is fine).
CEPO_FX_YEARS = (2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025)
# Years the BCRA carried remunerated quasi-fiscal debt that must be consolidated into the FPI
# debt stock (Lebac creation 2002 through the 2023 peak; 2024-2025 wind-down may reach zero).
BCRA_QF_YEARS = range(2003, 2024)
FPI_COLUMNS = ("Debt_GDP", "Debt_Exports", "Result_Revenue", "Result_DebtServ")

SERIES = {
    "NY.GDP.DEFL.KD.ZG": "Inflation, GDP deflator (annual %)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "FP.CPI.TOTL": "Consumer price index (2010 = 100)",
    "FP.WPI.TOTL": "Wholesale price index (2010 = 100)",
    "PA.NUS.ATLS": "Official exchange rate (LCU per US$, period average)",
    "NY.GDP.PCAP.KD.ZG": "GDP per capita growth (annual %)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-year", type=int, default=2025)
    return parser.parse_args()


def audit_indicator_file(path: Path) -> dict[str, dict[str, object]]:
    stats = {
        code: {"name": name, "min_year": None, "max_year": None, "count": 0, "years": set()}
        for code, name in SERIES.items()
    }

    with gzip.open(path, "rt", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = row["IndicatorCode"]
            if code not in stats:
                continue

            year = int(row["Year"])
            stat = stats[code]
            stat["min_year"] = year if stat["min_year"] is None or year < stat["min_year"] else stat["min_year"]
            stat["max_year"] = year if stat["max_year"] is None or year > stat["max_year"] else stat["max_year"]
            stat["count"] = int(stat["count"]) + 1
            stat["years"].add(year)

    return stats


def audit_interest_file(path: Path) -> dict[str, object]:
    stat: dict[str, object] = {
        "name": "Interest proxy series",
        "min_year": None,
        "max_year": None,
        "count": 0,
        "years": set(),
    }

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            year = int(float(row["Year"]))
            stat["min_year"] = year if stat["min_year"] is None or year < stat["min_year"] else stat["min_year"]
            stat["max_year"] = year if stat["max_year"] is None or year > stat["max_year"] else stat["max_year"]
            stat["count"] = int(stat["count"]) + 1
            stat["years"].add(year)

    return stat


def audit_alt_cpi(path: Path) -> list[int]:
    """Return the 2007-2015 years that lack a usable AltAvg in the intervention override file."""
    if not path.exists():
        return list(ALT_CPI_YEARS)

    present: dict[int, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                present[int(float(row["Year"]))] = (row.get("AltAvg") or "").strip()
            except (TypeError, ValueError):
                continue

    return [year for year in ALT_CPI_YEARS if not present.get(year)]


def audit_parallel_fx(path: Path, target_year: int) -> list[int]:
    """Return the cepo years (<= target_year) lacking a usable free-market rate override."""
    if not path.exists():
        return [year for year in CEPO_FX_YEARS if year <= target_year]

    present: dict[int, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                present[int(float(row["Year"]))] = (row.get("ParallelARS") or "").strip()
            except (TypeError, ValueError):
                continue

    return [year for year in CEPO_FX_YEARS if year <= target_year and not present.get(year)]


def audit_fpi_fiscal(path: Path, target_year: int) -> list[dict[str, object]]:
    """Validate the committed FPI dataset: corrections applied, no holes.

    This is the check that catches the silent-cepo-skip failure mode: if the official-FX raw
    data is missing when the FPI CSV is regenerated, Cepo_Factor quietly stays 1.0 and the
    debt-stock components revert to the uncorrected official series.
    """
    problems: list[dict[str, object]] = []
    if not path.exists():
        return [{"series": "fpi", "name": "FPI fiscal dataset missing", "reason": str(path)}]

    rows: dict[int, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                rows[int(float(row["Year"]))] = row
            except (TypeError, ValueError):
                continue

    for year in range(1853, target_year + 1):
        row = rows.get(year)
        if row is None:
            problems.append({"series": "fpi", "name": f"FPI row missing for {year}",
                             "reason": "no row in FPI fiscal CSV"})
            continue
        missing = [col for col in FPI_COLUMNS if not (row.get(col) or "").strip()]
        if missing:
            problems.append({"series": "fpi", "name": f"FPI components missing for {year}",
                             "reason": "empty columns: " + ", ".join(missing)})

    for year in CEPO_FX_YEARS:
        if year > target_year:
            continue
        row = rows.get(year)
        factor = float(row["Cepo_Factor"]) if row and (row.get("Cepo_Factor") or "").strip() else None
        if factor is None or factor <= 1.0:
            problems.append({
                "series": "fpi",
                "name": f"Cepo correction not applied for {year}",
                "reason": f"Cepo_Factor is {factor!r}; expected > 1.0 on exchange-control years "
                          "(regenerate with generate_fiscal_fpi-fiscal.py after the WB downloads)",
            })

    for year in BCRA_QF_YEARS:
        if year > target_year:
            continue
        row = rows.get(year)
        bcra = float(row["BCRA_QuasiFiscal_GDP"]) if row and (row.get("BCRA_QuasiFiscal_GDP") or "").strip() else None
        if not bcra or bcra <= 0:
            problems.append({
                "series": "fpi",
                "name": f"BCRA quasi-fiscal consolidation missing for {year}",
                "reason": f"BCRA_QuasiFiscal_GDP is {bcra!r}; expected > 0 for 2003-2023",
            })

    return problems


# First administration-year the notebook ranks (Illia, 1964); 1963 is only the legacy baseline.
FIRST_COMPARISON_YEAR = 1964


def cmpi_uncomputable_years(
    indicator_stats: dict[str, dict[str, object]],
    interest_stat: dict[str, object],
    target_year: int,
) -> list[dict[str, object]]:
    """Return the comparison years whose CMPI cannot be computed without a NaN.

    This mirrors how the notebook builds each input, so it catches interior holes (e.g. the
    missing 2001 wholesale year) that endpoint min/max coverage checks would miss. A price
    component is considered available when the GDP deflator exists for the year, or a CPI/WPI
    level exists for the year and its predecessor; the NaN-robust mean only needs one of CPI/WPI.
    """
    deflator = indicator_stats["NY.GDP.DEFL.KD.ZG"]["years"]
    cpi_level = indicator_stats["FP.CPI.TOTL"]["years"]
    wpi_level = indicator_stats["FP.WPI.TOTL"]["years"]
    fx = indicator_stats["PA.NUS.ATLS"]["years"]
    growth = indicator_stats["NY.GDP.PCAP.KD.ZG"]["years"]
    interest = interest_stat["years"]

    problems: list[dict[str, object]] = []
    for year in range(FIRST_COMPARISON_YEAR, target_year + 1):
        cpi_ok = year in deflator or ({year, year - 1} <= cpi_level)
        wpi_ok = {year, year - 1} <= wpi_level
        missing = []
        if not (cpi_ok or wpi_ok):
            missing.append("price (CPI/WPI/deflator)")
        if not ({year, year - 1} <= fx):
            missing.append("devaluation (PA.NUS.ATLS)")
        if year not in growth:
            missing.append("growth (NY.GDP.PCAP.KD.ZG)")
        if year not in interest:
            missing.append("interest")
        if missing:
            problems.append({"year": year, "missing": missing})

    return problems


def main() -> int:
    args = parse_args()

    indicator_stats = audit_indicator_file(INDICATOR_FILE)
    interest_stat = audit_interest_file(INTEREST_FILE)

    report = {
        "target_year": args.target_year,
        "indicator_file": str(INDICATOR_FILE),
        "interest_file": str(INTEREST_FILE),
        "series": indicator_stats,
        "interest": interest_stat,
        "missing_or_incomplete": [],
    }

    required_for_current_method = [
        "FP.CPI.TOTL",
        "FP.WPI.TOTL",
        "PA.NUS.ATLS",
        "NY.GDP.PCAP.KD.ZG",
    ]

    for code in required_for_current_method:
        stat = indicator_stats[code]
        if stat["count"] == 0:
            report["missing_or_incomplete"].append(
                {
                    "series": code,
                    "name": stat["name"],
                    "reason": "no published observations in local dataset",
                }
            )
            continue

        if int(stat["max_year"]) < args.target_year:
            report["missing_or_incomplete"].append(
                {
                    "series": code,
                    "name": stat["name"],
                    "reason": f"latest local observation is {stat['max_year']}",
                }
            )

    if interest_stat["count"] == 0:
        report["missing_or_incomplete"].append(
            {
                "series": "interest",
                "name": interest_stat["name"],
                "reason": "no rows found in local interest dataset",
            }
        )
    elif int(interest_stat["max_year"]) < args.target_year:
        report["missing_or_incomplete"].append(
            {
                "series": "interest",
                "name": interest_stat["name"],
                "reason": f"latest local observation is {interest_stat['max_year']}",
            }
        )

    common_max_year_candidates = [
        stat["max_year"]
        for code, stat in indicator_stats.items()
        if code in {"FP.CPI.TOTL", "FP.WPI.TOTL", "PA.NUS.ATLS", "NY.GDP.PCAP.KD.ZG"}
        and stat["max_year"] is not None
    ]
    if interest_stat["max_year"] is not None:
        common_max_year_candidates.append(interest_stat["max_year"])
    report["common_max_year_across_required_inputs"] = (
        min(common_max_year_candidates) if common_max_year_candidates else None
    )

    # Interior-gap check: every comparison year must yield a NaN-free CMPI, not just have its
    # endpoints covered. This is what actually guarantees the notebook runs clean end to end.
    uncomputable = cmpi_uncomputable_years(indicator_stats, interest_stat, args.target_year)
    report["cmpi_uncomputable_years"] = uncomputable
    for problem in uncomputable:
        report["missing_or_incomplete"].append(
            {
                "series": "cmpi",
                "name": f"CMPI not computable for {problem['year']}",
                "reason": "missing inputs: " + ", ".join(problem["missing"]),
            }
        )

    # The 2007-2015 INDEC-intervention override must cover every year in its window.
    alt_cpi_missing = audit_alt_cpi(ALT_CPI_FILE)
    report["alt_cpi_file"] = str(ALT_CPI_FILE)
    report["alt_cpi_missing_years"] = alt_cpi_missing
    for year in alt_cpi_missing:
        report["missing_or_incomplete"].append(
            {
                "series": "alt_cpi",
                "name": f"Alternative inflation override missing {year}",
                "reason": f"no usable AltAvg for {year} in {ALT_CPI_FILE}",
            }
        )

    # The cepo free-market exchange-rate override must cover every cepo year up to the target.
    parallel_fx_missing = audit_parallel_fx(PARALLEL_FX_FILE, args.target_year)
    report["parallel_fx_file"] = str(PARALLEL_FX_FILE)
    report["parallel_fx_missing_years"] = parallel_fx_missing
    for year in parallel_fx_missing:
        report["missing_or_incomplete"].append(
            {
                "series": "parallel_fx",
                "name": f"Cepo free-market FX override missing {year}",
                "reason": f"no usable ParallelARS for {year} in {PARALLEL_FX_FILE}",
            }
        )

    # The committed FPI dataset must carry the section-6.0 corrections and have no holes.
    fpi_problems = audit_fpi_fiscal(FPI_FISCAL_FILE, args.target_year)
    report["fpi_fiscal_file"] = str(FPI_FISCAL_FILE)
    report["missing_or_incomplete"].extend(fpi_problems)

    # Sets are not JSON-serialisable; drop them before printing the report.
    for stat in indicator_stats.values():
        stat.pop("years", None)
    interest_stat.pop("years", None)

    print(json.dumps(report, indent=2))

    return 0 if not report["missing_or_incomplete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
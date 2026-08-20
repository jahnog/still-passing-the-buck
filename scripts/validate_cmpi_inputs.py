#!/usr/bin/env python3

import argparse
import csv
import gzip
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.pipeline_config import target_year as default_target_year
from scripts.wb_raw import wb_series_from_raw

INDICATOR_FILE = paths.INDICATORS_GZ
INTEREST_FILE = paths.INTEREST_CSV
ALT_CPI_FILE = paths.ALT_CPI_CSV
QUALITY_FLAGS_FILE = paths.DATA_QUALITY_FLAGS_CSV
# Every CMPI/FPI input variable must carry a quality grade for every ranked year; the BCRA
# quasi-fiscal series is only required from the Lebac era onward.
FLAG_VARIABLES = (
    "Inflation",
    "Devaluation",
    "Interest",
    "Growth",
    "Debt_GDP",
    "Debt_Exports",
    "Result_Revenue",
    "Result_DebtServ",
)
FLAG_FIRST_YEAR = 1853
BCRA_FLAG_VARIABLE = "BCRA_QuasiFiscal"
BCRA_FLAG_FIRST_YEAR = 2001
# Grade-D (provisional) cells that can be superseded once the World Bank publishes the year.
PROVISIONAL_SUPERSEDE_CODES = {
    "Growth": "NY.GDP.PCAP.KD.ZG",
    "Debt_GDP": "NY.GDP.MKTP.CD",
    "Debt_Exports": "BX.GSR.TOTL.CD",
}
ALT_CPI_YEARS = range(2007, 2016)  # 2007-2015 INDEC-manipulation override window
PARALLEL_FX_FILE = paths.PARALLEL_CEPO_CSV
FPI_FISCAL_FILE = paths.FPI_FISCAL_CSV
# Cepo years whose devaluation must use the free-market rate (2012-2015 and 2019 onward); the
# 2016-2018 float is intentionally excluded (the brecha was < 1%, so the official rate is fine).
CEPO_FX_YEARS = (2012, 2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025)
# Years the BCRA carried remunerated quasi-fiscal debt that must be consolidated into the FPI
# debt stock: Lebac creation in 2002 through the post-LeFi residual in 2025. The 2024-25 stock
# is economically negligible (~0.03% of GDP) but measured, not zero.
BCRA_QF_YEARS = range(2002, 2026)
FPI_COLUMNS = ("Debt_GDP", "Debt_Exports", "Result_Revenue", "Result_DebtServ")
FPI_CORRECTED_COLUMNS = (
    "Debt_GDP_corrected",
    "Debt_Exports_corrected",
    "Result_Revenue_corrected",
    "Result_DebtServ_corrected",
)
FPI_PAPER_EXTENSION_COLUMNS = (
    "Debt_GDP_paper_extension",
    "Debt_Exports_paper_extension",
    "Result_Revenue_paper_extension",
    "Result_DebtServ_paper_extension",
)
# Sensitivity memo columns (section 6.0 C): present for every year, equal to the baseline
# outside their adjustment windows. Their absence means the FPI CSV predates the
# default-integrity machinery and must be regenerated.
FPI_MEMO_COLUMNS = (
    "Debt_GDP_holdouts",
    "Result_DebtServ_capitalized_interest",
    "Result_Revenue_structural",
    "Result_DebtServ_structural",
    "Debt_GDP_arrears",
    # Exports-side counterparts, so a section-6.0 variant can isolate a correction on both
    # debt ratios rather than only Debt/GDP.
    "Debt_Exports_holdouts",
    "Debt_Exports_arrears",
)
FPI_RATIO_GAP_YEARS = (1861, 1862, 1863)
FPI_RATIO_GAP_ENDPOINTS = (1860, 1864)
FPI_RATIO_GAP_COLUMNS = (
    "Result_Revenue",
    "Result_DebtServ",
)
FPI_RATIO_GAP_DERIVED_COLUMNS = (
    "Result_Revenue_paper_extension",
    "Result_DebtServ_paper_extension",
    "Result_Revenue_corrected",
    "Result_DebtServ_corrected",
    "Result_DebtServ_capitalized_interest",
    "Result_Revenue_structural",
    "Result_DebtServ_structural",
)
COMPLETE_YEAR = 2025
REQUIRED_2025_WB_CODES = (
    "NY.GDP.PCAP.KD.ZG",
    "NY.GDP.MKTP.CD",
    "BX.GSR.TOTL.CD",
    "NY.GDP.MKTP.KD",
    "NE.EXP.GNFS.CD",
    "NE.EXP.GNFS.KD",
)
REQUIRED_2025_FPI_FIELDS = (
    "Debt_Stock_USD",
    "GDP_CD_USD",
    "Exports_CD_USD",
    "CurrentRevenue",
    "PrimaryResult",
    "FinancialResult",
    "InterestMeasure",
    "Debt_GDP_corrected",
    "Debt_Exports_corrected",
    "Result_Revenue_corrected",
    "Result_DebtServ_corrected",
    "BCRA_QuasiFiscal_GDP",
    "Cepo_Factor",
)

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
    parser.add_argument("--target-year", type=int, default=default_target_year())
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

    header = next(iter(rows.values()), {})
    fpi_missing = [
        col
        for col in (*FPI_CORRECTED_COLUMNS, *FPI_PAPER_EXTENSION_COLUMNS, *FPI_MEMO_COLUMNS)
        if col not in header
    ]
    if fpi_missing:
        problems.append({"series": "fpi",
                         "name": "FPI corrected columns missing",
                         "reason": "regenerate with generate_fiscal_fpi-fiscal.py: "
                                   + ", ".join(fpi_missing)})

    required_value_columns = (
        *FPI_COLUMNS,
        *FPI_CORRECTED_COLUMNS,
        *FPI_PAPER_EXTENSION_COLUMNS,
        *FPI_MEMO_COLUMNS,
    )
    for year in range(1853, target_year + 1):
        row = rows.get(year)
        if row is None:
            problems.append({"series": "fpi", "name": f"FPI row missing for {year}",
                             "reason": "no row in FPI fiscal CSV"})
            continue
        missing = [
            col
            for col in required_value_columns
            if col in header and not (row.get(col) or "").strip()
        ]
        if missing:
            problems.append({"series": "fpi", "name": f"FPI components missing for {year}",
                             "reason": "empty columns: " + ", ".join(missing)})

    start_year, end_year = FPI_RATIO_GAP_ENDPOINTS
    start_row = rows.get(start_year)
    end_row = rows.get(end_year)
    if start_row is None or end_row is None:
        problems.append({
            "series": "fpi",
            "name": "FPI interpolation endpoints missing",
            "reason": f"need observed {start_year} and {end_year} rows to check 1861-63 fills",
        })
    else:
        span = end_year - start_year
        for col in FPI_RATIO_GAP_COLUMNS:
            try:
                start = float(start_row[col])
                end = float(end_row[col])
            except (KeyError, TypeError, ValueError):
                problems.append({
                    "series": "fpi",
                    "name": f"FPI interpolation endpoints missing for {col}",
                    "reason": f"{start_year}/{end_year} {col} is empty or non-numeric",
                })
                continue
            for year in FPI_RATIO_GAP_YEARS:
                row = rows.get(year)
                if row is None:
                    continue
                expected = start + ((year - start_year) / span) * (end - start)
                try:
                    actual = float(row[col])
                except (KeyError, TypeError, ValueError):
                    continue
                if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
                    problems.append({
                        "series": "fpi",
                        "name": f"FPI historical gap interpolation mismatch for {year} {col}",
                        "reason": (
                            f"expected arithmetic fill {expected!r} between {start_year} and "
                            f"{end_year}; got {actual!r}"
                        ),
                    })
                for derived in FPI_RATIO_GAP_DERIVED_COLUMNS:
                    if not derived.startswith(col) or derived not in header:
                        continue
                    derived_value = (row.get(derived) or "").strip()
                    if not derived_value:
                        continue
                    if not math.isclose(float(derived_value), actual, rel_tol=0.0, abs_tol=1e-12):
                        problems.append({
                            "series": "fpi",
                            "name": f"FPI derived {derived} diverges from interpolated {col} in {year}",
                            "reason": f"{derived}={derived_value!r}, {col}={actual!r}",
                        })

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
                "reason": f"BCRA_QuasiFiscal_GDP is {bcra!r}; expected > 0 for 2002-2025",
            })

    return problems


def audit_quality_flags(
    path: Path, target_year: int
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Audit the data-quality flag file.

    Returns (problems, provisional): `problems` are fatal coverage holes (every ranked year of
    every CMPI/FPI variable must carry a grade); `provisional` lists the grade-D cells so the
    caller can check whether an official source has since published them.
    """
    if not path.exists():
        return (
            [{"series": "quality_flags", "name": "Quality-flag file missing", "reason": str(path)}],
            [],
        )

    coverage: dict[str, set[int]] = {var: set() for var in FLAG_VARIABLES + (BCRA_FLAG_VARIABLE,)}
    provisional: list[dict[str, object]] = []
    problems: list[dict[str, object]] = []

    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            var = (row.get("Variable") or "").strip()
            if var not in coverage:
                problems.append({"series": "quality_flags", "name": f"Unknown variable {var!r}",
                                 "reason": "not one of the CMPI/FPI input variables"})
                continue
            grade = (row.get("Grade") or "").strip()
            note = (row.get("Note") or "").strip()
            try:
                y0, y1 = int(row["YearStart"]), int(row["YearEnd"])
            except (KeyError, TypeError, ValueError):
                problems.append({"series": "quality_flags", "name": f"Bad year range for {var}",
                                 "reason": repr(row)})
                continue
            if grade not in {"A", "B", "C", "D"}:
                problems.append({"series": "quality_flags", "name": f"Bad grade {grade!r} for {var}",
                                 "reason": f"rows {y0}-{y1}"})
                continue
            if not note:
                problems.append({"series": "quality_flags", "name": f"Empty note for {var}",
                                 "reason": f"rows {y0}-{y1}: every grade needs a sourced note"})
            overlap = coverage[var].intersection(range(y0, y1 + 1))
            if overlap:
                problems.append({"series": "quality_flags", "name": f"Overlapping ranges for {var}",
                                 "reason": f"years {min(overlap)}-{max(overlap)} graded twice"})
            coverage[var].update(range(y0, y1 + 1))
            if grade == "D":
                provisional.append({"variable": var, "year_start": y0, "year_end": y1, "note": note})

    for var in FLAG_VARIABLES:
        missing = [y for y in range(FLAG_FIRST_YEAR, target_year + 1) if y not in coverage[var]]
        if missing:
            problems.append({"series": "quality_flags", "name": f"Ungraded years for {var}",
                             "reason": f"{missing[0]}-{missing[-1]} ({len(missing)} years)"})
    bcra_missing = [
        y for y in range(BCRA_FLAG_FIRST_YEAR, target_year + 1) if y not in coverage[BCRA_FLAG_VARIABLE]
    ]
    if bcra_missing:
        problems.append({"series": "quality_flags", "name": f"Ungraded years for {BCRA_FLAG_VARIABLE}",
                         "reason": f"{bcra_missing[0]}-{bcra_missing[-1]}"})

    return problems, provisional


def provisional_supersession_warnings(provisional: list[dict[str, object]]) -> list[str]:
    """Warn when an official source has published a year still graded D (provisional)."""
    warnings: list[str] = []
    for entry in provisional:
        code = PROVISIONAL_SUPERSEDE_CODES.get(str(entry["variable"]))
        if not code:
            continue
        published = wb_series_from_raw(code)
        years = [
            y for y in range(int(entry["year_start"]), int(entry["year_end"]) + 1) if y in published
        ]
        if years:
            warnings.append(
                f"{entry['variable']} {years[0]}-{years[-1]} is graded D (provisional) but the World "
                f"Bank raw snapshot now carries {code} for those years; rerun the download/generate "
                f"scripts and upgrade the flag in {QUALITY_FLAGS_FILE.name}."
            )
    return warnings


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


def _csv_year_row(path: Path, year: int) -> dict[str, str] | None:
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                row_year = int(float(row["Year"]))
            except (KeyError, TypeError, ValueError):
                continue
            if row_year == year:
                return row
    return None


def _required_numeric_fields(
    row: dict[str, str] | None,
    fields: tuple[str, ...],
    *,
    source: str,
) -> tuple[dict[str, float], list[str]]:
    values: dict[str, float] = {}
    missing: list[str] = []
    for field in fields:
        raw = None if row is None else row.get(field)
        try:
            value = float(raw) if raw is not None and str(raw).strip() else math.nan
        except (TypeError, ValueError):
            value = math.nan
        if not math.isfinite(value):
            missing.append(f"{source}:{field}")
        else:
            values[field] = value
    return values, missing


def audit_complete_2025_inputs() -> dict[str, object]:
    """Return a machine-readable proof that every 2025 scoring input is present."""
    missing: list[str] = []
    values: dict[str, object] = {}

    wb_values: dict[str, float] = {}
    for code in REQUIRED_2025_WB_CODES:
        value = wb_series_from_raw(code).get(COMPLETE_YEAR)
        if value is None or not math.isfinite(float(value)):
            missing.append(f"World Bank:{code}")
        else:
            wb_values[code] = float(value)
    values["world_bank"] = wb_values

    component_specs = (
        (
            paths.PROCESSED
            / "inflation"
            / "converted_inflation_cpi-wpi-blend_1944-01_2025-12.csv",
            ("Blend_log", "Blend_pct"),
            "inflation",
        ),
        (paths.DEC_DEC_MODERN_CSV, ("DecRate", "DevaluationLog"), "devaluation"),
        (paths.INTEREST_CSV, ("Interest",), "embig"),
        (paths.US_REAL_YIELD_CSV, ("USRealYield10Y",), "us_real_yield"),
        (paths.FPI_FISCAL_CSV, REQUIRED_2025_FPI_FIELDS, "fpi"),
        (
            paths.PROCESSED
            / "fiscal"
            / "converted_fiscal_denominator-neutral_1960-01_2025-12.csv",
            (
                "GDP_Deflator_USD",
                "Exports_Deflator_USD",
                "GDP_CD_USD",
                "GDP_KD_USD",
                "Exports_CD_USD",
                "Exports_KD_USD",
            ),
            "denominator_neutral",
        ),
        (
            paths.OFFICIAL_CAPITALIZED_INTEREST_CSV,
            ("CashInterest_ARS_M", "CapitalizedInterest_ARS_M", "NominalGDP_ARS_M"),
            "capitalized_interest",
        ),
    )
    for path, fields, label in component_specs:
        component_values, component_missing = _required_numeric_fields(
            _csv_year_row(path, COMPLETE_YEAR),
            fields,
            source=label,
        )
        values[label] = component_values
        missing.extend(component_missing)

    return {
        "year": COMPLETE_YEAR,
        "status": "complete" if not missing else "incomplete",
        "missing": missing,
        "values": values,
    }


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

    # The 2007-2015 INDEC-manipulation override must cover every year in its window.
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

    # The committed FPI dataset must carry the section-6.0 corrections and have no
    # unexplained holes. The two source fiscal-result blanks in 1861-63 are arithmetically
    # interpolated between 1860 and 1864 so every component has 173 complete rows.
    fpi_problems = audit_fpi_fiscal(FPI_FISCAL_FILE, args.target_year)
    report["fpi_fiscal_file"] = str(FPI_FISCAL_FILE)
    report["missing_or_incomplete"].extend(fpi_problems)

    # Every ranked year of every input variable must carry a data-quality grade, and grade-D
    # (provisional) cells are warned about once an official source has published the year.
    flag_problems, provisional = audit_quality_flags(QUALITY_FLAGS_FILE, args.target_year)
    report["quality_flags_file"] = str(QUALITY_FLAGS_FILE)
    report["provisional_cells"] = provisional
    report["missing_or_incomplete"].extend(flag_problems)
    report["warnings"] = provisional_supersession_warnings(provisional)

    if args.target_year >= COMPLETE_YEAR:
        complete_2025 = audit_complete_2025_inputs()
        report["complete_2025"] = complete_2025
        if complete_2025["missing"]:
            report["missing_or_incomplete"].append(
                {
                    "series": "complete_2025",
                    "name": "Published annual 2025 scoring inputs",
                    "reason": "missing inputs: " + ", ".join(complete_2025["missing"]),
                }
            )

    # Sets are not JSON-serialisable; drop them before printing the report.
    for stat in indicator_stats.values():
        stat.pop("years", None)
    interest_stat.pop("years", None)

    print(json.dumps(report, indent=2))

    return 0 if not report["missing_or_incomplete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

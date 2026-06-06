#!/usr/bin/env python3

import csv
import gzip
import io
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen


COUNTRY_CODE = "ARG"
COUNTRY_NAME = "Argentina"
WIDE_SOURCE_PATH = Path("WDIData2.csv")
LONG_FORM_PATH = Path("Indicators.csv")
LONG_FORM_GZIP_PATH = Path("Indicators.csv.gz")

INDEC_IPC_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv"
INDEC_SIPM_1956_1995_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/sipm-serie56-95.xls"
INDEC_SIPM_1996_ONWARD_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/sipm-dde1996.xls"
INDEC_SIPM_REFERENCE_2015_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/series_sipm_dic2015.xls"
BCRA_A3500_URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls"
# INDEC 2022-census national population projections (2022-2040), mid-year total country,
# semicolon-delimited CSV with columns Edad;Sexo;Poblacion;Fecha.
INDEC_POP_PROJECTIONS_URL = (
    "https://www.indec.gob.ar/ftp/cuadros/poblacion/proyecciones_nacionales_2022_2040_base.csv"
)

# These are the CMPI-related World Bank series we need to keep fresh, even if the
# bulk export lags or omits them locally.
API_SUPPLEMENT_CODES = {
    "FP.CPI.TOTL": "Consumer price index (2010 = 100)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "NY.GDP.DEFL.KD.ZG": "Inflation, GDP deflator (annual %)",
    "NY.GDP.PCAP.KD.ZG": "GDP per capita growth (annual %)",
    "PA.NUS.ATLS": "Official exchange rate (LCU per US$, period average)",
}

# Official INDEC annual real GDP (PIB) growth, in percent, for years the World Bank API has
# not yet published. Sourced from the INDEC "Informe de avance del nivel de actividad" press
# releases. The notebook needs GDP *per capita* growth, so build_indec_growth_rows() converts
# these totals using official INDEC mid-year population (INDEC_POP_PROJECTIONS_URL).
#   2025 = +4.4%: Informe de avance del nivel de actividad, 4o trimestre de 2025
#   (published 2026-03-20, https://www.indec.gob.ar/uploads/informesdeprensa/pib_03_26D14C2E1ADC.pdf)
INDEC_OFFICIAL_GDP_GROWTH = {
    2025: 4.4,
}


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "StillPassingTheBuck/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def require_xlrd():
    try:
        import xlrd  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "xlrd is required to parse the official INDEC .xls workbooks. "
            "Install it or run this script with .venv/bin/python."
        ) from exc

    return xlrd


def format_number(value: float) -> str:
    formatted = f"{value:.12f}".rstrip("0").rstrip(".")
    return formatted or "0"


def build_indicator_row(indicator_code: str, indicator_name: str, year: int, value: float) -> dict[str, str]:
    return {
        "CountryName": COUNTRY_NAME,
        "CountryCode": COUNTRY_CODE,
        "IndicatorName": indicator_name,
        "IndicatorCode": indicator_code,
        "Year": str(year),
        "Value": format_number(value),
    }


def parse_year_label(value: object) -> int | None:
    if isinstance(value, float) and value.is_integer() and 1000 <= int(value) <= 9999:
        return int(value)

    text = str(value).strip()
    if len(text) == 4 and text.isdigit():
        return int(text)

    return None


def upsert_indicator_rows(
    rows: dict[tuple[str, int], dict[str, str]],
    series_rows: list[dict[str, str]],
    *,
    replace_existing: bool = False,
) -> None:
    if replace_existing:
        indicator_codes = {row["IndicatorCode"] for row in series_rows}
        for key in [existing_key for existing_key in rows if existing_key[0] in indicator_codes]:
            del rows[key]

    for series_row in series_rows:
        key = (series_row["IndicatorCode"], int(series_row["Year"]))
        rows[key] = series_row


def annualize_monthly_index(monthly_values: dict[int, list[float]]) -> tuple[dict[int, float], set[int]]:
    complete_years = {year for year, values in monthly_values.items() if len(values) == 12}
    if not monthly_values:
        return {}, complete_years

    first_year = min(monthly_values)
    annual_values: dict[int, float] = {}
    for year in sorted(monthly_values):
        values = monthly_values[year]
        if year == first_year or year in complete_years:
            annual_values[year] = sum(values) / len(values)

    return annual_values, complete_years


def find_sheet_row(sheet, code: str) -> int:
    for row_index in range(sheet.nrows):
        if str(sheet.cell_value(row_index, 0)).strip() == code:
            return row_index

    raise RuntimeError(f"Could not find row {code!r} in {sheet.name!r}.")


def build_indec_ipc_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    payload = fetch_bytes(INDEC_IPC_URL).decode("latin-1")
    reader = csv.DictReader(io.StringIO(payload), delimiter=";")

    monthly_values: dict[int, list[float]] = defaultdict(list)
    for raw_row in reader:
        if raw_row.get("Codigo") != "0" or raw_row.get("Region") != "Nacional":
            continue

        period = (raw_row.get("Periodo") or "").strip()
        value = (raw_row.get("Indice_IPC") or "").strip()
        if len(period) != 6 or not period.isdigit() or value in {"", "NA"}:
            continue

        monthly_values[int(period[:4])].append(float(value.replace(",", ".")))

    annual_index, complete_years = annualize_monthly_index(monthly_values)
    level_rows = [
        build_indicator_row(
            "FP.CPI.TOTL",
            "Consumer price index (INDEC IPC Nacional, Dec 2016 = 100)",
            year,
            value,
        )
        for year, value in sorted(annual_index.items())
    ]

    growth_rows: list[dict[str, str]] = []
    previous_year: int | None = None
    for year in sorted(annual_index):
        if previous_year is None:
            previous_year = year
            continue

        if year not in complete_years or previous_year not in complete_years:
            previous_year = year
            continue

        current_value = annual_index[year]
        prior_value = annual_index[previous_year]
        growth_rows.append(
            build_indicator_row(
                "FP.CPI.TOTL.ZG",
                "Inflation, consumer prices (annual %, derived from INDEC IPC annual average)",
                year,
                ((current_value / prior_value) - 1) * 100,
            )
        )
        previous_year = year

    return level_rows, growth_rows


def parse_sipm_1956_1995_ipim() -> dict[int, float]:
    xlrd = require_xlrd()
    workbook = xlrd.open_workbook(file_contents=fetch_bytes(INDEC_SIPM_1956_1995_URL))
    sheet = workbook.sheet_by_index(0)

    annual_values: dict[int, float] = {}
    for row_index in range(8, sheet.nrows):
        year = parse_year_label(sheet.cell_value(row_index, 0))
        value = sheet.cell_value(row_index, 1)
        if year is None or not isinstance(value, (int, float)):
            continue

        annual_values[year] = float(value)

    return annual_values


def parse_sipm_1996_onward_ipim(*, include_partial_years: bool = False) -> dict[int, float]:
    xlrd = require_xlrd()
    workbook = xlrd.open_workbook(file_contents=fetch_bytes(INDEC_SIPM_1996_ONWARD_URL))
    sheet = workbook.sheet_by_index(0)

    annual_values: dict[int, float] = {}
    current_year: int | None = None
    monthly_values: list[float] = []

    for row_index in range(8, sheet.nrows):
        label = sheet.cell_value(row_index, 0)
        year = parse_year_label(label)
        if year is not None:
            if current_year is not None and (len(monthly_values) == 12 or (include_partial_years and monthly_values)):
                annual_values[current_year] = sum(monthly_values) / len(monthly_values)
            current_year = year
            monthly_values = []
            continue

        value = sheet.cell_value(row_index, 1)
        if current_year is None or not isinstance(value, (int, float)) or not str(label).strip():
            continue

        monthly_values.append(float(value))

    if current_year is not None and (len(monthly_values) == 12 or (include_partial_years and monthly_values)):
        annual_values[current_year] = sum(monthly_values) / len(monthly_values)

    return annual_values


def parse_sipm_reference_2015_ipim() -> dict[int, float]:
    xlrd = require_xlrd()
    workbook = xlrd.open_workbook(file_contents=fetch_bytes(INDEC_SIPM_REFERENCE_2015_URL))
    sheet = workbook.sheet_by_name("IPIM")
    row_index = find_sheet_row(sheet, "NG")

    monthly_values: dict[int, list[float]] = defaultdict(list)
    current_year: int | None = None
    for column_index in range(2, sheet.ncols):
        year_header = parse_year_label(sheet.cell_value(3, column_index))
        if year_header is not None:
            current_year = year_header

        month_label = str(sheet.cell_value(4, column_index)).strip()
        value = sheet.cell_value(row_index, column_index)
        if current_year is None or not month_label or not isinstance(value, (int, float)):
            continue

        monthly_values[current_year].append(float(value))

    annual_values, _ = annualize_monthly_index(monthly_values)
    return annual_values


def build_indec_wpi_rows() -> list[dict[str, str]]:
    annual_index = parse_sipm_1956_1995_ipim()
    annual_index.update(parse_sipm_1996_onward_ipim())

    current_reference_values = parse_sipm_reference_2015_ipim()
    historical_anchor_values = parse_sipm_1996_onward_ipim(include_partial_years=True)

    anchor_year = 2015
    if anchor_year not in historical_anchor_values or anchor_year not in current_reference_values:
        raise RuntimeError(
            "The INDEC IPIM fallback is missing the 2015 anchor required to chain the current reference-period series."
        )

    bridge_factor = historical_anchor_values[anchor_year] / current_reference_values[anchor_year]
    annual_index.update(
        {
            year: value * bridge_factor
            for year, value in current_reference_values.items()
        }
    )

    # NOTE: the INDEC IPIM workbooks only expose years with twelve complete months, so the 2001
    # crisis year is dropped, leaving an interior hole in the wholesale level series. We do NOT
    # interpolate it: a log-linear fill between 2000 and 2002 would inject a spurious ~+31% into
    # 2001 (a mildly deflationary year) and understate the 2002 devaluation jump. The notebook
    # instead falls back to the available consumer-price change for 2001 (see the NaN-robust mean
    # in the inflation cell), which is closer to the truth than interpolating the wholesale gap.
    base_year = 2010
    if base_year not in annual_index:
        raise RuntimeError(f"The INDEC IPIM fallback is missing base year {base_year}.")

    base_value = annual_index[base_year]
    return [
        build_indicator_row(
            "FP.WPI.TOTL",
            "Wholesale price index (INDEC IPIM, rebased to 2010 = 100)",
            year,
            (value / base_value) * 100,
        )
        for year, value in sorted(annual_index.items())
    ]


def build_bcra_exchange_rows() -> list[dict[str, str]]:
    xlrd = require_xlrd()
    workbook = xlrd.open_workbook(file_contents=fetch_bytes(BCRA_A3500_URL))
    sheet = workbook.sheet_by_name("Serie de TCNPM")

    monthly_values: dict[int, list[float]] = defaultdict(list)
    for row_index in range(3, sheet.nrows):
        date_value = sheet.cell_value(row_index, 1)
        exchange_value = sheet.cell_value(row_index, 2)
        if not isinstance(date_value, (int, float)) or not isinstance(exchange_value, (int, float)):
            continue

        year = xlrd.xldate.xldate_as_datetime(date_value, workbook.datemode).year
        monthly_values[year].append(float(exchange_value))

    annual_values, _ = annualize_monthly_index(monthly_values)
    return [
        build_indicator_row(
            "PA.NUS.ATLS",
            "Official exchange rate (BCRA TCNPM annual average, ARS per US$)",
            year,
            value,
        )
        for year, value in sorted(annual_values.items())
        if year >= 2020
    ]


def build_indec_population_totals() -> dict[int, float]:
    payload = fetch_bytes(INDEC_POP_PROJECTIONS_URL).decode("latin-1")
    reader = csv.DictReader(io.StringIO(payload), delimiter=";")

    totals: dict[int, float] = defaultdict(float)
    for raw_row in reader:
        year = parse_year_label((raw_row.get("Fecha") or "").strip())
        value = (raw_row.get("Poblacion") or "").strip()
        if year is None or value in {"", "NA"}:
            continue

        totals[year] += float(value.replace(",", "."))

    return dict(totals)


def build_indec_growth_rows() -> list[dict[str, str]]:
    if not INDEC_OFFICIAL_GDP_GROWTH:
        return []

    population_totals = build_indec_population_totals()

    rows: list[dict[str, str]] = []
    for year, gdp_growth_pct in sorted(INDEC_OFFICIAL_GDP_GROWTH.items()):
        current_pop = population_totals.get(year)
        prior_pop = population_totals.get(year - 1)
        if not current_pop or not prior_pop:
            raise RuntimeError(
                "INDEC population projections are missing the totals needed to convert official "
                f"{year} GDP growth into a per-capita rate (need {year} and {year - 1})."
            )

        population_growth = current_pop / prior_pop - 1
        per_capita_growth = ((1 + gdp_growth_pct / 100) / (1 + population_growth) - 1) * 100
        rows.append(
            build_indicator_row(
                "NY.GDP.PCAP.KD.ZG",
                "GDP per capita growth (annual %, INDEC PIB minus INDEC population growth fallback)",
                year,
                per_capita_growth,
            )
        )

    return rows


def build_rows_from_wide_export(source_path: Path) -> dict[tuple[str, int], dict[str, str]]:
    rows: dict[tuple[str, int], dict[str, str]] = {}

    with source_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        year_columns = [column for column in reader.fieldnames or [] if "[YR" in column]

        for raw_row in reader:
            if raw_row.get("Country Code") != COUNTRY_CODE:
                continue

            for year_column in year_columns:
                value = raw_row.get(year_column, "")
                if value in ("", ".."):
                    continue

                year = int(year_column.split(" ", 1)[0])
                key = (raw_row["Series Code"], year)
                rows[key] = {
                    "CountryName": raw_row["Country Name"],
                    "CountryCode": raw_row["Country Code"],
                    "IndicatorName": raw_row["Series Name"],
                    "IndicatorCode": raw_row["Series Code"],
                    "Year": str(year),
                    "Value": value,
                }

    return rows


def fetch_world_bank_series(indicator_code: str) -> list[dict[str, str]]:
    url = (
        f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}/indicator/"
        f"{indicator_code}?format=json&per_page=200"
    )

    with urlopen(url, timeout=60) as response:
        payload = json.load(response)

    series_rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    collected: list[dict[str, str]] = []

    for series_row in series_rows:
        value = series_row.get("value")
        if value is None:
            continue

        collected.append(
            {
                "CountryName": COUNTRY_NAME,
                "CountryCode": COUNTRY_CODE,
                "IndicatorName": series_row["indicator"]["value"],
                "IndicatorCode": series_row["indicator"]["id"],
                "Year": series_row["date"],
                "Value": str(value),
            }
        )

    return collected


def write_long_form(rows: dict[tuple[str, int], dict[str, str]], output_path: Path) -> None:
    fieldnames = [
        "CountryName",
        "CountryCode",
        "IndicatorName",
        "IndicatorCode",
        "Year",
        "Value",
    ]

    ordered_rows = sorted(
        rows.values(),
        key=lambda row: (row["CountryName"], row["IndicatorCode"], int(row["Year"])),
    )

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered_rows)


def gzip_file(source_path: Path, target_path: Path) -> None:
    with source_path.open("rb") as source_handle:
        with gzip.open(target_path, "wb") as target_handle:
            shutil.copyfileobj(source_handle, target_handle)


def main() -> int:
    if not WIDE_SOURCE_PATH.exists():
        print(f"Missing source file: {WIDE_SOURCE_PATH}", file=sys.stderr)
        return 1

    try:
        rows = build_rows_from_wide_export(WIDE_SOURCE_PATH)

        for indicator_code in API_SUPPLEMENT_CODES:
            for series_row in fetch_world_bank_series(indicator_code):
                key = (series_row["IndicatorCode"], int(series_row["Year"]))
                rows[key] = series_row

        ipc_level_rows, ipc_growth_rows = build_indec_ipc_rows()
        upsert_indicator_rows(rows, ipc_level_rows, replace_existing=True)
        upsert_indicator_rows(rows, ipc_growth_rows, replace_existing=True)
        upsert_indicator_rows(rows, build_indec_wpi_rows(), replace_existing=True)
        upsert_indicator_rows(rows, build_bcra_exchange_rows())

        # Only fill GDP per-capita-growth years the World Bank API has not yet published, so a
        # later WB release of the same year transparently supersedes the INDEC fallback.
        growth_fallback_rows = [
            row
            for row in build_indec_growth_rows()
            if (row["IndicatorCode"], int(row["Year"])) not in rows
        ]
        upsert_indicator_rows(rows, growth_fallback_rows)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_long_form(rows, LONG_FORM_PATH)
    gzip_file(LONG_FORM_PATH, LONG_FORM_GZIP_PATH)

    print(f"Wrote {len(rows)} Argentina indicator rows to {LONG_FORM_PATH}")
    print(f"Compressed {LONG_FORM_GZIP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
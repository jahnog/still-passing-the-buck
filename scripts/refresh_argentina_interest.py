#!/usr/bin/env python3

import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


COUNTRY_NAME = "Argentina"
COUNTRY_CODE = "ARG"
INTEREST_PATH = Path("data/argentina/interest/wb-ids-arg.csv")

# BCRP (Banco Central de Reserva del Perú) redistributes J.P. Morgan's EMBIG. PD04710XD is the
# *daily EMBIG Argentina spread in basis points*. Annual averages of this series reproduce the
# legacy 2000-2019 values already committed in the file (e.g. 2002 ~= 5792 bps = 57.9%,
# 2019 ~= 1316 bps = 13.2%), so continuing it past 2019 keeps the whole 2000+ segment one
# consistent country-risk series in the same units the paper's interest variable uses.
#
# This replaces an earlier BCRA *nominal USD lending rate* stopgap (~5-9%), which was a different
# construct and scale from the 2000-2019 EMBI segment. Because lower interest scores as "better",
# that stopgap fabricated a country-risk "improvement" for 2020-2023 (when real riesgo país in
# fact rose to ~1500-2500 bps) and hid the 2024-2025 collapse (~1900 -> ~600 bps), badly
# flattering Fernández and penalising Milei. EMBIG fixes both.
#
# BCRP history: the EMBIG series (PD04710XD) starts from January 1998 in the BCRP database.
# Setting LEGACY_CUTOFF_YEAR = 1997 allows the script to replace the flat Menem II term
# averages (9.75%) for 1998-1999 with actual annual EMBIG values (1998 ≈ 5.98%, 1999 ≈ 7.20%).
BCRP_EMBIG_URL = (
    "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04710XD/json/"
    "{start}-01-01/{end}-12-31"
)
LEGACY_CUTOFF_YEAR = 1997  # years ≤ 1997 preserved from file; 1998+ fetched from BCRP
DECEMBER_TOKEN = "Dic"  # BCRP date labels look like "02.Dic.98"; used as a year-complete marker


def format_number(value: float) -> str:
    formatted = f"{value:.12f}".rstrip("0").rstrip(".")
    return formatted or "0"


def load_legacy_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"Missing interest file: {path}")

    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            year = int(float(row["Year"]))
            if year <= LEGACY_CUTOFF_YEAR:
                rows.append(
                    {
                        "CountryName": row["CountryName"],
                        "CountryCode": row["CountryCode"],
                        "Year": str(year),
                        "Interest": row["Interest"],
                    }
                )

    if not rows:
        raise RuntimeError(
            "Could not find the legacy 1958-1997 interest rows required to preserve the pre-EMBIG history."
        )

    return rows


def fetch_embig_payload() -> dict:
    url = BCRP_EMBIG_URL.format(start=LEGACY_CUTOFF_YEAR + 1, end=date.today().year)
    request = Request(url, headers={"User-Agent": "StillPassingTheBuck/1.0"})
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def build_embig_rows() -> list[dict[str, str]]:
    payload = fetch_embig_payload()

    spreads_bps: dict[int, list[float]] = defaultdict(list)
    months_present: dict[int, set[str]] = defaultdict(set)
    for period in payload.get("periods", []):
        parts = str(period.get("name", "")).split(".")
        if len(parts) != 3:
            continue

        _day, month_token, year_token = parts
        if not year_token.isdigit():
            continue

        two_digit_year = int(year_token)
        year = 2000 + two_digit_year if two_digit_year < 80 else 1900 + two_digit_year

        try:
            spread = float(period.get("values", [None])[0])
        except (TypeError, ValueError):
            continue

        spreads_bps[year].append(spread)
        months_present[year].add(month_token)

    rows: list[dict[str, str]] = []
    for year in sorted(spreads_bps):
        if year <= LEGACY_CUTOFF_YEAR:
            continue
        # Skip the still-running current year: no December observations yet.
        if DECEMBER_TOKEN not in months_present[year]:
            continue

        annual_percent = statistics.mean(spreads_bps[year]) / 100.0  # basis points -> percent
        rows.append(
            {
                "CountryName": COUNTRY_NAME,
                "CountryCode": COUNTRY_CODE,
                "Year": str(year),
                "Interest": format_number(annual_percent),
            }
        )

    if not rows:
        raise RuntimeError(
            "No complete EMBIG Argentina years (>=1998) were found in the BCRP PD04710XD series."
        )

    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["CountryName", "CountryCode", "Year", "Interest"]
    ordered_rows = sorted(rows, key=lambda row: int(row["Year"]))

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered_rows)


def main() -> int:
    try:
        rows = load_legacy_rows(INTEREST_PATH)
        rows.extend(build_embig_rows())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_rows(INTEREST_PATH, rows)
    print(f"Wrote {len(rows)} annual interest rows to {INTEREST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

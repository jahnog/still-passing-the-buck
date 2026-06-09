#!/usr/bin/env python3
"""Generate interest series from BCRP EMBIG raw JSON + legacy rows."""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import latest_raw

COUNTRY_NAME = "Argentina"
COUNTRY_CODE = "ARG"
LEGACY_CUTOFF_YEAR = 1997
DECEMBER_TOKEN = "Dic"
LEGACY_SOURCE = paths.INTEREST_CSV


def format_number(value: float) -> str:
    formatted = f"{value:.12f}".rstrip("0").rstrip(".")
    return formatted or "0"


def load_legacy_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise RuntimeError(f"Missing interest file for legacy rows: {path}")

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
            "Could not find legacy 1958-1997 interest rows required to preserve pre-EMBIG history."
        )
    return rows


def build_embig_rows(raw_path: Path) -> list[dict[str, str]]:
    payload = json.loads(raw_path.read_text(encoding="utf-8"))

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
        if DECEMBER_TOKEN not in months_present[year]:
            continue

        annual_percent = statistics.mean(spreads_bps[year]) / 100.0
        rows.append(
            {
                "CountryName": COUNTRY_NAME,
                "CountryCode": COUNTRY_CODE,
                "Year": str(year),
                "Interest": format_number(annual_percent),
            }
        )

    if not rows:
        raise RuntimeError("No complete EMBIG Argentina years (>=1998) in BCRP raw JSON.")
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["CountryName", "CountryCode", "Year", "Interest"]
    ordered_rows = sorted(rows, key=lambda row: int(row["Year"]))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered_rows)


def main() -> int:
    raw = latest_raw("bcrp", "estadisticas_pd04710xd")
    if raw is None:
        print("Missing BCRP raw JSON; run download_bcrp_estadisticas_pd04710xd.py", file=sys.stderr)
        return 1
    try:
        rows = load_legacy_rows(LEGACY_SOURCE)
        rows.extend(build_embig_rows(raw))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_rows(paths.INTEREST_CSV, rows)
    print(f"Wrote {len(rows)} rows to {paths.INTEREST_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

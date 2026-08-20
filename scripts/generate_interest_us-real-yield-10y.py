#!/usr/bin/env python3
"""Generate the measured 10-year US real-yield leg from Fed H.15 annual data."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.data_io import RAW_ROOT, write_meta_sidecar

FIRST_MEASURED_YEAR = 2003
REQUIRED_COMPLETE_YEAR = 2025
SOURCE = (
    "Fed H.15 complete annual 10y TIPS constant-maturity yield "
    "(RIFLGFCY10_XII_N.A via DBnomics)"
)


def _format(value: float) -> str:
    return f"{value:.12f}".rstrip("0").rstrip(".")


def main() -> int:
    candidates = sorted(
        (
            path
            for path in (RAW_ROOT / "fed").glob("h15_tips10y-annual_*.json")
            if not path.name.endswith(".meta.json")
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError(
            "Missing Fed H.15 annual TIPS raw JSON; run download_fed_h15-tips10y.py."
        )
    raw_path = candidates[0]

    document = json.loads(raw_path.read_text(encoding="utf-8"))
    docs = document.get("series", {}).get("docs", [])
    if len(docs) != 1:
        raise RuntimeError(f"Expected one Fed H.15 series in {raw_path.name}, found {len(docs)}")
    series = docs[0]
    periods = series.get("period", [])
    values = series.get("value", [])
    if len(periods) != len(values):
        raise RuntimeError("Fed H.15 period/value lengths differ")

    measured = {
        int(str(period)[:4]): float(value)
        for period, value in zip(periods, values, strict=True)
        if value is not None and int(str(period)[:4]) >= FIRST_MEASURED_YEAR
    }
    if REQUIRED_COMPLETE_YEAR not in measured:
        raise RuntimeError(
            f"Fed H.15 annual series does not contain complete {REQUIRED_COMPLETE_YEAR}"
        )

    if not paths.US_REAL_YIELD_CSV.is_file():
        raise RuntimeError(f"Missing {paths.US_REAL_YIELD_CSV}; cannot retain 1998-2002 seam rows.")
    legacy: list[dict[str, str]] = []
    with paths.US_REAL_YIELD_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["Year"]) < FIRST_MEASURED_YEAR:
                legacy.append(row)

    rows = legacy + [
        {
            "Year": str(year),
            "USRealYield10Y": _format(value),
            "Source": SOURCE,
        }
        for year, value in sorted(measured.items())
    ]
    with paths.US_REAL_YIELD_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Year", "USRealYield10Y", "Source"])
        writer.writeheader()
        writer.writerows(rows)

    write_meta_sidecar(
        paths.US_REAL_YIELD_CSV,
        script=Path(__file__).name,
        sources=[str(raw_path.relative_to(ROOT))],
        notes=(
            "Fed H.15 annual observations replace all rows from 2003 onward; "
            "1998-2002 estimates are retained for the pre-H.15 seam."
        ),
    )
    print(
        f"Wrote {len(rows)} rows to {paths.US_REAL_YIELD_CSV}; "
        f"{REQUIRED_COMPLETE_YEAR}={measured[REQUIRED_COMPLETE_YEAR]:.2f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

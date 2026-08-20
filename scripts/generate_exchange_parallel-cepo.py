#!/usr/bin/env python3
"""Generate cepo-year parallel exchange-rate override from argentinadatos raw JSON."""

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

CCL_YEARS = [2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
BLUE_YEARS = [2012]
MIN_OBSERVATIONS = 200


def annual_averages(records: list[dict]) -> dict[int, list[float]]:
    by_year: dict[int, list[float]] = defaultdict(list)
    for record in records:
        fecha = str(record.get("fecha", ""))
        if len(fecha) < 4 or not fecha[:4].isdigit():
            continue
        rate = record.get("venta")
        if rate is None:
            rate = record.get("compra")
        if rate is None:
            continue
        by_year[int(fecha[:4])].append(float(rate))
    return by_year


def load_json_raw(provider: str, prefix: str) -> list[dict]:
    path = latest_raw(provider, prefix)
    if path is None:
        raise RuntimeError(f"Missing raw file for {provider}/{prefix}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        ccl = annual_averages(load_json_raw("argentinadatos", "api_cotizaciones-ccl"))
        blue = annual_averages(load_json_raw("argentinadatos", "api_cotizaciones-blue"))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    requested = [(year, "CCL", ccl) for year in CCL_YEARS] + [
        (year, "blue", blue) for year in BLUE_YEARS
    ]

    rows: list[dict[str, str]] = []
    for year, rate_name, by_year in requested:
        values = by_year.get(year, [])
        if len(values) < MIN_OBSERVATIONS:
            print(
                f"Refusing {year}: only {len(values)} daily {rate_name} observations "
                f"(need >= {MIN_OBSERVATIONS}).",
                file=sys.stderr,
            )
            return 1
        label = "Dólar CCL" if rate_name == "CCL" else "Dólar blue"
        rows.append(
            {
                "Year": str(year),
                "ParallelARS": f"{statistics.mean(values):.4f}",
                "Rate": rate_name,
                "Source": f"{label} annual average (argentinadatos.com)",
            }
        )

    rows.sort(key=lambda row: int(row["Year"]))
    out = paths.PARALLEL_CEPO_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Year", "ParallelARS", "Rate", "Source"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

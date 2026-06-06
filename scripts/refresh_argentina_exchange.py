#!/usr/bin/env python3
"""Refresh the cepo-years free-market (parallel) exchange-rate override.

During Argentina's exchange-control ("cepo") periods the official ARS/USD rate (the notebook's
PA.NUS.ATLS) was administratively suppressed while the economy actually transacted at the
free-market rate. Scoring devaluation on the official rate makes the administration that *builds*
the gap (brecha) look good and the one that *unifies* the rate (a one-off catch-up jump) look
terrible -- exactly backwards. This script writes the annual-average free-market rate for the
cepo years so the notebook can substitute it for the official rate on those years only.

Source: argentinadatos.com public API (a community aggregator of Argentine FX quotes). There is
no *official* parallel rate by construction -- under the cepo the BCRA only publishes the official
A3500 -- so a transparent market aggregator is the most faithful reproducible source. CCL (contado
con liquidación) is the capital-flow rate analysts use for the "real" peso value; the blue
(informal) rate fills 2012, before CCL was widely quoted.

Cepo windows where the official rate was suppressed and a gap opened:
  2012-2015  first cepo (Oct 2011 - Dec 2015); 2011's gap was negligible so it stays official.
  2019-2025  second cepo (Sep 2019 - 2025); the gap collapsed as Milei lifted controls through 2025.
2016-2018 (the Macri float) are NOT overridden: the brecha was < 1%, so official == free-market.
"""

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen


OUTPUT_PATH = Path("data/argentina/exchange/parallel-cepo.csv")
CCL_URL = "https://api.argentinadatos.com/v1/cotizaciones/dolares/contadoconliqui"
BLUE_URL = "https://api.argentinadatos.com/v1/cotizaciones/dolares/blue"

CCL_YEARS = [2013, 2014, 2015, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
BLUE_YEARS = [2012]  # CCL not quoted before 2013
MIN_OBSERVATIONS = 200  # daily quotes per year; guards against partial / current years


def fetch_json(url: str) -> list[dict]:
    request = Request(url, headers={"User-Agent": "StillPassingTheBuck/1.0"})
    with urlopen(request, timeout=120) as response:
        return json.load(response)


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


def main() -> int:
    try:
        ccl = annual_averages(fetch_json(CCL_URL))
        blue = annual_averages(fetch_json(BLUE_URL))
    except Exception as exc:  # noqa: BLE001 - surface any network/parse error as a clean failure
        print(f"Failed to fetch parallel FX series: {exc}", file=sys.stderr)
        return 1

    requested = [(year, "CCL", ccl) for year in CCL_YEARS] + [
        (year, "blue", blue) for year in BLUE_YEARS
    ]

    rows: list[dict[str, str]] = []
    for year, rate_name, by_year in requested:
        values = by_year.get(year, [])
        if len(values) < MIN_OBSERVATIONS:
            print(
                f"Refusing to write {year}: only {len(values)} daily {rate_name} observations "
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Year", "ParallelARS", "Rate", "Source"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} cepo-year parallel-rate rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

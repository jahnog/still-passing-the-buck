#!/usr/bin/env python3
"""Download Argentina World Bank indicator API snapshots (all CMPI + FPI codes)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_write_bytes, fetch_bytes, raw_path

COUNTRY = "ARG"
INDICATOR_CODES = [
    "FP.CPI.TOTL",
    "FP.CPI.TOTL.ZG",
    "NY.GDP.DEFL.KD.ZG",
    "NY.GDP.PCAP.KD.ZG",
    "PA.NUS.ATLS",
    "NY.GDP.MKTP.CD",
    "BX.GSR.TOTL.CD",
]
DATE_FROM = "1960-01"
DATE_TO = "2025-12"


def main() -> int:
    for code in INDICATOR_CODES:
        slug = code.lower().replace(".", "-")
        url = (
            f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{code}"
            f"?format=json&per_page=200"
        )
        payload = fetch_bytes(url)
        dest = raw_path("worldbank", "api", slug, DATE_FROM, DATE_TO, "json")
        atomic_write_bytes(payload, dest, min_size=50)
        print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

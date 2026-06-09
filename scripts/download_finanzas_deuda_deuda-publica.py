#!/usr/bin/env python3
"""Download Secretaría de Finanzas annual public-debt workbooks (2019-2025+)."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

BASE = "https://www.argentina.gob.ar/sites/default/files"
DEFAULT_FIRST = 2019
DEFAULT_LAST = min(2025, date.today().year)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=DEFAULT_FIRST)
    parser.add_argument("--to-year", type=int, default=DEFAULT_LAST)
    args = parser.parse_args()

    failures = 0
    for year in range(args.from_year, args.to_year + 1):
        url = f"{BASE}/deuda_publica_31-12-{year}.xlsx"
        dest = raw_path(
            "finanzas",
            "deuda",
            "deuda-publica",
            f"{year}-01",
            f"{year}-12",
            "xlsx",
        )
        time.sleep(0.5)
        try:
            atomic_download(url, dest, timeout=120, min_size=50_000)
            print(f"Wrote {dest}")
        except HTTPError as exc:
            failures += 1
            print(f"SKIP {year}: HTTP {exc.code} for {url}", file=sys.stderr)
    return 1 if failures and failures == (args.to_year - args.from_year + 1) else 0


if __name__ == "__main__":
    raise SystemExit(main())

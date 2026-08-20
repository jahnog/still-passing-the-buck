#!/usr/bin/env python3
"""Download Secretaría de Finanzas year-end debt workbooks used for A.2.5 stocks."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import RAW_ROOT, atomic_write_bytes, fetch_bytes, write_meta_sidecar
from scripts.pipeline_config import target_year

BASE_URL = "https://www.argentina.gob.ar/sites/default/files"
DEFAULT_FIRST = 2019
DEFAULT_LAST = min(target_year(), date.today().year)


def workbook_url(year: int) -> str:
    return f"{BASE_URL}/deuda_publica_31-12-{year}.xlsx"


def workbook_artifact(year: int) -> Path:
    return RAW_ROOT / "finanzas" / f"deuda_deuda-publica_{year}-01_{year}-12.xlsx"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=DEFAULT_FIRST)
    parser.add_argument("--to-year", type=int, default=DEFAULT_LAST)
    args = parser.parse_args()

    years = list(range(args.from_year, args.to_year + 1))
    failures = 0
    for year in years:
        url = workbook_url(year)
        artifact = workbook_artifact(year)
        try:
            content = fetch_bytes(url, timeout=120)
            atomic_write_bytes(content, artifact, min_size=50_000)
            write_meta_sidecar(
                artifact,
                script=Path(__file__).name,
                sources=[url],
                notes=(
                    f"Datos de Deuda Pública al 31 de diciembre de {year}; "
                    "year-end Secretaría de Finanzas workbook retained for the A.2.5 "
                    "Sector Público Nacional gross-debt stock."
                ),
            )
            print(f"Wrote {artifact.relative_to(ROOT)}")
        except HTTPError as exc:
            failures += 1
            print(f"SKIP {year}: HTTP {exc.code} for {url}", file=sys.stderr)
    return 1 if failures and failures == len(years) else 0


if __name__ == "__main__":
    raise SystemExit(main())

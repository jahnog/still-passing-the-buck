#!/usr/bin/env python3
"""Download INDEC IPIM workbook 1956-1995."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = "https://www.indec.gob.ar/ftp/cuadros/economia/sipm-serie56-95.xls"
DATE_FROM = "1956-01"
DATE_TO = "1995-12"


def main() -> int:
    dest = raw_path("indec", "economia", "sipm-serie56-95", DATE_FROM, DATE_TO, "xls")
    atomic_download(URL, dest, min_size=10_000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Download BCRA com3500 official exchange-rate workbook."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls"
DATE_FROM = "1960-01"
DATE_TO = "2025-12"


def main() -> int:
    dest = raw_path("bcra", "publicaciones", "com3500", DATE_FROM, DATE_TO, "xls")
    atomic_download(URL, dest, min_size=100_000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

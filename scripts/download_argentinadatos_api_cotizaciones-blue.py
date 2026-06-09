#!/usr/bin/env python3
"""Download argentinadatos blue-dollar quotes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = "https://api.argentinadatos.com/v1/cotizaciones/dolares/blue"
DATE_FROM = "2012-01"
DATE_TO = "2025-12"


def main() -> int:
    dest = raw_path("argentinadatos", "api", "cotizaciones-blue", DATE_FROM, DATE_TO, "json")
    atomic_download(URL, dest, timeout=120, min_size=1000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

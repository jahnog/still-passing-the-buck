#!/usr/bin/env python3
"""Download Secretaría de Finanzas IMIG provisional workbook (2025 bridge)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = (
    "https://www.argentina.gob.ar/sites/default/files/2025/01/"
    "sector_publico_base_caja_diciembre_2024.xlsx"
)
DATE_FROM = "2024-01"
DATE_TO = "2024-12"


def main() -> int:
    dest = raw_path(
        "finanzas",
        "sector-publico",
        "sector-publico-base-caja",
        DATE_FROM,
        DATE_TO,
        "xlsx",
    )
    atomic_download(URL, dest, timeout=120, min_size=20_000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

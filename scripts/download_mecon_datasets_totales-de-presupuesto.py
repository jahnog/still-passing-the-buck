#!/usr/bin/env python3
"""Download MECON budget execution totals zip (datos.gob.ar)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = "https://dgsiaf-repo.mecon.gob.ar/repository/pa/datasets/totales-de-presupuesto.zip"
DATE_FROM = "2019-01"
DATE_TO = "2025-12"


def main() -> int:
    dest = raw_path("mecon", "datasets", "totales-de-presupuesto", DATE_FROM, DATE_TO, "zip")
    atomic_download(URL, dest, timeout=120, min_size=1_000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Download INDEC IPC nacional divisions CSV."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

URL = "https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv"
DATE_FROM = "2016-01"
DATE_TO = "2025-12"


def main() -> int:
    dest = raw_path("indec", "economia", "serie-ipc-divisiones", DATE_FROM, DATE_TO, "csv")
    atomic_download(URL, dest, min_size=5000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

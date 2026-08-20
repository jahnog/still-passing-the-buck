#!/usr/bin/env python3
"""Download BCRP EMBIG Argentina spread (PD04710XD) JSON series."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, raw_path

START_YEAR = 1998
END_YEAR = date.today().year
URL = (
    "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04710XD/json/"
    f"{START_YEAR}-01-01/{END_YEAR}-12-31"
)


def main() -> int:
    dest = raw_path(
        "bcrp",
        "estadisticas",
        "pd04710xd",
        f"{START_YEAR}-01",
        f"{END_YEAR}-12",
        "json",
    )
    atomic_download(URL, dest, timeout=120, min_size=100)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

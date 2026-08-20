#!/usr/bin/env python3
"""Download argentinadatos blue-dollar quotes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_download, atomic_write_bytes, fetch_bytes, raw_path
from scripts.download_schemas import validate_argentinadatos_cotizaciones
from scripts.pipeline_config import date_to

URL = "https://api.argentinadatos.com/v1/cotizaciones/dolares/blue"
DATE_FROM = "2012-01"
DATE_TO = date_to()


def main() -> int:
    payload = fetch_bytes(URL, timeout=120)
    document = json.loads(payload)
    validate_argentinadatos_cotizaciones(document)
    dest = raw_path("argentinadatos", "api", "cotizaciones-blue", DATE_FROM, DATE_TO, "json")
    atomic_write_bytes(json.dumps(document).encode("utf-8"), dest, min_size=1000)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

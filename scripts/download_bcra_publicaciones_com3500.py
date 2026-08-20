#!/usr/bin/env python3
"""Download BCRA com3500 official exchange-rate workbook."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import atomic_write_bytes, fetch_bytes, raw_path
from scripts.pipeline_config import date_to

URLS = (
    "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls",
    "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/com3500.xls",
)
DATE_FROM = "1960-01"
DATE_TO = date_to()
MIN_SIZE = 100_000
OLE2_SIGNATURE = bytes.fromhex("d0cf11e0a1b11ae1")


def validate_com3500_xls(content: bytes, *, source: str) -> None:
    """Reject BCRA soft-404/HTML responses before they replace the raw workbook."""
    if len(content) < MIN_SIZE:
        raise RuntimeError(
            f"BCRA COM3500 download from {source} too small "
            f"({len(content)} bytes); expected >= {MIN_SIZE}"
        )
    if not content.startswith(OLE2_SIGNATURE):
        preview = content[:120].decode("utf-8", errors="replace").replace("\n", " ")
        raise RuntimeError(
            "BCRA COM3500 response is not an OLE2 .xls workbook "
            f"from {source}: {preview!r}"
        )


def fetch_com3500_workbook() -> tuple[str, bytes]:
    errors: list[str] = []
    for url in URLS:
        try:
            content = fetch_bytes(url, timeout=120)
            validate_com3500_xls(content, source=url)
        except Exception as exc:
            errors.append(f"{url}: {exc}")
            continue
        return url, content
    raise RuntimeError("Could not fetch a valid BCRA COM3500 workbook:\n- " + "\n- ".join(errors))


def main() -> int:
    dest = raw_path("bcra", "publicaciones", "com3500", DATE_FROM, DATE_TO, "xls")
    source, content = fetch_com3500_workbook()
    atomic_write_bytes(content, dest, min_size=MIN_SIZE)
    print(f"Wrote {dest} from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Download World Bank WDI bulk CSV zip."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urllib.error import HTTPError, URLError

from scripts.data_io import atomic_write_bytes, fetch_bytes, latest_raw, raw_path

# World Bank rotates bulk-export URLs; fall back to the newest committed raw copy.
URLS = [
    "https://databankfiles.worldbank.org/public/ddpext_download/WDI_csv.zip",
    "https://databank.worldbank.org/data/download/WDI_csv.zip",
]
DATE_FROM = "1960-01"
DATE_TO = "2025-12"
MIN_ZIP_SIZE = 100_000


def _valid_zip(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < MIN_ZIP_SIZE:
        return False
    return path.read_bytes()[:2] == b"PK"


def main() -> int:
    dest = raw_path("worldbank", "wdi", "wdi-csv", DATE_FROM, DATE_TO, "zip")
    if _valid_zip(dest):
        print(f"Already have {dest}")
        return 0

    last_error: Exception | None = None
    for url in URLS:
        try:
            content = fetch_bytes(url, timeout=300)
            if len(content) >= MIN_ZIP_SIZE and content[:2] == b"PK":
                atomic_write_bytes(content, dest, min_size=MIN_ZIP_SIZE)
                print(f"Wrote {dest} (from {url})")
                return 0
        except (HTTPError, URLError, RuntimeError) as exc:
            last_error = exc

    fallback = latest_raw("worldbank", "wdi_wdi-csv")
    if fallback and _valid_zip(fallback) and fallback.resolve() != dest.resolve():
        atomic_write_bytes(fallback.read_bytes(), dest, min_size=MIN_ZIP_SIZE)
        print(f"Wrote {dest} (from local fallback {fallback})")
        return 0

    if _valid_zip(dest):
        print(f"Already have {dest}")
        return 0

    print(f"WDI download failed; no usable remote URL or local fallback: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

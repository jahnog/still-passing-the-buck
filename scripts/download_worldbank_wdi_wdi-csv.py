#!/usr/bin/env python3
"""Download World Bank WDI bulk CSV zip."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from urllib.error import HTTPError, URLError

from scripts.data_io import ROOT, atomic_download, atomic_write_bytes, fetch_bytes, raw_path

# World Bank rotates bulk-export URLs; the local `data/WDI_csv.zip` is the fallback seed.
URLS = [
    "https://databankfiles.worldbank.org/public/ddpext_download/WDI_csv.zip",
    "https://databank.worldbank.org/data/download/WDI_csv.zip",
]
LOCAL_FALLBACK = ROOT / "data" / "WDI_csv.zip"
DATE_FROM = "1960-01"
DATE_TO = "2025-12"


def main() -> int:
    dest = raw_path("worldbank", "wdi", "wdi-csv", DATE_FROM, DATE_TO, "zip")
    last_error: Exception | None = None
    for url in URLS:
        try:
            content = fetch_bytes(url, timeout=300)
            if len(content) >= 100_000 and content[:2] == b"PK":
                atomic_write_bytes(content, dest, min_size=100_000)
                print(f"Wrote {dest} (from {url})")
                return 0
        except (HTTPError, URLError, RuntimeError) as exc:
            last_error = exc

    if LOCAL_FALLBACK.is_file():
        atomic_write_bytes(LOCAL_FALLBACK.read_bytes(), dest, min_size=100_000)
        print(f"Wrote {dest} (from local fallback {LOCAL_FALLBACK})")
        return 0

    print(f"WDI download failed; no usable remote URL or local fallback: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

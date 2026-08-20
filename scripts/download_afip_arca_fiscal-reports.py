#!/usr/bin/env python3
"""Download pinned AFIP/ARCA reports used for measured one-off receipts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.official_correction_sources import download_provider


if __name__ == "__main__":
    raise SystemExit(download_provider("afip", script=Path(__file__).name))

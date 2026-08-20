#!/usr/bin/env python3
"""Download official Santa Fe, CABA, and San Luis CPI source artifacts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.official_correction_sources import download_provider


if __name__ == "__main__":
    script = Path(__file__).name
    for provider in ("santafe", "caba", "sanluis"):
        download_provider(provider, script=script)

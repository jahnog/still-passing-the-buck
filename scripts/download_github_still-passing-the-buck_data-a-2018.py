#!/usr/bin/env python3
"""Download paper authors' data_a_2018.xlsx into data/provided/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import PROVIDED_ROOT, atomic_download

URL = (
    "https://github.com/jahnog/still-passing-the-buck/raw/refs/heads/main/"
    "data/provided/data_a_2018.xlsx?download="
)
DEST = PROVIDED_ROOT / "data_a_2018.xlsx"


def main() -> int:
    atomic_download(URL, DEST, min_size=10_000)
    print(f"Wrote {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

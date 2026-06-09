#!/usr/bin/env python3
"""Generate Argentina WDI indicators from raw downloads and wide WDI export."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.paths import INDICATORS_CSV, INDICATORS_GZ, WIDE_WDI_CSV
from scripts.indicator_build import build_indicator_rows, write_indicators


def main() -> int:
    if not WIDE_WDI_CSV.exists():
        print(f"Missing wide WDI source: {WIDE_WDI_CSV}", file=sys.stderr)
        return 1

    try:
        rows = build_indicator_rows(WIDE_WDI_CSV)
        write_indicators(rows, INDICATORS_CSV, INDICATORS_GZ)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {len(rows)} Argentina indicator rows to {INDICATORS_CSV}")
    print(f"Compressed {INDICATORS_GZ}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

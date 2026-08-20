#!/usr/bin/env python3
"""Exit non-zero when processed CSVs / Indicators files diverge from checksums.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.processed_checksums import check_manifest


def main() -> int:
    problems = check_manifest()
    if problems:
        print("Processed-data checksum regression failed:", file=sys.stderr)
        for msg in problems:
            print(f"  - {msg}", file=sys.stderr)
        print(
            "Regenerate with `make generate` then "
            "`uv run python scripts/update_processed_checksums.py` if intentional.",
            file=sys.stderr,
        )
        return 1
    print("processed checksums OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
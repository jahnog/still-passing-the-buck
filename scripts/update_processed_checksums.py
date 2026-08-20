#!/usr/bin/env python3
"""Refresh data/processed/checksums.json from the committed on-disk outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.processed_checksums import MANIFEST_PATH, write_manifest


def main() -> int:
    manifest = write_manifest()
    print(f"Wrote {len(manifest)} entries to {MANIFEST_PATH}")
    print(json.dumps({"files": len(manifest), "manifest": str(MANIFEST_PATH)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
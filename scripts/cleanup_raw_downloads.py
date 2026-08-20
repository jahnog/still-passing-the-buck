#!/usr/bin/env python3
"""Keep only the last two copies of each rotated raw download.

Downloaders write a stable dest name under ``data/raw/``. When that dest already
exists, ``data_io.atomic_write_bytes`` moves it to the next free
``<stem>_N.<ext>`` and writes the new file in its place.

This script walks ``data/raw/`` and, for each dest family, keeps the live file
plus its newest previous copy. Pinned official artifacts that were never
rotated are left untouched. Year tokens in dest names (``imig-anual_2017.xlsx``,
``…_2019-12.xlsx``) are not treated as rotation generations.

Usage:
  uv run python scripts/cleanup_raw_downloads.py
  uv run python scripts/cleanup_raw_downloads.py --dry-run
  uv run python scripts/cleanup_raw_downloads.py --keep 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import DEFAULT_ROTATION_KEEP, RAW_ROOT, cleanup_rotated_raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=RAW_ROOT,
        help="Raw-download tree to prune (default: data/raw)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=DEFAULT_ROTATION_KEEP,
        help="Copies to retain per dest family (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be deleted without removing them",
    )
    args = parser.parse_args()

    removed = cleanup_rotated_raw(args.root, keep=args.keep, dry_run=args.dry_run)
    verb = "Would delete" if args.dry_run else "Deleted"
    if not removed:
        print("No rotated raw downloads to prune.")
        return 0
    for path in removed:
        try:
            display = path.relative_to(ROOT)
        except ValueError:
            display = path
        print(f"{verb} {display}")
    print(f"{verb} {len(removed)} file(s); kept {args.keep} set(s) per dest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

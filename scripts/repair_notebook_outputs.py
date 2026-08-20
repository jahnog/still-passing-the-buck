#!/usr/bin/env python3
"""Fill nbformat v4 required fields that editors often strip from cell outputs.

Cursor / VS Code omit empty ``metadata`` on ``display_data`` / ``execute_result``,
``execution_count`` on ``execute_result``, and ``name`` on ``stream``. nbconvert
7.16+ then fails validation with ``'metadata' is a required property``.

This script only inserts missing keys. It does not re-execute the notebook or
rewrite payloads.

Usage:
    uv run python scripts/repair_notebook_outputs.py
    uv run python scripts/repair_notebook_outputs.py path/to/notebook.ipynb
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK = ROOT / "Historical_CMPI_Extension.ipynb"


def repair_outputs(nb: Any) -> int:
    """Insert missing schema fields on cell outputs. Returns the number added."""
    added = 0
    for cell in nb.get("cells", []):
        for out in cell.get("outputs") or []:
            output_type = out.get("output_type")
            if output_type in ("display_data", "execute_result"):
                if "metadata" not in out:
                    out["metadata"] = {}
                    added += 1
                if output_type == "execute_result" and "execution_count" not in out:
                    out["execution_count"] = None
                    added += 1
            elif output_type == "stream" and "name" not in out:
                out["name"] = "stdout"
                added += 1
    return added


def repair_notebook_file(path: Path) -> int:
    nb = json.loads(path.read_text(encoding="utf-8"))
    added = repair_outputs(nb)
    path.write_text(
        json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notebook",
        nargs="?",
        type=Path,
        default=DEFAULT_NOTEBOOK,
        help=f"Notebook to repair in place (default: {DEFAULT_NOTEBOOK.name})",
    )
    args = parser.parse_args()
    path = args.notebook.expanduser().resolve()
    if not path.is_file():
        print(f"notebook not found: {path}", file=sys.stderr)
        return 1
    added = repair_notebook_file(path)
    print(f"{path.name}: added {added} missing output field(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

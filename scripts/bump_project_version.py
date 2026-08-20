#!/usr/bin/env python3
"""Bump the project version in committed literals that cannot be templated.

Rewrites ``[project].version`` in pyproject.toml and the top-level ``version:``
field in CITATION.cff (never ``cff-version:``). Then refreshes ``uv.lock``,
resolves ``paper/generated/paper_resolved.md``, and rewrites the SHA256 manifest.

Usage:
    uv run python scripts/bump_project_version.py 1.3.3
    make bump VERSION=1.3.3
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
PYPROJECT_VERSION_LINE = re.compile(
    r'^(\s*version\s*=\s*")[^"]*("\s*(?:#.*)?(?:\n)?)$'
)
CFF_VERSION_LINE = re.compile(r"^(version:\s*)(\S+)[ \t]*$", re.MULTILINE)
CFF_DATE_LINE = re.compile(r"^(date-released:\s*)(\S+)[ \t]*$", re.MULTILINE)
SECTION_HEADER = re.compile(r"^\s*\[([^\]]+)\]\s*(?:#.*)?$")


def replace_pyproject_version(text: str, version: str) -> str:
    """Replace ``version`` only inside the ``[project]`` table."""
    in_project = False
    found = False
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        header = SECTION_HEADER.match(line)
        if header is not None:
            in_project = header.group(1).strip() == "project"
        if in_project:
            match = PYPROJECT_VERSION_LINE.match(line)
            if match is not None:
                line = f"{match.group(1)}{version}{match.group(2)}"
                found = True
                in_project = False
        out.append(line)
    if not found:
        raise ValueError('pyproject.toml has no [project] version = "..." field')
    return "".join(out)


def replace_citation_version(text: str, version: str) -> str:
    """Replace the top-level ``version:`` field, never ``cff-version:``."""
    matches = list(CFF_VERSION_LINE.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one top-level 'version:' line in CITATION.cff, "
            f"found {len(matches)}"
        )
    return CFF_VERSION_LINE.sub(rf"\g<1>{version}", text, count=1)


def replace_citation_date(text: str, date_released: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_released):
        raise ValueError(
            f"date-released must be YYYY-MM-DD, got {date_released!r}"
        )
    matches = list(CFF_DATE_LINE.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one 'date-released:' line in CITATION.cff, "
            f"found {len(matches)}"
        )
    return CFF_DATE_LINE.sub(rf'\g<1>"{date_released}"', text, count=1)


def bump(
    version: str,
    *,
    root: Path = ROOT,
    date_released: str | None = None,
    skip_lock: bool = False,
    skip_paper: bool = False,
    skip_manifest: bool = False,
) -> None:
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"version must be X.Y.Z, got {version!r}")

    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        replace_pyproject_version(pyproject.read_text(encoding="utf-8"), version),
        encoding="utf-8",
    )

    cff = root / "CITATION.cff"
    cff_text = replace_citation_version(cff.read_text(encoding="utf-8"), version)
    if date_released is not None:
        cff_text = replace_citation_date(cff_text, date_released)
    cff.write_text(cff_text, encoding="utf-8")

    if not skip_lock:
        subprocess.run(["uv", "lock"], cwd=root, check=True)
    if not skip_paper:
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "build_paper.py"),
                "--skip-extract",
                "--skip-pdf",
            ],
            cwd=root,
            check=True,
        )
    if not skip_manifest:
        subprocess.run(
            [sys.executable, str(root / "scripts" / "write_data_manifest.py")],
            cwd=root,
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="New project version (X.Y.Z)")
    parser.add_argument(
        "--date",
        dest="date_released",
        default=None,
        help="Optional CITATION.cff date-released (YYYY-MM-DD). Default: leave unchanged.",
    )
    parser.add_argument("--skip-lock", action="store_true", help="Do not run uv lock")
    parser.add_argument(
        "--skip-paper",
        action="store_true",
        help="Do not resolve paper/generated/paper_resolved.md",
    )
    parser.add_argument(
        "--skip-manifest",
        action="store_true",
        help="Do not rewrite data/file-manifest.json",
    )
    args = parser.parse_args()
    try:
        bump(
            args.version,
            date_released=args.date_released,
            skip_lock=args.skip_lock,
            skip_paper=args.skip_paper,
            skip_manifest=args.skip_manifest,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"bumped project version to {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

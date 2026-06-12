#!/usr/bin/env python3
"""Build the publication manuscript PDF from paper/paper.md.

The manuscript source (paper/paper.md, pandoc Markdown) holds the prose; every
figure and ranking table is extracted from the *executed* notebook so the
paper's numbers cannot drift from the pipeline's output:

1. Extract figure PNGs and ranking tables (HTML outputs) from named notebook
   cells into paper/generated/.
2. Resolve {{table:NAME}} directives in paper/paper.md into Markdown tables.
3. Run pandoc (citeproc bibliography, XeLaTeX engine) to produce the PDF.

Usage:
    uv run python scripts/build_paper.py                  # full build
    uv run python scripts/build_paper.py --skip-extract   # reuse paper/generated/
    uv run python scripts/build_paper.py --output my.pdf

Requirements beyond pyproject.toml: pandoc and a XeLaTeX installation
(e.g. `apt install pandoc texlive-xetex texlive-fonts-extra`).
"""

from __future__ import annotations

import argparse
import base64
import re
import subprocess
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NOTEBOOK = REPO / "Historical_CMPI_Extension.ipynb"
PAPER_DIR = REPO / "paper"
GENERATED = PAPER_DIR / "generated"
SOURCE = PAPER_DIR / "paper.md"

# Paper figure name -> notebook cell id (first image/png output of the cell).
FIGURES = {
    "quality": "quality_heatmap",
    "inflation": "hist_infl_diag",
    "cepo": "hist_cepo_diag",
    "gdp": "gdp_revision_chart",
    "debt-layers": "debt_layers_chart",
    "primary": "primary_result_chart",
    "quasi-fiscal": "quasi_fiscal_chart",
}


@dataclass(frozen=True)
class TableSpec:
    """Columns to keep from a notebook HTML table, as (source, output) headers.

    A source header of "" selects the DataFrame index column. `round_to`
    rounds numeric cells that the notebook emits unrounded.
    """

    cell_id: str
    columns: tuple[tuple[str, str], ...]
    round_to: int | None = None


TABLES = {
    "cmpi": TableSpec(
        "a1000031",
        (
            ("", "Administration"),
            ("Rank", "Rank"),
            ("Term", "Years"),
            ("Regime", "Regime"),
            ("Inflation", "Inflation"),
            ("Devaluation", "Devaluation"),
            ("Interest", "Interest"),
            ("Growth", "Growth"),
            ("CMPI", "CMPI"),
        ),
    ),
    "fpi": TableSpec(
        "5b764aca",
        (
            ("", "Administration"),
            ("FPI Rank", "Rank"),
            ("Term", "Years"),
            ("Debt/GDP", "Debt / GDP"),
            ("Debt/Exp", "Debt / Exp"),
            ("Res/Rev", "Res / Rev"),
            ("Res/DebtSv", "Res / DebtSv"),
            ("(1+r)/(1+g)", "(1+r) / (1+g)"),
            ("FPI", "FPI"),
        ),
    ),
    "overall": TableSpec(
        "ce14434f",
        (
            ("", "Administration"),
            ("Overall Rank", "Rank"),
            ("Term", "Years"),
            ("CMPI Rank", "CMPI Rank"),
            ("FPI Rank", "FPI Rank"),
            ("CMPI", "CMPI"),
            ("FPI", "FPI"),
            ("Overall", "Overall"),
            ("Borda Rank", "Borda Rank"),
        ),
    ),
    "milei-menem": TableSpec(
        "a5bea984",
        (
            ("", "Year"),
            ("Admin", "Administration"),
            ("Inflation", "Inflation"),
            ("Devaluation", "Devaluation"),
            ("Interest", "Interest"),
            ("Growth", "Growth"),
            ("CMPI", "CMPI"),
        ),
    ),
    "cepo-bcra": TableSpec(
        "fpi60tbl",
        (
            ("", "Administration"),
            ("Term", "Years"),
            ("Debt/GDP off.", "Debt/GDP off."),
            ("Cepo x", "Cepo x"),
            ("BCRA %GDP", "BCRA % GDP"),
            ("Debt/GDP adj.", "Debt/GDP adj."),
        ),
    ),
    "fpi-sensitivity": TableSpec(
        "fpi_sens_code",
        (
            ("", "Administration"),
            ("Baseline rank", "Baseline"),
            ("Measured FX share", "Measured FX share"),
            ("Cepo 50% FX share", "50% FX share"),
            ("rg w/ total growth", "Total-growth r/g"),
        ),
    ),
    "first-two-years": TableSpec(
        "first2_code",
        (
            ("", "Administration"),
            ("Full-term rank", "Full-term rank"),
            ("First-2-years rank", "First-2-years rank"),
        ),
    ),
    "bootstrap-ci": TableSpec(
        "boot_ci_tbl",
        (
            ("", "Administration"),
            ("CMPI med", "CMPI median"),
            ("CMPI 95% CI", "CMPI 95% CI"),
            ("FPI med", "FPI median"),
            ("FPI 95% CI", "FPI 95% CI"),
            ("Overall med", "Overall median"),
            ("Overall 95% CI", "Overall 95% CI"),
            ("P(Overall top 5)", "P(top 5)"),
        ),
    ),
    "contemporaneous": TableSpec(
        "a1000025",
        (
            ("", "Administration"),
            ("YearFrom", "From"),
            ("YearTo", "To"),
            ("InflationAvg", "Inflation"),
            ("Devaluation", "Devaluation"),
            ("Interest", "Interest"),
            ("Growth", "Growth"),
        ),
        round_to=2,
    ),
}


class _TableGrab(HTMLParser):
    """Collect the text grid of the first <table> in an HTML fragment."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._in_table = False
        self._done = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if self._done:
            return
        if tag == "table":
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._row = []
        elif self._in_table and tag in ("td", "th"):
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if self._done or not self._in_table:
            return
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif tag == "table":
            self._in_table = False
            self._done = True

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)


def _load_cells() -> dict[str, dict]:
    import nbformat

    nb = nbformat.read(NOTEBOOK, as_version=4)
    return {c["id"]: c for c in nb.cells if c.cell_type == "code"}


def _cell_output(cell: dict, mime: str) -> str | None:
    for out in cell.get("outputs", []):
        data = out.get("data", {})
        if mime in data:
            payload = data[mime]
            return payload if isinstance(payload, str) else "".join(payload)
    return None


def _to_markdown(html: str, spec: TableSpec) -> str:
    parser = _TableGrab()
    parser.feed(html)
    # Drop pandas index-name rows (only the first cell is populated).
    rows = [r for r in parser.rows if sum(1 for c in r if c) > 1]
    if not rows:
        raise SystemExit(f"no table rows found in cell {spec.cell_id}")
    header, data = rows[0], rows[1:]
    try:
        idx = [header.index(src) for src, _ in spec.columns]
    except ValueError as exc:
        raise SystemExit(f"cell {spec.cell_id}: column not found: {exc}; have {header}")

    def cell_text(value: str) -> str:
        if spec.round_to is not None and re.fullmatch(r"-?\d*\.\d+", value):
            value = f"{float(value):.{spec.round_to}f}"
        return value.replace("|", r"\|")

    def fmt(row: list[str]) -> str:
        cells = [cell_text(row[i]) if i < len(row) else "" for i in idx]
        return "| " + " | ".join(cells) + " |"

    body = [fmt(r) for r in data]
    out_header = [dst for _, dst in spec.columns]
    lines = ["| " + " | ".join(out_header) + " |"]
    # When the table is wider than the text column pandoc derives the relative
    # column widths from the dash counts, so size each delimiter to the
    # column's longest content (name columns wide, numeric columns narrow).
    # Headers can't hyphenate, so the longest unbreakable header word also
    # sets a floor on the column width.
    widths = [max(max(len(w) for w in h.split()) + 4,
                  max(len(r[i]) if i < len(r) else 0 for r in data) + 2)
              for h, i in zip(out_header, idx)]
    # Unbreakable name/year strings need headroom or LaTeX lets them overflow.
    widths[0] = int(widths[0] * 1.3)
    lines.append("|:" + "-" * max(widths[0], 4)
                 + "".join("|" + "-" * max(w, 4) + ":" for w in widths[1:]) + "|")
    lines.extend(body)
    return "\n".join(lines)


def extract() -> None:
    cells = _load_cells()
    GENERATED.mkdir(parents=True, exist_ok=True)
    for name, cell_id in FIGURES.items():
        png = _cell_output(cells[cell_id], "image/png")
        if png is None:
            raise SystemExit(f"figure cell {cell_id} has no image/png output — run `make execute`")
        (GENERATED / f"fig_{name}.png").write_bytes(base64.b64decode(png))
    for name, spec in TABLES.items():
        html = _cell_output(cells[spec.cell_id], "text/html")
        if html is None:
            raise SystemExit(f"table cell {spec.cell_id} has no text/html output — run `make execute`")
        (GENERATED / f"tbl_{name}.md").write_text(_to_markdown(html, spec) + "\n")
    print(f"extracted {len(FIGURES)} figures and {len(TABLES)} tables to {GENERATED}")


def resolve_source() -> Path:
    text = SOURCE.read_text()

    def sub(match: re.Match) -> str:
        name = match.group(1)
        path = GENERATED / f"tbl_{name}.md"
        if not path.exists():
            raise SystemExit(f"unknown table directive {{{{table:{name}}}}} (no {path})")
        return path.read_text().rstrip("\n")

    text = re.sub(r"^\{\{table:([a-z0-9-]+)\}\}$", sub, text, flags=re.MULTILINE)
    leftover = re.search(r"\{\{[a-z]+:[^}]*\}\}", text)
    if leftover:
        raise SystemExit(f"unresolved directive: {leftover.group(0)}")
    resolved = GENERATED / "paper_resolved.md"
    resolved.write_text(text)
    return resolved


def build_pdf(resolved: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pandoc",
        str(resolved),
        "--from", "markdown+smart",
        "--pdf-engine", "xelatex",
        "--citeproc",
        "--number-sections",
        "--include-in-header", str(PAPER_DIR / "preamble.tex"),
        "--resource-path", f"{PAPER_DIR}:{GENERATED}",
        "--metadata", f"bibliography={PAPER_DIR / 'references.bib'}",
        "--output", str(output),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-extract", action="store_true",
                        help="reuse the existing paper/generated/ artifacts")
    parser.add_argument("--output", type=Path,
                        default=PAPER_DIR / "output" / "still-passing-the-buck.pdf")
    args = parser.parse_args()
    if not args.skip_extract:
        extract()
    build_pdf(resolve_source(), args.output)


if __name__ == "__main__":
    sys.exit(main())

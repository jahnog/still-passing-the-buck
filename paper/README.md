# Manuscript

This directory contains the manuscript. The notebook is the computational
replication; [`output/still-passing-the-buck.pdf`](output/still-passing-the-buck.pdf)
is the citable paper, archived on
[Zenodo](https://doi.org/10.5281/zenodo.20651730) and
[MPRA](https://mpra.ub.uni-muenchen.de/id/eprint/130511).

| File | Purpose |
|------|---------|
| `paper.md` | The manuscript source — pandoc Markdown with a YAML metadata header. Edit prose here. |
| `references.bib` | BibTeX bibliography (cited with `[@key]`; rendered in Chicago author–date). |
| `preamble.tex` | LaTeX typography tweaks (table sizing, captions, float placement). |
| `generated/` | Build artifacts written by `scripts/build_paper.py` (tables, figures, resolved markdown). |
| `output/` | The built PDF — committed, as the distributed artifact linked from the README. |

## Build

```bash
make paper            # full build: extract from notebook + pandoc -> PDF
uv run python scripts/build_paper.py --skip-pdf       # extract + resolve without TeX
uv run python scripts/build_paper.py --skip-extract   # prose-only iteration
```

Requires `pandoc` and XeLaTeX (`apt install pandoc texlive-xetex tex-gyre`)
in addition to the Python environment.

## How figures and tables stay in sync with the data

Every figure and ranking table in the PDF is extracted at build time from the
executed notebook (`scripts/build_paper.py` maps named notebook cells to
`paper/generated/`).
Lines of the form `{{table` + `:name}}` in `paper.md` are replaced with the
extracted tables; the caption line (starting with `:`) must stay immediately
below each directive. After a data refresh, run `make execute` then `make paper`;
the build fails if a table directive cannot be resolved.

Table and figure numbers in the prose are written manually; if floats are
added or reordered, update the cross-references.

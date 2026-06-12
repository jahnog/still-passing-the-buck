# Manuscript

The paper, as a standalone manuscript. The notebook is the replication
package; this directory is the citable object. The published paper is
archived on Zenodo:
[doi:10.5281/zenodo.20651731](https://doi.org/10.5281/zenodo.20651731)
(v1.0.0; concept DOI
[10.5281/zenodo.20651730](https://doi.org/10.5281/zenodo.20651730)).

| File | Purpose |
|------|---------|
| `paper.md` | The manuscript source — pandoc Markdown with a YAML metadata header. Edit prose here. |
| `references.bib` | BibTeX bibliography (cited with `[@key]`; rendered in Chicago author–date). |
| `preamble.tex` | LaTeX typography tweaks (table sizing, captions, float placement). |
| `generated/` | Build artifacts extracted from the notebook (gitignored). |
| `output/` | The built PDF (gitignored). |

## Build

```bash
make paper            # full build: extract from notebook + pandoc -> PDF
uv run python scripts/build_paper.py --skip-extract   # prose-only iteration
```

Requires `pandoc` and XeLaTeX (`apt install pandoc texlive-xetex tex-gyre`)
in addition to the Python environment.

## How figures and tables stay honest

Every figure and ranking table in the PDF is extracted at build time from the
*executed* notebook (`scripts/build_paper.py` maps named notebook cells to
`paper/generated/`), so the paper's numbers cannot drift from the pipeline.
Lines of the form `{{table` + `:name}}` in `paper.md` are replaced with the
extracted tables; the caption line (starting with `:`) must stay immediately
below each directive. After a data refresh, run `make execute` then
`make paper` and re-read the prose around each table — the numbers update
themselves, the words do not (TODO markers in `paper.md` flag the spots that
must be re-verified).

Table and figure numbers in the prose are written manually; if floats are
added or reordered, update the cross-references.

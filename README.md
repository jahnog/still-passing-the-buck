# Still Passing the Buck

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jahnog/still-passing-the-buck/blob/main/Historical_CMPI_Extension.ipynb)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20651731.svg)](https://doi.org/10.5281/zenodo.20651731)

A data-driven comparison of how successive Argentine administrations actually
performed economically — ranking them on long-run macroeconomic indicators
(inflation, GDP, public debt, exchange-rate and fiscal pressure) instead of
arguing about it. The analysis combines World Bank World Development Indicators
with official Argentine sources (INDEC, BCRA, Ministerio de Economía, BCRP) and
historical series reaching back to 1853.

📄 **Paper:** *Still Passing the Buck: Macroeconomic and Fiscal Performance of
Argentine Administrations, 1853–2025* — published on Zenodo:
<https://zenodo.org/records/20651731>
([doi:10.5281/zenodo.20651731](https://doi.org/10.5281/zenodo.20651731))

📊 **Write-up:** <https://jahnog.github.io/Argentine-monetary-and-fiscal-policies-analyzed/>

## Citation

If you use this work, please cite the published paper:

> Nogueira, Javier Hernan. 2026. "Still Passing the Buck: Macroeconomic and
> Fiscal Performance of Argentine Administrations, 1853–2025." Working paper.
> Zenodo. <https://doi.org/10.5281/zenodo.20651731> (v1.0.0)

- Zenodo record: <https://zenodo.org/records/20651731>
  (the concept DOI [10.5281/zenodo.20651730](https://doi.org/10.5281/zenodo.20651730)
  always resolves to the latest version)
- PDF in this repository: [`paper/output/still-passing-the-buck.pdf`](paper/output/still-passing-the-buck.pdf)
- Machine-readable metadata: [`CITATION.cff`](CITATION.cff) (GitHub's
  "Cite this repository" button)
- Author ORCID: [0009-0006-1945-7870](https://orcid.org/0009-0006-1945-7870)

## Notebook

| Notebook | Purpose |
|----------|---------|
| `Historical_CMPI_Extension.ipynb` | The complete analysis — the Classical Macroeconomic Performance Index (CMPI), the Fiscal Pressure Index (FPI), and their combined Overall Index for all 41 Argentine administrations, 1853–2025, with documented corrections for every known statistical manipulation. |

The wide World Bank export (`data/provided/WDIData2.csv`) is reshaped into the long form the
notebook consumes by `scripts/generate_indicators_wdi-argentina.py`.

Outside a repo checkout (e.g. the Colab badge above) the notebook self-bootstraps: it
fetches its data, portraits, and helper modules from the public S3 mirror
(`https://jnpublicdata.s3.us-east-1.amazonaws.com/still-passing-the-buck/`), which is
kept in sync with `make upload` (`scripts/upload_s3_notebook-data.py`).

A prioritized roadmap of planned improvements is in
[`docs/IMPROVEMENT_PLAN.md`](docs/IMPROVEMENT_PLAN.md).

## Data

All inputs are kept repo-local (via Git LFS) so the notebook reruns without live
network access. The folder layout and the full inventory of download/generate
scripts are documented in [`data/README.md`](data/README.md); the methodological
lineage of each Argentine series is in
[`data/argentina/README.md`](data/argentina/README.md).

- `data/raw/<provider>/` — downloaded source files
- `data/processed/<purpose>/` — generated notebook inputs
- `data/provided/` — curated exceptions (`Indicators.csv*`, `data_a_2018.xlsx`, …)

## Reproduce

```bash
uv sync             # create the environment from pyproject.toml / uv.lock

make verify         # offline end-to-end: unit tests + input validator + headless execution
make reproduce      # full refresh: downloads -> generators -> validator -> tests -> execution
```

(The Makefile targets wrap the per-source `scripts/download_*.py` and `scripts/generate_*.py`
scripts documented in `data/README.md`.) CI runs `make verify`'s steps on every push
(`.github/workflows/ci.yml`); because every table and the §8.4 narrative are rendered from the
live pipeline, a green execution is also a prose-vs-output consistency check. Data vintages are
stamped under the notebook's Figure 0 from the `.meta.json` sidecars; baseline-affecting data
changes are logged in [`data/REVISIONS.md`](data/REVISIONS.md). Citable analysis snapshots are
tagged and archived on Zenodo (v1.0.0 →
[doi:10.5281/zenodo.20651731](https://doi.org/10.5281/zenodo.20651731); the concept DOI
[10.5281/zenodo.20651730](https://doi.org/10.5281/zenodo.20651730) always resolves to the latest
version) so results can be referenced against a frozen data state.

Export the notebook to a print-optimized PDF with
`scripts/render_notebook_paper.py` (see [`docs/paper-export.md`](docs/paper-export.md)).

## Manuscript

The standalone paper lives in [`paper/`](paper/) (pandoc Markdown source,
BibTeX bibliography). `make paper` extracts every figure and ranking table
from the executed notebook and builds the publication PDF with
pandoc + XeLaTeX — see [`paper/README.md`](paper/README.md). The published
paper is archived on Zenodo:
[doi:10.5281/zenodo.20651731](https://doi.org/10.5281/zenodo.20651731).

## Tests

```bash
pytest -m "not network"      # offline unit tests
pytest -m network            # tests that hit live data sources
```

## Stack

Python · pandas · NumPy · matplotlib · Jupyter · uv · Git LFS

## License

This work is licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
— see [`LICENSE`](LICENSE). You are free to use, share, and adapt it for any
purpose, **provided you explicitly credit the author and reference this work**
(see the [Citation](#citation) section above).

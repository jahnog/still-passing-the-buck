# Still Passing the Buck

A data-driven comparison of how successive Argentine administrations actually
performed economically — ranking them on long-run macroeconomic indicators
(inflation, GDP, public debt, exchange-rate and fiscal pressure) instead of
arguing about it. The analysis combines World Bank World Development Indicators
with official Argentine sources (INDEC, BCRA, Ministerio de Economía, BCRP) and
historical series reaching back to 1853.

📊 **Write-up:** <https://jahnog.github.io/Argentine-monetary-and-fiscal-policies-analyzed/>

## Notebook

| Notebook | Purpose |
|----------|---------|
| `Historical_CMPI_Extension.ipynb` | The complete analysis — the Classical Macroeconomic Performance Index (CMPI), the Fiscal Pressure Index (FPI), and their combined Overall Index for all 41 Argentine administrations, 1853–2025, with documented corrections for every known statistical manipulation. |

The wide World Bank export (`data/provided/WDIData2.csv`) is reshaped into the long form the
notebook consumes by `scripts/generate_indicators_wdi-argentina.py`.

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
changes are logged in [`data/REVISIONS.md`](data/REVISIONS.md). For citable analysis snapshots,
tag a release and archive it (e.g. on Zenodo for a DOI) so results can be referenced against a
frozen data state.

Export the notebook to a print-optimized PDF with
`scripts/render_notebook_paper.py` (see [`docs/paper-export.md`](docs/paper-export.md)).

## Tests

```bash
pytest -m "not network"      # offline unit tests
pytest -m network            # tests that hit live data sources
```

## Stack

Python · pandas · NumPy · matplotlib · Jupyter · uv · Git LFS

## License & citation

This work is licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
— see [`LICENSE`](LICENSE). You are free to use, share, and adapt it for any
purpose, **provided you explicitly credit the author and reference this work**.

Suggested citation:

> Javier (jahnog), *Still Passing the Buck — Historical CMPI & FPI Extension:
> Argentina 1853–2025*, 2026. https://github.com/jahnog

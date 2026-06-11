# Notebook PDF Export

Use `scripts/render_notebook_paper.py` to turn the notebook into a print-optimized PDF paper.

## Requirements

- Python dependencies from `pyproject.toml` installed in the environment you will use.
- A Chromium-compatible browser available on `PATH` (`chromium`, `chromium-browser`, `google-chrome`, or similar).

## Basic usage

```bash
python3 scripts/render_notebook_paper.py \
  Historical_CMPI_Extension.ipynb \
  --output docs/Historical_CMPI_Extension.pdf
```

The script re-executes the notebook by default so the PDF contains fresh figures and tables.

## Useful options

```bash
# Reuse the current notebook outputs without executing it again.
python3 scripts/render_notebook_paper.py --skip-execute

# Keep the intermediate print HTML for inspection or manual tweaks.
python3 scripts/render_notebook_paper.py \
  --html-output tmp/Historical_CMPI_Extension.print.html

# Use a specific browser binary.
python3 scripts/render_notebook_paper.py \
  --browser /usr/bin/chromium
```

The generated PDF uses print-specific CSS tuned for article-style typography, wide tables, and figure scaling.
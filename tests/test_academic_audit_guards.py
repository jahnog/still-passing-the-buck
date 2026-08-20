from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths
from scripts.repair_notebook_outputs import repair_outputs


def test_provenance_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_provenance.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_correction_taxonomy_matches_catalogue_size_and_headline_policy() -> None:
    taxonomy = pd.read_csv(paths.CORRECTION_TAXONOMY_CSV)
    assert taxonomy["PracticeID"].astype(int).tolist() == list(range(1, 24))
    corrected = taxonomy[taxonomy["Treatment"] == "Corrected baseline"]
    assert corrected["HeadlineAffected"].astype(str).str.lower().eq("true").all()
    assert corrected["AffectedColumns"].astype(str).str.strip().astype(bool).all()


def test_repair_outputs_fills_stripped_schema_fields() -> None:
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "outputs": [
                    {"output_type": "display_data", "data": {"text/plain": "x"}},
                    {"output_type": "execute_result", "data": {"text/plain": "1"}},
                    {"output_type": "stream", "text": "hello\n"},
                ],
            }
        ]
    }
    assert repair_outputs(nb) == 4
    display_data, execute_result, stream = nb["cells"][0]["outputs"]
    assert display_data["metadata"] == {}
    assert execute_result["metadata"] == {}
    assert execute_result["execution_count"] is None
    assert stream["name"] == "stdout"
    assert repair_outputs(nb) == 0


def test_notebook_nbformat_schema_valid() -> None:
    import nbformat
    from nbformat.validator import validate

    notebook_path = ROOT / "Historical_CMPI_Extension.ipynb"
    nb = nbformat.read(notebook_path, as_version=4)
    validate(nb)


def test_statistical_bootstrap_analysis_is_absent() -> None:
    paper = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    nb = json.loads((ROOT / "Historical_CMPI_Extension.ipynb").read_text(encoding="utf-8"))
    notebook_source = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    builder = (ROOT / "scripts" / "build_paper.py").read_text(encoding="utf-8")
    forbidden = (
        "PAPER_SCALARS_JSON:",
        "{{scalar:",
        "boot_ci",
        "n_boot",
        "np.random.seed(42)",
        "np.random.seed(43)",
        "bootstrap confidence",
        "bootstrap rank",
    )
    for text in (paper, notebook_source, builder):
        lowered = text.lower()
        assert not [token for token in forbidden if token.lower() in lowered]
    assert not (ROOT / "paper" / "generated" / "tbl_bootstrap-ci.md").exists()
    assert not (ROOT / "paper" / "generated" / "paper_scalars.json").exists()

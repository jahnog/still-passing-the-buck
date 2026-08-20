"""Lock the project version to pyproject.toml and guard CFF rewrite anchors."""

from __future__ import annotations

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bump_project_version import (
    replace_citation_date,
    replace_citation_version,
    replace_pyproject_version,
)
from scripts.project_meta import project_version

ZENODO_DOI = "10.5281/zenodo.20651730"
FROZEN_ZENODO_VERSION = re.compile(
    r"Zenodo[^\n]{0,80}\(v\d+\.\d+(?:\.\d+)?\)"
    r"|\(v\d+\.\d+(?:\.\d+)?\)[^\n]{0,80}(?:concept DOI|" + re.escape(ZENODO_DOI) + r")",
    re.IGNORECASE,
)
NOTEBOOK = ROOT / "Historical_CMPI_Extension.ipynb"


def _lockfile_project_version() -> str:
    with (ROOT / "uv.lock").open("rb") as handle:
        data = tomllib.load(handle)
    for package in data.get("package", []):
        if package.get("name") == "stillpassingthebuck":
            return str(package["version"])
    raise AssertionError("uv.lock has no stillpassingthebuck package")


def _cff_field(name: str) -> str:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(name)}:\s*(\S+)\s*$", text, re.MULTILINE)
    assert match is not None, f"CITATION.cff missing {name!r}"
    return match.group(1).strip().strip('"')


def test_citation_cff_version_matches_pyproject():
    assert _cff_field("version") == project_version()


def test_citation_cff_spec_version_is_not_rewritten_as_project_version():
    spec = _cff_field("cff-version")
    assert spec.startswith("1.")
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert re.search(r"^cff-version:\s*", text, re.MULTILINE)
    assert re.search(
        rf"^version:\s*{re.escape(project_version())}\s*$", text, re.MULTILINE
    )


def test_uv_lock_virtual_package_matches_pyproject():
    assert _lockfile_project_version() == project_version()


def test_paper_source_keeps_version_placeholder():
    text = (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")
    assert "{{project_version}}" in text


def test_readmes_do_not_freeze_a_zenodo_version():
    for rel in ("README.md", "paper/README.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        match = FROZEN_ZENODO_VERSION.search(text)
        assert match is None, f"{rel} still embeds a frozen Zenodo version: {match.group(0)!r}"
        assert ZENODO_DOI in text


def test_notebook_badge_reads_pyproject_toml():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cell = next(c for c in nb["cells"] if c.get("id") == "project_version_badge")
    source = "".join(cell["source"])
    tree = ast.parse(source)
    assert any(
        isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PROJECT_VERSION" for t in node.targets)
        for node in ast.walk(tree)
    )
    assert "tomllib" in source
    assert '["project"]["version"]' in source


def test_replace_citation_version_does_not_touch_cff_version():
    text = (
        "cff-version: 1.3.1\n"
        "title: example\n"
        "version: 1.3.1\n"
        "license: CC-BY-4.0\n"
    )
    updated = replace_citation_version(text, "1.4.0")
    assert "cff-version: 1.3.1" in updated
    assert re.search(r"^version: 1.4.0$", updated, re.MULTILINE)
    assert updated.count("1.3.1") == 1


def test_replace_pyproject_version_only_touches_project_table():
    text = (
        "[project]\n"
        'name = "stillpassingthebuck"\n'
        'version = "1.3.1"\n'
        "\n"
        "[tool.dummy]\n"
        'version = "1.3.1"\n'
    )
    updated = replace_pyproject_version(text, "1.4.0")
    assert 'version = "1.4.0"' in updated
    assert '[tool.dummy]\nversion = "1.3.1"' in updated


def test_replace_citation_date_quotes_iso_date():
    text = 'cff-version: 1.2.0\nversion: 1.0.0\ndate-released: "2026-01-01"\n'
    updated = replace_citation_date(text, "2026-08-19")
    assert 'date-released: "2026-08-19"' in updated
    assert "version: 1.0.0" in updated


def test_bump_rewrites_tmp_tree_without_touching_cff_spec(tmp_path: Path):
    from scripts.bump_project_version import bump

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "stillpassingthebuck"\nversion = "1.3.1"\n',
        encoding="utf-8",
    )
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: 1.3.1\nversion: 1.3.1\n",
        encoding="utf-8",
    )
    bump(
        "1.4.0",
        root=tmp_path,
        skip_lock=True,
        skip_paper=True,
        skip_manifest=True,
    )
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    cff = (tmp_path / "CITATION.cff").read_text(encoding="utf-8")
    assert 'version = "1.4.0"' in pyproject
    assert "cff-version: 1.3.1" in cff
    assert re.search(r"^version: 1.4.0$", cff, re.MULTILINE)

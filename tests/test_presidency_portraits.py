"""Tests for portrait slug naming, base_url (Colab) mode, and the S3 upload inventory.

Run with: pytest -q tests/test_presidency_portraits.py
All tests are offline.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

# Make project imports (scripts.*, data.*) work when running tests directly or via uv run / make.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.presidency_portraits as pp
from scripts.cmpi_core import render_minister_img
from scripts.presidency_portraits import (
    PORTRAIT_SOURCE_URLS,
    _ambiguous_slugs,
    localize_presidency_terms,
    portrait_filename,
    portrait_slug,
)


def test_slug_examples():
    assert (
        portrait_slug(
            "https://upload.wikimedia.org/wikipedia/commons/9/9c/Jos%C3%A9_Mar%C3%ADa_Guido_3_%28cropped%29_2.jpg"
        )
        == "jose-maria-guido-3-cropped-2.jpg"
    )
    # Non-JPEG sources are still .jpg: the downloader re-encodes everything as JPEG.
    assert (
        portrait_slug("https://upload.wikimedia.org/wikipedia/commons/b/b6/Manuel_Quintana_presidente.png")
        == "manuel-quintana-presidente.jpg"
    )
    assert portrait_slug("https://cdi.mecon.gob.ar/img/cavallo.jpg") == "cavallo.jpg"


def test_all_source_urls_have_unique_slugs():
    urls = set(PORTRAIT_SOURCE_URLS)
    names = {portrait_filename(u).lower() for u in urls}
    assert len(names) == len(urls)
    # If this fails, a newly added URL collides: portrait_filename starts hash-suffixing
    # both colliding names, so existing S3 keys and local files must be re-synced.
    assert pp._AMBIGUOUS_SLUGS == frozenset()


def test_collision_guard_is_deterministic_and_order_independent():
    a = "https://example.org/img/one/Cavallo.jpg"
    b = "https://example.org/img/two/cavallo.jpg"
    assert portrait_slug(a) == portrait_slug(b)
    assert _ambiguous_slugs((a, b)) == _ambiguous_slugs((b, a)) == frozenset({"cavallo.jpg"})

    ambiguous = _ambiguous_slugs((a, b))
    original = pp._AMBIGUOUS_SLUGS
    pp._AMBIGUOUS_SLUGS = ambiguous
    try:
        name_a, name_b = portrait_filename(a), portrait_filename(b)
    finally:
        pp._AMBIGUOUS_SLUGS = original
    assert name_a != name_b
    assert name_a.startswith("cavallo-") and name_b.startswith("cavallo-")


def test_localize_base_url_mode_is_manifest_free(monkeypatch):
    def _boom():
        raise AssertionError("base_url mode must not read the manifest")

    monkeypatch.setattr(pp, "load_manifest", _boom)
    terms = [
        (
            "X",
            2000,
            2001,
            "https://upload.wikimedia.org/wikipedia/commons/d/db/NestorKirchner.jpeg",
            "Roberto Lavagna|https://cdi.mecon.gob.ar/img/lavagna.jpg",
        )
    ]
    (term,) = localize_presidency_terms(terms, base_url="https://x/")
    assert term[3] == "https://x/assets/portraits/nestorkirchner.jpg"
    assert term[4] == "Roberto Lavagna|https://x/assets/portraits/lavagna.jpg"


def test_render_minister_img_accepts_local_image_paths():
    html = render_minister_img("Roberto Lavagna|assets/portraits/lavagna.jpg")
    assert '<img src="assets/portraits/lavagna.jpg"' in html
    assert "Roberto Lavagna" in html
    # A bare name (no portrait) still renders as a text box, not an image.
    assert "<img" not in render_minister_img("José Benjamín Gorostiaga")


def _load_upload_module():
    spec = importlib.util.spec_from_file_location(
        "upload_s3_notebook_data", ROOT / "scripts" / "upload_s3_notebook-data.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upload_inventory_covers_notebook_data_reads():
    upload = _load_upload_module()
    uncovered = upload.verify_notebook_coverage(list(upload.DATA_FILES))
    assert uncovered == [], f"notebook reads files missing from DATA_FILES: {uncovered}"


def test_manifest_paths_match_deterministic_names():
    manifest_path = ROOT / "assets" / "portraits" / "manifest.json"
    if not manifest_path.is_file():
        return  # fresh checkout without downloaded portraits
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for url, entry in manifest.items():
        assert entry["path"] == pp.portrait_relative_path(url)
        assert entry["filename"] == portrait_filename(url)

"""Offline schema checks for JSON download payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.download_schemas import (
    SchemaError,
    validate_argentinadatos_cotizaciones,
    validate_bcra_monetarias_catalog,
    validate_bcra_monetarias_snapshot,
    validate_worldbank_indicator_payload,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "download"


def _load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_worldbank_fixture_passes():
    validate_worldbank_indicator_payload(_load("worldbank_indicator_sample.json"))


def test_bcra_snapshot_fixture_passes():
    validate_bcra_monetarias_snapshot(_load("bcra_monetarias_snapshot_sample.json"))


def test_bcra_catalog_fixture_passes():
    validate_bcra_monetarias_catalog(_load("bcra_monetarias_catalog_sample.json"))


def test_argentinadatos_fixture_passes():
    validate_argentinadatos_cotizaciones(_load("argentinadatos_cotizaciones_sample.json"))


@pytest.mark.parametrize(
    "validator,payload",
    [
        (validate_worldbank_indicator_payload, []),
        (validate_bcra_monetarias_snapshot, {"results": []}),
        (validate_bcra_monetarias_catalog, {"results": []}),
        (validate_argentinadatos_cotizaciones, []),
    ],
)
def test_empty_payloads_fail(validator, payload):
    with pytest.raises(SchemaError):
        validator(payload)
"""Pipeline year configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import pipeline_config


def test_date_to_uses_target_year(monkeypatch):
    monkeypatch.delenv("CMPI_TARGET_YEAR", raising=False)
    monkeypatch.delenv("TARGET_YEAR", raising=False)
    monkeypatch.setenv("CMPI_TARGET_YEAR", "2027")
    assert pipeline_config.target_year() == 2027
    assert pipeline_config.date_to() == "2027-12"


def test_target_year_prefers_cmpi_env(monkeypatch):
    monkeypatch.setenv("CMPI_TARGET_YEAR", "2026")
    monkeypatch.setenv("TARGET_YEAR", "2024")
    assert pipeline_config.target_year() == 2026
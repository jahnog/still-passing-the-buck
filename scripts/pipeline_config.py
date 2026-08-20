"""Central CMPI pipeline year configuration.

TARGET_YEAR / CMPI_TARGET_YEAR (env) set the analysis horizon shared by download
scripts (DATE_TO filenames) and validators.
"""

from __future__ import annotations

import os

DEFAULT_TARGET_YEAR = 2025


def target_year() -> int:
    """Return the pipeline target year from CMPI_TARGET_YEAR, TARGET_YEAR, or default."""
    for key in ("CMPI_TARGET_YEAR", "TARGET_YEAR"):
        raw = os.environ.get(key)
        if raw:
            return int(raw)
    return DEFAULT_TARGET_YEAR


def date_to(*, year: int | None = None, month: int = 12) -> str:
    """Return ``YYYY-MM`` for the pipeline end date (default: December of target year)."""
    y = year if year is not None else target_year()
    return f"{y}-{month:02d}"
#!/usr/bin/env python3
"""Load World Bank indicator series from raw API JSON snapshots."""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

from scripts.data_io import latest_raw


def wb_series_from_raw(code: str) -> dict[int, float]:
    slug = code.lower().replace(".", "-")
    path = latest_raw("worldbank", f"api_{slug}")
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    return {int(r["date"]): r["value"] for r in records if r.get("value") is not None}


def official_fx_series() -> dict[int, float]:
    """Official ARS/US$ annual average for the cepo factor.

    Primary source is raw PA.NUS.FCRF (the actual official period-average rate). Years the World
    Bank has not yet published are filled from PA.NUS.ATLS rows in the generated Indicators.csv.gz,
    whose recent years (2020+) are genuine BCRA com3500 annual averages, not Atlas-smoothed values.
    """
    from data import paths

    series: dict[int, float] = {}
    if paths.INDICATORS_GZ.exists():
        with gzip.open(paths.INDICATORS_GZ, "rt", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["IndicatorCode"] == "PA.NUS.ATLS":
                    series[int(row["Year"])] = float(row["Value"])
    series.update(wb_series_from_raw("PA.NUS.FCRF"))
    return series

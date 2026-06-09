#!/usr/bin/env python3
"""Load World Bank indicator series from raw API JSON snapshots."""

from __future__ import annotations

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

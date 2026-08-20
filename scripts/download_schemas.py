"""Lightweight structural checks for JSON download payloads (no jsonschema dependency)."""

from __future__ import annotations

from typing import Any


class SchemaError(ValueError):
    """Raised when a downloaded JSON payload does not match the expected shape."""


def _require_mapping(obj: Any, label: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise SchemaError(f"{label}: expected object, got {type(obj).__name__}")
    return obj


def _require_list(obj: Any, label: str) -> list[Any]:
    if not isinstance(obj, list):
        raise SchemaError(f"{label}: expected array, got {type(obj).__name__}")
    return obj


def validate_worldbank_indicator_payload(data: Any) -> None:
    """World Bank indicator API: ``[metadata, observations]``."""
    payload = _require_list(data, "worldbank indicator")
    if len(payload) != 2:
        raise SchemaError(f"worldbank indicator: expected length-2 array, got {len(payload)}")
    meta = _require_mapping(payload[0], "worldbank metadata")
    for key in ("page", "pages", "per_page", "total"):
        if key not in meta:
            raise SchemaError(f"worldbank metadata: missing {key!r}")
    rows = _require_list(payload[1], "worldbank observations")
    if not rows:
        raise SchemaError("worldbank observations: empty array")
    for i, row in enumerate(rows[:3]):
        obs = _require_mapping(row, f"worldbank observation[{i}]")
        for key in ("indicator", "country", "date"):
            if key not in obs:
                raise SchemaError(f"worldbank observation[{i}]: missing {key!r}")


def validate_bcra_monetarias_snapshot(data: Any) -> None:
    """BCRA monetarias download bundle: ``{series_metadata, results}``."""
    doc = _require_mapping(data, "bcra monetarias snapshot")
    for key in ("series_metadata", "results"):
        if key not in doc:
            raise SchemaError(f"bcra monetarias snapshot: missing {key!r}")
    _require_mapping(doc["series_metadata"], "bcra series_metadata")
    results = _require_list(doc["results"], "bcra results")
    if not results:
        raise SchemaError("bcra results: empty array")
    for i, row in enumerate(results[:3]):
        obs = _require_mapping(row, f"bcra observation[{i}]")
        for key in ("fecha", "valor"):
            if key not in obs:
                raise SchemaError(f"bcra observation[{i}]: missing {key!r}")


def validate_bcra_monetarias_catalog(data: Any) -> None:
    """BCRA monetarias catalog page: ``{results, metadata}``."""
    doc = _require_mapping(data, "bcra monetarias catalog")
    results = _require_list(doc.get("results"), "bcra catalog results")
    if not results:
        raise SchemaError("bcra catalog results: empty array")
    row = _require_mapping(results[0], "bcra catalog row")
    if "idVariable" not in row:
        raise SchemaError("bcra catalog row: missing idVariable")


def validate_argentinadatos_cotizaciones(data: Any) -> None:
    """argentinadatos cotizaciones endpoint: array of daily quote rows."""
    rows = _require_list(data, "argentinadatos cotizaciones")
    if not rows:
        raise SchemaError("argentinadatos cotizaciones: empty array")
    for i, row in enumerate(rows[:3]):
        obs = _require_mapping(row, f"argentinadatos row[{i}]")
        for key in ("casa", "compra", "venta", "fecha"):
            if key not in obs:
                raise SchemaError(f"argentinadatos row[{i}]: missing {key!r}")
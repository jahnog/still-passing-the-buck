#!/usr/bin/env python3
"""Download BCRA "Estadísticas Monetarias" v4 API series snapshots.

Series fetched (daily/monthly, full history):
- 27   Inflación mensual (monthly CPI variation, 1943-03 →) — reproducible CPI source
       for the 1964–2006 inflation variant (IMF IFS routes are dead; see REVISIONS.md).
- 196  LEFI held by financial entities (Treasury letters; cross-check only — Treasury debt,
       NOT part of the BCRA remunerated-liability consolidation).
- 1258 Lebac/Nobac and other BCRA letters in pesos (2002-03 →).
- 1259 Lebac/Nobac and other BCRA letters in foreign currency (2002-03 →).
- 1260 Leliq y Notaliq (2018-01 →).
- 1262 Posición de pases pasivos (1996-01 →).

Together 1258+1259+1260+1262 give the audited daily stock of the central bank's
remunerated liabilities, replacing the curated year-end anchors in
`generate_fiscal_bcra-quasi-fiscal.py` (grade C → B).

The BCRA endpoint serves an incomplete TLS chain on some networks; on certificate
failure the fetch retries without verification (public statistical data; values are
cross-checked against the documented anchors downstream).
"""

from __future__ import annotations

import json
import ssl
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_io import USER_AGENT, atomic_write_bytes, raw_path, write_meta_sidecar

API_BASE = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"
DATE_TO = "2026-12"
PAGE_LIMIT = 3000

# (idVariable, filename slug, series start for the filename date range)
SERIES = [
    (27, "monetarias-27-inflacion-mensual", "1943-01"),
    (196, "monetarias-196-lefi", "2003-01"),
    (1258, "monetarias-1258-lebac-nobac-ars", "2002-01"),
    (1259, "monetarias-1259-lebac-nobac-fx", "2002-01"),
    (1260, "monetarias-1260-leliq-notaliq", "2018-01"),
    (1262, "monetarias-1262-pases-pasivos", "1996-01"),
]


def fetch_json(url: str, *, timeout: int = 120) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        print(f"  TLS verification failed for {url}; retrying unverified (public data)")
        context = ssl._create_unverified_context()
        with urlopen(request, timeout=timeout, context=context) as response:
            return json.loads(response.read())


def fetch_catalog() -> dict[int, dict]:
    entries: dict[int, dict] = {}
    offset = 0
    while True:
        payload = fetch_json(f"{API_BASE}?limit=1000&offset={offset}")
        results = payload.get("results", [])
        for row in results:
            entries[row["idVariable"]] = row
        count = payload.get("metadata", {}).get("resultset", {}).get("count", 0)
        offset += 1000
        if offset >= count or not results:
            return entries


def fetch_series(series_id: int, date_from: str) -> list[dict]:
    """Return [{fecha, valor}, ...]; the v4 detail endpoint wraps observations in
    results[0].detalle (newest first) and paginates with limit/offset over them."""
    observations: list[dict] = []
    offset = 0
    while True:
        url = (
            f"{API_BASE}/{series_id}?desde={date_from}-01&hasta=2026-12-31"
            f"&limit={PAGE_LIMIT}&offset={offset}"
        )
        payload = fetch_json(url)
        results = payload.get("results", [])
        page = results[0].get("detalle", []) if results else []
        observations.extend(page)
        count = payload.get("metadata", {}).get("resultset", {}).get("count", 0)
        offset += PAGE_LIMIT
        if not page or offset >= count:
            return observations


def main() -> int:
    catalog = fetch_catalog()
    for series_id, slug, date_from in SERIES:
        meta = catalog.get(series_id, {})
        observations = fetch_series(series_id, date_from)
        if not observations:
            raise RuntimeError(f"BCRA series {series_id} returned no observations")
        document = {"series_metadata": meta, "results": observations}
        payload = json.dumps(document, ensure_ascii=False).encode("utf-8")
        dest = raw_path("bcra", "api", slug, date_from, DATE_TO, "json")
        atomic_write_bytes(payload, dest, min_size=200)
        write_meta_sidecar(
            dest,
            script=Path(__file__).name,
            sources=[f"{API_BASE}/{series_id}"],
            notes=meta.get("descripcion", "").strip(),
        )
        print(f"Wrote {len(observations)} obs to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

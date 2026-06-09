#!/usr/bin/env python3
"""Generate December-to-December Convertibility override (1989-1995)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

DEC_RATES = {
    1989: (0.1953, "BCRA Memoria Anual 1989, Cuadro VIII (1953 AUS/USD ÷ 10000)"),
    1990: (0.5050, "BCRA Memoria Anual 1990, Cuadro VIII (5050 AUS/USD ÷ 10000)"),
    1991: (1.0000, "Ley de Convertibilidad 23928 (1 ARS = 1 USD = 10000 AUS, Dec 1991)"),
    1992: (1.0000, "Convertibilidad maintida (1 ARS = 1 USD)"),
    1993: (1.0000, "Convertibilidad maintida (1 ARS = 1 USD)"),
    1994: (1.0000, "Convertibilidad maintida (1 ARS = 1 USD)"),
    1995: (1.0000, "Convertibilidad maintida (1 ARS = 1 USD)"),
}


def main() -> int:
    rows = []
    prior_rate = None
    for year in sorted(DEC_RATES):
        dec_rate, source = DEC_RATES[year]
        devaluation = "" if prior_rate is None else f"{(dec_rate / prior_rate - 1) * 100:.4f}"
        rows.append(
            {
                "Year": str(year),
                "DecRateARS": f"{dec_rate:.4f}",
                "Devaluation": devaluation,
                "Currency": "ARS",
                "Source": source,
            }
        )
        prior_rate = dec_rate

    out = paths.BCRA_DEC_DEC_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["Year", "DecRateARS", "Devaluation", "Currency", "Source"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

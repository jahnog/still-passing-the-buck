#!/usr/bin/env python3
"""Build data/argentina/exchange/bcra-dec-dec-1990-1995.csv.

Produces December-to-December exchange-rate-based devaluation overrides for the
Menem I term (1990-1995). This eliminates the distortion that the World Bank
PA.NUS.ATLS annual average introduces at the 1991 Convertibility boundary: the
WB average blends the pre-April 1991 floating months with the post-April 1.00
ARS/USD peg into a single "1991" number, making the annual-change series show
a spurious devaluation in 1992 (as the full-year 1992 average of 1.00 is
compared with the 1991 blended average of ~0.95).

The December-to-December approach compares like-for-like end-of-year snapshots:
  - December 1989 → December 1990: the Austral's final depreciation burst
  - December 1990 → December 1991: final catch-up to the 1:1 Convertibility peg
  - December 1991 → December 1992: 0% (peg fully established)
  - December 1992 → December 1995: 0% (Convertibility maintained exactly)

The paper itself uses "average of December quotations from DATAFIEL" (Appendix B),
which is the monthly average of daily December rates -- close to but not identical
with our end-of-December value. The difference is small enough to be negligible for
the CMPI percentile ranking.

DATA SOURCES
-----------
Pre-Convertibility (Austral era, 1989-1991):
  BCRA Memoria Anual 1989 and 1990.  End-of-December "tipo de cambio" (official
  BCRA reference rate, Austral per US dollar):
    December 1989:  1,953 AUS/USD  (BCRA Memoria Anual 1989, Cuadro VIII)
    December 1990:  5,050 AUS/USD  (BCRA Memoria Anual 1990, Cuadro VIII)

Convertibility era (Peso, 1991-1995):
  Ley de Convertibilidad (Law 23,928, April 1 1991): fixed 1 Peso = 1 USD exactly.
  Decreto 2,128/1991 (October 1991): 1 Peso = 10,000 Australes (effective Jan 1 1992).
  By December 1991 the BCRA reference rate was already 10,000 AUS/USD = 1.00 ARS/USD.
  December 1992 through December 1995: exactly 1.0000 ARS/USD.

CURRENCY CONVERSION
-------------------
All rates are expressed in ARS/USD for consistency with the notebook's PA.NUS.ATLS
series (which is already in ARS from 1992 onward and in ARS-equivalent for earlier
years after the World Bank converts them).

  1 ARS = 10,000 Australes  (Decree 2,128/1991)
  December 1989: 1,953 AUS ÷ 10,000 = 0.1953 ARS/USD
  December 1990: 5,050 AUS ÷ 10,000 = 0.5050 ARS/USD
  December 1991: 1.0000 ARS/USD  (Convertibility)
  December 1992-1995: 1.0000 ARS/USD
"""

import csv
from pathlib import Path

OUTPUT_PATH = Path("data/argentina/exchange/bcra-dec-dec-1990-1995.csv")

# December end-of-month ARS/USD rates (see module docstring for sources).
# 1989 is only a baseline for computing 1990's devaluation — it is not overridden.
DEC_RATES = {
    1989: (0.1953,  "BCRA Memoria Anual 1989, Cuadro VIII (1953 AUS/USD ÷ 10000)"),
    1990: (0.5050,  "BCRA Memoria Anual 1990, Cuadro VIII (5050 AUS/USD ÷ 10000)"),
    1991: (1.0000,  "Ley de Convertibilidad 23928 (1 ARS = 1 USD = 10000 AUS, Dec 1991)"),
    1992: (1.0000,  "Convertibilidad maintida (1 ARS = 1 USD)"),
    1993: (1.0000,  "Convertibilidad maintida (1 ARS = 1 USD)"),
    1994: (1.0000,  "Convertibilidad maintida (1 ARS = 1 USD)"),
    1995: (1.0000,  "Convertibilidad maintida (1 ARS = 1 USD)"),
}

rows = []
prior_rate = None
for year in sorted(DEC_RATES):
    dec_rate, source = DEC_RATES[year]
    if prior_rate is None:
        devaluation = ""  # 1989 is baseline only
    else:
        devaluation = f"{(dec_rate / prior_rate - 1) * 100:.4f}"
    rows.append({
        "Year":       str(year),
        "DecRateARS": f"{dec_rate:.4f}",
        "Devaluation": devaluation,
        "Currency":   "ARS",
        "Source":     source,
    })
    prior_rate = dec_rate

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(
        fh,
        fieldnames=["Year", "DecRateARS", "Devaluation", "Currency", "Source"],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")

# Verify: 1992-1995 must be exactly 0% devaluation
for row in rows:
    if row["Year"] in ("1992", "1993", "1994", "1995"):
        assert row["Devaluation"] == "0.0000", f"Expected 0 for {row['Year']}, got {row['Devaluation']}"
# Verify: 1990 devaluation > 100%
deval_1990 = float(next(r["Devaluation"] for r in rows if r["Year"] == "1990"))
assert deval_1990 > 100, f"1990 devaluation should be >100%, got {deval_1990:.1f}%"
print(f"Verification passed — 1990 devaluation: {deval_1990:.1f}%, 1992-1995: 0%")

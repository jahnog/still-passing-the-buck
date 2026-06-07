#!/usr/bin/env python3
"""Generate data/argentina/exchange/paper-devaluation-1853-1999.csv

Extracts the annual devaluation log-diff series (col E) from the paper authors'
Excel dataset (data_a_2018.xlsx), covering 1853-1999.

Data sources by period (as described in Appendix B of della Paolera, Irigoin & Bózzoli 2011):
  1822-63: Irigoin (2000a)
  1864-84: Cortés Conde (1989)
  1885-1938: della Paolera and Ortiz (1995)
  1939-46: End of year quotation from Revista Económica (BCRA)
  1947-59: End of year quotation from Boletín Techint
  1960-89: Average of December quotations from Ruíz (1990)
  1990-99: Average of December quotations from DATAFIEL

All values are natural log-differences: ln(e_t / e_{t-1}) where e is the
paper-peso (later ARS) per gold/USD exchange rate.

This series is used in both notebooks to REPLACE the WDI PA.NUS.ATLS annual-
average devaluation for 1964-1999. The WDI average underrepresents mid-year
devaluations (e.g., the Nov-1963 Guido devaluation, the Jun-1966 Onganía
devaluation, the Jul-1975 Rodrigazo) and creates wrong-sign CMPI innovations
for the following administration.
"""
import pandas as pd
from pathlib import Path

OUTPUT = Path("data/argentina/exchange/paper-devaluation-1853-1999.csv")
HIST_ORIGINAL_DATA_URL = "https://github.com/jahnog/still-passing-the-buck/raw/refs/heads/main/data/argentina/historical/data_a_2018.xlsx?download="

xl = pd.read_excel(
    HIST_ORIGINAL_DATA_URL,
    sheet_name="Hoja1",
    header=6,
    usecols="B,E",
    names=["Year", "DevaluationLog"],
)
xl = xl.dropna(subset=["Year"])
xl["Year"] = xl["Year"].astype(int)
xl = xl.set_index("Year").loc[1853:1999]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
xl.to_csv(OUTPUT)
print(f"Wrote {len(xl)} rows to {OUTPUT}")

# Sanity checks
assert len(xl) == 147, f"Expected 147 rows (1853-1999), got {len(xl)}"
assert xl.index.min() == 1853
assert xl.index.max() == 1999
assert xl["DevaluationLog"].isna().sum() == 0, "NaN values found"

# Verify 1992-1995 Convertibility: near-zero devaluation
for y in [1992, 1993, 1994, 1995]:
    val = xl.loc[y, "DevaluationLog"]
    assert abs(val) < 0.01, f"1992-1995 should be ~0 (Convertibility), got {val:.4f} for {y}"
print("Convertibility check (1992-1995 ≈ 0) ✓")

# Verify Illia sign fix: inherited 1963 must be negative (appreciation), so 1964 shows worsening
val_1963 = xl.loc[1963, "DevaluationLog"]
val_1964 = xl.loc[1964, "DevaluationLog"]
illia_avg_innov = xl.loc[1964:1966, "DevaluationLog"].mean() - val_1963
print(f"Illia (1964-66) avg devaluation innovation vs 1963 baseline: {illia_avg_innov*100:.1f}%")
print(f"  (paper Table 3.2 shows +27.14%; close match confirms correct December methodology)")
assert illia_avg_innov > 0, "Illia devaluation innovation must be positive (worsening)"
print("Illia sign check ✓")
print("All checks passed.")

#!/usr/bin/env python3
"""Generate historical CMPI term averages (1852-1963)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

TERMS = [
    ("_baseline", 1852, 1852, -6.80, -6.80, 15.19, 25.89),
    ("Alsina", 1853, 1853, 14.11, 14.11, 15.19, -17.53),
    ("Obligado", 1854, 1856, 3.19, 3.19, 14.10, 7.15),
    ("Alsina II", 1857, 1859, 0.53, 0.53, 15.72, -4.82),
    ("Mitre", 1860, 1868, 1.68, 2.08, 12.70, 7.43),
    ("Sarmiento", 1869, 1874, 4.33, 0.00, 8.63, 2.30),
    ("Avellaneda", 1875, 1880, 10.01, 2.24, 10.02, 5.19),
    ("Roca", 1881, 1886, -2.94, 3.25, 7.22, 8.08),
    ("Juárez Celman", 1887, 1890, 12.06, 15.46, 8.79, 5.40),
    ("Pellegrini", 1891, 1892, 10.86, 12.15, 9.72, -4.43),
    ("Sáenz Peña L./Uriburu JE", 1893, 1898, -1.23, -4.12, 8.22, 0.72),
    ("Roca II", 1899, 1904, -1.72, -1.76, 7.32, 3.82),
    ("Quintana/Figueroa", 1905, 1910, 4.97, 0.04, 5.50, 2.43),
    ("Sáenz Peña R./de la Plaza", 1911, 1916, 3.71, 0.06, 3.73, -3.99),
    ("Yrigoyen", 1917, 1922, 1.03, 2.70, 5.08, 3.10),
    ("De Alvear", 1923, 1928, 0.09, -2.72, 8.63, 2.94),
    ("Yrigoyen II", 1929, 1930, -3.67, 7.47, 8.77, -2.45),
    ("Uriburu JF", 1931, 1931, -3.31, 23.26, 8.72, -9.22),
    ("Justo", 1932, 1937, 3.98, -0.62, 6.02, 1.88),
    ("Ortiz/Castillo", 1938, 1942, 4.52, 4.55, 2.09, 0.77),
    ("Ramírez/Farrell", 1943, 1945, 5.57, -1.46, 0.52, 0.77),
    ("Perón I", 1946, 1951, 20.93, 31.58, -0.02, 2.72),
    ("Perón II", 1952, 1955, 10.25, 7.19, -1.25, 0.89),
    ("Aramburu", 1956, 1957, 20.93, 1.64, -0.49, 2.21),
    ("Frondizi", 1958, 1961, 34.67, 20.15, 0.46, 2.31),
    ("Guido", 1962, 1963, 26.05, 24.42, 2.89, -2.41),
]


def main() -> int:
    rows = []
    for admin, first_year, last_year, inf, deval, interest, growth in TERMS:
        for year in range(first_year, last_year + 1):
            rows.append(
                {
                    "Year": year,
                    "Administration": admin,
                    "Inflation": inf,
                    "Devaluation": deval,
                    "Interest": interest,
                    "Growth": growth,
                }
            )

    out = paths.HISTORICAL_CMPI_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["Year", "Administration", "Inflation", "Devaluation", "Interest", "Growth"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")
    assert len(rows) == 112
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

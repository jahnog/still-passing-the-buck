#!/usr/bin/env python3
"""Generate paper-method devaluation series from data_a_2018.xlsx."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

OUTPUT = paths.PAPER_DEVALUATION_CSV


def main() -> int:
    if not paths.DATA_A_2018_XLSX.exists():
        print(f"Missing {paths.DATA_A_2018_XLSX}", file=sys.stderr)
        return 1

    xl = pd.read_excel(
        paths.DATA_A_2018_XLSX,
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

    assert len(xl) == 147
    assert xl.index.min() == 1853
    assert xl.index.max() == 1999
    assert xl["DevaluationLog"].isna().sum() == 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract pre-WDI annual series (cols D,E,F) from provided data_a_2018.xlsx."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import paths

OUTPUT = (
    paths.PROCESSED
    / "historical"
    / "converted_historical_data-a-2018-excel_1853-01_1963-12.csv"
)


def main() -> int:
    if not paths.DATA_A_2018_XLSX.exists():
        print(f"Missing {paths.DATA_A_2018_XLSX}", file=sys.stderr)
        return 1

    xl = pd.read_excel(
        paths.DATA_A_2018_XLSX,
        sheet_name="Hoja1",
        header=6,
        usecols="B,D,E,F",
        names=["Year", "InflationLog", "DevaluationLog", "Growth"],
    )
    xl = xl.dropna(subset=["Year"])
    xl["Year"] = xl["Year"].astype(int)
    out_df = xl.set_index("Year").loc[1853:1963].reset_index()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(out_df)} rows to {OUTPUT}")
    assert len(out_df) == 111
    assert out_df["Year"].min() == 1853
    assert out_df["Year"].max() == 1963
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

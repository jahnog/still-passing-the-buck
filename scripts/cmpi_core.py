"""Core CMPI and FPI scoring logic (pure functions).

Extracted from Historical_CMPI_Extension.ipynb for reuse, testing, and clarity.
The notebook remains responsible for:
- Building the unified series (inflation, devaluation, interest, growth)
- Building fpi_data and the fpi_rg series
- Defining the presidency_terms list
- Supplying DATA_END_YEAR and PERIODS_PER_YEAR when needed for descriptive tables

All scoring here operates on pre-computed inputs so the functions are testable
in isolation (no global state, no I/O).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Default variable sets and sort directions (paper Table 3.6 conventions)
CMPI_VARIABLES: List[str] = ["Inflation", "Devaluation", "Interest", "Growth"]
CMPI_SORT_ASCENDING: Dict[str, bool] = {
    "Inflation": False,
    "Devaluation": False,
    "Interest": False,
    "Growth": True,
}

FPI_VARIABLES: List[str] = [
    "FPI_Debt_GDP",
    "FPI_Debt_Exports",
    "FPI_Result_Rev",
    "FPI_Result_DS",
    "FPI_rg",
]
FPI_SORT: Dict[str, bool] = {
    "FPI_Debt_GDP": False,
    "FPI_Debt_Exports": False,
    "FPI_Result_Rev": True,
    "FPI_Result_DS": True,
    "FPI_rg": False,
}


def splice_series(hist_part: pd.Series, modern_part: pd.Series) -> pd.Series:
    """Splice historical and modern series (priority to non-NaN modern values)."""
    result = hist_part.copy()
    result = result.reindex(result.index.union(modern_part.index))
    modern_valid = modern_part.dropna()
    result[modern_valid.index] = modern_valid
    return result.sort_index()


def composite_rate(
    start_level: float, end_level: float, years: int, periods_per_year: int
) -> float:
    """Compound annual rate used for descriptive term-average tables."""
    if years <= 0:
        return 0.0
    return periods_per_year * (pow((end_level / start_level), 1 / (periods_per_year * years)) - 1)


def _percentile_assign(
    df: pd.DataFrame, col: str, ascending: bool
) -> pd.DataFrame:
    """Assign [0, 1] percentile positions in sort order (0 = worst for the variable's semantics)."""
    n = len(df)
    if n == 0:
        df[col + "Pos"] = 0.0
        return df
    increment = 1.0 / n
    pos = 0.0
    for row in df.sort_values(by=col, ascending=ascending).itertuples():
        df.loc[row.Index, col + "Pos"] = pos
        pos += increment
    return df


def compute_innovations(
    terms: List[Tuple[str, int, int, str, str]],
    year_value_fn,
) -> pd.DataFrame:
    """Build the year-level innovation frame (current - inherited from prior term's last year).

    terms: list of (name, first_year, last_year, photo_url, minister)
    year_value_fn(year) -> pd.Series with the four (or five) raw level values for that year.
    """
    records: Dict[int, pd.Series] = {}
    term_of: Dict[int, str] = {}
    for name, first_year, last_year, *_ in terms:
        inherited = year_value_fn(first_year - 1)
        for year in range(first_year, last_year + 1):
            records[year] = year_value_fn(year) - inherited
            term_of[year] = name
    innov = pd.DataFrame(records).T
    innov["Term"] = pd.Series(term_of)
    return innov


def cmpi_scores_from_innovations(
    innovations: pd.DataFrame,
    terms: List[Tuple[str, int, int, str, str]],
    variables: Optional[List[str]] = None,
    pool_start: Optional[int] = None,
    pool_end: Optional[int] = None,
    return_pool: bool = False,
) -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
    """CMPI from a pre-computed innovations DataFrame.

    Returns a DataFrame indexed by term name with component + CMPI columns (sorted by CMPI desc).
    If return_pool=True also returns the (possibly sliced) pool with Pos columns.
    """
    if variables is None:
        variables = CMPI_VARIABLES

    pool_start = innovations.index.min() if pool_start is None else pool_start
    pool_end = innovations.index.max() if pool_end is None else pool_end

    pool = innovations[
        (innovations.index >= pool_start) & (innovations.index <= pool_end)
    ].copy()

    for col in variables:
        pool = _percentile_assign(pool, col, ascending=CMPI_SORT_ASCENDING[col])

    rows: Dict[str, Dict[str, float]] = {}
    for name, first_year, last_year, *_ in terms:
        years = [y for y in range(first_year, last_year + 1) if pool_start <= y <= pool_end]
        if not years:
            continue
        comp = {col: pool.loc[years, col + "Pos"].mean() for col in variables}
        comp["CMPI"] = sum(comp.values()) / len(variables)
        rows[name] = comp

    result = pd.DataFrame(rows).T.sort_values("CMPI", ascending=False)
    return (result, pool) if return_pool else result


def fpi_scores_from_innovations(
    fpi_innovations: pd.DataFrame,
    terms: List[Tuple[str, int, int, str, str]],
    pool_start: Optional[int] = None,
    pool_end: Optional[int] = None,
) -> pd.DataFrame:
    """FPI from a pre-computed 5-variable innovations DataFrame (same percentile machinery)."""
    pool_start = fpi_innovations.index.min() if pool_start is None else pool_start
    pool_end = fpi_innovations.index.max() if pool_end is None else pool_end

    pool = fpi_innovations[
        (fpi_innovations.index >= pool_start) & (fpi_innovations.index <= pool_end)
    ].copy()

    for col in FPI_VARIABLES:
        pool = _percentile_assign(pool, col, ascending=FPI_SORT[col])

    rows: Dict[str, Dict[str, float]] = {}
    for name, first_year, last_year, *_ in terms:
        years = [y for y in range(first_year, last_year + 1) if pool_start <= y <= pool_end]
        if not years:
            continue
        comp = {col: pool.loc[years, col + "Pos"].mean() for col in FPI_VARIABLES}
        comp["FPI"] = sum(comp.values()) / len(FPI_VARIABLES)
        rows[name] = comp

    return pd.DataFrame(rows).T.sort_values("FPI", ascending=False)


# Convenience year-value factories (callers can also supply their own)
def make_cmpi_year_value_fn(
    unified_inflation: pd.Series,
    unified_devaluation: pd.Series,
    unified_interest: pd.Series,
    unified_growth: pd.Series,
) -> callable:
    def year_values(year: int) -> pd.Series:
        return pd.Series(
            {
                "Inflation": unified_inflation.get(year, np.nan),
                "Devaluation": unified_devaluation.get(year, np.nan),
                "Interest": unified_interest.get(year, np.nan),
                "Growth": unified_growth.get(year, np.nan),
            }
        )

    return year_values


def make_fpi_year_value_fn(fpi_data: pd.DataFrame) -> callable:
    def fpi_year_values(year: int) -> pd.Series:
        if year not in fpi_data.index:
            return pd.Series({v: np.nan for v in FPI_VARIABLES})
        row = fpi_data.loc[year]
        return pd.Series({v: row[v] for v in FPI_VARIABLES})

    return fpi_year_values


# --- Rendering helpers (extracted from notebook for reuse and to shrink large result cells) ---

def render_president_img(path: object) -> str:
    """Return HTML for a president photo (or empty placeholder)."""
    if not str(path).strip():
        return '<div style="width:100px; height:100px;"></div>'
    return (
        f'<div style="width:100px; height:100px; display:flex; align-items:center; '
        f'justify-content:center; margin:0 auto;">'
        f'<img src="{path}" style="max-width:100px; max-height:100px; width:auto; height:auto;"/>'
        f'</div>'
    )


def render_minister_img(path: object) -> str:
    """Return HTML for one or more economy ministers (supports 'Name|url' or 'Name|url|Name2|url2')."""
    raw = str(path).strip()
    if not raw:
        return '<div style="width:100px; height:100px;"></div>'
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    blocks = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if p.startswith("http"):
            name = None
            url = p
            i += 1
        else:
            name = p
            if i + 1 < len(parts) and parts[i + 1].startswith("http"):
                url = parts[i + 1]
                i += 2
            else:
                url = None
                i += 1
        if url:
            img = (
                f'<div style="width:100px; height:100px; display:flex; align-items:center; '
                f'justify-content:center; margin:0 auto;">'
                f'<img src="{url}" style="max-width:100px; max-height:100px; width:auto; height:auto;"/>'
                f'</div>'
            )
            if name:
                label = f'<div style="font-size:9px; line-height:1.1; text-align:center; max-width:100px; word-break:break-word; margin-bottom:2px;">{name}</div>'
                blocks.append(label + img)
            else:
                blocks.append(img)
        else:
            if name:
                box = (
                    f'<div style="width:100px; height:100px; display:flex; align-items:center; '
                    f'justify-content:center; font-size:9px; text-align:center; padding:3px; '
                    f'box-sizing:border-box; word-break:break-word;">{name}</div>'
                )
                blocks.append(box)
    return "".join(blocks) if blocks else '<div style="width:100px; height:100px;"></div>'


# Back-compat aliases (so existing notebook formatters={"President": president_img, ...} keep working
# while we clean up the notebook cells). These point to the extracted pure versions.
president_img = render_president_img
minister_img = render_minister_img


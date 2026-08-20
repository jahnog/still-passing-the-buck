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
FPI_RATIO_GAP_COLUMNS: Tuple[str, ...] = ("Result_Revenue", "Result_DebtServ")
FPI_RATIO_GAP_YEARS: Tuple[int, ...] = (1861, 1862, 1863)
FPI_RATIO_GAP_ENDPOINTS: Tuple[int, int] = (1860, 1864)
PROGRAM_CONTINUITY_DOMAINS = {
    "fiscal",
    "monetary",
    "exchange_rate",
    "banking",
    "sovereign_debt",
}


def term_year_assignment(
    terms: List[Tuple[str, int, int, str, str]],
    start_year: int,
    end_year: int,
) -> Dict[int, str]:
    """Return a complete, non-overlapping administration assignment by year."""
    assignment: Dict[int, str] = {}
    for name, first_year, last_year, *_ in terms:
        if first_year > last_year:
            raise ValueError(f"Invalid term for {name}: {first_year}>{last_year}")
        for year in range(first_year, last_year + 1):
            if year in assignment:
                raise ValueError(
                    f"Overlapping term assignment for {year}: "
                    f"{assignment[year]} and {name}"
                )
            assignment[year] = name

    expected = set(range(start_year, end_year + 1))
    actual = set(assignment)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"Term assignment does not partition {start_year}-{end_year}; "
            f"missing={missing}, extra={extra}"
        )
    return assignment


def apply_program_continuity_exceptions(
    majority_terms: List[Tuple[str, int, int, str, str]],
    exceptions: List[dict],
    *,
    min_continuous_domains: int = 4,
) -> List[Tuple[str, int, int, str, str]]:
    """Move qualifying transition years to outgoing-originated policy episodes.

    Each exception must identify ``year``, ``outgoing``, ``incoming`` and five
    boolean ``domains``. The year moves only when the incoming administration
    owns it in the majority specification, the outgoing economy minister is
    retained through year-end, the transition year is the program's first full
    calendar-year observation, and at least ``min_continuous_domains`` are true.
    """
    adjusted = [list(term) for term in majority_terms]
    by_name = {term[0]: term for term in adjusted}

    for exception in exceptions:
        year = int(exception["year"])
        domains = exception["domains"]
        if set(domains) != PROGRAM_CONTINUITY_DOMAINS:
            raise ValueError(
                f"Continuity exception for {year} must assess exactly "
                f"{sorted(PROGRAM_CONTINUITY_DOMAINS)}"
            )
        qualifies = (
            bool(exception["incoming_would_receive_year"])
            and bool(exception["economy_minister_retained_through_year_end"])
            and int(exception["first_complete_calendar_year"]) == year
            and sum(bool(value) for value in domains.values())
            >= min_continuous_domains
        )
        if not qualifies:
            continue

        outgoing = by_name[exception["outgoing"]]
        incoming = by_name[exception["incoming"]]
        if outgoing[2] != year - 1 or incoming[1] != year:
            raise ValueError(
                f"Continuity exception for {year} is not a majority-rule boundary: "
                f"{outgoing[0]} ends {outgoing[2]}, {incoming[0]} starts {incoming[1]}"
            )
        outgoing[2] = year
        incoming[1] = year + 1

    return [tuple(term) for term in adjusted]


def splice_series(hist_part: pd.Series, modern_part: pd.Series) -> pd.Series:
    """Splice historical and modern series (priority to non-NaN historical values).

    The historical (paper-authors') value is used wherever it exists; the modern
    series fills all other years. This mirrors the notebook's `_splice`, keeping a
    single, well-defined data regime per year.
    """
    result = modern_part.copy()
    result = result.reindex(result.index.union(hist_part.index))
    hist_valid = hist_part.dropna()
    result[hist_valid.index] = hist_valid
    return result.sort_index()


def interpolate_fpi_ratio_gaps(hist: pd.DataFrame) -> pd.DataFrame:
    """Fill the workbook's 1861-63 primary-result blanks by arithmetic interpolation.

    The paper-author source has no Result_Revenue or Result_DebtServ observations
    between the 1860 and 1864 endpoints. Geometric interpolation is undefined
    because Result_Revenue changes sign. Filling at the raw-ratio stage keeps
    every FPI component on the same 173-year pool for scoring and for
    contemporaneous averages.
    """
    hist = hist.copy()
    start_year, end_year = FPI_RATIO_GAP_ENDPOINTS
    span = end_year - start_year
    missing_endpoints = [year for year in (start_year, end_year) if year not in hist.index]
    if missing_endpoints:
        raise ValueError(f"Cannot interpolate FPI ratio gaps without {missing_endpoints}")
    already_filled = [
        col
        for col in FPI_RATIO_GAP_COLUMNS
        if hist.loc[list(FPI_RATIO_GAP_YEARS), col].notna().any()
    ]
    if already_filled:
        raise ValueError(
            "FPI ratio gaps must be blank in the source before interpolation: "
            + ", ".join(already_filled)
        )
    for col in FPI_RATIO_GAP_COLUMNS:
        start = hist.loc[start_year, col]
        end = hist.loc[end_year, col]
        if pd.isna(start) or pd.isna(end):
            raise ValueError(f"Interpolation endpoints for {col!r} must be observed")
        for year in FPI_RATIO_GAP_YEARS:
            weight = (year - start_year) / span
            hist.loc[year, col] = start + weight * (end - start)
    return hist


def composite_rate(
    start_level: float, end_level: float, years: int, periods_per_year: int
) -> float:
    """Compound annual rate used for descriptive term-average tables."""
    if years <= 0:
        return 0.0
    return periods_per_year * (pow((end_level / start_level), 1 / (periods_per_year * years)) - 1)


def _percentile_assign(
    df: pd.DataFrame,
    col: str,
    ascending: bool,
) -> pd.DataFrame:
    """Assign [0, 1] percentile positions in sort order (0 = worst for the variable's semantics)."""
    missing = df[col].isna()
    if missing.any():
        # NaN sorts last, so it would silently receive the *best* percentile.
        bad_years = list(df.index[missing])
        raise ValueError(f"NaN innovations in pool column {col!r} for years {bad_years}")

    n = int((~missing).sum())
    if n == 0:
        df[col + "Pos"] = 0.0
        return df
    # Tied innovations share the average of the percentile slots they span, so identical
    # values always score identically. This matters: the 1852-1997 interest series is built
    # from flat term averages, leaving only 57 distinct values in that column and putting 86%
    # of its 173 observations in a tied group; resolving them in sort order left the headline
    # ranking dependent on a non-stable sort.
    ranks = df[col].rank(method="average", ascending=ascending)
    df[col + "Pos"] = (ranks - 1.0) / n
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

    pool_years = set(pool.index)
    rows: Dict[str, Dict[str, float]] = {}
    for name, first_year, last_year, *_ in terms:
        years = [
            y
            for y in range(first_year, last_year + 1)
            if pool_start <= y <= pool_end and y in pool_years
        ]
        if not years:
            continue
        comp = {col: pool.loc[years, col + "Pos"].mean() for col in variables}
        comp["CMPI"] = sum(comp.values()) / len(variables)
        rows[name] = comp

    if not rows:
        result = pd.DataFrame(columns=[*variables, "CMPI"])
    else:
        result = pd.DataFrame(rows).T.sort_values("CMPI", ascending=False)
    return (result, pool) if return_pool else result


def fpi_scores_from_innovations(
    fpi_innovations: pd.DataFrame,
    terms: List[Tuple[str, int, int, str, str]],
    pool_start: Optional[int] = None,
    pool_end: Optional[int] = None,
    return_pool: bool = False,
) -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
    """FPI from a pre-computed 5-variable innovations DataFrame (same percentile machinery)."""
    pool_start = fpi_innovations.index.min() if pool_start is None else pool_start
    pool_end = fpi_innovations.index.max() if pool_end is None else pool_end

    pool = fpi_innovations[
        (fpi_innovations.index >= pool_start) & (fpi_innovations.index <= pool_end)
    ].copy()

    for col in FPI_VARIABLES:
        pool = _percentile_assign(pool, col, ascending=FPI_SORT[col])

    pool_years = set(pool.index)
    rows: Dict[str, Dict[str, float]] = {}
    for name, first_year, last_year, *_ in terms:
        years = [
            y
            for y in range(first_year, last_year + 1)
            if pool_start <= y <= pool_end and y in pool_years
        ]
        if not years:
            continue
        comp = {col: pool.loc[years, col + "Pos"].mean() for col in FPI_VARIABLES}
        comp["FPI"] = sum(comp.values()) / len(FPI_VARIABLES)
        rows[name] = comp

    if not rows:
        result = pd.DataFrame(columns=[*FPI_VARIABLES, "FPI"])
    else:
        result = pd.DataFrame(rows).T.sort_values("FPI", ascending=False)
    return (result, pool) if return_pool else result


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

def _is_img_ref(part: str) -> bool:
    """True for portrait references: remote URLs or image file paths (never minister names)."""
    return part.startswith("http") or part.lower().endswith((".jpg", ".jpeg", ".png"))


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
        if _is_img_ref(p):
            name = None
            url = p
            i += 1
        else:
            name = p
            if i + 1 < len(parts) and _is_img_ref(parts[i + 1]):
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


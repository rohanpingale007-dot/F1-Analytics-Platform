"""
data_utils.py
Data loading, cleaning and shared aggregation helpers for the F1 Analytics Dashboard.
"""
import os
import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "f1_master_clean.csv")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load the pre-cleaned master results table."""
    df = pd.read_csv(DATA_PATH, parse_dates=["race_date"])
    bool_cols = ["classified", "dns", "dnf", "win", "podium", "points_finish"]
    for c in bool_cols:
        df[c] = df[c].astype(bool)
    return df


def apply_filters(
    df: pd.DataFrame,
    seasons=None,
    drivers=None,
    constructors=None,
    circuits=None,
    countries=None,
) -> pd.DataFrame:
    """Apply the global sidebar filters. Empty/None selections mean 'no filter'."""
    out = df
    if seasons:
        out = out[out["season"].isin(seasons)]
    if drivers:
        out = out[out["driver_name"].isin(drivers)]
    if constructors:
        out = out[out["constructor"].isin(constructors)]
    if circuits:
        out = out[out["circuit_name"].isin(circuits)]
    if countries:
        out = out[out["country"].isin(countries)]
    return out


def format_seconds(sec):
    """Format a seconds float as m:ss.sss, used for fastest lap times."""
    if pd.isna(sec):
        return "N/A"
    m = int(sec // 60)
    s = sec - m * 60
    return f"{m}:{s:06.3f}"


def safe_mean(series):
    if series is None or len(series.dropna()) == 0:
        return np.nan
    return series.mean()


def pct(numerator, denominator, decimals=1):
    if denominator in (0, None) or pd.isna(denominator) or denominator == 0:
        return np.nan
    return round(100 * numerator / denominator, decimals)


# ---------------------------------------------------------------------------
# Reusable aggregation helpers shared across pages
# ---------------------------------------------------------------------------

def driver_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per driver with headline career/period stats, for the filtered df."""
    if df.empty:
        return pd.DataFrame()
    starts = df[~df["dns"]]
    g = df.groupby("driver_name")
    gs = starts.groupby("driver_name")
    summary = pd.DataFrame({
        "races": g["race_id"].nunique(),
        "wins": g["win"].sum(),
        "podiums": g["podium"].sum(),
        "points": g["points"].sum(),
        "avg_finish": gs["finish_position"].mean(),
        "avg_grid": gs["grid_position"].apply(lambda s: s[s > 0].mean()),
        "dnfs": g["dnf"].sum(),
        "starts": gs.size(),
    })
    summary["win_pct"] = (summary["wins"] / summary["starts"] * 100).round(1)
    summary["podium_pct"] = (summary["podiums"] / summary["starts"] * 100).round(1)
    summary["dnf_pct"] = (summary["dnfs"] / summary["starts"] * 100).round(1)
    return summary.reset_index().sort_values("points", ascending=False)


def constructor_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    starts = df[~df["dns"]]
    g = df.groupby("constructor")
    gs = starts.groupby("constructor")
    summary = pd.DataFrame({
        "races": g["race_id"].nunique(),
        "wins": g["win"].sum(),
        "podiums": g["podium"].sum(),
        "points": g["points"].sum(),
        "avg_finish": gs["finish_position"].mean(),
        "dnfs": g["dnf"].sum(),
        "starts": gs.size(),
    })
    summary["dnf_pct"] = (summary["dnfs"] / summary["starts"] * 100).round(1)
    return summary.reset_index().sort_values("points", ascending=False)

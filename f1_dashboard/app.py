"""
F1 Analytics Platform
======================
A portfolio-grade Formula 1 analytics dashboard built with Streamlit + Plotly.

Run with:
    streamlit run app.py
"""
import streamlit as st

from data_utils import load_data, apply_filters
from styles import inject_css, apply_plotly_theme
from pages_lib import (
    overview, driver, constructor, season,
    qualifying_vs_race, circuit, reliability, pitstop, fastestlap,
)

st.set_page_config(
    page_title="F1 Analytics Platform",
    page_icon="\U0001F3CE",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
apply_plotly_theme()

df = load_data()

# ---------------------------------------------------------------------------
# Sidebar — branding, navigation and global filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 4px 0 14px 0;">
            <div style="font-size:1.05rem; font-weight:800; letter-spacing:0.02em;">
                F1 ANALYTICS <span style="color:#E10600;">PLATFORM</span>
            </div>
            <div style="font-size:0.75rem; color:#8B93A7; margin-top:2px;">
                Driver, constructor & race intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    PAGES = {
        "Overview": overview,
        "Driver Analytics": driver,
        "Constructor Analytics": constructor,
        "Season Analysis": season,
        "Qualifying vs Race": qualifying_vs_race,
        "Circuit Analysis": circuit,
        "Reliability": reliability,
        "Pit Stop Analysis": pitstop,
        "Fastest Lap": fastestlap,
    }
    page_name = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem; letter-spacing:0.08em; color:#8B93A7; '
        'font-weight:700; margin-bottom:6px;">GLOBAL FILTERS</div>',
        unsafe_allow_html=True,
    )

    min_season, max_season = int(df["season"].min()), int(df["season"].max())
    season_range = st.slider(
        "Season range", min_value=min_season, max_value=max_season,
        value=(min_season, max_season),
    )
    seasons_selected = list(range(season_range[0], season_range[1] + 1))

    country_sel = st.multiselect("Country", sorted(df["country"].unique()))

    # narrow driver/constructor/circuit option lists by season+country so the
    # dropdowns stay relevant to what's actually selectable
    scoped = df[df["season"].between(*season_range)]
    if country_sel:
        scoped = scoped[scoped["country"].isin(country_sel)]

    driver_sel = st.multiselect("Driver", sorted(scoped["driver_name"].unique()))
    constructor_sel = st.multiselect("Constructor", sorted(scoped["constructor"].unique()))
    circuit_sel = st.multiselect("Circuit", sorted(scoped["circuit_name"].unique()))

    st.divider()
    st.caption(
        f"Dataset: {df['season'].min()}\u2013{df['season'].max()} \u00b7 "
        f"{len(df):,} results \u00b7 {df['race_id'].nunique():,} races"
    )

filtered_df = apply_filters(
    df,
    seasons=seasons_selected,
    drivers=driver_sel,
    constructors=constructor_sel,
    circuits=circuit_sel,
    countries=country_sel,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.2rem;">
        <h1 style="margin:0;">F1 Analytics Platform</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

active_filters = []
if seasons_selected != list(range(min_season, max_season + 1)):
    active_filters.append(f"Seasons {season_range[0]}\u2013{season_range[1]}")
if driver_sel:
    active_filters.append(f"{len(driver_sel)} driver(s)")
if constructor_sel:
    active_filters.append(f"{len(constructor_sel)} constructor(s)")
if circuit_sel:
    active_filters.append(f"{len(circuit_sel)} circuit(s)")
if country_sel:
    active_filters.append(f"{len(country_sel)} countr{'y' if len(country_sel)==1 else 'ies'}")

filter_caption = " \u00b7 ".join(active_filters) if active_filters else "All seasons, all drivers, all constructors"
st.caption(filter_caption)
st.write("")

# ---------------------------------------------------------------------------
# Route to selected page
# ---------------------------------------------------------------------------
PAGES[page_name].render(filtered_df)

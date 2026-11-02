import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Constructor Analytics")
    st.caption("Team-level performance, driver contribution and reliability.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    constructors = sorted(df["constructor"].unique())
    default_c = df.groupby("constructor")["points"].sum().idxmax()
    constructor = st.selectbox("Select a constructor", constructors, index=constructors.index(default_c))

    d = df[df["constructor"] == constructor].sort_values("race_date")
    starts = d[~d["dns"]]

    cols = st.columns(6)
    kpis = [
        ("Wins", int(d["win"].sum())),
        ("Podiums", int(d["podium"].sum())),
        ("Points", f"{d['points'].sum():,.0f}"),
        ("Avg Finish", f"{starts['finish_position'].mean():.1f}" if len(starts) else "N/A"),
        ("DNFs", int(d["dnf"].sum())),
        ("Races", d["race_id"].nunique()),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        section_header("Constructor Points by Season")
        by_season = d.groupby("season")["points"].sum().reset_index()
        fig = px.bar(by_season, x="season", y="points")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[0])
        fig.update_layout(height=320, xaxis_title="Season", yaxis_title="Points")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Constructor Wins by Season")
        wins = d.groupby("season")["win"].sum().reset_index()
        fig = px.bar(wins, x="season", y="win")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=320, xaxis_title="Season", yaxis_title="Wins")
        st.plotly_chart(fig, use_container_width=True)

    section_header("Constructor Performance Trend", "Average finish position per season (lower is better)")
    trend = starts.groupby("season")["finish_position"].mean().reset_index()
    if trend.empty:
        st.info("No data for a performance trend.")
    else:
        fig = px.line(trend, x="season", y="finish_position", markers=True)
        fig.update_traces(line_color=CATEGORICAL_SEQUENCE[4])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=320, xaxis_title="Season", yaxis_title="Avg Finish Position")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section_header("Driver Contribution to Points")
        contrib = d.groupby("driver_name")["points"].sum().sort_values(ascending=False)
        contrib = contrib[contrib > 0]
        if contrib.empty:
            st.info("No points scored by any driver for this selection.")
        else:
            fig = px.pie(values=contrib.values, names=contrib.index, hole=0.55)
            fig.update_traces(textinfo="percent+label", textfont_size=11)
            fig.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Reliability by Season", "DNF rate per season")
        rel = starts.groupby("season")["dnf"].mean().reset_index()
        rel["dnf"] = rel["dnf"] * 100
        if rel.empty:
            st.info("No reliability data available.")
        else:
            fig = px.area(rel, x="season", y="dnf")
            fig.update_traces(line_color=CATEGORICAL_SEQUENCE[3], fillcolor="rgba(225,6,0,0.15)")
            fig.update_layout(height=360, xaxis_title="Season", yaxis_title="DNF Rate (%)")
            st.plotly_chart(fig, use_container_width=True)

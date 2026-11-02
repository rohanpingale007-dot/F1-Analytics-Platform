import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE
from insights import generate_executive_insights


def render_insights_panel(df: pd.DataFrame):
    insights = generate_executive_insights(df, max_insights=5)
    rows_html = ""
    for ins in insights:
        metric_html = f'<span style="float:right;color:#00D4B5;font-weight:700;font-size:0.82rem;">{ins["metric"]}</span>' if ins.get("metric") else ""
        rows_html += f"""
        <div class="insight-row">
            <div class="insight-dot">&#9679;</div>
            <div style="flex:1;">
                <div class="insight-category">{ins['category']}</div>
                <div class="insight-title">{ins['title']}{metric_html}</div>
                <div class="insight-text">{ins['insight']}</div>
            </div>
        </div>
        """
    st.markdown(
        f"""
        <div class="insights-panel">
            <div class="insights-title">EXECUTIVE INSIGHTS</div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render(df: pd.DataFrame):
    st.markdown("### Overview")
    st.caption("A high-level read of the currently filtered dataset.")

    render_insights_panel(df)

    if df.empty:
        st.warning("No data matches the current filters. Adjust your selection in the sidebar.")
        return

    # --- KPI row ---------------------------------------------------------
    total_points = df["points"].sum()
    cols = st.columns(6)
    kpis = [
        ("Seasons", df["season"].nunique()),
        ("Races", df["race_id"].nunique()),
        ("Drivers", df["driver_name"].nunique()),
        ("Constructors", df["constructor"].nunique()),
        ("Circuits", df["circuit_name"].nunique()),
        ("Total Points", f"{total_points:,.0f}"),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")

    # --- Points by season --------------------------------------------------
    section_header("Points by Season", "Total championship points awarded per season")
    by_season = df.groupby("season")["points"].sum().reset_index()
    fig = px.bar(by_season, x="season", y="points")
    fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[0])
    fig.update_layout(height=340, xaxis_title="Season", yaxis_title="Points")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        section_header("Top 10 Drivers by Wins")
        wins = df.groupby("driver_name")["win"].sum().sort_values(ascending=False).head(10)
        wins = wins[wins > 0]
        if wins.empty:
            st.info("No wins recorded for this selection.")
        else:
            wins_df = wins.reset_index().rename(columns={"win": "wins"}).iloc[::-1]
            fig = px.bar(wins_df, x="wins", y="driver_name", orientation="h")
            fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1], showlegend=False)
            fig.update_layout(height=380, xaxis_title="Wins", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Top 10 Constructors by Wins")
        wins_c = df.groupby("constructor")["win"].sum().sort_values(ascending=False).head(10)
        wins_c = wins_c[wins_c > 0]
        if wins_c.empty:
            st.info("No wins recorded for this selection.")
        else:
            wins_c_df = wins_c.reset_index().rename(columns={"win": "wins"}).iloc[::-1]
            fig = px.bar(wins_c_df, x="wins", y="constructor", orientation="h")
            fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2], showlegend=False)
            fig.update_layout(height=380, xaxis_title="Wins", yaxis_title="", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # --- Wins by constructor over time -------------------------------------
    section_header("Wins by Constructor Over Time", "Top 6 constructors by total wins in the current selection")
    top6 = df.groupby("constructor")["win"].sum().sort_values(ascending=False).head(6).index
    trend = (
        df[df["constructor"].isin(top6)]
        .groupby(["season", "constructor"])["win"]
        .sum()
        .reset_index()
    )
    if trend.empty:
        st.info("No constructor win data for this selection.")
    else:
        fig = px.line(trend, x="season", y="win", color="constructor", markers=True)
        fig.update_layout(height=380, xaxis_title="Season", yaxis_title="Wins", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    # --- DNF trend by season -------------------------------------------------
    section_header("DNF Trend by Season", "Share of starts ending in a DNF, per season")
    starts = df[~df["dns"]]
    dnf_trend = starts.groupby("season")["dnf"].mean().reset_index()
    dnf_trend["dnf"] = dnf_trend["dnf"] * 100
    fig = px.area(dnf_trend, x="season", y="dnf")
    fig.update_traces(line_color=CATEGORICAL_SEQUENCE[3], fillcolor="rgba(225,6,0,0.15)")
    fig.update_layout(height=320, xaxis_title="Season", yaxis_title="DNF Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

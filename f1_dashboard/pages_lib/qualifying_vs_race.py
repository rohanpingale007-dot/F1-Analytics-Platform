import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Qualifying vs Race")
    st.caption(
        "How well grid position predicts race outcome. All figures below are "
        "descriptive correlations from the filtered results — not causal claims."
    )

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    d = df[(~df["dns"]) & (df["grid_position"] > 0)].copy()
    if d.empty:
        st.info("No graded starts (with a known grid position) in this selection.")
        return

    d["position_change"] = d["grid_position"] - d["finish_position"]

    cols = st.columns(4)
    kpi_card_data = [
        ("Graded Starts", f"{len(d):,}"),
        ("Avg Position Change", f"{d['position_change'].mean():+.2f}"),
        ("Win Rate from Pole", f"{d[d['grid_position']==1]['win'].mean()*100:.1f}%" if (d['grid_position']==1).any() else "N/A"),
        ("Podium Rate, Top-3 Start", f"{d[d['grid_position']<=3]['podium'].mean()*100:.1f}%" if (d['grid_position']<=3).any() else "N/A"),
    ]
    for c, (label, value) in zip(cols, kpi_card_data):
        with c:
            kpi_card(label, value)

    st.write("")
    section_header("Grid vs Finish Position", "Each point is one race result. The dotted line marks 'no change'.")
    sample = d if len(d) <= 6000 else d.sample(6000, random_state=42)
    fig = px.scatter(
        sample, x="grid_position", y="finish_position",
        opacity=0.35, color_discrete_sequence=[CATEGORICAL_SEQUENCE[1]],
        hover_data=["driver_name", "season", "race_name"],
    )
    max_pos = int(max(d["grid_position"].max(), d["finish_position"].max()))
    fig.add_shape(type="line", x0=1, y0=1, x1=max_pos, y1=max_pos,
                  line=dict(color="#8B93A7", dash="dot"))
    fig.update_layout(height=420, xaxis_title="Grid Position", yaxis_title="Finish Position")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Average Finish by Starting Position")
        by_grid = d.groupby("grid_position")["finish_position"].mean().reset_index()
        by_grid = by_grid[by_grid["grid_position"] <= 20]
        fig = px.line(by_grid, x="grid_position", y="finish_position", markers=True)
        fig.update_traces(line_color=CATEGORICAL_SEQUENCE[0])
        fig.update_layout(height=360, xaxis_title="Grid Position", yaxis_title="Avg Finish Position")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Position Gained/Lost Distribution")
        fig = px.histogram(d, x="position_change", nbins=40)
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[4])
        fig.add_vline(x=0, line_dash="dot", line_color="#8B93A7")
        fig.update_layout(height=360, xaxis_title="Positions Gained (+) / Lost (\u2212)", yaxis_title="Results")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section_header("Win Rate by Starting Position")
        by_grid_wr = d.groupby("grid_position")["win"].mean().reset_index()
        by_grid_wr = by_grid_wr[by_grid_wr["grid_position"] <= 20]
        by_grid_wr["win"] *= 100
        fig = px.bar(by_grid_wr, x="grid_position", y="win")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=340, xaxis_title="Grid Position", yaxis_title="Win Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Podium Rate by Starting Position")
        by_grid_pr = d.groupby("grid_position")["podium"].mean().reset_index()
        by_grid_pr = by_grid_pr[by_grid_pr["grid_position"] <= 20]
        by_grid_pr["podium"] *= 100
        fig = px.bar(by_grid_pr, x="grid_position", y="podium")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2])
        fig.update_layout(height=340, xaxis_title="Grid Position", yaxis_title="Podium Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

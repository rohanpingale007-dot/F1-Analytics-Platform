import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE
from data_utils import format_seconds


def render(df: pd.DataFrame):
    st.markdown("### Fastest Lap")
    st.caption("Outright pace: fastest-lap speed and time across drivers, teams, circuits and seasons.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    speed_df = df.dropna(subset=["fastest_lap_speed"])
    coverage = len(speed_df) / len(df) * 100 if len(df) else 0

    cols = st.columns(3)
    kpis = [
        ("Avg Fastest-Lap Speed", f"{speed_df['fastest_lap_speed'].mean():.1f} km/h" if len(speed_df) else "N/A"),
        ("Fastest Recorded Lap", f"{speed_df['fastest_lap_speed'].max():.1f} km/h" if len(speed_df) else "N/A"),
        ("Data Coverage", f"{coverage:.0f}% of results"),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    if coverage < 100:
        st.caption(
            f"Fastest-lap speed/time is missing for {100 - coverage:.0f}% of results "
            "(older seasons in particular) and is excluded from the averages below."
        )

    if speed_df.empty:
        st.info("No fastest-lap speed data available for this selection.")
        return

    st.write("")
    section_header("Average Fastest-Lap Speed by Season")
    by_season = speed_df.groupby("season")["fastest_lap_speed"].mean().reset_index()
    fig = px.line(by_season, x="season", y="fastest_lap_speed", markers=True)
    fig.update_traces(line_color=CATEGORICAL_SEQUENCE[0])
    fig.update_layout(height=340, xaxis_title="Season", yaxis_title="Avg Speed (km/h)")
    st.plotly_chart(fig, use_container_width=True)

    section_header("Fastest Circuits", "Average fastest-lap speed by circuit")
    by_circuit = speed_df.groupby("circuit_name")["fastest_lap_speed"].mean().sort_values(ascending=False).head(15)
    by_circuit_df = by_circuit.reset_index().rename(columns={"fastest_lap_speed": "avg_speed"}).iloc[::-1]
    fig = px.bar(by_circuit_df, x="avg_speed", y="circuit_name", orientation="h")
    fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2], showlegend=False)
    fig.update_layout(height=440, xaxis_title="Avg Speed (km/h)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Driver Fastest-Lap Performance", "Top 15 drivers by average fastest-lap speed (min. 5 results)")
        grp = speed_df.groupby("driver_name").agg(n=("fastest_lap_speed", "size"), avg=("fastest_lap_speed", "mean"))
        grp = grp[grp["n"] >= 5].sort_values("avg", ascending=False).head(15)
        fig = px.bar(grp.sort_values("avg")[["avg"]].reset_index(), x="avg", y="driver_name", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1])
        fig.update_layout(height=440, xaxis_title="Avg Speed (km/h)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Constructor Fastest-Lap Performance", "Top 15 constructors by average fastest-lap speed (min. 5 results)")
        grp2 = speed_df.groupby("constructor").agg(n=("fastest_lap_speed", "size"), avg=("fastest_lap_speed", "mean"))
        grp2 = grp2[grp2["n"] >= 5].sort_values("avg", ascending=False).head(15)
        fig = px.bar(grp2.sort_values("avg")[["avg"]].reset_index(), x="avg", y="constructor", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=440, xaxis_title="Avg Speed (km/h)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    time_df = df.dropna(subset=["fastest_lap_time_sec"])
    if not time_df.empty:
        section_header("Outright Fastest Laps (Time)", "Quickest recorded lap per circuit in the current selection")
        idx = time_df.groupby("circuit_name")["fastest_lap_time_sec"].idxmin()
        best = time_df.loc[idx, ["circuit_name", "driver_name", "season", "fastest_lap_time_sec"]]
        best = best.sort_values("fastest_lap_time_sec").head(15).copy()
        best["Fastest Lap"] = best["fastest_lap_time_sec"].apply(format_seconds)
        best = best.rename(columns={
            "circuit_name": "Circuit", "driver_name": "Driver", "season": "Season"
        })[["Circuit", "Driver", "Season", "Fastest Lap"]]
        st.dataframe(best, use_container_width=True, hide_index=True)

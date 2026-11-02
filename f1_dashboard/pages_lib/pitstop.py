import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Pit Stop Analysis")
    st.caption(
        "Pit-stop counts by season, team and circuit. Associations with finishing "
        "position are descriptive, not causal — strategy, safety cars and race "
        "incidents all influence stop counts."
    )

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    starts = df[(~df["dns"]) & (df["laps"] > 0)]

    cols = st.columns(3)
    kpis = [
        ("Avg Pit Stops / Race", f"{starts['pit_stops'].mean():.2f}" if len(starts) else "N/A"),
        ("Max Pit Stops (single race)", int(starts["pit_stops"].max()) if len(starts) else 0),
        ("Zero-Stop Results", int((starts["pit_stops"] == 0).sum())),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")
    section_header("Average Pit Stops by Season")
    by_season = starts.groupby("season")["pit_stops"].mean().reset_index()
    fig = px.line(by_season, x="season", y="pit_stops", markers=True)
    fig.update_traces(line_color=CATEGORICAL_SEQUENCE[0])
    fig.update_layout(height=340, xaxis_title="Season", yaxis_title="Avg Pit Stops")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Pit Stops by Constructor", "Top 15 by number of starts")
        grp = starts.groupby("constructor").agg(n=("pit_stops", "size"), avg=("pit_stops", "mean"))
        grp = grp.sort_values("n", ascending=False).head(15)
        fig = px.bar(grp.sort_values("avg").reset_index(), x="avg", y="constructor", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1])
        fig.update_layout(height=440, xaxis_title="Avg Pit Stops", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Pit Stops by Circuit", "Top 15 by number of starts")
        grp2 = starts.groupby("circuit_name").agg(n=("pit_stops", "size"), avg=("pit_stops", "mean"))
        grp2 = grp2.sort_values("n", ascending=False).head(15)
        fig = px.bar(grp2.sort_values("avg").reset_index(), x="avg", y="circuit_name", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2])
        fig.update_layout(height=440, xaxis_title="Avg Pit Stops", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    section_header("Pit Stops vs Finish Position", "Average number of stops for each finishing position")
    classified = starts[starts["classified"]]
    by_finish = classified.groupby("finish_position")["pit_stops"].mean().reset_index()
    by_finish = by_finish[by_finish["finish_position"] <= 20]
    fig = px.bar(by_finish, x="finish_position", y="pit_stops")
    fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
    fig.update_layout(height=340, xaxis_title="Finish Position", yaxis_title="Avg Pit Stops")
    st.plotly_chart(fig, use_container_width=True)

import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Circuit Analysis")
    st.caption("Track-by-track characteristics: pace, attrition and pit-stop patterns.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    circuits = sorted(df["circuit_name"].unique())
    default_c = df["circuit_name"].value_counts().idxmax()
    circuit = st.selectbox("Select a circuit", circuits, index=circuits.index(default_c))

    d = df[df["circuit_name"] == circuit]
    starts = d[~d["dns"]]

    cols = st.columns(5)
    kpis = [
        ("Races Hosted", d["race_id"].nunique()),
        ("Avg Finish", f"{starts['finish_position'].mean():.1f}" if len(starts) else "N/A"),
        ("Avg Fastest-Lap Speed", f"{d['fastest_lap_speed'].mean():.1f} km/h" if d["fastest_lap_speed"].notna().any() else "N/A"),
        ("Avg Pit Stops", f"{starts['pit_stops'].mean():.2f}" if len(starts) else "N/A"),
        ("DNF Rate", f"{starts['dnf'].mean()*100:.1f}%" if len(starts) else "N/A"),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")
    section_header("Fastest Circuits", "Average fastest-lap speed across circuits in the current selection")
    speed_by_circuit = (
        df.dropna(subset=["fastest_lap_speed"])
        .groupby("circuit_name")["fastest_lap_speed"]
        .mean()
        .sort_values(ascending=False)
        .head(15)
    )
    if speed_by_circuit.empty:
        st.info("No fastest-lap speed data available.")
    else:
        colors = [CATEGORICAL_SEQUENCE[3] if c == circuit else CATEGORICAL_SEQUENCE[0] for c in speed_by_circuit.index]
        speed_df = speed_by_circuit.reset_index().rename(columns={"fastest_lap_speed": "avg_speed"}).iloc[::-1]
        fig = px.bar(speed_df, x="avg_speed", y="circuit_name", orientation="h")
        fig.update_traces(marker_color=colors[::-1], showlegend=False)
        fig.update_layout(height=440, xaxis_title="Avg Fastest-Lap Speed (km/h)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("DNF Rate by Circuit", "Top 15 by number of starts in the current selection")
        starts_all = df[~df["dns"]]
        grp = starts_all.groupby("circuit_name").agg(n=("dnf", "size"), dnf_rate=("dnf", "mean"))
        grp = grp.sort_values("n", ascending=False).head(15)
        grp["dnf_rate"] *= 100
        fig = px.bar(grp.reset_index(), x="circuit_name", y="dnf_rate")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=380, xaxis_title="", yaxis_title="DNF Rate (%)", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Pit Stops by Circuit", "Top 15 by number of starts in the current selection")
        grp2 = starts_all.groupby("circuit_name").agg(n=("pit_stops", "size"), avg_pits=("pit_stops", "mean"))
        grp2 = grp2.sort_values("n", ascending=False).head(15)
        fig = px.bar(grp2.reset_index(), x="circuit_name", y="avg_pits")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1])
        fig.update_layout(height=380, xaxis_title="", yaxis_title="Avg Pit Stops", xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    section_header("Average Finishing Position by Circuit", f"Trend at {circuit} across seasons")
    trend = starts.groupby("season")["finish_position"].mean().reset_index()
    if trend.empty:
        st.info("No finishing-position history for this circuit in the current selection.")
    else:
        fig = px.line(trend, x="season", y="finish_position", markers=True)
        fig.update_traces(line_color=CATEGORICAL_SEQUENCE[2])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=340, xaxis_title="Season", yaxis_title="Avg Finish Position (field)")
        st.plotly_chart(fig, use_container_width=True)

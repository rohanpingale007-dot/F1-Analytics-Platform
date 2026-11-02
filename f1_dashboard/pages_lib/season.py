import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Season Analysis")
    st.caption("A single season, race by race.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    seasons = sorted(df["season"].unique(), reverse=True)
    season = st.selectbox("Select a season", seasons, index=0)

    d = df[df["season"] == season]
    winners = d[d["win"]]

    cols = st.columns(5)
    kpis = [
        ("Races", d["race_id"].nunique()),
        ("Different Winners", winners["driver_name"].nunique()),
        ("Drivers", d["driver_name"].nunique()),
        ("Constructors", d["constructor"].nunique()),
        ("Total Points", f"{d['points'].sum():,.0f}"),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        section_header("Driver Points", f"{season} championship standings")
        dp = d.groupby("driver_name")["points"].sum().sort_values(ascending=False).head(15)
        dp_df = dp.reset_index().iloc[::-1]
        fig = px.bar(dp_df, x="points", y="driver_name", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[0], showlegend=False)
        fig.update_layout(height=420, xaxis_title="Points", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Constructor Points", f"{season} championship standings")
        cp = d.groupby("constructor")["points"].sum().sort_values(ascending=False).head(15)
        cp_df = cp.reset_index().iloc[::-1]
        fig = px.bar(cp_df, x="points", y="constructor", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1], showlegend=False)
        fig.update_layout(height=420, xaxis_title="Points", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # order races chronologically
    race_order = (
        d[["race_id", "race_name", "race_date"]]
        .drop_duplicates()
        .sort_values("race_date")
    )
    race_order["race_label"] = race_order["race_name"]

    section_header("Race Winners", f"Winner of each round in {season}, in order")
    win_rows = winners.merge(race_order[["race_id", "race_date"]], on="race_id")
    win_rows = win_rows.sort_values("race_date")
    if win_rows.empty:
        st.info("No classified winners for this selection.")
    else:
        fig = px.bar(win_rows, x="race_name", y="win", color="driver_name",
                      category_orders={"race_name": race_order["race_label"].tolist()})
        fig.update_layout(height=380, xaxis_title="", yaxis_title="", yaxis_visible=False,
                          legend_title="Driver", xaxis_tickangle=-40)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section_header("DNFs by Race")
        starts = d[~d["dns"]].merge(race_order[["race_id", "race_date"]], on="race_id")
        dnf_by_race = starts.groupby(["race_id", "race_name"])["dnf"].sum().reset_index()
        dnf_by_race = dnf_by_race.merge(race_order[["race_id", "race_date"]], on="race_id").sort_values("race_date")
        fig = px.bar(dnf_by_race, x="race_name", y="dnf")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=360, xaxis_title="", yaxis_title="DNFs", xaxis_tickangle=-40)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Fastest-Lap-Speed Trend", "Average fastest-lap speed per race")
        speed = d.dropna(subset=["fastest_lap_speed"]).merge(race_order[["race_id", "race_date"]], on="race_id")
        speed_by_race = speed.groupby(["race_id", "race_name"])["fastest_lap_speed"].mean().reset_index()
        speed_by_race = speed_by_race.merge(race_order[["race_id", "race_date"]], on="race_id").sort_values("race_date")
        if speed_by_race.empty:
            st.info("No fastest-lap speed data available for this season.")
        else:
            fig = px.line(speed_by_race, x="race_name", y="fastest_lap_speed", markers=True)
            fig.update_traces(line_color=CATEGORICAL_SEQUENCE[2])
            fig.update_layout(height=360, xaxis_title="", yaxis_title="Speed (km/h)", xaxis_tickangle=-40)
            st.plotly_chart(fig, use_container_width=True)

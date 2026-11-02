import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def _driver_kpis(d: pd.DataFrame):
    starts = d[~d["dns"]]
    graded = starts[starts["grid_position"] > 0]
    return {
        "wins": int(d["win"].sum()),
        "podiums": int(d["podium"].sum()),
        "points": d["points"].sum(),
        "avg_finish": starts["finish_position"].mean() if len(starts) else np.nan,
        "avg_grid": graded["grid_position"].mean() if len(graded) else np.nan,
        "dnfs": int(d["dnf"].sum()),
        "races": d["race_id"].nunique(),
    }


def _render_kpi_row(k):
    cols = st.columns(7)
    vals = [
        ("Wins", k["wins"]),
        ("Podiums", k["podiums"]),
        ("Points", f"{k['points']:,.0f}"),
        ("Avg Finish", f"{k['avg_finish']:.1f}" if not pd.isna(k["avg_finish"]) else "N/A"),
        ("Avg Grid", f"{k['avg_grid']:.1f}" if not pd.isna(k["avg_grid"]) else "N/A"),
        ("DNFs", k["dnfs"]),
        ("Races", k["races"]),
    ]
    for c, (label, value) in zip(cols, vals):
        with c:
            kpi_card(label, value)


def render(df: pd.DataFrame):
    st.markdown("### Driver Analytics")
    st.caption("Individual driver performance, and head-to-head comparison.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    drivers = sorted(df["driver_name"].unique())
    default_driver = df.groupby("driver_name")["points"].sum().idxmax()
    driver = st.selectbox("Select a driver", drivers, index=drivers.index(default_driver))

    d = df[df["driver_name"] == driver].sort_values("race_date")

    k = _driver_kpis(d)
    _render_kpi_row(k)
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        section_header("Points by Season")
        by_season = d.groupby("season")["points"].sum().reset_index()
        fig = px.bar(by_season, x="season", y="points")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[0])
        fig.update_layout(height=320, xaxis_title="Season", yaxis_title="Points")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Wins & Podiums by Season")
        wp = d.groupby("season").agg(wins=("win", "sum"), podiums=("podium", "sum")).reset_index()
        fig = go.Figure()
        fig.add_bar(x=wp["season"], y=wp["podiums"], name="Podiums", marker_color=CATEGORICAL_SEQUENCE[1])
        fig.add_bar(x=wp["season"], y=wp["wins"], name="Wins", marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(barmode="overlay", height=320, xaxis_title="Season", yaxis_title="Count", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section_header("Grid Position vs Finish Position")
        graded = d[(d["grid_position"] > 0)]
        if graded.empty:
            st.info("No graded starts available.")
        else:
            fig = px.scatter(
                graded, x="grid_position", y="finish_position", color="season",
                hover_data=["race_name", "season", "status"],
                color_continuous_scale=px.colors.sequential.Teal,
            )
            max_pos = max(graded["grid_position"].max(), graded["finish_position"].max())
            fig.add_shape(type="line", x0=1, y0=1, x1=max_pos, y1=max_pos,
                          line=dict(color="#8B93A7", dash="dot"))
            fig.update_layout(height=340, xaxis_title="Grid Position", yaxis_title="Finish Position")
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Finishing-Position Distribution")
        classified = d[d["classified"]]
        if classified.empty:
            st.info("No classified finishes available.")
        else:
            fig = px.histogram(classified, x="finish_position", nbins=20)
            fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2])
            fig.update_layout(height=340, xaxis_title="Finish Position", yaxis_title="Races")
            st.plotly_chart(fig, use_container_width=True)

    section_header("Driver Performance Trend", "Average finish position per season (lower is better)")
    starts = d[~d["dns"]]
    trend = starts.groupby("season")["finish_position"].mean().reset_index()
    if trend.empty:
        st.info("No data for a performance trend.")
    else:
        fig = px.line(trend, x="season", y="finish_position", markers=True)
        fig.update_traces(line_color=CATEGORICAL_SEQUENCE[4])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=320, xaxis_title="Season", yaxis_title="Avg Finish Position")
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    st.divider()
    st.markdown("#### Driver A vs Driver B")
    c1, c2 = st.columns(2)
    with c1:
        driver_a = st.selectbox("Driver A", drivers, index=drivers.index(driver), key="driver_a")
    with c2:
        other_options = [x for x in drivers if x != driver_a] or drivers
        default_b = other_options[0]
        driver_b = st.selectbox("Driver B", other_options, index=0, key="driver_b")

    da = df[df["driver_name"] == driver_a]
    db = df[df["driver_name"] == driver_b]
    ka, kb = _driver_kpis(da), _driver_kpis(db)

    compare_rows = [
        ("Wins", ka["wins"], kb["wins"]),
        ("Podiums", ka["podiums"], kb["podiums"]),
        ("Points", round(ka["points"], 1), round(kb["points"], 1)),
        ("Avg Finish", round(ka["avg_finish"], 2) if not pd.isna(ka["avg_finish"]) else None,
         round(kb["avg_finish"], 2) if not pd.isna(kb["avg_finish"]) else None),
        ("Avg Grid Position", round(ka["avg_grid"], 2) if not pd.isna(ka["avg_grid"]) else None,
         round(kb["avg_grid"], 2) if not pd.isna(kb["avg_grid"]) else None),
        ("DNFs", ka["dnfs"], kb["dnfs"]),
    ]
    comp_df = pd.DataFrame(compare_rows, columns=["Metric", driver_a, driver_b])
    st.dataframe(comp_df.set_index("Metric"), use_container_width=True)

    bar_metrics = ["Wins", "Podiums", "DNFs"]
    bar_df = comp_df[comp_df["Metric"].isin(bar_metrics)].melt(
        id_vars="Metric", var_name="Driver", value_name="Value"
    )
    fig = px.bar(bar_df, x="Metric", y="Value", color="Driver", barmode="group")
    fig.update_layout(height=340, xaxis_title="", yaxis_title="Count", legend_title="")
    st.plotly_chart(fig, use_container_width=True)

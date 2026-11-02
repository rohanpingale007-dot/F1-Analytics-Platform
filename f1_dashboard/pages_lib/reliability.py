import pandas as pd
import plotly.express as px
import streamlit as st

from styles import section_header, kpi_card, CATEGORICAL_SEQUENCE


def render(df: pd.DataFrame):
    st.markdown("### Reliability")
    st.caption("Race status, DNF patterns and how attrition has evolved.")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    starts = df[~df["dns"]]

    cols = st.columns(3)
    kpis = [
        ("DNF Count", int(starts["dnf"].sum())),
        ("DNF %", f"{starts['dnf'].mean()*100:.1f}%" if len(starts) else "N/A"),
        ("Classified Finishes", int(starts["classified"].sum())),
    ]
    for c, (label, value) in zip(cols, kpis):
        with c:
            kpi_card(label, value)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        section_header("DNF Rate by Driver", "Top 15 drivers by number of starts")
        grp = starts.groupby("driver_name").agg(n=("dnf", "size"), dnf_rate=("dnf", "mean"))
        grp = grp.sort_values("n", ascending=False).head(15)
        grp["dnf_rate"] *= 100
        fig = px.bar(grp.sort_values("dnf_rate").reset_index(), x="dnf_rate", y="driver_name", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[3])
        fig.update_layout(height=440, xaxis_title="DNF Rate (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("DNF Rate by Constructor", "Top 15 constructors by number of starts")
        grp2 = starts.groupby("constructor").agg(n=("dnf", "size"), dnf_rate=("dnf", "mean"))
        grp2 = grp2.sort_values("n", ascending=False).head(15)
        grp2["dnf_rate"] *= 100
        fig = px.bar(grp2.sort_values("dnf_rate").reset_index(), x="dnf_rate", y="constructor", orientation="h")
        fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[1])
        fig.update_layout(height=440, xaxis_title="DNF Rate (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    section_header("DNF Rate by Season")
    by_season = starts.groupby("season")["dnf"].mean().reset_index()
    by_season["dnf"] *= 100
    fig = px.area(by_season, x="season", y="dnf")
    fig.update_traces(line_color=CATEGORICAL_SEQUENCE[3], fillcolor="rgba(225,6,0,0.15)")
    fig.update_layout(height=320, xaxis_title="Season", yaxis_title="DNF Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

    section_header("Status Distribution", "All race-classification outcomes in the current selection")
    status_counts = df["status"].value_counts().head(20).reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.bar(status_counts, x="count", y="status", orientation="h")
    fig.update_traces(marker_color=CATEGORICAL_SEQUENCE[2])
    fig.update_layout(height=520, xaxis_title="Results", yaxis_title="",
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

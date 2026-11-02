"""
styles.py
Dark, motorsport-inspired visual theme: CSS for the Streamlit shell + a shared
Plotly template so every chart in the app looks consistent.
"""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --- palette -----------------------------------------------------------
BG = "#0B0E14"
PANEL = "#12161F"
PANEL_BORDER = "#232838"
TEXT = "#E7E9EE"
SUBTEXT = "#8B93A7"
ACCENT = "#E10600"        # restrained F1 red, used sparingly
ACCENT_2 = "#00D4B5"      # teal accent for secondary series
ACCENT_3 = "#3B82F6"      # blue accent
ACCENT_4 = "#F5A623"      # amber accent
GRID = "#1E2330"

CATEGORICAL_SEQUENCE = ["#00D4B5", "#3B82F6", "#F5A623", "#E10600", "#A855F7",
                         "#EC4899", "#84CC16", "#06B6D4", "#F97316", "#64748B"]


def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BG};
            color: {TEXT};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {PANEL};
            border-right: 1px solid {PANEL_BORDER};
        }}
        h1, h2, h3, h4 {{
            font-family: 'Inter', 'Helvetica Neue', sans-serif;
            letter-spacing: -0.01em;
        }}
        h1 {{
            font-weight: 800;
        }}
        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }}
        /* KPI cards */
        .kpi-card {{
            background: linear-gradient(180deg, {PANEL} 0%, #0F1219 100%);
            border: 1px solid {PANEL_BORDER};
            border-radius: 10px;
            padding: 16px 18px;
            height: 100%;
        }}
        .kpi-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {SUBTEXT};
            margin-bottom: 6px;
            font-weight: 600;
        }}
        .kpi-value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: {TEXT};
            line-height: 1.1;
        }}
        .kpi-sub {{
            font-size: 0.75rem;
            color: {SUBTEXT};
            margin-top: 4px;
        }}
        .kpi-accent {{
            color: {ACCENT_2};
        }}
        /* section header strip */
        .section-header {{
            border-left: 3px solid {ACCENT};
            padding-left: 12px;
            margin: 6px 0 14px 0;
        }}
        .section-header h3 {{
            margin: 0;
            font-size: 1.05rem;
            color: {TEXT};
        }}
        .section-header p {{
            margin: 2px 0 0 0;
            color: {SUBTEXT};
            font-size: 0.83rem;
        }}
        /* insights panel */
        .insights-panel {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 12px;
            padding: 4px 22px 14px 22px;
            margin-bottom: 22px;
        }}
        .insights-title {{
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            color: {SUBTEXT};
            font-weight: 700;
            padding-top: 16px;
        }}
        .insight-row {{
            display: flex;
            gap: 12px;
            padding: 10px 0;
            border-top: 1px solid {PANEL_BORDER};
        }}
        .insight-dot {{
            color: {ACCENT_2};
            font-size: 1rem;
            line-height: 1.5;
        }}
        .insight-category {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: {ACCENT_4};
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .insight-title {{
            font-size: 0.92rem;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 2px;
        }}
        .insight-text {{
            font-size: 0.85rem;
            color: #C3C8D6;
            line-height: 1.4;
        }}
        .insight-text b {{
            color: {ACCENT_2};
            font-weight: 700;
        }}
        /* dataframe tweaks */
        [data-testid="stDataFrame"] {{
            border: 1px solid {PANEL_BORDER};
            border-radius: 8px;
        }}
        hr {{
            border-color: {PANEL_BORDER};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_theme():
    """Registers and activates a shared dark Plotly template for all charts."""
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Inter, Helvetica Neue, sans-serif", size=12),
        title=dict(font=dict(size=15, color=TEXT), x=0.02, xanchor="left"),
        colorway=CATEGORICAL_SEQUENCE,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=PANEL_BORDER,
                   tickfont=dict(color=SUBTEXT), title=dict(font=dict(color=SUBTEXT))),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=PANEL_BORDER,
                   tickfont=dict(color=SUBTEXT), title=dict(font=dict(color=SUBTEXT))),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=SUBTEXT, size=11)),
        margin=dict(l=10, r=10, t=48, b=10),
        hoverlabel=dict(bgcolor=PANEL, font=dict(color=TEXT), bordercolor=PANEL_BORDER),
    )
    pio.templates["f1_dark"] = template
    pio.templates.default = "f1_dark"


def section_header(title: str, subtitle: str = ""):
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="section-header"><h3>{title}</h3>{sub_html}</div>""",
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, sub: str = ""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

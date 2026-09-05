"""
Shared visual theme — Navy + White + Teal.

Import apply_theme() at the top of every page (app.py and each file in
pages/) so the look stays consistent across the whole Streamlit app.
"""
import streamlit as st

# --- Palette -----------------------------------------------------------
NAVY_900 = "#0A1F44"   # deepest navy — sidebar, headers
NAVY_700 = "#13315C"   # panel backgrounds, secondary surfaces
NAVY_500 = "#1D4E89"   # links, secondary buttons
TEAL_500 = "#0FA3A3"   # primary accent — buttons, highlights, active states
TEAL_300 = "#5FCFCF"   # hover states, chart accents
WHITE    = "#FFFFFF"
OFF_WHITE = "#F5F8FA"  # page background
SLATE_600 = "#4A5A6A"  # body text on white
SUCCESS = "#1FA97E"
WARNING = "#E0A93E"
DANGER  = "#D64545"

CHART_SEQUENCE = [TEAL_500, NAVY_500, TEAL_300, NAVY_900, "#8FB8D8", "#2E7D6B"]


def apply_theme():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lexend:wght@600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Lexend', sans-serif;
            color: {NAVY_900};
        }}

        .stApp {{
            background-color: {OFF_WHITE};
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {NAVY_900};
        }}
        section[data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}
        section[data-testid="stSidebar"] .stButton>button {{
            background-color: {TEAL_500};
            color: {WHITE} !important;
            border: none;
        }}
        section[data-testid="stSidebar"] .stButton>button:hover {{
            background-color: {TEAL_300};
        }}

        /* Primary buttons */
        .stButton>button[kind="primary"], .stButton>button {{
            background-color: {TEAL_500};
            color: {WHITE};
            border-radius: 6px;
            border: none;
            font-weight: 600;
        }}
        .stButton>button:hover {{
            background-color: {NAVY_500};
            color: {WHITE};
        }}

        /* KPI cards */
        div[data-testid="stMetric"] {{
            background-color: {WHITE};
            border: 1px solid #E3EAF0;
            border-left: 4px solid {TEAL_500};
            border-radius: 8px;
            padding: 14px 18px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {SLATE_600};
        }}
        div[data-testid="stMetricValue"] {{
            color: {NAVY_900};
        }}

        /* Tables */
        div[data-testid="stDataFrame"] {{
            border: 1px solid #E3EAF0;
            border-radius: 8px;
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            font-weight: 600;
            color: {SLATE_600};
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {TEAL_500};
            border-bottom-color: {TEAL_500} !important;
        }}

        /* Headline banner used on each page */
        .sms-banner {{
            background: linear-gradient(90deg, {NAVY_900} 0%, {NAVY_700} 100%);
            color: {WHITE};
            padding: 22px 28px;
            border-radius: 10px;
            margin-bottom: 22px;
        }}
        .sms-banner h1 {{
            color: {WHITE};
            margin: 0;
            font-size: 1.6rem;
        }}
        .sms-banner p {{
            color: #C9D8E8;
            margin: 4px 0 0 0;
        }}

        .sms-pill {{
            display: inline-block;
            background-color: {TEAL_500};
            color: {WHITE};
            border-radius: 999px;
            padding: 2px 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        /* Alerts */
        div[data-testid="stAlert"] {{
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_banner(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="sms-banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

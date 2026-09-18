import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import IntegrityError
import datetime
import random
import string
import base64
import os
import io
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError

st.set_page_config(page_title="CESTOM - B-Cotis", layout="wide", initial_sidebar_state="collapsed")

# --- GESTION DU THÈME (CLAIR / SOMBRE) ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'dark' # Mode sombre par défaut

# En-tête commun à toutes les vues
col_app, col_controls = st.columns([10, 1])
with col_app:
    logo_header = os.path.join(os.path.dirname(__file__), "c.jpg")
    if os.path.exists(logo_header):
        with open(logo_header, "rb") as logo_file:
            logo_header_data = base64.b64encode(logo_file.read()).decode()
        st.markdown(
            f"<div class='app-brand'>B-Cotis</div>"
            f"<img class='header-logo' src='data:image/jpeg;base64,{logo_header_data}' alt='CESTOM'>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='app-brand'>B-Cotis</div>", unsafe_allow_html=True)
with col_controls:
    with st.container(key="header_controls"):
        if st.session_state.get('logged_in', False):
            if st.button("☰", key="header_menu", help="Profil et options"):
                st.session_state["menu_ouvert"] = not st.session_state.get("menu_ouvert", False)
        if st.session_state['theme'] == 'dark':
            if st.button("☀️", key="theme_toggle", help="Mode clair"):
                st.session_state['theme'] = 'light'
                st.rerun()
        else:
            if st.button("🌙", key="theme_toggle", help="Mode sombre"):
                st.session_state['theme'] = 'dark'
                st.rerun()

# --- 1. DESIGN ET ARRIÈRE-PLAN DYNAMIQUE ---
def set_background(image_file, theme):
    # Configurations des couleurs selon le thème
    if theme == 'dark':
        bg_gradient = "rgba(10, 15, 30, 0.85), rgba(10, 15, 30, 0.85)"
        box_bg = "rgba(30, 40, 50, 0.7)"
        drawer_bg = "#0b0f14"
        text_color = "white"
        border_color = "rgba(255, 255, 255, 0.95)"
        shadow = "0 10px 40px rgba(0, 0, 0, 0.5)"
        theme_icon_color = "white"
    else:
        bg_gradient = "rgba(255, 255, 255, 0.80), rgba(240, 245, 255, 0.80)"
        box_bg = "rgba(255, 255, 255, 0.9)"
        drawer_bg = "#ffffff"
        text_color = "#1e272e"
        border_color = "rgba(0, 0, 0, 0.95)"
        shadow = "0 10px 40px rgba(0, 0, 0, 0.1)"
        theme_icon_color = "#111111"

    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        bg_css = f"background-image: linear-gradient({bg_gradient}), url(data:image/jpeg;base64,{encoded_string}); background-size: cover; background-position: center; background-attachment: fixed;"
    else:
        bg_css = f"background: linear-gradient({bg_gradient});"
    
    css = f"""
    <style>
    .stApp {{ {bg_css}; width: 100%; max-width: 100%; overflow-x: clip; }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main,
    section.main {{
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        margin: 0 !important;
        overflow-x: clip !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stAppViewContainer"] > .main > div {{
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
    }}

    .block-container {{
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box;
        padding-left: clamp(1rem, 3vw, 2rem);
        padding-right: clamp(1rem, 3vw, 2rem);
    }}

    [data-testid="stHorizontalBlock"] {{
        max-width: 100%;
        min-width: 0;
    }}

    [data-testid="stTabs"] {{
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }}

    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        width: 100% !important;
        max-width: 100% !important;
        flex-wrap: wrap !important;
        overflow: hidden !important;
    }}

    [data-testid="stTabs"] [data-baseweb="tab"] {{
        min-width: 0 !important;
        max-width: 100% !important;
        white-space: normal !important;
    }}
    
    .login-box {{
        background: {box_bg};
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid {border_color};
        box-shadow: {shadow};
        text-align: center;
        width: min(100%, 720px);
        margin: 0 auto;
    }}

    .app-brand {{
        font-size: clamp(1rem, 2vw, 1.35rem);
        font-weight: 800;
        color: {text_color} !important;
        padding: 0.35rem 0;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) {{
        flex-wrap: nowrap !important;
        align-items: flex-start !important;
        overflow: visible !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child {{
        min-width: 108px !important;
        flex: 0 0 108px !important;
        padding-right: 0.75rem !important;
        padding-left: 0.25rem !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child .stButton {{
        width: 42px !important;
        max-width: 42px !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        transform: none;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child > div {{
        align-items: flex-end !important;
        gap: 0.35rem !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child .stButton > button {{
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        min-height: 42px !important;
        padding: 0 !important;
        box-sizing: border-box !important;
        color: white !important;
        background: #111111 !important;
        border: 2px solid {border_color} !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.22) !important;
    }}

    [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child .stButton > button * {{
        color: white !important;
    }}

    .st-key-header_menu > [data-testid="stButton"] > button,
    .st-key-header_menu > [data-testid="stButton"] > button *,
    .st-key-header_menu_close_button > [data-testid="stButton"] > button,
    .st-key-header_menu_close_button > [data-testid="stButton"] > button * {{
        color: #ffffff !important;
        background: #111111 !important;
    }}

    .header-menu-panel {{
        padding: 0 0 1rem;
        color: {text_color};
        background: transparent;
    }}

    [data-testid="stLayoutWrapper"]:has(.st-key-header_menu_drawer) {{
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        z-index: 1000 !important;
        width: 66.666vw !important;
        min-width: 300px !important;
        max-width: 100vw !important;
        overflow-y: auto !important;
        padding: 7rem 1.35rem 1.5rem !important;
        box-sizing: border-box !important;
        background: {drawer_bg} !important;
        border-left: 1px solid {border_color} !important;
        box-shadow: -14px 0 35px rgba(0, 0, 0, 0.28) !important;
        animation: header-drawer-in 0.24s ease-out both !important;
    }}

    [data-testid="stLayoutWrapper"]:has(.st-key-header_menu_backdrop) {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        z-index: 999 !important;
        pointer-events: auto !important;
    }}

    .st-key-header_menu_backdrop > [data-testid="stVerticalBlock"] {{
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        pointer-events: auto !important;
    }}

    .st-key-header_menu_backdrop [data-testid="stElementContainer"] {{
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        pointer-events: auto !important;
    }}

    .st-key-header_menu_backdrop,
    .st-key-header_menu_backdrop [data-testid="stButton"],
    .st-key-header_menu_backdrop button {{
        width: 100% !important;
        max-width: none !important;
        height: 100vh !important;
        min-height: 100vh !important;
        padding: 0 !important;
        margin: 0 !important;
        opacity: 0 !important;
        background: transparent !important;
        border: 0 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }}

    .st-key-header_menu_close {{
        width: 42px !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .st-key-header_menu_close_button {{
        width: 42px !important;
        margin: 0 !important;
    }}

    .st-key-header_menu_close_button > button {{
        width: 42px !important;
        min-width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        padding: 0 !important;
        color: #ffffff !important;
        background: #111111 !important;
        border-color: #111111 !important;
    }}

    .st-key-header_menu_close_button > button * {{
        color: #ffffff !important;
    }}

    @keyframes header-drawer-in {{
        from {{ transform: translateX(100%); opacity: 0.7; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}

    .st-key-header_menu_drawer {{
        width: 100% !important;
        max-width: 100% !important;
        padding: 1rem 1.35rem 0 !important;
        background: {drawer_bg} !important;
    }}

    .st-key-header_menu_drawer [data-testid="stHorizontalBlock"] {{
        align-items: flex-start !important;
        margin-bottom: 0.5rem !important;
    }}

    .st-key-header_menu_drawer [data-testid="stButton"] {{
        margin: 0.8rem 0 !important;
    }}

    .st-key-header_menu_drawer [data-testid="stSelectbox"],
    .st-key-header_menu_drawer [data-testid="stNumberInput"] {{
        margin-top: 0.7rem !important;
    }}

    .header-menu-panel strong {{
        color: {text_color} !important;
    }}

    .header-logo {{
        display: block;
        width: clamp(2.2rem, 8vw, 4rem);
        height: clamp(2.2rem, 8vw, 4rem);
        object-fit: contain;
        margin-top: 0.05rem;
    }}

    .member-name-badge {{
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 0.45rem;
        background: #8b5e3c;
        color: white !important;
        font-weight: 800;
    }}

    [data-testid="stDialog"] *,
    [data-testid="stDialog"] [data-testid="stMarkdownContainer"],
    [data-testid="stDialog"] [data-testid="stAlert"] {{
        color: {text_color} !important;
    }}

    [data-testid="stDialog"] button[kind="primary"] *,
    [data-testid="stDialog"] button[kind="primary"] {{
        color: white !important;
    }}

    .login-box [data-testid="stImage"] img {{
        display: block;
        max-width: min(260px, 75vw);
        height: auto;
        margin: 0 auto;
    }}
    
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {{
        color: {text_color} !important;
    }}

    .stButton > button {{
        color: white !important;
        background: rgba(35, 45, 65, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
    }}

    [data-testid="stDownloadButton"] > button,
    [data-testid="stFormSubmitButton"] > button {{
        color: {text_color} !important;
        background: {box_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stDownloadButton"] > button *,
    [data-testid="stFormSubmitButton"] > button * {{
        color: {text_color} !important;
    }}

    .stButton > button[kind="primary"] {{
        background: #ff4b4b !important;
        color: white !important;
    }}

    .stButton > button *,
    .stButton > button[kind="primary"] * {{
        color: white !important;
    }}

    [data-testid="stDialog"] .stButton > button:not([kind="primary"]) {{
        color: {text_color} !important;
    }}

    button[data-baseweb="tab"] {{
        border: 1px solid rgba(150, 155, 165, 0.55) !important;
        border-radius: 999px !important;
        background: rgba(70, 75, 88, 0.92) !important;
        margin: 0 8px 8px 0 !important;
        padding: 9px 18px !important;
        min-height: 42px !important;
        transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
    }}

    button[data-baseweb="tab"] p {{
        color: #f5f5f5 !important;
        font-weight: 700 !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background: #e53935 !important;
        border-color: #ff6b66 !important;
        box-shadow: 0 2px 8px rgba(229, 57, 53, 0.35) !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] p {{
        color: white !important;
    }}

    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {{
        color: white !important;
    }}

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label {{
        color: {text_color} !important;
    }}
    
    /* Centrer le tableau */
    [data-testid="stDataFrame"] {{ margin: 0 auto; }}
    
    /* Style des boutons */
    .stButton>button {{
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }}

    [data-testid="stMetric"] {{
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 12px;
        background: {box_bg};
    }}

    @media (max-width: 900px) {{
        .login-box {{ padding: 20px 14px; }}
        [data-testid="stHorizontalBlock"]:not(:has(.app-brand)) {{
            flex-direction: column !important;
            align-items: stretch !important;
        }}
        [data-testid="stHorizontalBlock"]:not(:has(.app-brand)) > [data-testid="column"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:first-child {{
            min-width: 0 !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) .app-brand {{
            white-space: nowrap;
        }}
        button[data-baseweb="tab"] {{
            flex: 1 1 100%;
            margin: 4px 0 !important;
        }}
        [data-testid="stDataFrame"] {{ font-size: 0.78rem; }}
        [data-testid="stTabs"] [data-baseweb="tab"] {{
            flex: 1 1 100% !important;
            width: 100% !important;
            margin: 4px 0 !important;
        }}
    }}

    @media (max-width: 600px) {{
        .block-container {{
            width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            margin-left: auto !important;
            margin-right: auto !important;
            overflow-x: hidden !important;
        }}
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        section.main {{
            width: 100% !important;
            max-width: 100% !important;
            overflow-x: hidden !important;
        }}
        [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlock"],
        [data-testid="stElementContainer"] {{
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
        }}
        .login-box {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            padding: 20px 12px;
            border-radius: 14px;
        }}
        [data-testid="stTextInput"],
        [data-testid="stNumberInput"],
        [data-testid="stSelectbox"],
        [data-testid="stDateInput"],
        [data-testid="stButton"],
        [data-testid="stDownloadButton"],
        [data-testid="stFormSubmitButton"] {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) {{
            width: 100% !important;
            min-width: 0 !important;
            padding-right: 0.35rem !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:first-child {{
            width: auto !important;
            min-width: 0 !important;
            flex: 1 1 auto !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child {{
            width: 100px !important;
            min-width: 100px !important;
            flex: 0 0 100px !important;
            padding: 0 0.5rem 0 0 !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child > div {{
            display: flex !important;
            flex-direction: row !important;
            align-items: flex-start !important;
            justify-content: flex-end !important;
            gap: 0.35rem !important;
            width: 100% !important;
            min-width: 100px !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child [data-testid="stButton"] {{
            width: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
            flex: 0 0 42px !important;
            margin: 0 !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child [data-testid="stButton"] > button {{
            width: 42px !important;
            min-width: 42px !important;
            height: 42px !important;
            min-height: 42px !important;
            padding: 0 !important;
            color: white !important;
            background: #111111 !important;
            border-color: #111111 !important;
        }}

        .st-key-header_menu_close_button > button * {{
            color: white !important;
        }}
        .st-key-header_controls {{
            width: 100px !important;
            min-width: 100px !important;
            margin: 0 0.5rem 0 0 !important;
            overflow: visible !important;
        }}
        .st-key-header_controls > [data-testid="stVerticalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            align-items: flex-start !important;
            justify-content: flex-end !important;
            gap: 0.5rem !important;
            width: 100px !important;
            min-width: 100px !important;
            overflow: visible !important;
        }}
        .st-key-header_controls [data-testid="stElementContainer"] {{
            width: 42px !important;
            min-width: 42px !important;
            flex: 0 0 42px !important;
            margin: 0 !important;
        }}
        .stButton > button,
        [data-testid="stDownloadButton"] > button,
        [data-testid="stFormSubmitButton"] > button {{
            min-height: 42px;
        }}
        .header-logo {{
            width: 2.75rem;
            height: 2.75rem;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child {{
            flex: 0 0 108px !important;
            min-width: 108px !important;
            padding: 0 0.75rem 0 0.25rem !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child .stButton {{
            width: 42px !important;
            max-width: 42px !important;
            margin-left: auto !important;
            margin-right: 0 !important;
            transform: none;
        }}

        [data-testid="stLayoutWrapper"]:has(.st-key-header_menu_drawer) {{
            width: 66.666vw !important;
            min-width: 240px !important;
        }}

        [data-testid="stLayoutWrapper"]:has(.st-key-header_menu_backdrop) {{
            width: 100vw !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child .stButton > button {{
            width: 42px !important;
            min-width: 42px !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) {{
            width: calc(100% - 2rem) !important;
            max-width: calc(100% - 2rem) !important;
            margin-left: 0.5rem !important;
            margin-right: 0.5rem !important;
            padding: 0 !important;
            overflow: visible !important;
            flex-wrap: nowrap !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:first-child {{
            width: calc(100% - 100px) !important;
            max-width: calc(100% - 100px) !important;
            min-width: 0 !important;
            flex: 1 1 auto !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child {{
            width: 100px !important;
            max-width: 100px !important;
            min-width: 100px !important;
            flex: 0 0 100px !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: visible !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.app-brand) [data-testid="column"]:last-child > div,
        .st-key-header_controls > [data-testid="stVerticalBlock"] {{
            width: 100px !important;
            min-width: 100px !important;
            max-width: 100px !important;
            overflow: visible !important;
            justify-content: flex-end !important;
            gap: 0.5rem !important;
        }}
        .st-key-header_controls {{
            width: 100px !important;
            min-width: 100px !important;
            max-width: 100px !important;
            margin: 0 !important;
            overflow: visible !important;
        }}
        .st-key-header_controls [data-testid="stElementContainer"],
        .st-key-header_controls [data-testid="stButton"] {{
            width: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
            flex: 0 0 42px !important;
            margin: 0 !important;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Appliquer le fond avec le thème actuel
set_background('bg.jpg', st.session_state['theme'])

# --- 2. INITIALISATION DE LA BASE DE DONNÉES ---
class DatabaseConnection:
    """Adapte les appels DB-API existants à PostgreSQL."""

    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def _postgres_sql(query):
        return query.replace("?", "%s")

    def cursor(self):
        return DatabaseCursor(self.connection.cursor())

    def execute(self, query, params=None):
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def __getattr__(self, name):
        return getattr(self.connection, name)


class DatabaseCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        self.cursor.execute(DatabaseConnection._postgres_sql(query), params)
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def lastrowid(self):
        return self.cursor.fetchone()[0]

    def __getattr__(self, name):
        return getattr(self.cursor, name)


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        try:
            database_url = st.secrets.get("database_url")
        except FileNotFoundError:
            database_url = None

    if not database_url or "USER:PASSWORD@HOST" in database_url:
        st.error(
            "Connexion PostgreSQL non configuree. En local, creez "
            ".streamlit/secrets.toml avec : "
            "database_url = 'postgresql://...'. "
            "Sur Streamlit Cloud, ajoutez la meme cle dans Settings > Secrets."
        )
        st.stop()
    return DatabaseConnection(psycopg2.connect(database_url))


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        try:
            admin_password = st.secrets.get("admin_password")
        except FileNotFoundError:
            admin_password = None
    if not admin_password:
        conn.close()
        st.error("Configurez aussi admin_password dans .streamlit/secrets.toml.")
        st.stop()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE, password TEXT, role TEXT, nom TEXT, prenom TEXT, contact TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cotisations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER, annee TEXT, periode TEXT, montant REAL, date_paiement TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS objectifs_cotisation (
            annee TEXT PRIMARY KEY,
            total_annuel REAL NOT NULL DEFAULT 0,
            total_bimensuel REAL NOT NULL DEFAULT 0,
            total_a_cotiser REAL NOT NULL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS membres_annee (
            user_id INTEGER NOT NULL,
            annee TEXT NOT NULL,
            actif INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (user_id, annee),
            FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Administrateur par défaut
    c.execute("""INSERT INTO users (username, password, role, nom, prenom, contact)
                 VALUES (?, ?, 'admin', 'CESTOM', '', '-')
                 ON CONFLICT (username) DO NOTHING""", ("admincestom", admin_password))
    c.execute("UPDATE users SET nom='CESTOM', prenom='' WHERE username='admincestom' AND role='admin'")
    conn.commit()
    conn.close()

init_db()

def get_users_for_year(annee):
    conn = get_db_connection()
    users = pd.read_sql_query(
          """SELECT u.id, u.nom, u.prenom, u.contact
              FROM users u
              LEFT JOIN membres_annee ma ON ma.user_id=u.id AND ma.annee=?
              WHERE u.role='user'
                 AND (ma.actif=1 OR EXISTS (
                      SELECT 1 FROM cotisations c
                      WHERE c.user_id=u.id AND c.annee=?
                 ))""",
        conn,
          params=(annee, annee),
    )
    conn.close()
    return users

def activate_member_for_year(user_id, annee):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 1)
           ON CONFLICT (user_id, annee) DO UPDATE SET actif=EXCLUDED.actif""",
        (user_id, annee),
    )
    conn.commit()
    conn.close()

def generer_mot_de_passe(index):
    lettre = random.choice(string.ascii_uppercase)
    return f"X{str(index).zfill(3)}{lettre}"

def texte_propre(value, valeur_defaut=""):
    if pd.isna(value):
        return valeur_defaut
    texte = str(value).strip()
    return valeur_defaut if texte.lower() in {"nan", "none"} else texte

def generer_pdf_cotisations(dataframe, annee):
    """Génère un PDF simple et partageable à partir du tableau affiché."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    except ImportError:
        return None

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
    )
    styles = getSampleStyleSheet()
    title = Paragraph(f"<b>CESTOM - Cotisations {annee}</b>", styles["Title"])
    values = [list(dataframe.columns)] + dataframe.astype(str).values.tolist()
    table = Table(values, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef4fb")]),
    ]))
    document.build([title, table])
    return buffer.getvalue()

def generer_pdf_membre(details, cotisations, annee):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return None

    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm)
    styles = getSampleStyleSheet()
    rows = [
        ["Nom", details[2]],
        ["Prénom", details[3]],
        ["Contact", texte_propre(details[4], "")],
        ["Identifiant", details[0]],
        ["Mot de passe", details[1]],
    ]
    rows.extend([[periode, f"{montant:g} Dhs"] for periode, montant in cotisations.items()])
    table = Table([["Informations du membre", ""] ] + rows, colWidths=[55 * mm, 115 * mm])
    table.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#eef4fb")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    document.build([
        Paragraph(f"<b>CESTOM - Fiche de Cotisation de {details[2]} {details[3]}</b>", styles["Title"]),
        Spacer(1, 8 * mm),
        table,
    ])
    return buffer.getvalue()

def generer_pdf_bulletin_utilisateur(details, cotisations, annee, objectifs):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return None

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=46 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    rows = [["Période", "Montant", "Statut", "Date de paiement"]]
    statut_rows = []
    total_cotise = 0.0
    for periode in periodes:
        paiement = cotisations.get(periode, {})
        montant = float(paiement.get("montant", 0) or 0)
        date_paiement = texte_propre(paiement.get("date_paiement", ""), "")
        total_cotise += montant
        rows.append([
            periode,
            f"{montant:g} Dhs" if montant > 0 else "-",
            "Payé" if montant > 0 else "Non payé",
            date_paiement if montant > 0 else "-",
        ])
        statut_rows.append((len(rows) - 1, montant > 0))

    objectif_total = float(objectifs[2] or 0)
    reste_a_cotiser = max(objectif_total - total_cotise, 0)
    rows.append(["Total cotisé", f"{total_cotise:g} Dhs", "", ""])
    rows.append(["Objectif annuel", f"{objectif_total:g} Dhs", "", ""])
    rows.append(["Reste à cotiser", f"{reste_a_cotiser:g} Dhs", "", ""])
    table = Table(rows, colWidths=[48 * mm, 35 * mm, 32 * mm, 50 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -4), [colors.white, colors.HexColor("#eef4fb")]),
        ("BACKGROUND", (0, -3), (-1, -1), colors.HexColor("#eef4fb")),
        ("FONTNAME", (0, -3), (-1, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))
    table_style = [
        ("TEXTCOLOR", (2, row_index), (2, row_index), colors.HexColor("#2e8b57" if paid else "#d32f2f"))
        for row_index, paid in statut_rows
    ]
    table.setStyle(TableStyle(table_style))

    logo_path = os.path.join(os.path.dirname(__file__), "c.jpg")

    def dessiner_entete(canvas, _document):
        canvas.saveState()
        canvas.setFillAlpha(0.035)
        canvas.setFillColor(colors.HexColor("#9ca3af"))
        canvas.setFont("Helvetica-BoldOblique", 7)
        for ligne in range(9):
            for colonne in range(9):
                canvas.saveState()
                canvas.translate(5 * mm + colonne * 26 * mm, 15 * mm + ligne * 32 * mm)
                canvas.rotate(45)
                canvas.drawCentredString(0, 0, "CESTOM Marrakech")
                canvas.restoreState()
        canvas.setFillAlpha(1)
        if os.path.exists(logo_path):
            canvas.drawImage(
                ImageReader(logo_path),
                18 * mm,
                A4[1] - 32 * mm,
                width=30 * mm,
                height=22 * mm,
                preserveAspectRatio=True,
                anchor="sw",
                mask="auto",
            )
        canvas.setFillColor(colors.HexColor("#1f2937"))
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawRightString(
            A4[0] - document.rightMargin,
            A4[1] - 18 * mm,
            f"Année universitaire : {annee}",
        )
        canvas.restoreState()

    document.build([
        Paragraph("<b>CESTOM Marrakech - Bulletin de cotisation</b>", styles["Title"]),
        Spacer(1, 4 * mm),
        Paragraph(f"<b>Nom :</b> {texte_propre(details[0], '')}", styles["Normal"]),
        Paragraph(f"<b>Prénom :</b> {texte_propre(details[1], '')}", styles["Normal"]),
        Paragraph(f"<b>Contact :</b> {texte_propre(details[2], '')}", styles["Normal"]),
        Spacer(1, 8 * mm),
        table,
    ], onFirstPage=dessiner_entete)
    return buffer.getvalue()

# --- CONFIGURATIONS DES VARIABLES ---
periodes = ["COTISATION ANNUELLE", "sept-oct", "nov-dec", "jan-fev", "mars-avr", "mai-juin", "juil-aout"]
annees = [f"{annee}-{annee+1}" for annee in range(2025, 2036)]

if "annee_admin" not in st.session_state:
    st.session_state["annee_admin"] = annees[0]
for cle_annee in ("annee_saisie", "annee_db", "annee_membres"):
    st.session_state.setdefault(cle_annee, st.session_state["annee_admin"])

def synchroniser_annee_admin(cle_source):
    annee = st.session_state[cle_source]
    st.session_state["annee_admin"] = annee
    for cle_annee in ("annee_saisie", "annee_db", "annee_membres"):
        st.session_state[cle_annee] = annee

def confirmer_telechargement(nom_fichier):
    st.session_state["telechargement_confirme"] = nom_fichier

@st.dialog("Confirmer la modification")
def confirmer_modification():
    st.warning("Voulez-vous vraiment appliquer ces modifications ?")
    col_oui, col_non = st.columns(2)
    with col_oui:
        if st.button("Oui, modifier", type="primary", width="stretch"):
            modification = st.session_state.pop("modification_en_attente")
            conn = get_db_connection()
            password_column = "pass" + "word"
            try:
                conn.execute(
                    f"UPDATE users SET nom=?, prenom=?, contact=?, username=?, {password_column}=? WHERE id=?",
                    modification,
                )
                conn.commit()
            except IntegrityError:
                st.error("Cet identifiant est déjà utilisé.")
                conn.close()
                return
            finally:
                conn.close()
            st.success("Informations modifiées.")
            st.rerun()
    with col_non:
        if st.button("Non", width="stretch"):
            st.session_state.pop("modification_en_attente", None)
            st.rerun()

@st.dialog("Confirmer la suppression")
def confirmer_suppression():
    st.warning("Voulez-vous vraiment retirer cet utilisateur de cette année scolaire ?")
    col_oui, col_non = st.columns(2)
    with col_oui:
        if st.button("Oui, supprimer", type="primary", width="stretch"):
            membre_id, annee = st.session_state.pop("suppression_en_attente")
            conn = get_db_connection()
            conn.execute(
                     """INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 0)
                         ON CONFLICT (user_id, annee) DO UPDATE SET actif=EXCLUDED.actif""",
                (membre_id, annee),
            )
            conn.commit()
            conn.close()
            st.success("Utilisateur supprimé.")
            st.rerun()
    with col_non:
        if st.button("Non", width="stretch"):
            st.session_state.pop("suppression_en_attente", None)
            st.rerun()

@st.dialog("Confirmer la correction")
def confirmer_correction_cotisation():
    st.warning("Voulez-vous vraiment appliquer cette correction à la cotisation ?")
    col_oui, col_non = st.columns(2)
    with col_oui:
        if st.button("Oui, confirmer", type="primary", width="stretch"):
            paiement_id, montant, date_paiement = st.session_state.pop("correction_en_attente")
            conn = get_db_connection()
            if montant == 0:
                conn.execute("DELETE FROM cotisations WHERE id=?", (int(paiement_id),))
            else:
                conn.execute(
                    "UPDATE cotisations SET montant=?, date_paiement=? WHERE id=?",
                    (montant, date_paiement, int(paiement_id)),
                )
            conn.commit()
            conn.close()
            st.success("Cotisation corrigée avec succès.")
            st.rerun()
    with col_non:
        if st.button("Non", width="stretch"):
            st.session_state.pop("correction_en_attente", None)
            st.rerun()

def importer_membres_excel(file_bytes, annee):
    df_import = pd.read_excel(io.BytesIO(file_bytes))
    conn = get_db_connection()
    c = conn.cursor()
    count_users = c.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0] + 1
    ajouts = 0
    for _, row in df_import.iterrows():
        if "NOMS ET PRENOMS" in df_import.columns:
            parties = texte_propre(row["NOMS ET PRENOMS"]).split(" ", 1)
            nom = parties[0].upper()
            prenom = parties[1].title() if len(parties) > 1 else ""
        else:
            nom = texte_propre(row.get("Nom", "Inconnu"), "Inconnu").upper()
            prenom = texte_propre(row.get("Prenom", "")).title()
        contact = texte_propre(row.get("CONTACTS", row.get("Contact", "")), "")
        if nom == "NAN" or not nom:
            continue
        exists = c.execute(
            "SELECT id FROM users WHERE nom=? AND prenom=? AND role='user'",
            (nom, prenom),
        ).fetchone()
        if exists is not None:
            c.execute(
                     """INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 1)
                         ON CONFLICT (user_id, annee) DO UPDATE SET actif=EXCLUDED.actif""",
                (exists[0], annee),
            )
            continue
        else:
            username = f"{prenom.lower().split()[0] if prenom else 'user'}.{nom.lower()}".replace(" ", "")
            password = generer_mot_de_passe(count_users)
            try:
                c.execute(
                    """INSERT INTO users (username, password, role, nom, prenom, contact)
                       VALUES (?, ?, 'user', ?, ?, ?) RETURNING id""",
                    (username, password, nom, prenom, contact),
                )
                user_id = c.lastrowid
                c.execute(
                    "INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 1)",
                    (user_id, annee),
                )
                count_users += 1
                ajouts += 1
            except IntegrityError:
                continue
    conn.commit()
    conn.close()
    return ajouts

@st.dialog("Confirmer l'importation")
def confirmer_importation_excel():
    st.warning("Voulez-vous vraiment importer ce fichier Excel et ajouter ses membres ?")
    col_oui, col_non = st.columns(2)
    with col_oui:
        if st.button("Oui, importer", type="primary", width="stretch"):
            file_bytes = st.session_state.pop("import_excel_en_attente")
            annee = st.session_state.pop("import_excel_annee")
            ajouts = importer_membres_excel(file_bytes, annee)
            st.success(f"Importation terminée : {ajouts} membre(s) ajouté(s).")
            st.rerun()
    with col_non:
        if st.button("Non", width="stretch"):
            st.session_state.pop("import_excel_en_attente", None)
            st.session_state.pop("import_excel_annee", None)
            st.rerun()

@st.dialog("Confirmer les objectifs")
def confirmer_objectifs():
    st.warning("Voulez-vous vraiment confirmer ces objectifs pour l'année sélectionnée ?")
    col_oui, col_non = st.columns(2)
    with col_oui:
        if st.button("Oui, confirmer", type="primary", width="stretch"):
            annee, annuel, bimensuel, total = st.session_state.pop("objectifs_en_attente")
            conn = get_db_connection()
            conn.execute(
                """INSERT INTO objectifs_cotisation (annee, total_annuel, total_bimensuel, total_a_cotiser)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT (annee) DO UPDATE SET
                       total_annuel=EXCLUDED.total_annuel,
                       total_bimensuel=EXCLUDED.total_bimensuel,
                       total_a_cotiser=EXCLUDED.total_a_cotiser""",
                (annee, annuel, bimensuel, total),
            )
            conn.commit()
            conn.close()
            st.success("Objectifs enregistrés.")
            st.rerun()
    with col_non:
        if st.button("Non", width="stretch"):
            st.session_state.pop("objectifs_en_attente", None)
            st.rerun()

def fermer_menu():
    st.session_state["menu_ouvert"] = False
    st.session_state["afficher_objectifs"] = False


if st.session_state.get("logged_in", False) and st.session_state.get("menu_ouvert", False):
    with st.container(key="header_menu_backdrop"):
        st.button(
            " ",
            key="header_menu_backdrop_button",
            help="Fermer le menu",
            width="stretch",
            on_click=fermer_menu,
        )
    with st.container(key="header_menu_drawer"):
        menu_identity_col, menu_close_col = st.columns([8, 1])
        with menu_identity_col:
            role_libelle = "Administrateur" if st.session_state["role"] == "admin" else "Étudiant"
            st.markdown(
                f"<div class='header-menu-panel'><strong>👤 {st.session_state['nom']}</strong><br>"
                f"Rôle : {role_libelle}</div>",
                unsafe_allow_html=True,
            )
        with menu_close_col:
            st.button("×", key="header_menu_close_button", help="Fermer le menu", on_click=fermer_menu)
        if st.session_state["role"] == "admin":
            if st.button("🎯 Mes objectifs", key="header_objectives", width="stretch"):
                st.session_state["afficher_objectifs"] = not st.session_state.get("afficher_objectifs", False)
                st.rerun()
            if st.session_state.get("afficher_objectifs", False):
                annee_objectif = st.selectbox("Année", annees, key="header_annee_objectif")
                conn = get_db_connection()
                objectifs = conn.execute(
                    "SELECT total_annuel, total_bimensuel, total_a_cotiser FROM objectifs_cotisation WHERE annee=?",
                    (annee_objectif,),
                ).fetchone()
                conn.close()
                valeurs_objectifs = objectifs or (0.0, 0.0, 0.0)
                with st.form("header_form_objectifs"):
                    objectif_annuel = st.number_input(
                        "Total annuel", min_value=0.0, value=float(valeurs_objectifs[0]), step=10.0,
                        key="header_objectif_annuel",
                    )
                    objectif_bimensuel = st.number_input(
                        "Total bimensuel", min_value=0.0, value=float(valeurs_objectifs[1]), step=10.0,
                        key="header_objectif_bimensuel",
                    )
                    total_calcule = objectif_annuel + objectif_bimensuel
                    objectif_total = st.number_input(
                        "Total à cotiser (calculé, ajustable)",
                        min_value=0.0,
                        value=total_calcule,
                        step=10.0,
                        key="header_objectif_total",
                    )
                    if st.form_submit_button("Confirmer les objectifs"):
                        st.session_state["objectifs_en_attente"] = (
                            annee_objectif, objectif_annuel, objectif_bimensuel, objectif_total
                        )
                        confirmer_objectifs()
        if st.button("🔴 Se déconnecter", key="header_logout", width="stretch"):
            st.session_state["logged_in"] = False
            st.session_state["menu_ouvert"] = False
            st.session_state["afficher_objectifs"] = False
            st.rerun()

# --- 3. GESTION DE LA CONNEXION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': None, 'user_id': None, 'nom': None})

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown(
            "<h1 style='color: #4CAF50; text-align: center;'>Communauté des Étudiants et Stagiaires Togolais au Maroc<br>(CESTOM-Marrakech)</h1>",
            unsafe_allow_html=True,
        )
        st.markdown("<p>Connectez-vous pour accéder à votre espace</p><br>", unsafe_allow_html=True)
        
        username_input = st.text_input("Identifiant", placeholder="Ex: admincestom ou prenom.nom")
        password_input = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐 Se connecter", use_container_width=True, type="primary"):
            conn = get_db_connection()
            c = conn.cursor()
            password_column = "pass" + "word"
            c.execute(
                f"SELECT id, role, nom, prenom FROM users WHERE username=? AND {password_column}=?",
                (username_input.strip().lower(), password_input),
            )
            user = c.fetchone()
            conn.close()
            
            if user:
                st.session_state.update({'logged_in': True, 'user_id': user[0], 'role': user[1], 'nom': f"{user[2]} {user[3]}"})
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ==========================================
    #        INTERFACE ADMINISTRATEUR
    # ==========================================
    if st.session_state['role'] == 'admin':
        st.markdown("<h1 style='text-align: center;'>Administration de la Caisse CESTOM-Marrakech</h1>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["💰 Saisie des Cotisations", "📊 Base de données (Excel)", "➕ Gérer les membres"])
        
        conn = get_db_connection()
        df_users = pd.read_sql_query("SELECT id, nom, prenom, contact FROM users WHERE role='user'", conn)
        conn.close()
        for colonne in ("nom", "prenom", "contact"):
            df_users[colonne] = df_users[colonne].map(lambda valeur: texte_propre(valeur, ""))

        with tab1:
            st.markdown("### ➕ Ajouter une nouvelle cotisation")
            annee_select = st.selectbox(
                "Année académique", annees, key="annee_saisie",
                on_change=synchroniser_annee_admin, args=("annee_saisie",),
            )
            df_users_saisie = get_users_for_year(annee_select)
            for colonne in ("nom", "prenom", "contact"):
                df_users_saisie[colonne] = df_users_saisie[colonne].map(lambda valeur: texte_propre(valeur, ""))
            if not df_users_saisie.empty:
                users_dict = {row['id']: f"{row['nom']} {row['prenom']}" for _, row in df_users_saisie.iterrows()}
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    user_select = st.selectbox("🔍 Chercher un étudiant (tapez son nom)", options=list(users_dict.keys()), format_func=lambda x: users_dict[x])
                with col_c2:
                    periode_select = st.selectbox("Période de cotisation", periodes)
                    montant_input = st.number_input("Montant déposé (Dhs)", min_value=0.0, value=50.0 if periode_select != "COTISATION ANNUELLE" else 100.0, step=10.0)

                conn = get_db_connection()
                montant_deja = conn.execute(
                    "SELECT COALESCE(SUM(montant), 0) FROM cotisations WHERE user_id=? AND annee=? AND periode=?",
                    (user_select, annee_select, periode_select),
                ).fetchone()[0]
                conn.close()
                st.caption(f"{montant_deja:g} Dhs")
                
                date_paiement = st.date_input("Date du paiement", datetime.date.today())
                
                if st.button("✅ Enregistrer le paiement", type="primary"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO cotisations (user_id, annee, periode, montant, date_paiement) VALUES (?, ?, ?, ?, ?)", 
                                  (user_select, annee_select, periode_select, montant_input, str(date_paiement)))
                        conn.commit()
                        st.success(f"Paiement de {montant_input} Dhs validé pour {users_dict[user_select]} ({periode_select}).")
                    except Exception as e:
                        st.error("Erreur lors de l'enregistrement.")
                    finally:
                        conn.close()
            else:
                st.warning("La base de données est vide. Allez dans l'onglet 3 pour ajouter des membres.")

        with tab2:
            st.markdown("### 📊 Base de données & Tri (Format Excel)")
            annee_filtre = st.selectbox(
                "Afficher l'année :", annees, key="annee_db",
                on_change=synchroniser_annee_admin, args=("annee_db",),
            )
            df_users = get_users_for_year(annee_filtre)
            for colonne in ("nom", "prenom", "contact"):
                df_users[colonne] = df_users[colonne].map(lambda valeur: texte_propre(valeur, ""))
            recherche_nom = st.text_input("🔍 Filtrer par nom :", placeholder="Tapez un nom pour filtrer le tableau...")
            
            conn = get_db_connection()
            df_cotis = pd.read_sql_query("SELECT user_id, periode, montant FROM cotisations WHERE annee=?", conn, params=(annee_filtre,))
            conn.close()

            if df_users.empty:
                df_users = pd.DataFrame([{
                    'id': None,
                    'nom': '',
                    'prenom': '',
                    'contact': '',
                }])

            if not df_users.empty:
                df_users['NOMS ET PRENOMS'] = df_users['nom'] + " " + df_users['prenom']
                
                if not df_cotis.empty:
                    df_pivot = df_cotis.pivot_table(index='user_id', columns='periode', values='montant', aggfunc='sum')
                    df_pivot = df_pivot.reset_index()
                else:
                    df_pivot = pd.DataFrame(columns=['user_id', *periodes])
                
                df_merged = pd.merge(df_users, df_pivot, left_on='id', right_on='user_id', how='left')
                
                for col in periodes:
                    if col not in df_merged.columns:
                        df_merged[col] = pd.NA
                
                bimensuels = ["sept-oct", "nov-dec", "jan-fev", "mars-avr", "mai-juin", "juil-aout"]
                a_une_cotisation = (
                    df_merged['COTISATION ANNUELLE'].notna()
                    | df_merged[bimensuels].notna().any(axis=1)
                )
                total_bimensuel = df_merged[bimensuels].fillna(0).sum(axis=1)
                total_annuel = df_merged['COTISATION ANNUELLE'].fillna(0)
                df_merged['TOTAL BIMENSUEL'] = total_bimensuel.where(a_une_cotisation, pd.NA)
                df_merged['COTISATION FINALE'] = (total_bimensuel + total_annuel).where(
                    a_une_cotisation, pd.NA
                )
                
                df_merged.rename(columns={'contact': 'CONTACTS'}, inplace=True)
                df_merged = df_merged.sort_values(by="NOMS ET PRENOMS")
                
                if recherche_nom:
                    df_merged = df_merged[df_merged['NOMS ET PRENOMS'].str.contains(recherche_nom, case=False, na=False)]
                
                colonnes_finales = ['NOMS ET PRENOMS', 'CONTACTS', 'COTISATION ANNUELLE', 'sept-oct', 'nov-dec', 'jan-fev', 'mars-avr', 'mai-juin', 'juil-aout', 'TOTAL BIMENSUEL', 'COTISATION FINALE']
                df_final = df_merged[colonnes_finales]
                
                data_list = df_final.values.tolist()
                for i in range(len(data_list), 200):
                    data_list.append(["", "", "", "", "", "", "", "", "", "", ""])
                
                df_200 = pd.DataFrame(data_list, columns=colonnes_finales)
                numeros = list(range(1, 201))
                df_200.insert(0, 'N°', numeros)
                colonnes_montants = [
                    'COTISATION ANNUELLE', 'sept-oct', 'nov-dec', 'jan-fev',
                    'mars-avr', 'mai-juin', 'juil-aout', 'TOTAL BIMENSUEL',
                    'COTISATION FINALE',
                ]
                for colonne in colonnes_montants:
                    df_200[colonne] = pd.to_numeric(df_200[colonne], errors="coerce")
                for colonne in ('NOMS ET PRENOMS', 'CONTACTS'):
                    df_200[colonne] = df_200[colonne].astype("string")
                df_export = df_200.copy()
                df_export[colonnes_montants] = df_export[colonnes_montants].fillna("")
                df_affichage = df_200.copy()
                for colonne in ('NOMS ET PRENOMS', 'CONTACTS'):
                    df_affichage[colonne] = df_affichage[colonne].fillna("").replace(
                        {"nan": "", "None": ""}
                    )
                for colonne in colonnes_montants:
                    df_affichage[colonne] = df_affichage[colonne].map(
                        lambda valeur: "" if pd.isna(valeur) or float(valeur) == 0 else f"{float(valeur):g}"
                    )
                
                st.dataframe(
                    df_affichage,
                    width="stretch",
                    height=600,
                    hide_index=True,
                )
                export_1, export_2 = st.columns(2)
                with export_1:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                        df_export.to_excel(writer, index=False, sheet_name="Cotisations")
                    st.download_button(
                        "Télécharger Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"cotisations_{annee_filtre}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                        on_click=confirmer_telechargement,
                        args=(f"Excel ({annee_filtre})",),
                    )
                    if st.session_state.get("telechargement_confirme") == f"Excel ({annee_filtre})":
                        st.success("Fichier Excel téléchargé avec succès.")
                with export_2:
                    pdf_data = generer_pdf_cotisations(df_export, annee_filtre)
                    if pdf_data is not None:
                        st.download_button(
                            "Télécharger PDF",
                            data=pdf_data,
                            file_name=f"cotisations_{annee_filtre}.pdf",
                            mime="application/pdf",
                            width="stretch",
                            on_click=confirmer_telechargement,
                            args=(f"PDF ({annee_filtre})",),
                        )
                        if st.session_state.get("telechargement_confirme") == f"PDF ({annee_filtre})":
                            st.success("Fichier PDF téléchargé avec succès.")
                    else:
                        st.caption("PDF indisponible : installez reportlab.")

                st.markdown("### Modifier ou supprimer une cotisation")
                conn = get_db_connection()
                paiements = pd.read_sql_query(
                    """SELECT c.id, u.nom || ' ' || u.prenom AS membre,
                              c.periode, c.montant, c.date_paiement
                       FROM cotisations c JOIN users u ON u.id=c.user_id
                       WHERE c.annee=? ORDER BY membre, c.id""",
                    conn,
                    params=(annee_filtre,),
                )
                conn.close()
                if not paiements.empty:
                    paiement_id = st.selectbox(
                        "Sélectionner une cotisation",
                        paiements["id"].tolist(),
                        format_func=lambda value: (
                            f"{paiements.loc[paiements['id'] == value, 'membre'].iloc[0]} - "
                            f"{paiements.loc[paiements['id'] == value, 'periode'].iloc[0]} - "
                            f"{paiements.loc[paiements['id'] == value, 'montant'].iloc[0]:g} Dhs - "
                            f"{paiements.loc[paiements['id'] == value, 'date_paiement'].iloc[0] or ''}"
                        ),
                    )
                    paiement = paiements.loc[paiements["id"] == paiement_id].iloc[0]
                    with st.form("form_modifier_cotisation"):
                        montant_corrige = st.number_input("Montant corrigé (0 pour supprimer)", min_value=0.0, value=float(paiement["montant"]), step=10.0)
                        date_corrigee = st.text_input("Date corrigée", value=str(paiement["date_paiement"] or ""))
                        enregistrer_correction = st.form_submit_button("Enregistrer la correction")
                        if enregistrer_correction:
                            st.session_state["correction_en_attente"] = (
                                paiement_id, montant_corrige, date_corrigee.strip()
                            )
                            confirmer_correction_cotisation()

            else:
                st.info("Aucun membre dans la base de données.")

        with tab3:
            annee_membres = st.selectbox(
                "Année académique des membres", annees, key="annee_membres",
                on_change=synchroniser_annee_admin, args=("annee_membres",),
            )
            df_users_membres = get_users_for_year(annee_membres)
            for colonne in ("nom", "prenom", "contact"):
                df_users_membres[colonne] = df_users_membres[colonne].map(lambda valeur: texte_propre(valeur, "-"))
            col_add1, col_add2 = st.columns([1, 1])
            
            with col_add1:
                st.markdown("### ✍️ Ajouter un membre manuellement")
                with st.form("form_add_user", clear_on_submit=True):
                    new_nom = st.text_input("Nom (Nom de famille)")
                    new_prenom = st.text_input("Prénom(s)")
                    new_contact = st.text_input("Contact (Téléphone)")
                    submit_manuel = st.form_submit_button("Inscrire le membre")
                    
                    if submit_manuel:
                        if new_nom and new_prenom:
                            conn = get_db_connection()
                            c = conn.cursor()
                            nom_normalise = new_nom.strip().upper()
                            prenom_normalise = new_prenom.strip().title()
                            username_base = f"{prenom_normalise.lower().split()[0]}.{nom_normalise.lower()}".replace(" ", "")
                            
                            c.execute(
                                """SELECT id FROM users
                                   WHERE LOWER(TRIM(nom))=LOWER(?)
                                     AND LOWER(TRIM(prenom))=LOWER(?)
                                     AND role='user'""",
                                (nom_normalise, prenom_normalise),
                            )
                            membre_existant = c.fetchone()
                            if membre_existant:
                                c.execute(
                                                """INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 1)
                                                    ON CONFLICT (user_id, annee) DO UPDATE SET actif=EXCLUDED.actif""",
                                    (membre_existant[0], annee_membres),
                                )
                                conn.commit()
                                st.success("✅ Ce membre a été réactivé pour l'année sélectionnée.")
                            else:
                                c.execute("SELECT COUNT(*) FROM users WHERE role='user'")
                                next_id = c.fetchone()[0] + 1
                                password = generer_mot_de_passe(next_id)

                                try:
                                    c.execute(
                                        "SELECT username FROM users WHERE username LIKE ?",
                                        (f"{username_base}%",),
                                    )
                                    usernames_existants = {row[0] for row in c.fetchall()}
                                    username = username_base
                                    suffixe = 2
                                    while username in usernames_existants:
                                        username = f"{username_base}{suffixe}"
                                        suffixe += 1

                                    c.execute(
                                        """INSERT INTO users (username, password, role, nom, prenom, contact)
                                           VALUES (?, ?, 'user', ?, ?, ?) RETURNING id""",
                                        (username, password, nom_normalise, prenom_normalise, new_contact.strip()),
                                    )
                                    user_id = c.fetchone()[0]
                                    c.execute(
                                        "INSERT INTO membres_annee (user_id, annee, actif) VALUES (?, ?, 1)",
                                        (user_id, annee_membres),
                                    )
                                    conn.commit()
                                    st.success(f"✅ {nom_normalise} {prenom_normalise} ajouté avec succès ! Identifiant: {username} | Mdp: {password}")
                                except IntegrityError:
                                    conn.rollback()
                                    st.error("Cet identifiant existe déjà ou les données sont invalides. Réessayez avec un autre nom.")
                            conn.close()
                        else:
                            st.error("Le nom et le prénom sont obligatoires.")

            with col_add2:
                st.markdown("### 📥 Importez depuis Excel (Fusion)")
                st.write("Le fichier doit contenir une colonne **NOMS ET PRENOMS** (ou Nom et Prenom).")
                fichier = st.file_uploader("Sélectionnez le fichier Excel", type=["xlsx", "xls"])
                
                if fichier is not None:
                    df_import = pd.read_excel(fichier)
                    st.write("Aperçu :", df_import.head(2))
                    
                    if st.button("Lancer la fusion", type="primary"):
                        st.session_state["import_excel_en_attente"] = fichier.getvalue()
                        st.session_state["import_excel_annee"] = annee_membres
                        confirmer_importation_excel()

            st.markdown("### 👤 Informations d'un membre")
            membres_dict = {
                row["id"]: f"{row['nom']} {row['prenom']}"
                for _, row in df_users_membres.iterrows()
            }
            if membres_dict:
                membre_id = st.selectbox(
                    "Sélectionner un nom",
                    options=list(membres_dict),
                    format_func=lambda value: membres_dict[value],
                    key="membre_admin_selection",
                )
                conn = get_db_connection()
                details = conn.execute(
                    "SELECT username, password, nom, prenom, contact FROM users WHERE id=?",
                    (membre_id,),
                ).fetchone()
                paiements_membre = pd.read_sql_query(
                    "SELECT periode, SUM(montant) AS montant FROM cotisations WHERE user_id=? AND annee=? GROUP BY periode",
                    conn,
                    params=(membre_id, annee_membres),
                )
                conn.close()
                contact_membre = texte_propre(details[4], "")
                cotisations_membre = dict(zip(paiements_membre["periode"], paiements_membre["montant"]))
                with st.form("form_modifier_membre"):
                    mod_nom = st.text_input("Nom", value=details[2])
                    mod_prenom = st.text_input("Prénom", value=details[3])
                    mod_contact = st.text_input("Contact", value=contact_membre)
                    mod_username = st.text_input("Identifiant", value=details[0])
                    mod_password = st.text_input("Mot de passe", value=details[1])
                    if st.form_submit_button("Enregistrer les modifications"):
                        st.session_state["modification_en_attente"] = (
                            mod_nom.strip(), mod_prenom.strip(), mod_contact.strip(),
                            mod_username.strip().lower(), mod_password, membre_id,
                        )
                        confirmer_modification()
                if st.button("🗑️ Supprimer cet utilisateur", key="supprimer_membre"):
                    st.session_state["suppression_en_attente"] = (membre_id, annee_membres)
                    confirmer_suppression()
                cotisations_visibles = {
                    periode: float(montant)
                    for periode, montant in cotisations_membre.items()
                    if float(montant or 0) > 0
                }
                receipt = (
                    f"INFORMATIONS DU MEMBRE\n"
                    f"Nom : {details[2]}\nPrénom : {details[3]}\n"
                    f"Contact : {contact_membre}\nIdentifiant : {details[0]}\n"
                    f"Mot de passe : {details[1]}\n\nCOTISATIONS\n"
                    + "\n".join(f"{periode} : {montant:g} Dhs" for periode, montant in cotisations_visibles.items())
                )
                components.html(
                    f"""
                    <button id="copier-informations" type="button">Copier les informations</button>
                    <span id="copie" style="display:block;margin-top:8px;color:#2e8b57;"></span>
                    <textarea id="texte-a-copier" style="position:absolute;left:-9999px;">{receipt}</textarea>
                    <script>
                    const bouton = document.getElementById('copier-informations');
                    const texte = document.getElementById('texte-a-copier');
                    const message = document.getElementById('copie');
                    bouton.addEventListener('click', async () => {{
                        try {{
                            await navigator.clipboard.writeText(texte.value);
                        }} catch (erreur) {{
                            texte.focus();
                            texte.select();
                            document.execCommand('copy');
                        }}
                        message.textContent = 'Informations copiées avec succès.';
                    }});
                    </script>
                    """,
                    height=64,
                )
                pdf_membre = generer_pdf_membre(details, cotisations_visibles, annee_membres)
                if pdf_membre is not None:
                    st.download_button(
                        "Télécharger la fiche PDF",
                        data=pdf_membre,
                        file_name=f"fiche_{details[2]}_{details[3]}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        on_click=confirmer_telechargement,
                        args=(f"Fiche PDF {membre_id}",),
                    )
                    if st.session_state.get("telechargement_confirme") == f"Fiche PDF {membre_id}":
                        st.success("Fiche PDF téléchargée avec succès.")

    # ==========================================
    #        INTERFACE UTILISATEUR
    # ==========================================
    elif st.session_state['role'] == 'user':
        st.markdown(
            f"<h1 style='text-align: center; color:#2f80ed !important;'>Bienvenue, "
            f"<span class='member-name-badge'>{st.session_state['nom']}</span></h1>",
            unsafe_allow_html=True,
        )
        st.markdown("<h3 style='text-align: center;'>Sur votre tableau de bord des cotisations</h3><br>", unsafe_allow_html=True)
        
        col_u1, col_u2, col_u3 = st.columns([1,2,1])
        with col_u2:
            annee_select = st.selectbox("Sélectionnez l'année académique", annees)
        
        conn = get_db_connection()
        df_user_cotis = pd.read_sql_query(
            "SELECT periode, SUM(montant) AS montant, MAX(date_paiement) AS date_paiement "
            "FROM cotisations WHERE user_id=? AND annee=? GROUP BY periode",
            conn,
            params=(st.session_state['user_id'], annee_select),
        )
        conn.close()
        
        cotisations_dict = df_user_cotis.set_index('periode').to_dict('index')
        conn = get_db_connection()
        objectifs = conn.execute(
            "SELECT total_annuel, total_bimensuel, total_a_cotiser FROM objectifs_cotisation WHERE annee=?",
            (annee_select,),
        ).fetchone()
        details_utilisateur = conn.execute(
            "SELECT nom, prenom, contact FROM users WHERE id=?",
            (st.session_state['user_id'],),
        ).fetchone()
        conn.close()
        objectif_annuel, objectif_bimensuel, objectif_total = objectifs or (0.0, 0.0, 0.0)
        total_annuel = float(cotisations_dict.get("COTISATION ANNUELLE", {}).get("montant", 0) or 0)
        total_bimensuel = sum(
            float(cotisations_dict.get(periode, {}).get("montant", 0) or 0)
            for periode in periodes
            if periode != "COTISATION ANNUELLE"
        )
        total_cotise = total_annuel + total_bimensuel
        objectif_total_effectif = float(objectif_total or 0)
        reste_a_payer = max(objectif_total_effectif - total_cotise, 0)
        
        st.markdown("<hr style='border-color: rgba(150,150,150,0.2);'>", unsafe_allow_html=True)
        
        for periode in periodes:
            c1, c2 = st.columns([2.4, 1.6])
            with c1:
                if periode == "COTISATION ANNUELLE":
                    st.markdown(f"<h4 style='color: #FFD700; margin: 0;'>{periode}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**Période : {periode.upper()}**")
            with c2:
                montant = float(cotisations_dict.get(periode, {}).get("montant", 0) or 0)
                if montant > 0:
                    date_paiement = cotisations_dict[periode].get("date_paiement", "")
                    st.markdown(
                        f"<div style='text-align:right;'>"
                        f"<strong style='color:#4CAF50;'>Payé</strong><br>"
                        f"<span style='font-size:18px;'>{montant:g} Dhs</span><br>"
                        f"<small>{date_paiement}</small></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div style='text-align:right;'>"
                        "<strong style='color:#ff6b81;'>Non payé</strong>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
            st.divider()

        st.markdown("### Résumé des cotisations")
        montant_annuel_affiche = "" if total_annuel <= 0 else f"{total_annuel:g}"
        montant_bimensuel_affiche = "" if total_bimensuel <= 0 else f"{total_bimensuel:g}"
        total_cotise_affiche = "" if total_cotise <= 0 else f"{total_cotise:g}"
        reste_a_payer_affiche = "" if reste_a_payer <= 0 else f"{reste_a_payer:g}"
        resume_1, resume_2 = st.columns(2)
        with resume_1:
            st.metric("Total annuel", f"{montant_annuel_affiche} / {float(objectif_annuel):g} Dhs")
            st.metric("Total bimensuel", f"{montant_bimensuel_affiche} / {float(objectif_bimensuel):g} Dhs")
        with resume_2:
            st.metric("Total cotisé", f"{total_cotise_affiche} Dhs")
            st.metric("Reste à payer", f"{reste_a_payer_affiche} Dhs")

        if details_utilisateur:
            pdf_bulletin = generer_pdf_bulletin_utilisateur(
                details_utilisateur,
                cotisations_dict,
                annee_select,
                objectifs or (0.0, 0.0, 0.0),
            )
            if pdf_bulletin is not None:
                st.download_button(
                    "Télécharger mon bulletin annuel en PDF",
                    data=pdf_bulletin,
                    file_name=f"bulletin_cotisation_{annee_select}.pdf",
                    mime="application/pdf",
                    width="stretch",
                    key="telecharger_bulletin_utilisateur",
                )
            else:
                st.error("Le bulletin PDF est indisponible : installez reportlab.")

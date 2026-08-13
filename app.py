"""
app.py — SuggestBot (Ayushveda) Premium Streamlit Frontend
A modern, beautiful AI-powered disease treatment assistant.
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from core.db_utils import (
    test_connection, get_table_preview, get_all_diseases,
    get_disease_count, query_treatment, initialize_chat_history_table,
    save_chat_message, load_chat_history, clear_chat_history,
    get_user_chat_dataframe
)
from core.disease_matcher import find_disease_in_query
from core.ai_engine import (
    initialize_gemini, initialize_grok, generate_treatment_response,
    generate_disease_info, generate_general_response, classify_query
)

# === Configuration ===
DB_PATH = os.environ.get("DB_PATH", "ritesh.db")
GEMINI_API_KEY = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()

# === Page Config ===
st.set_page_config(
    page_title="Ayushveda — AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Premium Custom CSS ===
st.markdown("""
<style>
    /* === Google Fonts === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* === Warm Beige & Orange Canvas === */
    html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
        background: #FAF4EB !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(243, 156, 18, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(230, 126, 34, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 30%, rgba(245, 233, 219, 0.5) 0px, transparent 60%) !important;
        background-attachment: fixed !important;
        color: #2D1C10 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* === Sidebar Styling & Distinct Vertical Divider Line === */
    section[data-testid="stSidebar"] {
        background: #F4EAE0 !important;
        border-right: 2.5px solid #D8C7B5 !important;
        box-shadow: 6px 0 20px rgba(54, 37, 24, 0.07) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: #4A3B2C !important;
        font-size: 0.9rem;
    }

    section[data-testid="stSidebar"] input {
        background: #FFFFFF !important;
        border: 1px solid #E6D8C8 !important;
        color: #2D1C10 !important;
        border-radius: 10px !important;
    }

    /* === Sidebar Slide Left / Reverse Expand Toggle Button === */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-header"],
    button[aria-label*="sidebar"],
    div[data-testid="stSidebarNav"] button,
    [data-testid="stHeader"] button {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #DFCFBD !important;
        border-radius: 50% !important;
        color: #EF7D1A !important;
        width: 38px !important;
        height: 38px !important;
        box-shadow: 0 4px 12px rgba(54, 37, 24, 0.12) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[data-testid="stSidebarCollapseButton"]:hover,
    button[aria-label*="sidebar"]:hover,
    [data-testid="stHeader"] button:hover {
        background: linear-gradient(135deg, #F39C12 0%, #EF7D1A 100%) !important;
        border-color: #DF7010 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(239, 125, 26, 0.4) !important;
        transform: scale(1.1) !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg,
    button[aria-label*="sidebar"] svg,
    [data-testid="stHeader"] button svg {
        fill: #EF7D1A !important;
        color: #EF7D1A !important;
    }

    button[data-testid="stSidebarCollapseButton"]:hover svg,
    button[aria-label*="sidebar"]:hover svg,
    [data-testid="stHeader"] button:hover svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* === Main Text & Headings Override === */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div {
        color: #2D1C10 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2D1C10 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* === Hero Section (Warm Beige Card) === */
    .hero-container {
        background: linear-gradient(135deg, #F5E9DB 0%, #FAF4EB 100%);
        border: 1px solid #E6D4C2;
        border-radius: 20px;
        padding: 2.2rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(74, 59, 44, 0.06);
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2D1C10, #EF7D1A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #635345;
        font-weight: 400;
        line-height: 1.6;
    }

    /* === Status Badge === */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    .status-online {
        background: #E8F8F0;
        color: #27AE60;
        border: 1px solid #C8E6D5;
    }

    .status-offline {
        background: #FDE8E8;
        color: #E74C3C;
        border: 1px solid #F5C6C6;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse-dot 2s ease-in-out infinite;
    }

    .status-dot.online { background: #27AE60; box-shadow: 0 0 10px #27AE60; }
    .status-dot.offline { background: #E74C3C; box-shadow: 0 0 10px #E74C3C; }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.85); }
    }

    /* === Stat Cards === */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 1.2rem 0;
    }

    .stat-card {
        background: #FFFFFF;
        border: 1px solid #EFE4D6;
        border-radius: 12px;
        padding: 1rem 0.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(74, 59, 44, 0.04);
    }

    .stat-card:hover {
        border-color: #EF7D1A;
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(239, 125, 26, 0.15);
    }

    .stat-number {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #EF7D1A, #E67E22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        font-size: 0.75rem;
        color: #786656;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 2px;
    }

    /* === Chat Messages Styling (Warm Beige & Orange Theme) === */
    div[data-testid="stChatMessage"] {
        border-radius: 18px !important;
        padding: 1.1rem 1.4rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(54, 37, 24, 0.04) !important;
    }

    /* Assistant / Received Messages (Left - Crisp White Card) */
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 🏥"]),
    div[data-testid="stChatMessage"]:has(img[alt="🏥"]),
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background: #FFFFFF !important;
        border: 1px solid #EFE4D6 !important;
        color: #2D1C10 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 🏥"]) .stMarkdown,
    div[data-testid="stChatMessage"]:has(div[aria-label="chat avatar 🏥"]) p,
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) .stMarkdown,
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) p {
        color: #2D1C10 !important;
    }

    /* === Custom User Chat Bubble (Vibrant Warm Orange matching Switch User) === */
    .user-chat-bubble {
        background: linear-gradient(135deg, #F39C12 0%, #EF7D1A 100%) !important;
        background-color: #EF7D1A !important;
        border: 1px solid #DF7010 !important;
        border-radius: 18px !important;
        padding: 0.95rem 1.4rem !important;
        margin: 1rem 0 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 22px rgba(239, 125, 26, 0.35) !important;
        display: flex !important;
        align-items: center !important;
        gap: 14px !important;
        width: 100% !important;
    }

    .user-chat-avatar {
        font-size: 1.25rem !important;
        background: rgba(255, 255, 255, 0.22) !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        color: #FFFFFF !important;
    }

    .user-chat-text {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        line-height: 1.5 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Headings inside Chat Messages (e.g. 🏥 Treatment for Anemia) — Warm Orange */
    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3,
    div[data-testid="stChatMessage"] h4,
    div[data-testid="stChatMessage"] h5,
    div[data-testid="stChatMessage"] h6 {
        color: #EF7D1A !important;
        -webkit-text-fill-color: #EF7D1A !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Switch User Primary Orange Button Override */
    button[key="switch_user_btn"],
    div.stButton > button[key="switch_user_btn"] {
        background: linear-gradient(135deg, #F39C12 0%, #EF7D1A 100%) !important;
        background-color: #EF7D1A !important;
        border: 1px solid #DF7010 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 20px rgba(239, 125, 26, 0.35) !important;
    }

    /* === Chat Input Bar & BaseWeb Overrides === */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background: transparent !important;
    }

    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] div[data-baseweb="base-input"],
    div[data-testid="stChatInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border-radius: 24px !important;
        border: 1.5px solid #E6D8C8 !important;
        box-shadow: 0 6px 25px rgba(54, 37, 24, 0.08) !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: #EF7D1A !important;
    }

    div[data-testid="stChatInput"] textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="base-input"] textarea {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder,
    div[data-baseweb="input"] input::placeholder {
        color: #9E8E80 !important;
        -webkit-text-fill-color: #9E8E80 !important;
    }

    /* === Send Button Accent === */
    div[data-testid="stChatInput"] button {
        background-color: #EF7D1A !important;
        border-radius: 50% !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    div[data-testid="stChatInput"] button svg {
        fill: #FFFFFF !important;
    }

    /* === ALL Text Inputs Fix (stTextInput, Username, Filter, API Key) === */
    div[data-testid="stTextInput"],
    div[data-testid="stTextInput"] *,
    div[data-baseweb="input"],
    div[data-baseweb="input"] *,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] * {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
        border: 1.5px solid #E6D8C8 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-baseweb="input"] input:focus {
        border-color: #EF7D1A !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="base-input"] input::placeholder {
        color: #9E8E80 !important;
        -webkit-text-fill-color: #9E8E80 !important;
    }

    /* === BaseWeb Select & Popover Menu Fix (Complete Elimination of Black Backgrounds) === */
    div[data-testid="stSelectbox"],
    div[data-testid="stSelectbox"] *,
    div[data-baseweb="select"],
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] > div,
    div[data-baseweb="icon"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
        border-color: #E6D8C8 !important;
    }

    div[data-baseweb="select"] svg,
    div[data-baseweb="icon"] svg {
        fill: #2D1C10 !important;
        color: #2D1C10 !important;
    }

    /* Floating Popover Overlay Menu */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] *,
    ul[role="listbox"],
    ul[role="listbox"] *,
    li[role="option"],
    li[role="option"] * {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
    }

    /* Hover & Active Selected Option in Dropdown */
    li[role="option"]:hover,
    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] * {
        background-color: #FDF1E6 !important;
        background: #FDF1E6 !important;
        color: #EF7D1A !important;
        -webkit-text-fill-color: #EF7D1A !important;
        font-weight: 700 !important;
    }

    /* === Streamlit Expanders Fix (Prevent Any Black Backgrounds) === */
    div[data-testid="stExpander"],
    details[data-testid="stExpander"],
    summary[data-testid="stExpanderSummary"],
    details[data-testid="stExpander"] summary {
        background-color: #F8EFE4 !important;
        background: #F8EFE4 !important;
        border: 1px solid #E8DCCF !important;
        border-radius: 14px !important;
        margin-bottom: 0.8rem !important;
    }

    summary[data-testid="stExpanderSummary"] *,
    details[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] summary * {
        color: #2D1C10 !important;
        -webkit-text-fill-color: #2D1C10 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    summary[data-testid="stExpanderSummary"]:hover,
    details[data-testid="stExpander"] summary:hover,
    details[data-testid="stExpander"] summary:hover * {
        background-color: #FDF1E6 !important;
        background: #FDF1E6 !important;
        color: #EF7D1A !important;
        -webkit-text-fill-color: #EF7D1A !important;
    }

    div[data-testid="stExpander"] summary svg {
        fill: #2D1C10 !important;
        color: #2D1C10 !important;
    }

    /* === Buttons Styling (Clean Cream Default -> Bright Orange on Cursor Hover/Click) === */
    .stButton > button,
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F5E9DB 100%) !important;
        border: 1px solid #E6D8C8 !important;
        color: #2D1C10 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 6px rgba(54, 37, 24, 0.05) !important;
    }

    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #F39C12 0%, #EF7D1A 100%) !important;
        color: #FFFFFF !important;
        border-color: #DF7010 !important;
        box-shadow: 0 8px 25px rgba(239, 125, 26, 0.45) !important;
        transform: translateY(-2px) !important;
    }

    .auth-input-label {
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        color: #362518 !important;
        font-weight: 600 !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
    }

    /* === Disease Grid Chips === */
    .disease-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 0.6rem;
        margin: 0.8rem 0;
    }

    .disease-chip {
        background: #FFFFFF;
        border: 1px solid #EFE4D6;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        text-align: center;
        color: #4A3B2C;
        font-size: 0.82rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .disease-chip:hover {
        background: #FDF1E6;
        border-color: #EF7D1A;
        color: #EF7D1A;
    }

    /* === Detection Badge === */
    .detection-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #FDF1E6;
        border: 1px solid #FCD3B1;
        border-radius: 100px;
        padding: 6px 14px;
        font-size: 0.84rem;
        color: #D96B18;
        margin-bottom: 0.8rem;
    }

    .detection-badge.fuzzy {
        background: #FFFBEB;
        border-color: #FDE68A;
        color: #D97706;
    }

    .detection-badge.context {
        background: #ECFDF5;
        border-color: #A7F3D0;
        color: #059669;
    }

    /* === Tip Cards === */
    .tip-card {
        background: #FFFFFF !important;
        border: 1px solid #EFE4D6 !important;
        border-radius: 16px !important;
        padding: 1.2rem 1.4rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(54, 37, 24, 0.04) !important;
    }

    .tip-card:hover {
        border-color: #EF7D1A !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(239, 125, 26, 0.18) !important;
    }

    .tip-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
    .tip-title { font-weight: 700; color: #2D1C10; font-size: 1.02rem; margin-bottom: 4px; }
    .tip-desc { color: #635345; font-size: 0.86rem; line-height: 1.5; }
    .tip-example { color: #EF7D1A; font-size: 0.82rem; font-style: italic; margin-top: 6px; }

    /* === Authentication Landing Slide CSS === */
    .auth-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem 1.5rem;
        text-align: center;
    }

    .auth-card {
        background: #FFFFFF;
        border: 1px solid #EFE4D6;
        border-radius: 24px;
        padding: 2.5rem 2rem 1.8rem;
        max-width: 600px;
        width: 100%;
        box-shadow: 0 15px 50px rgba(54, 37, 24, 0.08);
        margin: 0 auto;
        text-align: center;
    }

    .auth-logo { font-size: 3.5rem; margin-bottom: 0.6rem; }

    .auth-badge {
        display: inline-block;
        background: #FDF1E6;
        border: 1px solid #FCD3B1;
        border-radius: 100px;
        padding: 6px 18px;
        font-size: 0.8rem;
        font-weight: 700;
        color: #EF7D1A;
        letter-spacing: 0.08em;
        margin-bottom: 1rem;
    }

    .auth-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2D1C10, #EF7D1A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.8rem;
    }

    .auth-subtitle {
        color: #635345;
        font-size: 1.02rem;
        line-height: 1.6;
        margin-bottom: 1.2rem;
    }

    .auth-features-grid {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }

    .auth-feature-chip {
        background: #FFFFFF;
        border: 1px solid #EFE4D6;
        border-radius: 100px;
        padding: 8px 18px;
        font-size: 0.84rem;
        color: #786656;
    }

    /* === User Profile Sidebar Badge === */
    .user-profile-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #FFFFFF;
        border: 1px solid #E6D8C8;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(54, 37, 24, 0.04);
    }

    .profile-avatar {
        font-size: 1.4rem;
        background: linear-gradient(135deg, #F39C12, #EF7D1A);
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(239, 125, 26, 0.3);
        color: #FFFFFF;
    }

    .profile-details {
        display: flex;
        flex-direction: column;
    }

    .profile-name {
        font-weight: 700;
        color: #2D1C10;
        font-size: 1rem;
    }

    .profile-status {
        font-size: 0.78rem;
        color: #27AE60;
        font-weight: 500;
    }

    /* === Section Divider === */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E6D8C8, transparent);
        margin: 1.2rem 0;
    }

    /* === Footer === */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #786656;
        font-size: 0.82rem;
        border-top: 1px solid #E6D8C8;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# === Initialize App State ===
def init_app():
    """Initialize application state and services."""
    # Initialize Gemini AI
    if GEMINI_API_KEY and "ai_initialized" not in st.session_state:
        try:
            model = initialize_gemini(GEMINI_API_KEY)
            st.session_state.ai_initialized = True if model else False
        except Exception:
            st.session_state.ai_initialized = False
    elif not GEMINI_API_KEY:
        st.session_state.ai_initialized = False

    # Initialize chat history table
    initialize_chat_history_table(DB_PATH)

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_disease" not in st.session_state:
        st.session_state.last_disease = None


def render_auth_slide():
    """Render the ultra-modern login / onboarding landing slide."""
    st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">🏥</div>
            <div class="auth-badge">✨ AI-POWERED HEALTH ENGINE</div>
            <h1 class="auth-title">Welcome to Ayushveda</h1>
            <p class="auth-subtitle">
                Enter your Username to start your personalized AI health consultation and session history.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="auth-input-label">Enter Username to Begin Session:</div>', unsafe_allow_html=True)
        name_input = st.text_input(
            "Username",
            placeholder="e.g. Ritesh Pandey",
            key="login_name_input",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Start Session", width="stretch", key="start_session_btn"):
                user_name = name_input.strip() if name_input.strip() else "User"
                st.session_state.username = user_name
                st.session_state.authenticated = True
                st.session_state.messages = load_chat_history(DB_PATH, user_name)
                st.rerun()
        with btn_col2:
            if st.button("Guest Access", width="stretch", key="guest_session_btn"):
                st.session_state.username = "Guest"
                st.session_state.authenticated = True
                st.session_state.messages = load_chat_history(DB_PATH, "Guest")
                st.rerun()

        st.markdown("""
        <div class="auth-features-grid">
            <div class="auth-feature-chip">Secure SQLite Session</div>
            <div class="auth-feature-chip">Powered by Gemini AI</div>
            <div class="auth-feature-chip">60+ Disease Treatments</div>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """Render the premium sidebar."""
    with st.sidebar:
        # Logo / Brand
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 1.2rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">🏥</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700;
                        background: linear-gradient(135deg, #2D1C10, #EF7D1A);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        background-clip: text;">Ayushveda</div>
            <div style="font-size: 0.72rem; color: #786656; letter-spacing: 0.1em; text-transform: uppercase;
                        margin-top: 2px;">AI Health Assistant</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # User Profile Expander (Minimizable User Account Section)
        with st.expander("User Account & Profile", expanded=True):
            st.markdown(f"""
            <div class="user-profile-badge">
                <div class="profile-avatar">👤</div>
                <div class="profile-details">
                    <div class="profile-name">{st.session_state.username}</div>
                    <div class="profile-status">● Active Session</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Switch User", type="primary", width="stretch", key="switch_user_btn"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.messages = []
                st.rerun()

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Database Status
        st.markdown("##### Database")
        db_ok, db_msg = test_connection(DB_PATH)
        if db_ok:
            st.markdown(f"""
            <div class="status-badge status-online">
                <div class="status-dot online"></div>
                {db_msg}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-badge status-offline">
                <div class="status-dot offline"></div>
                {db_msg}
            </div>
            """, unsafe_allow_html=True)

        # Stats
        disease_count = get_disease_count(DB_PATH)
        msg_count = len(st.session_state.messages)
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{disease_count}</div>
                <div class="stat-label">Diseases</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{msg_count}</div>
                <div class="stat-label">Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{'🟢' if st.session_state.get('ai_initialized') else '🔴'}</div>
                <div class="stat-label">Gemini AI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Preview Table
        with st.expander("Preview Treatment Data"):
            preview = get_table_preview(DB_PATH)
            if preview is not None:
                st.dataframe(preview, width="stretch", hide_index=True)
            else:
                st.caption("No data available")

        # Disease Browser & Interactive Selector
        with st.expander("Browse & Select Diseases"):
            diseases = get_all_diseases(DB_PATH)
            if diseases:
                selected_disease = st.selectbox(
                    "Search or select a disease:",
                    options=["-- Select a Disease --"] + diseases,
                    key="sidebar_disease_selectbox"
                )
                if selected_disease != "-- Select a Disease --":
                    # Check if this disease selection is new
                    if st.session_state.get("last_selected_disease") != selected_disease:
                        st.session_state.last_selected_disease = selected_disease
                        st.session_state.pending_prompt = f"What is the treatment for {selected_disease}?"
                        st.rerun()

                    if st.button(f"Get Treatment for {selected_disease}", width="stretch", key="ask_selected_disease_btn"):
                        st.session_state.pending_prompt = f"What is the treatment for {selected_disease}?"
                        st.rerun()

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                search = st.text_input("Filter list below...", key="disease_filter", placeholder="Type to filter...")
                filtered = [d for d in diseases if search.lower() in d.lower()] if search else diseases

                cols = st.columns(2)
                for idx, d in enumerate(filtered[:24]):
                    with cols[idx % 2]:
                        if st.button(f"{d}", key=f"dis_chip_btn_{idx}", width="stretch"):
                            st.session_state.pending_prompt = f"What is the treatment for {d}?"
                            st.rerun()

                if len(filtered) > 24:
                    st.caption(f"Showing 24 of {len(filtered)} matching diseases. Use search/dropdown above to view all.")
            else:
                st.caption("No diseases in database")

        # Saved Queries & Export Log
        with st.expander("Saved Queries & Export"):
            chat_df = get_user_chat_dataframe(DB_PATH, st.session_state.username)
            if not chat_df.empty:
                st.dataframe(chat_df, width="stretch", hide_index=True)
                csv_data = chat_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download History (CSV)",
                    data=csv_data,
                    file_name=f"{st.session_state.username}_health_queries.csv",
                    mime="text/csv",
                    width="stretch"
                )
            else:
                st.caption("No saved queries found for your user.")

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", width="stretch"):
                username = None
                clear_chat_history(DB_PATH, username)
                st.session_state.messages = []
                st.session_state.last_disease = None 
                st.rerun()
        with col2:
            if st.button("Refresh", width="stretch"):
                st.rerun()

        # API Key input if not set
        if not GEMINI_API_KEY and not st.session_state.get('ai_initialized'):
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("##### API Configuration")
            api_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key.strip()
                try:
                    model = initialize_gemini(api_key.strip())
                    if model:
                        st.session_state.ai_initialized = True
                        st.success("Gemini API connected!")
                        st.rerun()
                    else:
                        st.error("Failed to initialize Gemini API.")
                except Exception as e:
                    st.error(f"Invalid API Key: {e}")


def render_hero():
    """Render the hero/welcome section."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Namaste! Welcome to Ayushveda</div>
        <div class="hero-subtitle">
            Your trusted AI assistant for disease treatments and health queries.
            Ask me about any disease — I'll find the best treatment information for you.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome_tips():
    """Show helpful tips and interactive prompt chips when chat is empty."""
    st.markdown("<h4 style='color: #ffffff; font-weight: 700; margin-bottom: 1rem;'>Quick Prompts & Examples</h4>", unsafe_allow_html=True)

    tips = [
        ("", "Treatment Queries", "What is the treatment for diabetes?", "Look up treatment guidelines from medical database"),
        ("", "Disease Summary", "Tell me about tuberculosis", "Get concise disease summaries powered by Gemini AI"),
        ("", "Symptom Analysis", "What are the symptoms of malaria?", "Learn about signs and when to seek urgent help"),
        ("", "General Health", "What is a healthy daily diet?", "Ask any general health or wellness question"),
    ]

    cols = st.columns(2)
    for i, (icon, title, example, desc) in enumerate(tips):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="tip-card">
                <div class="tip-icon">{icon}</div>
                <div class="tip-title">{title}</div>
                <div class="tip-desc">{desc}</div>
                <div class="tip-example">"{example}"</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Try: {example}", key=f"quick_btn_{i}", width="stretch"):
                st.session_state.pending_prompt = example
                st.rerun()


def process_query(question):
    """Process a user query and return a response."""
    diseases = get_all_diseases(DB_PATH)
    query_type = classify_query(question)

    # Try to detect a disease in the question
    disease, match_method = find_disease_in_query(
        question, diseases, st.session_state.last_disease
    )

    if disease:
        st.session_state.last_disease = disease

        # Show detection badge
        badge_class = {
            "exact": "",
            "fuzzy": " fuzzy",
            "context": " context"
        }.get(match_method, "")

        method_label = {
            "exact": "Exact match",
            "fuzzy": "Fuzzy match",
            "context": "From context"
        }.get(match_method, "Detected")

        st.markdown(f"""
        <div class="detection-badge{badge_class}">
            🎯 Detected: <strong>{disease}</strong> — {method_label}
        </div>
        """, unsafe_allow_html=True)

    if query_type == "treatment" and disease:
        # Fetch treatment from DB
        treatment = query_treatment(DB_PATH, disease)
        if treatment:
            response = generate_treatment_response(disease, treatment)
        else:
            response = f"I don't have treatment information for **{disease}** in my database yet."

    elif query_type == "symptom" and disease:
        # Generate disease info via Grok
        response = generate_disease_info(disease, question)

    elif disease:
        # Disease found but generic question — provide treatment
        treatment = query_treatment(DB_PATH, disease)
        if treatment:
            response = generate_treatment_response(disease, treatment)
        else:
            response = generate_disease_info(disease, question)

    else:
        # General query — use Grok
        # Build recent context
        recent = st.session_state.messages[-6:] if len(st.session_state.messages) > 0 else []
        context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        response = generate_general_response(question, context)

    return response


def main():
    """Main application entry point."""
    init_app()

    # Authentication Landing Slide
    if not st.session_state.get("authenticated"):
        render_auth_slide()
        return

    render_sidebar()

    # Hero section (only show when chat is empty)
    if not st.session_state.messages:
        render_hero()
        render_welcome_tips()

    # Chat history display
    for msg in st.session_state.messages:
        if msg["role"] == "human":
            st.markdown(f"""
            <div class="user-chat-bubble">
                <div class="user-chat-avatar">👤</div>
                <div class="user-chat-text">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🏥"):
                st.markdown(msg["content"])

    # Chat input & pending quick prompt
    prompt = st.chat_input("Ask me about any disease or health topic...")
    if st.session_state.get("pending_prompt"):
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "human", "content": prompt})
        save_chat_message(DB_PATH, st.session_state.username, "human", prompt)

        st.markdown(f"""
        <div class="user-chat-bubble">
            <div class="user-chat-avatar">👤</div>
            <div class="user-chat-text">{prompt}</div>
        </div>
        """, unsafe_allow_html=True)

        # Generate response
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("Thinking..."):
                response = process_query(prompt)

            # Typewriter effect
            placeholder = st.empty()
            displayed = ""
            for char in response:
                displayed += char
                placeholder.markdown(displayed + "▌")
                time.sleep(0.006)
            placeholder.markdown(response)

        # Save response
        st.session_state.messages.append({"role": "ai", "content": response})
        save_chat_message(DB_PATH, st.session_state.username, "ai", response)

    # Footer
    st.markdown("""
    <div class="footer">
        <div><strong>Ayushveda</strong> — AI-Powered Disease Treatment Assistant</div>
        <div style="margin-top: 4px;">Built with Streamlit • Powered by Google Gemini AI • Data stored in SQLite</div>
        <div style="margin-top: 4px;">This is for informational purposes only. Always consult a healthcare professional.</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Vercel top-level export handler
app = main
application = main
handler = main

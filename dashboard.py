import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import re
import subprocess
import threading
import os
import time
import sys
import logging
import shutil
from datetime import datetime
from tools.remediation import remediate_finding

# Suppress Streamlit thread warnings
logging.getLogger("streamlit.runtime.scriptrunner.script_runner").setLevel(
    logging.ERROR
)

st.set_page_config(
    page_title="SecureScan Data Discovery Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ANIMATIONS & KEYFRAMES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(59,130,246,0.3); }
        50% { box-shadow: 0 0 15px rgba(59,130,246,0.6); }
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* BASE STYLING */
    /* ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1117 0%, #0a0e17 100%);
        color: #e2e8f0;
    }
    [data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #1e2535;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        animation: fadeIn 0.5s ease-out;
    }

    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    p, li, span { color: #94a3b8; }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* PAGE HEADER */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 32px;
        padding-bottom: 24px;
        border-bottom: 2px solid rgba(59,130,246,0.2);
        animation: slideDown 0.6s ease-out;
    }
    .logo-text {
        font-size: 32px;
        font-weight: 900;
        color: #f1f5f9;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .logo-accent {
        color: #3b82f6;
        -webkit-text-fill-color: #3b82f6;
    }
    .logo-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
        letter-spacing: 0.5px;
    }
    .header-badge {
        background: linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(79,172,254,0.1) 100%);
        border: 1px solid rgba(59,130,246,0.4);
        color: #60a5fa;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.05em;
        animation: glow 2s ease-in-out infinite;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* NAVIGATION TABS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button {
        background: #161b27 !important;
        color: #94a3b8 !important;
        border: 1px solid #1e2535 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        background: #1a2332 !important;
        border-color: #3b82f6 !important;
        color: #f1f5f9 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(59,130,246,0.2) !important;
    }
    .stButton > button[type="primary"] {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(30,64,175,0.4) !important;
    }
    .stButton > button[type="primary"]:hover {
        box-shadow: 0 8px 24px rgba(30,64,175,0.6) !important;
        transform: translateY(-3px);
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* METRIC CARDS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .metric-card {
        background: linear-gradient(135deg, #161b27 0%, #0f1117 100%);
        border: 1px solid #1e2535;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.6s ease-out;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent);
    }
    .metric-card:hover {
        border-color: rgba(59,130,246,0.5);
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(59,130,246,0.15);
        background: linear-gradient(135deg, #1a2332 0%, #161b27 100%);
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1;
        margin: 8px 0;
        animation: fadeIn 0.7s ease-out;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #64748b;
        margin-top: 8px;
    }
    .metric-total .metric-value { color: #60a5fa; text-shadow: 0 0 20px rgba(96,165,250,0.4); }
    .metric-critical .metric-value { color: #ff6b6b; text-shadow: 0 0 20px rgba(255,107,107,0.4); }
    .metric-medium .metric-value { color: #ffa94d; text-shadow: 0 0 20px rgba(255,169,77,0.4); }
    .metric-low .metric-value { color: #51cf66; text-shadow: 0 0 20px rgba(81,207,102,0.4); }
    .metric-remediated .metric-value { color: #b197fc; text-shadow: 0 0 20px rgba(177,151,252,0.4); }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* SECTION HEADERS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .section-header {
        font-size: 16px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(59,130,246,0.2);
        position: relative;
        display: inline-block;
        width: 100%;
    }
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, transparent);
        width: 100%;
        animation: slideInLeft 0.6s ease-out;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* CHART CONTAINERS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .chart-card {
        background: linear-gradient(135deg, #161b27 0%, #0f1117 100%);
        border: 1px solid #1e2535;
        border-radius: 14px;
        padding: 24px;
        transition: all 0.4s ease;
        animation: fadeIn 0.6s ease-out;
    }
    .chart-card:hover {
        border-color: rgba(59,130,246,0.3);
        box-shadow: 0 12px 28px rgba(59,130,246,0.1);
        transform: translateY(-4px);
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* BADGES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        animation: fadeIn 0.5s ease-out;
    }
    .badge-critical {
        background: rgba(255,107,107,0.15);
        color: #ff6b6b;
        box-shadow: 0 0 10px rgba(255,107,107,0.2);
    }
    .badge-medium {
        background: rgba(255,169,77,0.15);
        color: #ffa94d;
        box-shadow: 0 0 10px rgba(255,169,77,0.2);
    }
    .badge-low {
        background: rgba(81,207,102,0.15);
        color: #51cf66;
        box-shadow: 0 0 10px rgba(81,207,102,0.2);
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FORMS & INPUTS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: linear-gradient(135deg, #0f1117 0%, #0a0e17 100%) !important;
        border: 1px solid #1e2535 !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        transition: all 0.3s ease !important;
        font-weight: 500;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59,130,246,0.2) !important;
        background: linear-gradient(135deg, #161b27 0%, #0f1117 100%) !important;
    }
    .stCheckbox > label {
        color: #94a3b8 !important;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stCheckbox > label:hover {
        color: #f1f5f9 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* EXPANDERS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #161b27 0%, #0f1117 100%) !important;
        border: 1px solid #1e2535 !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        transition: all 0.3s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #1a2332 0%, #161b27 100%) !important;
        border-color: rgba(59,130,246,0.3) !important;
    }
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #0f1117 0%, #0a0e17 100%) !important;
        border: 1px solid #1e2535 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* DATAFRAME */
    /* ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e2535 !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: rgba(59,130,246,0.08) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ALERTS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid !important;
        animation: slideInLeft 0.4s ease-out;
    }
    .stAlert[kind="info"] {
        background: rgba(59,130,246,0.12) !important;
        border-left-color: #3b82f6 !important;
    }
    .stAlert[kind="warning"] {
        background: rgba(255,169,77,0.12) !important;
        border-left-color: #ffa94d !important;
    }
    .stAlert[kind="error"] {
        background: rgba(255,107,107,0.12) !important;
        border-left-color: #ff6b6b !important;
    }
    .stAlert[kind="success"] {
        background: rgba(81,207,102,0.12) !important;
        border-left-color: #51cf66 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* LOG BOX */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .log-box {
        background: #0a0e17;
        border: 1px solid #1e2535;
        border-radius: 12px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #94a3b8;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.6;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.3);
        animation: fadeIn 0.5s ease-out;
    }
    .log-line-ok { color: #51cf66; font-weight: 600; }
    .log-line-err { color: #ff6b6b; font-weight: 600; }
    .log-line-info { color: #74c0fc; font-weight: 600; }

    /* Scrollbar styling */
    .log-box::-webkit-scrollbar {
        width: 8px;
    }
    .log-box::-webkit-scrollbar-track {
        background: #0a0e17;
    }
    .log-box::-webkit-scrollbar-thumb {
        background: #1e2535;
        border-radius: 4px;
    }
    .log-box::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* STATUS INDICATORS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
        position: relative;
    }
    .dot-ok {
        background: #51cf66;
        box-shadow: 0 0 12px #51cf66, inset 0 0 4px rgba(81,207,102,0.5);
        animation: pulse 2s ease-in-out infinite;
    }
    .dot-warn {
        background: #ffa94d;
        box-shadow: 0 0 12px #ffa94d, inset 0 0 4px rgba(255,169,77,0.5);
        animation: pulse 1.5s ease-in-out infinite;
    }
    .dot-err {
        background: #ff6b6b;
        box-shadow: 0 0 12px #ff6b6b, inset 0 0 4px rgba(255,107,107,0.5);
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* SCAN PANEL */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .scan-title {
        font-size: 28px;
        font-weight: 900;
        color: #f1f5f9;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .scan-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 24px;
        letter-spacing: 0.3px;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* MISC */
    /* ═══════════════════════════════════════════════════════════════════════ */
    hr {
        border-color: #1e2535 !important;
        margin: 20px 0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #60a5fa) !important;
        animation: shimmer 2s infinite;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .page-header { margin-bottom: 20px; }
        .logo-text { font-size: 24px; }
        .metric-value { font-size: 2rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)


# Global variable to track scan process
current_scan_process = None


@st.cache_data(ttl=30)
def load_data():
    try:
        conn = sqlite3.connect("outputs/findings.db")
        df = pd.read_sql_query("SELECT * FROM findings", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_remediated_data():
    try:
        conn = sqlite3.connect("outputs/remediated.db")
        df = pd.read_sql_query("SELECT * FROM remediated_findings", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def clean_context_analysis(text):
    if not text:
        return "No context analysis available"
    text = re.sub(r"Finding \d+:.*?\n", "", text)
    text = re.sub(r"\*\*Finding \d+.*?\*\*", "", text)
    text = re.sub(r'\{[^}]*"file_type"[^}]*\}', "", text)
    text = re.sub(r"```json[\s\S]*?```", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"Here[\s\S]*?JSON format:?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Here is my answer[\s\S]*?:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"My answer in JSON format:?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Explanation:", "**Analysis:**", text)
    text = re.sub(r"\*\*File Type\*\*:.*?\n", "", text)
    text = re.sub(r"\*\*Security Status\*\*:.*?\n", "", text)
    text = re.sub(r"\*\* \*\*", "", text)
    text = re.sub(r"\*\*\s*\*\*", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_badge(risk):
    cls = {
        "Critical": "badge-critical",
        "Medium": "badge-medium",
        "Low": "badge-low",
    }.get(risk, "badge-medium")
    return f'<span class="badge {cls}">{risk}</span>'


def stop_scan():
    """Stop the currently running scan process"""
    global current_scan_process
    if current_scan_process and current_scan_process.poll() is None:
        try:
            if sys.platform == "win32":
                import signal

                os.kill(current_scan_process.pid, signal.CTRL_C_EVENT)
                time.sleep(0.5)
                if current_scan_process.poll() is None:
                    subprocess.call(
                        ["taskkill", "/F", "/T", "/PID", str(current_scan_process.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            else:
                import signal

                os.kill(current_scan_process.pid, signal.SIGINT)
                time.sleep(0.5)
                if current_scan_process.poll() is None:
                    current_scan_process.kill()

            stop_msg = "\n[!] Scan stopped by user (Ctrl+C)\n"
            st.session_state.scan_log = st.session_state.get("scan_log", "") + stop_msg
            try:
                with open("outputs/scan.log", "a") as f:
                    f.write(stop_msg)
            except:
                pass

            st.session_state.scan_status = "stopped"
            st.session_state.scan_done = True
            current_scan_process = None
            return True
        except Exception as e:
            print(f"Error stopping scan: {e}", flush=True)
            return False
    return False


def run_scan_background(cmd, log_key, status_key, done_key):
    global current_scan_process
    try:
        with open("outputs/scan.log", "w") as f:
            f.write("")

        if sys.platform == "win32":
            current_scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            current_scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                preexec_fn=os.setsid,
            )

        for line in iter(current_scan_process.stdout.readline, ""):
            if line:
                if st.session_state.get(status_key) == "running":
                    st.session_state[log_key] = st.session_state.get(log_key, "") + line
                    with open("outputs/scan.log", "a") as f:
                        f.write(line)
                else:
                    break

        current_scan_process.wait()

        if st.session_state.get(status_key) != "stopped":
            st.session_state[status_key] = (
                "done" if current_scan_process.returncode == 0 else "error"
            )
    except Exception as e:
        error_msg = f"\nError: {e}"
        if st.session_state.get(status_key) != "stopped":
            st.session_state[log_key] = st.session_state.get(log_key, "") + error_msg
            with open("outputs/scan.log", "a") as f:
                f.write(error_msg)
            st.session_state[status_key] = "error"
    finally:
        st.session_state[done_key] = True
        current_scan_process = None


# Page header
st.markdown(
    """
<div class="page-header">
    <div>
        <div class="logo-text">Secure<span class="logo-accent">Scan</span></div>
        <div class="logo-subtitle">Autonomous Credit Card Data Discovery & Compliance System</div>
    </div>
    <div class="header-badge">Data Security v4.0</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- Navigation ---
TABS = ["Overview", "Run Scan", "AI Analysis", "Remediated", "Executive Report"]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

nav_cols = st.columns(len(TABS))
for i, (col, name) in enumerate(zip(nav_cols, TABS)):
    with col:
        btn_type = "primary" if st.session_state.active_tab == i else "secondary"
        if st.button(name, key=f"nav_{i}", type=btn_type, use_container_width=True):
            st.session_state.active_tab = i
            st.rerun()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

df = load_data()

# ── SHARED METRICS ─────────────────────────────────────────────────────────────
if not df.empty:
    total_findings = len(df)
    critical_count = len(df[df["risk_level"] == "Critical"])
    medium_count = len(df[df["risk_level"] == "Medium"])
    low_count = len(df[df["risk_level"] == "Low"])
    
    # Load remediated count from remediated.db
    remediated_df_count = load_remediated_data()
    remediated_count = len(remediated_df_count) if not remediated_df_count.empty else 0
    
    scan_date = df["scan_date"].max() if "scan_date" in df.columns else "N/A"

    mc = st.columns(5)
    cards = [
        ("metric-total", str(total_findings), "Total Findings"),
        ("metric-critical", str(critical_count), "Critical Risk"),
        ("metric-medium", str(medium_count), "Medium Risk"),
        ("metric-low", str(low_count), "Low Risk"),
        ("metric-remediated", str(remediated_count), "Remediated"),
    ]
    for col, (cls, val, lbl) in zip(mc, cards):
        with col:
            st.markdown(
                f"""
            <div class="metric-card {cls}">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 0 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == 0:
    if df.empty:
        st.markdown(
            """
        <div style="text-align:center;padding:100px 0;animation:fadeIn 0.6s ease-out">
            <div style="margin-bottom:20px">
                <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
            </div>
            <div style="font-size:24px;font-weight:800;color:#f1f5f9;margin-bottom:12px">No scan results yet</div>
            <div style="color:#64748b;font-size:15px">Head to the <b>Run Scan</b> tab to start your first compliance scan</div>
        </div>""",
            unsafe_allow_html=True,
        )
    else:
        color_map = {"Critical": "#ff6b6b", "Medium": "#ffa94d", "Low": "#51cf66"}
        chart_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", size=12, family="Arial, sans-serif"),
            margin=dict(l=8, r=8, t=28, b=8),
            hovermode="closest",
        )

        r1c1, r1c2 = st.columns(2)

        with r1c1:
            st.markdown(
                '<div class="chart-card" style="border:none;background:transparent;padding:0"><div class="section-header">Risk Distribution</div></div>',
                unsafe_allow_html=True,
            )
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=risk_counts["Risk Level"],
                        values=risk_counts["Count"],
                        hole=0.55,
                        marker=dict(
                            colors=[
                                color_map.get(x, "#94a3b8")
                                for x in risk_counts["Risk Level"]
                            ]
                        ),
                        textposition="inside",
                        textinfo="percent+label",
                        textfont=dict(color="#fff", size=13, family="Arial"),
                        hovertemplate="<b>%{label}</b><br>%{value} findings<br>%{percent}<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                **chart_layout,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8", size=11),
                ),
            )
            st.plotly_chart(
                fig, use_container_width=True, config={"displayModeBar": False}
            )

        with r1c2:
            st.markdown(
                '<div class="chart-card" style="border:none;background:transparent;padding:0"><div class="section-header">Findings by File Extension</div></div>',
                unsafe_allow_html=True,
            )
            df["extension"] = df["file"].str.extract(r"\.([^.]+)$").fillna("none")
            ext_counts = df["extension"].value_counts().head(8).reset_index()
            ext_counts.columns = ["Extension", "Count"]
            fig2 = go.Figure(
                data=[
                    go.Bar(
                        x=ext_counts["Extension"],
                        y=ext_counts["Count"],
                        marker=dict(
                            color=ext_counts["Count"],
                            colorscale=[[0, "#0f1117"], [1, "#60a5fa"]],
                            showscale=False,
                            line=dict(color="#1e2535", width=1),
                        ),
                        text=ext_counts["Count"],
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>%{y} findings<extra></extra>",
                    )
                ]
            )
            fig2.update_layout(
                **chart_layout,
                showlegend=False,
                xaxis=dict(gridcolor="#1e2535", title=""),
                yaxis=dict(gridcolor="#1e2535", title=""),
            )
            st.plotly_chart(
                fig2, use_container_width=True, config={"displayModeBar": False}
            )

        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.markdown(
                '<div class="chart-card" style="border:none;background:transparent;padding:0"><div class="section-header">Source Breakdown</div></div>',
                unsafe_allow_html=True,
            )
            df["source"] = df["file"].apply(
                lambda x: "S3" if x.startswith("s3://") else ("Cloud" if x.startswith("gdrive://") else "Local")
            )
            source_counts = df["source"].value_counts().reset_index()
            source_counts.columns = ["Source", "Count"]
            fig3 = go.Figure(
                data=[
                    go.Bar(
                        x=source_counts["Source"],
                        y=source_counts["Count"],
                        marker=dict(
                            color=[
                                {"Local": "#60a5fa", "Cloud": "#ffa94d", "S3": "#b197fc"}[s]
                                for s in source_counts["Source"]
                            ],
                            line=dict(color="#1e2535", width=1),
                        ),
                        text=source_counts["Count"],
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>%{y} findings<extra></extra>",
                    )
                ]
            )
            fig3.update_layout(
                **chart_layout,
                showlegend=False,
                xaxis=dict(gridcolor="#1e2535", title=""),
                yaxis=dict(gridcolor="#1e2535", title=""),
            )
            st.plotly_chart(
                fig3, use_container_width=True, config={"displayModeBar": False}
            )

        with r2c2:
            st.markdown(
                '<div class="chart-card" style="border:none;background:transparent;padding:0"><div class="section-header">Risk by File Category</div></div>',
                unsafe_allow_html=True,
            )

            def categorize(path):
                p = path.lower()
                if "config" in p or p.endswith((".env", ".ini", ".conf")):
                    return "Config"
                if "log" in p:
                    return "Logs"
                if "backup" in p or p.endswith(".sql"):
                    return "Backup"
                if p.endswith((".csv", ".json", ".xml")):
                    return "Data"
                return "Other"

            df["file_cat"] = df["file"].apply(categorize)
            ftr = (
                df.groupby(["file_cat", "risk_level"]).size().reset_index(name="count")
            )
            fig4 = go.Figure()
            for risk in ["Critical", "Medium", "Low"]:
                risk_data = ftr[ftr["risk_level"] == risk]
                fig4.add_trace(
                    go.Bar(
                        x=risk_data["file_cat"],
                        y=risk_data["count"],
                        name=risk,
                        marker=dict(
                            color=color_map[risk], line=dict(color="#1e2535", width=0.5)
                        ),
                        hovertemplate="<b>%{x}</b> - "
                        + risk
                        + "<br>%{y} findings<extra></extra>",
                    )
                )
            fig4.update_layout(
                **chart_layout,
                barmode="stack",
                xaxis=dict(title="", gridcolor="#1e2535"),
                yaxis=dict(title="", gridcolor="#1e2535"),
            )
            st.plotly_chart(
                fig4, use_container_width=True, config={"displayModeBar": False}
            )

        # --- Findings table ---
        st.markdown(
            '<div class="section-header" style="margin-top:20px">Findings Table</div>',
            unsafe_allow_html=True,
        )
        fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
        with fc1:
            search_q = st.text_input(
                "Search by file path",
                placeholder="e.g. /logs/app.log",
                label_visibility="collapsed",
            )
        with fc2:
            risk_opts = sorted(df["risk_level"].dropna().unique().tolist())
            selected_risks = st.multiselect(
                "Risk filter",
                risk_opts,
                default=risk_opts,
                label_visibility="collapsed",
                key="overview_risk",
            )
        with fc3:
            sort_by = st.selectbox(
                "Sort",
                ["Recent", "Risk Level", "File Name"],
                label_visibility="collapsed",
                key="overview_sort",
            )
        with fc4:
            if st.button("Clear All Findings", use_container_width=True, type="secondary", key="clear_findings_btn"):
                try:
                    if os.path.exists("outputs/findings.db"):
                        os.remove("outputs/findings.db")
                    if os.path.exists("outputs/findings.json"):
                        os.remove("outputs/findings.json")
                    if os.path.exists("outputs/report.txt"):
                        os.remove("outputs/report.txt")
                    if os.path.exists("outputs/scan.log"):
                        os.remove("outputs/scan.log")
                    load_data.clear()
                    st.success("All findings cleared!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        filtered = df[df["risk_level"].isin(selected_risks)].copy()
        if search_q:
            filtered = filtered[
                filtered["file"].str.contains(search_q, case=False, na=False)
            ]

        # Apply sorting
        if sort_by == "Risk Level":
            risk_order = {"Critical": 0, "Medium": 1, "Low": 2}
            filtered["risk_sort"] = filtered["risk_level"].map(risk_order)
            filtered = filtered.sort_values("risk_sort").drop("risk_sort", axis=1)
        elif sort_by == "File Name":
            filtered = filtered.sort_values("file")
        else:
            filtered = filtered.sort_values("scan_date", ascending=False)

        display = filtered[["file", "card_number", "risk_level", "scan_date"]].copy()
        display["card_number"] = display["card_number"].apply(
            lambda x: f"{str(x)[:4]}{'*' * 8}{str(x)[-4:]}" if len(str(x)) >= 8 else x
        )
        if "remediation" in filtered.columns:
            display["status"] = filtered["remediation"].apply(
                lambda x: "Remediated" if "Masked and saved" in str(x) else "Pending"
            )

        if len(display) > 0:
            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "file": st.column_config.TextColumn("File Path", width="large"),
                    "card_number": st.column_config.TextColumn(
                        "Card (Masked)", width="small"
                    ),
                    "risk_level": st.column_config.TextColumn("Risk", width="small"),
                    "scan_date": st.column_config.TextColumn(
                        "Scan Date", width="medium"
                    ),
                },
            )
            st.caption(f"📊 Showing {len(display)} of {len(df)} findings")
        else:
            st.info("No findings match your filters.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 – RUN SCAN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 1:
    if "scan_log" not in st.session_state:
        st.session_state.scan_log = ""
    if "scan_status" not in st.session_state:
        st.session_state.scan_status = "idle"
    if "scan_done" not in st.session_state:
        st.session_state.scan_done = False

    st.markdown(
        '<div class="scan-title">Run Security Scan</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="scan-subtitle">Configure your scan targets, then launch to detect sensitive data exposure</div>',
        unsafe_allow_html=True,
    )

    # --- Source selection ---
    st.markdown(
        '<div class="section-header">Scan Sources</div>', unsafe_allow_html=True
    )
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        use_local = st.checkbox("Local File System", value=True)
    with sc2:
        use_cloud = st.checkbox("Google Drive (Cloud)", value=False)
    with sc3:
        use_s3 = st.checkbox("AWS S3", value=False)
    with sc4:
        use_sample = st.checkbox("Use Sample Files", value=False)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # --- Path input ---
    if use_local and not use_sample:
        st.markdown(
            '<div class="section-header">Local Paths</div>', unsafe_allow_html=True
        )
        path_input = st.text_area(
            "Enter one or more paths (one per line)",
            placeholder="/var/log/app.log\n/home/user/documents\nC:\\Users\\user\\Desktop\\files",
            height=110,
            label_visibility="collapsed",
        )
        paths = [p.strip() for p in path_input.strip().splitlines() if p.strip()]
    elif use_sample:
        paths = ["sample_files"]
        st.info("Will scan the built-in `sample_files/` directory.")
    else:
        paths = []

    if use_cloud and not use_sample:
        st.markdown(
            '<div class="section-header" style="margin-top:12px">Cloud Configuration</div>',
            unsafe_allow_html=True,
        )
        gdrive_col1, gdrive_col2 = st.columns(2)
        with gdrive_col1:
            creds_file = st.text_input(
                "credentials.json path", value="cloud/credentials.json"
            )
        with gdrive_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if not os.path.exists(creds_file):
                st.warning(
                    "credentials.json not found — Google Drive scan will be skipped"
                )
    
    if use_s3 and not use_sample:
        st.markdown(
            '<div class="section-header" style="margin-top:12px">AWS S3 Configuration</div>',
            unsafe_allow_html=True,
        )
        s3_col1, s3_col2 = st.columns(2)
        with s3_col1:
            s3_bucket = st.text_input(
                "S3 Bucket Name (optional - leave empty to scan all accessible buckets)",
                placeholder="my-bucket-name",
                help="Leave empty to scan all accessible buckets"
            )
        with s3_col2:
            s3_prefix = st.text_input(
                "S3 Prefix/Folder (optional)",
                placeholder="logs/",
                help="Optional folder path within bucket"
            )
        
        st.info(
            "💡 AWS credentials should be configured via:\n"
            "- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)\n"
            "- AWS credentials file (~/.aws/credentials)\n"
            "- IAM role (if running on EC2)"
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # --- Scan status & launch ---
    scan_running = st.session_state.scan_status == "running"
    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        launch = st.button(
            "Launch Scan" if not scan_running else "Scanning...",
            type="primary",
            use_container_width=True,
            disabled=scan_running,
        )
    with col_status:
        if st.session_state.scan_status == "running":
            with st.spinner("Scan in progress..."):
                st.markdown(
                    '<span style="color:#ffa94d;font-weight:600">Scanning files and analyzing data...</span>',
                    unsafe_allow_html=True,
                )
        elif st.session_state.scan_status == "done":
            st.markdown(
                '<span class="status-dot dot-ok"></span><span style="color:#51cf66;font-weight:600">Scan completed successfully</span>',
                unsafe_allow_html=True,
            )
        elif st.session_state.scan_status == "error":
            st.markdown(
                '<span class="status-dot dot-err"></span><span style="color:#ff6b6b;font-weight:600">Scan encountered an error</span>',
                unsafe_allow_html=True,
            )
        elif st.session_state.scan_status == "stopped":
            st.markdown(
                '<span class="status-dot dot-warn"></span><span style="color:#ffa94d;font-weight:600">Scan stopped by user</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-dot" style="background:#334155"></span><span style="color:#64748b">Idle — configure options above and click Launch</span>',
                unsafe_allow_html=True,
            )

    if launch:
        # Determine scan mode based on selections
        if use_s3 and not use_local and not use_cloud:
            # S3 only mode
            target_path = "--s3-only"
        elif use_cloud and not use_local and not use_s3:
            # Cloud only mode
            target_path = "--cloud-only"
        elif paths:
            target_path = paths[0]
        else:
            target_path = "sample_files"
        
        cmd = ["python", "main.py", target_path]

        st.session_state.scan_log = ""
        st.session_state.scan_status = "running"
        st.session_state.scan_done = False
        load_data.clear()

        thread = threading.Thread(
            target=run_scan_background,
            args=(cmd, "scan_log", "scan_status", "scan_done"),
            daemon=True,
        )
        thread.start()
        st.rerun()

    # --- Log output ---
    if st.session_state.scan_log or scan_running:
        st.markdown(
            '<div class="section-header" style="margin-top:20px">Scan Output</div>',
            unsafe_allow_html=True,
        )

        log_lines = st.session_state.scan_log.splitlines()
        colored = []
        for line in log_lines[-80:]:
            if any(
                k in line
                for k in ["✓", "complete", "Done", "success", "generated", "saved"]
            ):
                colored.append(f'<span class="log-line-ok">{line}</span>')
            elif any(k in line for k in ["Error", "error", "fail", "Fail", "WARN"]):
                colored.append(f'<span class="log-line-err">{line}</span>')
            elif any(
                k in line for k in ["[", "Scanning", "Processing", "Classif", "Generat"]
            ):
                colored.append(f'<span class="log-line-info">{line}</span>')
            else:
                colored.append(line)

        log_html = "\n".join(colored)
        st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

        if scan_running:
            time.sleep(1.5)
            st.rerun()

    # --- Post-scan actions ---
    if st.session_state.scan_status == "done":
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        pa1, pa2 = st.columns(2)
        with pa1:
            if st.button("View Results", use_container_width=True, type="primary"):
                load_data.clear()
                st.session_state.scan_status = "idle"
                st.session_state.scan_log = ""
                st.session_state.active_tab = 0
                st.rerun()
        with pa2:
            if st.button(
                "Run Another Scan", use_container_width=True, type="secondary"
            ):
                st.session_state.scan_status = "idle"
                st.session_state.scan_log = ""
                st.rerun()

    # --- Multiple paths UI hint ---
    if use_local and not use_sample and (not scan_running):
        if paths and len(paths) > 1:
            st.markdown(
                f"""
            <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.25);
                        border-radius:12px;padding:16px;margin-top:12px;animation:slideInLeft 0.4s ease-out">
                <span style="color:#60a5fa;font-weight:700">Multi-path mode:</span>
                <span style="color:#94a3b8"> {len(paths)} paths queued. Only the first path is passed to the scanner in this version.</span>
            </div>""",
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – AI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 2:
    if df.empty:
        st.info("No scan data available. Run a scan first.")
    else:
        st.markdown(
            '<div class="section-header">AI Analysis per Finding</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="color:#64748b;font-size:14px;margin-bottom:16px">LLM-powered contextual analysis for each credit card exposure</div>',
            unsafe_allow_html=True,
        )

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            risk_opts = sorted(df["risk_level"].dropna().unique().tolist())
            risk_filter = st.multiselect(
                "Risk Level", risk_opts, default=risk_opts, key="ai_risk"
            )
        with fc2:
            source_filter = st.multiselect(
                "Source",
                ["Local", "Cloud", "S3"],
                default=["Local", "Cloud", "S3"],
                key="ai_source",
            )
        with fc3:
            search_ai = st.text_input(
                "Search file", placeholder="filter by path...", key="ai_search"
            )

        filtered_df = df[df["risk_level"].isin(risk_filter)].copy()
        
        # Apply source filters
        if len(source_filter) < 3:  # Not all sources selected
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            
            if "Local" in source_filter:
                mask |= ~(filtered_df["file"].str.startswith("gdrive://") | filtered_df["file"].str.startswith("s3://"))
            if "Cloud" in source_filter:
                mask |= filtered_df["file"].str.startswith("gdrive://")
            if "S3" in source_filter:
                mask |= filtered_df["file"].str.startswith("s3://")
            
            filtered_df = filtered_df[mask]
        if search_ai:
            filtered_df = filtered_df[
                filtered_df["file"].str.contains(search_ai, case=False, na=False)
            ]

        st.markdown(
            f'<div style="color:#64748b;font-size:13px;margin-bottom:16px;padding:12px;background:rgba(59,130,246,0.08);border-radius:8px;border-left:3px solid #3b82f6">{len(filtered_df)} findings shown</div>',
            unsafe_allow_html=True,
        )

        if len(filtered_df) > 0:
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                risk = row.get("risk_level", "Unknown")
                
                # Use plain text for expander title
                file_display = row['file'][:80] if len(row['file']) > 80 else row['file']
                expander_title = f"{file_display} - {risk}"

                with st.expander(expander_title, expanded=(idx == 0)):
                    # Show badge at the top of expander content
                    badge = get_badge(risk)
                    st.markdown(badge, unsafe_allow_html=True)
                    st.markdown("---")
                    
                    left, right = st.columns([1, 3])
                    with left:
                        card_str = str(row["card_number"])
                        masked = (
                            f"{card_str[:4]}{'*' * 8}{card_str[-4:]}"
                            if len(card_str) >= 8
                            else card_str
                        )
                        st.markdown(f"**Card:** `{masked}`")
                        source_lbl = (
                            "S3"
                            if str(row["file"]).startswith("s3://")
                            else ("Cloud" if str(row["file"]).startswith("gdrive://") else "Local")
                        )
                        st.markdown(f"**Source:** {source_lbl}")
                        if "remediation" in row and row["remediation"]:
                            is_done = "Masked and saved" in str(row["remediation"])
                            st.markdown(
                                f"**Status:** {'Remediated' if is_done else 'Pending'}"
                            )

                        st.markdown("---")
                        if st.button(
                            "Delete Finding",
                            key=f"del_{idx}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            try:
                                conn = sqlite3.connect("outputs/findings.db")
                                cursor = conn.cursor()
                                cursor.execute(
                                    "DELETE FROM findings WHERE id = ?", (row["id"],)
                                )
                                conn.commit()
                                conn.close()
                                load_data.clear()
                                st.success("Finding deleted!")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                        if st.button(
                            "Remediate",
                            key=f"rem_{idx}",
                            use_container_width=True,
                            type="primary",
                        ):
                            try:
                                is_s3 = str(row["file"]).startswith("s3://")
                                
                                success, message, remediated_path = remediate_finding(
                                    row["file"], row["card_number"]
                                )

                                if not success:
                                    st.error(message)
                                else:
                                    if is_s3:
                                        st.success("Remediated and uploaded to S3!")
                                    elif "Google Drive" in message:
                                        st.success(
                                            "Remediated locally and uploaded to Google Drive!"
                                        )
                                    else:
                                        st.success("Remediated locally!")

                                    rem_conn = sqlite3.connect("outputs/remediated.db")
                                    rem_cursor = rem_conn.cursor()
                                    rem_cursor.execute(
                                        """
                                        CREATE TABLE IF NOT EXISTS remediated_findings (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            original_file TEXT,
                                            remediated_file TEXT,
                                            card_number TEXT,
                                            risk_level TEXT,
                                            remediation TEXT,
                                            scan_date TEXT,
                                            remediation_date TEXT,
                                            context_analysis TEXT
                                        )
                                    """
                                    )
                                    
                                    # Update message for display
                                    display_message = message
                                    if is_s3:
                                        display_message = f"Masked and uploaded to S3: {remediated_path}"
                                    
                                    rem_cursor.execute(
                                        """
                                        INSERT INTO remediated_findings
                                        (original_file, remediated_file, card_number, risk_level, remediation, scan_date, remediation_date, context_analysis)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    """,
                                        (
                                            row["file"],
                                            remediated_path,
                                            row["card_number"],
                                            row["risk_level"],
                                            display_message,
                                            row["scan_date"],
                                            datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            ),
                                            row.get("context_analysis", ""),
                                        ),
                                    )
                                    rem_conn.commit()
                                    rem_conn.close()

                                    conn = sqlite3.connect("outputs/findings.db")
                                    cursor = conn.cursor()
                                    cursor.execute(
                                        "DELETE FROM findings WHERE id = ?",
                                        (row["id"],),
                                    )
                                    conn.commit()
                                    conn.close()

                                    load_data.clear()
                                    load_remediated_data.clear()
                                    st.success("Remediated! Card masked in file.")
                                    time.sleep(1)
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with right:
                        analysis = clean_context_analysis(
                            row.get("context_analysis", "")
                        )
                        st.markdown(analysis)
                        if "remediation" in row and "Masked and saved" in str(
                            row.get("remediation", "")
                        ):
                            st.success("✓ " + row["remediation"])
        else:
            st.info("No findings match your filters.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – REMEDIATED
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 3:
    remediated_df = load_remediated_data()

    if remediated_df.empty:
        st.info(
            "No remediated findings yet. Remediate findings from the AI Analysis tab."
        )
    else:
        st.markdown(
            '<div class="section-header">Remediated Findings</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="color:#64748b;font-size:14px;margin-bottom:16px">Total remediated: <span style="color:#51cf66;font-weight:700">{len(remediated_df)}</span></div>',
            unsafe_allow_html=True,
        )

        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            search_rem = st.text_input(
                "Search by file path",
                placeholder="e.g. /logs/app.log",
                label_visibility="collapsed",
                key="rem_search",
            )
        with fc2:
            risk_opts_rem = sorted(
                remediated_df["risk_level"].dropna().unique().tolist()
            )
            selected_risks_rem = st.multiselect(
                "Risk filter",
                risk_opts_rem,
                default=risk_opts_rem,
                label_visibility="collapsed",
                key="rem_risk",
            )
        with fc3:
            if st.button(
                "Clear Remediated Data", use_container_width=True, type="secondary", key="clear_all_rem_btn"
            ):
                try:
                    if os.path.exists("outputs/remediated.db"):
                        os.remove("outputs/remediated.db")
                    if os.path.exists("outputs/remediated_files"):
                        shutil.rmtree("outputs/remediated_files")
                    load_remediated_data.clear()
                    st.success("Remediated data cleared!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        filtered_rem = remediated_df[
            remediated_df["risk_level"].isin(selected_risks_rem)
        ]
        if search_rem:
            filtered_rem = filtered_rem[
                (
                    filtered_rem["original_file"].str.contains(
                        search_rem, case=False, na=False
                    )
                )
                | (
                    filtered_rem["remediated_file"].str.contains(
                        search_rem, case=False, na=False
                    )
                )
            ]

        st.markdown(
            f'<div style="color:#64748b;font-size:13px;margin-bottom:16px;padding:12px;background:rgba(81,207,102,0.08);border-radius:8px;border-left:3px solid #51cf66">{len(filtered_rem)} remediated findings shown</div>',
            unsafe_allow_html=True,
        )

        if len(filtered_rem) > 0:
            for idx, (_, row) in enumerate(filtered_rem.iterrows()):
                risk = row.get("risk_level", "Unknown")
                display_name = row.get("original_file", row.get("file", "Unknown"))
                
                # Use plain text for expander title
                file_display = display_name[:80] if len(display_name) > 80 else display_name
                expander_title = f"{file_display} - {risk}"

                with st.expander(expander_title):
                    # Show badge at the top of expander content
                    badge = get_badge(risk)
                    st.markdown(badge, unsafe_allow_html=True)
                    st.markdown("---")
                    
                    left, right = st.columns([1, 3])
                    with left:
                        card_str = str(row["card_number"])
                        masked = (
                            f"{card_str[:4]}{'*' * 8}{card_str[-4:]}"
                            if len(card_str) >= 8
                            else card_str
                        )
                        st.markdown(f"**Card:** `{masked}`")
                        st.markdown(f"**Status:** Remediated")
                        st.markdown(f"**Scanned:** {row['scan_date']}")
                        st.markdown(f"**Remediated:** {row['remediation_date']}")
                        if row.get("original_file"):
                            st.markdown(
                                f"**Original:** `{row['original_file'][:50]}...`"
                            )
                        if row.get("remediated_file"):
                            st.markdown(
                                f"**Remediated:** `{row['remediated_file'][:50]}...`"
                            )

                        st.markdown("---")
                        if st.button(
                            "Delete Record",
                            key=f"del_rem_{idx}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            try:
                                conn = sqlite3.connect("outputs/remediated.db")
                                cursor = conn.cursor()
                                cursor.execute(
                                    "DELETE FROM remediated_findings WHERE id = ?",
                                    (row["id"],),
                                )
                                conn.commit()
                                conn.close()
                                load_remediated_data.clear()
                                st.success("Record deleted!")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with right:
                        analysis = clean_context_analysis(
                            row.get("context_analysis", "")
                        )
                        st.markdown(analysis)
                        st.success("✓ This finding has been remediated")
                        if row.get("remediation"):
                            st.info(row["remediation"])
        else:
            st.info("No remediated findings match your filters.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 – EXECUTIVE REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 4:
    st.markdown(
        '<div class="section-header">Executive Compliance Report</div>',
        unsafe_allow_html=True,
    )
    try:
        with open("outputs/report.txt", "r", encoding="utf-8") as f:
            report_content = f.read()

        lines = report_content.split("\n")
        filtered_lines = []
        skip_section = False
        for line in lines:
            if line.strip().startswith("## Overview"):
                skip_section = True
            elif line.strip().startswith("## Detailed Findings"):
                break
            elif line.strip().startswith("---") and skip_section:
                skip_section = False
                continue
            elif not skip_section:
                filtered_lines.append(line)

        st.markdown(
            '<div style="background:linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(79,172,254,0.05) 100%);border:1px solid rgba(59,130,246,0.2);border-radius:14px;padding:24px;margin-bottom:24px;animation:fadeIn 0.6s ease-out">'
            + "\n".join(filtered_lines)
            + "</div>",
            unsafe_allow_html=True,
        )

        with open("outputs/report.txt", "r", encoding="utf-8") as f:
            raw = f.read()

        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                "Download Report",
                data=raw,
                file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            report_size = len(raw) / 1024
            st.metric("Report Size", f"{report_size:.1f} KB")
    except Exception:
        st.error(
            "No report found. Run a scan first to generate the executive report."
        )

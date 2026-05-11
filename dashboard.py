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
import json
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
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
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
    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255,169,77,0.3);
        border-top-color: #ffa94d;
        border-radius: 50%;
        animation: rotate 0.8s linear infinite;
        margin-right: 8px;
        vertical-align: middle;
    }
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
    }
    .dot-warn {
        background: #ffa94d;
        box-shadow: 0 0 12px #ffa94d, inset 0 0 4px rgba(255,169,77,0.5);
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
    .scan-summary-card {
        background: linear-gradient(135deg, rgba(22,27,39,0.95) 0%, rgba(15,17,23,0.95) 100%);
        border: 1px solid rgba(59,130,246,0.18);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
        animation: fadeIn 0.4s ease-out;
    }
    .scan-summary-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 8px;
    }
    .scan-summary-value {
        font-size: 16px;
        font-weight: 700;
        color: #f1f5f9;
    }
    .scan-summary-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }
    .scan-summary-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .scan-summary-chip-active {
        background: rgba(59,130,246,0.16);
        border: 1px solid rgba(59,130,246,0.28);
        color: #60a5fa;
    }
    .scan-summary-chip-muted {
        background: rgba(100,116,139,0.16);
        border: 1px solid rgba(100,116,139,0.24);
        color: #94a3b8;
    }
    .scan-status-panel {
        background: linear-gradient(135deg, rgba(22,27,39,0.95) 0%, rgba(15,17,23,0.95) 100%);
        border: 1px solid #1e2535;
        border-radius: 14px;
        padding: 16px 18px;
        animation: fadeIn 0.4s ease-out;
    }
    .scan-status-row {
        display: flex;
        align-items: center;
        min-height: 24px;
    }
    .status-message {
        font-weight: 600;
    }
    .status-message-running {
        color: #ffa94d;
    }
    .status-message-success {
        color: #51cf66;
    }
    .status-message-error {
        color: #ff6b6b;
    }
    .status-message-idle {
        color: #64748b;
    }
    .scan-meta {
        margin-top: 10px;
        font-size: 12px;
        color: #64748b;
    }
    .section-header-spaced {
        margin-top: 20px;
    }
    .section-header-tight {
        margin-top: 12px;
    }
    .scan-note-card {
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
        animation: slideInLeft 0.4s ease-out;
    }
    .scan-note-title {
        color: #60a5fa;
        font-weight: 700;
    }
    .scan-note-copy {
        color: #94a3b8;
    }
    .spacer-xs {
        height: 8px;
    }
    .spacer-sm {
        height: 12px;
    }
    .spacer-md {
        height: 16px;
    }
    .spacer-lg {
        height: 24px;
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
    /* CARDHOLDER DATA */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .cardholder-data-banner {
        background: rgba(255,107,107,0.12);
        border: 2px solid #ff6b6b;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 12px 0;
    }
    .cardholder-data-title {
        color: #ff6b6b;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .cardholder-data-summary {
        color: #f1f5f9;
        font-size: 13px;
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
SCAN_LOG_PATH = os.path.join("outputs", "scan.log")
SCAN_STATE_PATH = os.path.join("outputs", "scan_state.json")


def ensure_scan_outputs():
    os.makedirs("outputs", exist_ok=True)


def read_scan_log():
    try:
        with open(SCAN_LOG_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def write_scan_log(content, clear=False):
    ensure_scan_outputs()
    mode = "w" if clear else "a"
    with open(SCAN_LOG_PATH, mode, encoding="utf-8") as f:
        f.write(content)


def load_scan_state():
    try:
        with open(SCAN_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_scan_state(**updates):
    ensure_scan_outputs()
    state = load_scan_state()
    state.update(updates)
    with open(SCAN_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state


def reset_scan_state():
    save_scan_state(
        status="idle",
        progress="",
        progress_value=0,
        pid=None,
        command=None,
        returncode=None,
        started_at=None,
        completed_at=None,
    )


def get_progress_update(line):
    line_lower = line.lower()
    if (
        "total findings" in line_lower
        or "scan complete" in line_lower
        or "report generated" in line_lower
        or "findings saved" in line_lower
    ):
        return "✅ Scan complete!", 100
    if "[1/6]" in line or "discovery" in line_lower:
        return "🔍 Discovering files...", 15
    if "[2/6]" in line or "detection" in line_lower:
        return "🔎 Detecting credit cards...", 35
    if "[3/6]" in line or "validation" in line_lower:
        return "✓ Validating cards...", 50
    if "[4/6]" in line or "context" in line_lower:
        return "🤖 AI analysis in progress...", 65
    if "[5/6]" in line or "risk" in line_lower:
        return "⚠️ Classifying risks...", 80
    if "[6/6]" in line or "reporting" in line_lower:
        return "📊 Generating report...", 92
    if "database created" in line_lower or "creating dashboard database" in line_lower:
        return "💾 Finalizing...", 97
    if "starting" in line_lower:
        return "🚀 Starting scan...", 8
    if "scanning" in line_lower:
        return "📂 Scanning files...", 12
    return None, None


def derive_progress_from_log(log_text):
    progress_text = "Initializing scan..."
    progress_value = 5
    for line in log_text.splitlines():
        candidate_text, candidate_value = get_progress_update(line)
        if candidate_text:
            progress_text = candidate_text
            progress_value = candidate_value
    return progress_text, progress_value


def is_process_running(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ProcessLookupError, ValueError):
        return False
    return True


def artifact_updated_after(path, started_at):
    if not os.path.exists(path):
        return False
    if not started_at:
        return True
    try:
        started_ts = datetime.fromisoformat(started_at).timestamp()
    except ValueError:
        return True
    return os.path.getmtime(path) >= started_ts


def scan_artifacts_indicate_completion(state, log_text):
    started_at = state.get("started_at")
    log_lower = log_text.lower()
    completion_markers = [
        "total findings",
        "findings saved",
        "report generated",
        "database created successfully",
    ]
    if any(marker in log_lower for marker in completion_markers):
        return True
    return artifact_updated_after(os.path.join("outputs", "findings.db"), started_at) or artifact_updated_after(
        os.path.join("outputs", "report.txt"), started_at
    )


def sync_scan_status():
    previous_status = st.session_state.get("scan_status", "idle")
    state = load_scan_state()
    log_text = read_scan_log()

    if not state and not log_text:
        return

    progress_text, progress_value = derive_progress_from_log(log_text)
    status = state.get("status", previous_status)
    pid = state.get("pid")
    returncode = state.get("returncode")
    now = datetime.now().isoformat(timespec="seconds")

    if status == "running":
        if pid and is_process_running(pid):
            pass
        elif returncode == 0 or scan_artifacts_indicate_completion(state, log_text):
            status = "done"
            progress_text = "✅ Scan complete!"
            progress_value = 100
            state = save_scan_state(
                status=status,
                progress=progress_text,
                progress_value=progress_value,
                pid=None,
                returncode=0,
                completed_at=state.get("completed_at") or now,
            )
        elif "scan stopped by user" in log_text.lower():
            status = "stopped"
            progress_text = "⏹️ Scan stopped"
            state = save_scan_state(
                status=status,
                progress=progress_text,
                progress_value=progress_value,
                pid=None,
                completed_at=state.get("completed_at") or now,
            )
        elif returncode not in (None, 0):
            status = "error"
            progress_text = "❌ Scan failed"
            progress_value = 100
            state = save_scan_state(
                status=status,
                progress=progress_text,
                progress_value=progress_value,
                pid=None,
                completed_at=state.get("completed_at") or now,
            )

    if status == "done":
        progress_text = "✅ Scan complete!"
        progress_value = 100
    elif status == "error":
        progress_text = state.get("progress") or "❌ Scan failed"
        progress_value = state.get("progress_value", 100)
    elif status == "stopped":
        progress_text = state.get("progress") or "⏹️ Scan stopped"
        progress_value = state.get("progress_value", progress_value)

    st.session_state.scan_log = log_text
    st.session_state.scan_status = status
    st.session_state.scan_progress = state.get("progress") or progress_text
    st.session_state.scan_progress_value = state.get("progress_value", progress_value)
    st.session_state.scan_done = status in {"done", "error", "stopped"}
    st.session_state.scan_pid = state.get("pid")
    st.session_state.scan_started_at = state.get("started_at")
    st.session_state.scan_command = state.get("command") or []

    if previous_status != status and status == "done":
        load_data.clear()


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
    state = load_scan_state()
    pid = current_scan_process.pid if current_scan_process and current_scan_process.poll() is None else state.get("pid")

    if not pid or not is_process_running(pid):
        return False

    try:
        if sys.platform == "win32":
            subprocess.call(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            import signal

            try:
                os.killpg(os.getpgid(pid), signal.SIGINT)
            except ProcessLookupError:
                pass
            time.sleep(0.5)
            if is_process_running(pid):
                try:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass

        stop_msg = "\n[!] Scan stopped by user\n"
        write_scan_log(stop_msg)
        progress_text, progress_value = derive_progress_from_log(read_scan_log())
        save_scan_state(
            status="stopped",
            progress="⏹️ Scan stopped",
            progress_value=progress_value,
            pid=None,
            completed_at=datetime.now().isoformat(timespec="seconds"),
        )
        st.session_state.scan_log = read_scan_log()
        st.session_state.scan_status = "stopped"
        st.session_state.scan_progress = "⏹️ Scan stopped"
        st.session_state.scan_progress_value = progress_value
        st.session_state.scan_done = True
        current_scan_process = None
        return True
    except Exception as e:
        print(f"Error stopping scan: {e}", flush=True)
        return False


def run_scan_background(cmd):
    global current_scan_process
    try:
        command_string = " ".join(cmd)
        write_scan_log(f"Executing command: {command_string}\n\n")
        save_scan_state(
            status="running",
            progress="Initializing scan...",
            progress_value=5,
            pid=None,
            command=cmd,
            returncode=None,
            started_at=datetime.now().isoformat(timespec="seconds"),
            completed_at=None,
        )

        if sys.platform == "win32":
            current_scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
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
                bufsize=1,
                universal_newlines=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                preexec_fn=os.setsid,
            )

        save_scan_state(pid=current_scan_process.pid)

        for line in iter(current_scan_process.stdout.readline, ""):
            if not line:
                continue
            write_scan_log(line)
            progress_text, progress_value = get_progress_update(line)
            if progress_text:
                save_scan_state(
                    status="running",
                    progress=progress_text,
                    progress_value=progress_value,
                    pid=current_scan_process.pid,
                )

        current_scan_process.wait()
        state = load_scan_state()
        if state.get("status") == "stopped":
            return

        if current_scan_process.returncode == 0:
            save_scan_state(
                status="done",
                progress="✅ Scan complete!",
                progress_value=100,
                pid=None,
                returncode=0,
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
        else:
            save_scan_state(
                status="error",
                progress="❌ Scan failed",
                progress_value=100,
                pid=None,
                returncode=current_scan_process.returncode,
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
    except Exception as e:
        error_msg = f"\nError: {e}\n"
        write_scan_log(error_msg)
        state = load_scan_state()
        if state.get("status") != "stopped":
            save_scan_state(
                status="error",
                progress="❌ Scan failed",
                progress_value=100,
                pid=None,
                returncode=-1,
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
    finally:
        current_scan_process = None


def run_multi_scan_background(commands):
    """Run multiple scans sequentially and merge results"""
    global current_scan_process
    import sqlite3
    
    try:
        total_commands = len(commands)
        
        for idx, cmd in enumerate(commands, 1):
            command_string = " ".join(cmd)
            write_scan_log(f"\n{'='*60}\n")
            write_scan_log(f"Scanning path {idx}/{total_commands}\n")
            write_scan_log(f"Command: {command_string}\n\n")
            
            if sys.platform == "win32":
                current_scan_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
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
                    bufsize=1,
                    universal_newlines=True,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                    preexec_fn=os.setsid,
                )

            save_scan_state(pid=current_scan_process.pid)

            for line in iter(current_scan_process.stdout.readline, ""):
                if not line:
                    continue
                write_scan_log(line)
                progress_text, progress_value = get_progress_update(line)
                if progress_text:
                    # Adjust progress based on current path
                    base_progress = ((idx - 1) / total_commands) * 100
                    path_progress = (progress_value / 100) * (100 / total_commands)
                    total_progress = int(base_progress + path_progress)
                    save_scan_state(
                        status="running",
                        progress=f"[{idx}/{total_commands}] {progress_text}",
                        progress_value=total_progress,
                        pid=current_scan_process.pid,
                    )

            current_scan_process.wait()
            
            state = load_scan_state()
            if state.get("status") == "stopped":
                return
            
            if current_scan_process.returncode != 0:
                write_scan_log(f"\n⚠️ Path {idx} scan failed with return code {current_scan_process.returncode}\n")
            else:
                write_scan_log(f"\n✓ Path {idx} scan completed successfully\n")
        
        # All scans complete
        write_scan_log(f"\n{'='*60}\n")
        write_scan_log(f"All {total_commands} path(s) scanned successfully!\n")
        
        save_scan_state(
            status="done",
            progress="✅ All scans complete!",
            progress_value=100,
            pid=None,
            returncode=0,
            completed_at=datetime.now().isoformat(timespec="seconds"),
        )
    except Exception as e:
        error_msg = f"\nError: {e}\n"
        write_scan_log(error_msg)
        state = load_scan_state()
        if state.get("status") != "stopped":
            save_scan_state(
                status="error",
                progress="❌ Scan failed",
                progress_value=100,
                pid=None,
                returncode=-1,
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
    finally:
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
                lambda x: "S3" if x.startswith("s3://") else "Local"
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
                                {"Local": "#60a5fa", "S3": "#b197fc"}.get(s, "#94a3b8")
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
    if "scan_progress" not in st.session_state:
        st.session_state.scan_progress = ""
    if "scan_progress_value" not in st.session_state:
        st.session_state.scan_progress_value = 0
    if "scan_pid" not in st.session_state:
        st.session_state.scan_pid = None
    if "scan_started_at" not in st.session_state:
        st.session_state.scan_started_at = None
    if "scan_command" not in st.session_state:
        st.session_state.scan_command = []

    sync_scan_status()

    st.markdown(
        '<div class="scan-title">Run Security Scan</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="scan-subtitle">Configure your scan targets, then launch to detect sensitive data exposure</div>',
        unsafe_allow_html=True,
    )

    if "use_local" not in st.session_state:
        st.session_state.use_local = False
    if "use_s3" not in st.session_state:
        st.session_state.use_s3 = False
    if "use_sample" not in st.session_state:
        st.session_state.use_sample = True

    st.markdown(
        '<div class="section-header">Scan Sources</div>', unsafe_allow_html=True
    )
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        use_local = st.checkbox("Local File System", value=st.session_state.use_local, key="chk_local")
        st.session_state.use_local = use_local
    with sc2:
        use_s3 = st.checkbox("AWS S3", value=st.session_state.use_s3, key="chk_s3")
        st.session_state.use_s3 = use_s3
    with sc3:
        use_sample = st.checkbox("Use Sample Files", value=st.session_state.use_sample, key="chk_sample")
        st.session_state.use_sample = use_sample

    st.markdown('<div class="spacer-xs"></div>', unsafe_allow_html=True)

    # Initialize session state for paths
    if "scan_paths" not in st.session_state:
        st.session_state.scan_paths = []

    paths = []
    if use_local and not use_sample:
        st.markdown(
            '<div class="section-header">Local Paths</div>', unsafe_allow_html=True
        )
        
        # Add new path input
        col_input, col_add = st.columns([4, 1])
        with col_input:
            new_path = st.text_input(
                "Add path to scan",
                placeholder="C:\\Users\\YourName\\Documents\\test_folder",
                label_visibility="collapsed",
                key="new_path_input",
            )
        with col_add:
            if st.button("➕ Add", use_container_width=True, type="secondary"):
                if new_path and new_path.strip():
                    if os.path.exists(new_path.strip()):
                        if new_path.strip() not in st.session_state.scan_paths:
                            st.session_state.scan_paths.append(new_path.strip())
                            st.rerun()
                        else:
                            st.warning("Path already added")
                    else:
                        st.error("⚠️ Path does not exist")
                else:
                    st.warning("Please enter a path")
        
        # Display added paths
        if st.session_state.scan_paths:
            st.markdown('<div style="margin-top:12px;margin-bottom:8px;color:#94a3b8;font-size:13px;font-weight:600">Paths to scan:</div>', unsafe_allow_html=True)
            for idx, path in enumerate(st.session_state.scan_paths):
                col_path, col_remove = st.columns([5, 1])
                with col_path:
                    st.markdown(
                        f'<div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;padding:10px;margin-bottom:6px;color:#e2e8f0;font-size:13px">'
                        f'<span style="color:#60a5fa;font-weight:600">{idx+1}.</span> {path}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_remove:
                    if st.button("🗑️", key=f"remove_{idx}", use_container_width=True, type="secondary"):
                        st.session_state.scan_paths.pop(idx)
                        st.rerun()
            
            if st.button("Clear All Paths", type="secondary"):
                st.session_state.scan_paths = []
                st.rerun()
        else:
            st.info("➕ Add one or more paths to scan using the input above")
        
        paths = st.session_state.scan_paths
    elif use_sample:
        paths = ["sample_files"]
        st.markdown(
            '<div style="background:rgba(81,207,102,0.1);border:1px solid rgba(81,207,102,0.3);border-radius:10px;padding:14px;margin-top:12px">'
            '<span style="color:#51cf66;font-weight:700">✓ Sample Files Mode:</span> '
            '<span style="color:#94a3b8">Will scan all files in the <code>sample_files/</code> directory</span>'
            '</div>',
            unsafe_allow_html=True
        )

    if use_s3 and not use_sample:
        st.markdown(
            '<div class="section-header section-header-tight">AWS S3 Configuration</div>',
            unsafe_allow_html=True,
        )
        s3_col1, s3_col2 = st.columns(2)
        with s3_col1:
            s3_bucket = st.text_input(
                "S3 Bucket Name (optional - leave empty to scan all accessible buckets)",
                placeholder="my-bucket-name",
                help="Leave empty to scan all accessible buckets",
            )
        with s3_col2:
            s3_prefix = st.text_input(
                "S3 Prefix/Folder (optional)",
                placeholder="logs/",
                help="Optional folder path within bucket",
            )

        st.info(
            "💡 AWS credentials should be configured via:\n"
            "- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)\n"
            "- AWS credentials file (~/.aws/credentials)\n"
            "- IAM role (if running on EC2)"
        )
    else:
        s3_bucket = ""
        s3_prefix = ""

    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

    scan_running = st.session_state.scan_status == "running"
    can_launch = False
    validation_msg = ""

    if use_sample:
        can_launch = True
    elif use_local and paths:
        valid_paths = [p for p in paths if os.path.exists(p)]
        if valid_paths:
            can_launch = True
        else:
            validation_msg = "No valid paths provided"
    elif use_s3:
        can_launch = True
    else:
        validation_msg = "Please select at least one scan source and provide valid paths"

    col_launch, col_stop, col_status = st.columns([1, 1, 3])
    with col_launch:
        launch = st.button(
            "Launch Scan" if not scan_running else "Scanning...",
            type="primary",
            use_container_width=True,
            disabled=scan_running or not can_launch,
        )
    with col_stop:
        stop_requested = st.button(
            "Stop Scan",
            use_container_width=True,
            disabled=not scan_running,
        )
    with col_status:
        if st.session_state.scan_status == "running":
            progress_text = st.session_state.get("scan_progress", "Initializing scan...")
            status_markup = (
                f'<div class="scan-status-panel"><div class="scan-status-row">'
                f'<span class="spinner"></span><span class="status-message status-message-running">{progress_text}</span>'
                f'</div></div>'
            )
        elif st.session_state.scan_status == "done":
            status_markup = (
                '<div class="scan-status-panel"><div class="scan-status-row">'
                '<span class="status-dot dot-ok"></span><span class="status-message status-message-success">Scan completed successfully</span>'
                '</div></div>'
            )
        elif st.session_state.scan_status == "error":
            status_markup = (
                '<div class="scan-status-panel"><div class="scan-status-row">'
                '<span class="status-dot dot-err"></span><span class="status-message status-message-error">Scan encountered an error</span>'
                '</div></div>'
            )
        elif st.session_state.scan_status == "stopped":
            status_markup = (
                '<div class="scan-status-panel"><div class="scan-status-row">'
                '<span class="status-dot dot-warn"></span><span class="status-message status-message-running">Scan stopped by user</span>'
                '</div></div>'
            )
        elif not can_launch and validation_msg:
            status_markup = (
                '<div class="scan-status-panel"><div class="scan-status-row">'
                f'<span class="status-dot dot-err"></span><span class="status-message status-message-error">{validation_msg}</span>'
                '</div></div>'
            )
        else:
            status_markup = (
                '<div class="scan-status-panel"><div class="scan-status-row">'
                '<span class="status-dot"></span><span class="status-message status-message-idle">Ready to scan — click Launch when ready</span>'
                '</div></div>'
            )
        st.markdown(status_markup, unsafe_allow_html=True)

    if stop_requested and scan_running:
        if stop_scan():
            st.rerun()
        st.warning("No running scan process was found.")

    progress_value = int(st.session_state.get("scan_progress_value", 0) or 0)
    progress_value = max(0, min(progress_value, 100))
    if st.session_state.scan_status in {"running", "done", "error", "stopped"}:
        st.progress(progress_value)
        meta = []
        if st.session_state.get("scan_pid"):
            meta.append(f"PID {st.session_state.scan_pid}")
        if st.session_state.get("scan_started_at"):
            meta.append(f"Started {st.session_state.scan_started_at}")
        if meta:
            st.markdown(
                f'<div class="scan-meta">{" • ".join(meta)}</div>',
                unsafe_allow_html=True,
            )

    if launch:
        # Determine paths to scan
        if use_sample:
            scan_paths_to_process = ["sample_files"]
        elif use_local and paths:
            scan_paths_to_process = paths
        elif use_s3:
            scan_paths_to_process = ["."]
        else:
            st.error("Please select at least one scan source.")
            st.stop()

        # Build commands for all paths
        all_commands = []
        for scan_path in scan_paths_to_process:
            cmd = [sys.executable, "main.py", scan_path]
            if use_s3:
                cmd.append("--s3")
            if use_s3 and not use_local and not use_sample:
                cmd.append("--skip-local")
            all_commands.append(cmd)

        sources_list = []
        if use_sample:
            sources_list.append("Sample Files")
        if use_local and paths and not use_sample:
            sources_list.extend([f"Local: {p}" for p in paths])
        if use_s3:
            bucket_details = f" ({s3_bucket})" if s3_bucket else ""
            prefix_details = f" / {s3_prefix}" if s3_prefix else ""
            sources_list.append(f"AWS S3{bucket_details}{prefix_details}")

        starting_log = f"Starting multi-path scan...\nTotal paths: {len(scan_paths_to_process)}\nSources: {', '.join(sources_list)}\n\n"
        for i, cmd in enumerate(all_commands, 1):
            starting_log += f"Path {i}/{len(all_commands)}: {' '.join(cmd)}\n"
        starting_log += "\n"
        write_scan_log(starting_log, clear=True)
        save_scan_state(
            status="running",
            progress="Initializing scan...",
            progress_value=5,
            pid=None,
            command=all_commands,
            returncode=None,
            started_at=datetime.now().isoformat(timespec="seconds"),
            completed_at=None,
        )
        st.session_state.scan_log = starting_log
        st.session_state.scan_status = "running"
        st.session_state.scan_done = False
        st.session_state.scan_progress = "Initializing scan..."
        st.session_state.scan_progress_value = 5
        st.session_state.scan_command = all_commands
        load_data.clear()

        # Run scans sequentially for all paths
        thread = threading.Thread(
            target=run_multi_scan_background,
            args=(all_commands,),
            daemon=True,
        )
        thread.start()
        st.rerun()

    if st.session_state.scan_log or scan_running:
        st.markdown(
            '<div class="section-header section-header-spaced">Scan Output</div>',
            unsafe_allow_html=True,
        )

        log_lines = st.session_state.scan_log.splitlines()
        colored = []
        for line in log_lines[-100:]:
            if any(
                k in line
                for k in ["✓", "complete", "Done", "success", "generated", "saved", "created"]
            ):
                colored.append(f'<span class="log-line-ok">{line}</span>')
            elif any(k in line for k in ["Error", "error", "fail", "Fail", "WARN"]):
                colored.append(f'<span class="log-line-err">{line}</span>')
            elif any(
                k in line for k in ["[", "Scanning", "Processing", "Classif", "Generat", "Starting", "Sources"]
            ):
                colored.append(f'<span class="log-line-info">{line}</span>')
            else:
                colored.append(line)

        log_html = "\n".join(colored)
        st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

        if scan_running:
            time.sleep(1.5)
            st.rerun()

    if st.session_state.scan_status == "done":
        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        pa1, pa2 = st.columns(2)
        with pa1:
            if st.button("View Results", use_container_width=True, type="primary"):
                load_data.clear()
                reset_scan_state()
                st.session_state.scan_status = "idle"
                st.session_state.scan_log = ""
                st.session_state.active_tab = 0
                st.rerun()
        with pa2:
            if st.button(
                "Run Another Scan", use_container_width=True, type="secondary"
            ):
                reset_scan_state()
                st.session_state.scan_status = "idle"
                st.session_state.scan_log = ""
                st.rerun()



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
                ["Local", "S3"],
                default=["Local", "S3"],
                key="ai_source",
            )
        with fc3:
            search_ai = st.text_input(
                "Search file", placeholder="filter by path...", key="ai_search"
            )

        filtered_df = df[df["risk_level"].isin(risk_filter)].copy()
        
        # Apply source filters
        if len(source_filter) < 2:  # Not all sources selected
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            
            if "Local" in source_filter:
                mask |= ~filtered_df["file"].str.startswith("s3://")
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
                
                # Get risk color for styling
                risk_colors = {
                    "Critical": "#ff6b6b",
                    "Medium": "#ffa94d",
                    "Low": "#51cf66"
                }
                risk_color = risk_colors.get(risk, "#94a3b8")
                
                # Use plain text for expander title - just the file path
                file_display = row['file']
                expander_title = file_display

                # Create custom styled expander with colored border and path
                st.markdown(
                    f'<div style="border-left:4px solid {risk_color};padding-left:12px;margin-bottom:8px">'
                    f'<span style="color:{risk_color};font-weight:600">{expander_title}</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
                
                with st.expander("View Details", expanded=(idx == 0)):
                    st.markdown("---")
                    
                    left, right = st.columns([1, 1])
                    with left:
                        st.markdown("**Card Details**")
                        card_str = str(row["card_number"])
                        masked = (
                            f"{card_str[:4]}{'*' * 8}{card_str[-4:]}"
                            if len(card_str) >= 8
                            else card_str
                        )
                        st.markdown(f"Card: `{masked}`")
                        source_lbl = (
                            "S3"
                            if str(row["file"]).startswith("s3://")
                            else ("Cloud" if str(row["file"]).startswith("gdrive://") else "Local")
                        )
                        st.markdown(f"Source: {source_lbl}")
                        if "remediation" in row and row["remediation"]:
                            is_done = "Masked and saved" in str(row["remediation"])
                            st.markdown(
                                f"Status: {'Remediated' if is_done else 'Pending'}"
                            )
                        
                        # Display cardholder data if present
                        if "cardholder_data" in row and row["cardholder_data"]:
                            try:
                                ch_data = json.loads(row["cardholder_data"]) if isinstance(row["cardholder_data"], str) else row["cardholder_data"]
                                if ch_data and ch_data.get("total_count", 0) > 0:
                                    st.markdown("")
                                    st.markdown(
                                        '<div class="cardholder-data-banner">'
                                        '<div class="cardholder-data-title">🚨 Additional Cardholder Data</div>'
                                        f'<div class="cardholder-data-summary">Total: {ch_data.get("total_count", 0)} items</div>'
                                        '</div>',
                                        unsafe_allow_html=True
                                    )

                                    findings = ch_data.get("findings", {})

                                    with st.expander("📋 View All Details", expanded=False):
                                        st.markdown("---")

                                        # CVV Codes
                                        if findings.get("cvv"):
                                            st.markdown(f"**CVV Codes ({len(findings['cvv'])}):**")
                                            cvv_items = [f"`{item['value']}`" for item in findings['cvv']]
                                            st.markdown(", ".join(cvv_items))
                                            st.markdown("")

                                        # Expiry Dates
                                        if findings.get("expiry_date"):
                                            st.markdown(f"**Expiry Dates ({len(findings['expiry_date'])}):**")
                                            expiry_items = [f"`{item['value']}`" for item in findings['expiry_date']]
                                            st.markdown(", ".join(expiry_items))
                                            st.markdown("")

                                        # Cardholder Names
                                        if findings.get("cardholder_name"):
                                            # Filter out false positives
                                            valid_names = [n for n in findings['cardholder_name'] if n['value'].lower() not in ['batch', 'expiry', 'card', 'payment']]
                                            if valid_names:
                                                st.markdown(f"**Cardholder Names ({len(valid_names)}):**")
                                                name_items = [f"`{n['value']}`" for n in valid_names]
                                                st.markdown(", ".join(name_items))
                                                st.markdown("")

                                        # PINs
                                        if findings.get("pin"):
                                            st.markdown(f"**PINs ({len(findings['pin'])}):**")
                                            pin_items = [f"`{'*' * len(item['value'])}`" for item in findings['pin']]
                                            st.markdown(", ".join(pin_items))
                                            st.markdown("")

                                        # Track Data
                                        if findings.get("track_data"):
                                            st.markdown(f"**Track Data ({len(findings['track_data'])}):**")
                                            track_items = [f"`{item['value'][:20]}...`" if len(item['value']) > 20 else f"`{item['value']}`" for item in findings['track_data']]
                                            st.markdown(", ".join(track_items))
                            except Exception as e:
                                pass

                        st.markdown("")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(
                                "🗑️ Delete",
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
                        with col2:
                            if st.button(
                                "✅ Remediate",
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
                        st.markdown("**AI Risk Analysis**")
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

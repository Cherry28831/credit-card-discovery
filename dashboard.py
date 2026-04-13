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
from datetime import datetime

st.set_page_config(
    page_title="PCI DSS Compliance Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* Base */
    [data-testid="stAppViewContainer"] {
        background-color: #0f1117;
        color: #e2e8f0;
    }
    [data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid #1e2535; }

    /* Remove default padding */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Typography */
    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    p, li, span { color: #94a3b8; }

    /* Nav bar */
    .nav-bar {
        display: flex; gap: 4px; background: #161b27;
        border: 1px solid #1e2535; border-radius: 12px;
        padding: 6px; margin-bottom: 24px;
    }
    .nav-btn {
        flex: 1; padding: 10px 16px; border-radius: 8px;
        text-align: center; cursor: pointer; font-weight: 600;
        font-size: 14px; transition: all 0.2s;
        color: #64748b; background: transparent; border: none;
    }
    .nav-btn.active {
        background: #1e40af; color: #fff;
        box-shadow: 0 2px 8px rgba(30,64,175,0.4);
    }

    /* Metric cards */
    .metric-card {
        background: #161b27; border: 1px solid #1e2535; border-radius: 12px;
        padding: 20px 24px; text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 800; line-height: 1.1; }
    .metric-label { font-size: 12px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #64748b; margin-top: 4px; }
    .metric-critical .metric-value { color: #ef4444; }
    .metric-medium .metric-value { color: #f59e0b; }
    .metric-low .metric-value { color: #10b981; }
    .metric-total .metric-value { color: #3b82f6; }
    .metric-remediated .metric-value { color: #8b5cf6; }

    /* Section headers */
    .section-header {
        font-size: 16px; font-weight: 700; color: #f1f5f9;
        margin-bottom: 12px; padding-bottom: 8px;
        border-bottom: 1px solid #1e2535;
    }

    /* Chart container */
    .chart-card {
        background: #161b27; border: 1px solid #1e2535;
        border-radius: 12px; padding: 20px;
    }

    /* Scan panel */
    .scan-panel {
        background: #161b27; border: 1px solid #1e2535;
        border-radius: 16px; padding: 28px 32px;
    }
    .scan-title {
        font-size: 22px; font-weight: 800; color: #f1f5f9;
        margin-bottom: 4px;
    }
    .scan-subtitle { font-size: 14px; color: #64748b; margin-bottom: 24px; }
    .source-option {
        background: #0f1117; border: 1px solid #1e2535;
        border-radius: 10px; padding: 14px 16px;
        cursor: pointer; transition: border-color 0.2s;
    }
    .source-option.selected { border-color: #3b82f6; }

    /* Badges */
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge-medium { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .badge-low { background: rgba(16,185,129,0.15); color: #10b981; }

    /* Log output */
    .log-box {
        background: #0a0e17; border: 1px solid #1e2535; border-radius: 10px;
        padding: 16px; font-family: 'JetBrains Mono', monospace;
        font-size: 13px; color: #94a3b8; max-height: 320px; overflow-y: auto;
        white-space: pre-wrap; line-height: 1.6;
    }
    .log-line-ok { color: #10b981; }
    .log-line-err { color: #ef4444; }
    .log-line-info { color: #3b82f6; }

    /* Progress bar */
    .stProgress > div > div > div > div { background: #3b82f6 !important; }

    /* Buttons */
    .stButton > button {
        background: #1e40af; color: #fff; border: none;
        border-radius: 8px; font-weight: 600; padding: 10px 24px;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #2563eb; }
    .stButton > button[kind="secondary"] {
        background: #161b27; color: #94a3b8; border: 1px solid #1e2535;
    }
    .stButton > button[kind="secondary"]:hover { border-color: #3b82f6; color: #f1f5f9; }

    /* Input fields */
    .stTextInput > div > div > input, .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #0f1117 !important; border: 1px solid #1e2535 !important;
        color: #e2e8f0 !important; border-radius: 8px !important;
    }
    .stCheckbox > label { color: #94a3b8 !important; }

    /* Expander */
    .streamlit-expanderHeader {
        background: #161b27 !important; border: 1px solid #1e2535 !important;
        border-radius: 10px !important; color: #f1f5f9 !important;
    }
    .streamlit-expanderContent {
        background: #0f1117 !important; border: 1px solid #1e2535 !important;
        border-top: none !important; border-radius: 0 0 10px 10px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #1e2535 !important; border-radius: 10px !important; }

    /* Info/warning/error */
    .stAlert { border-radius: 10px !important; }

    /* Divider */
    hr { border-color: #1e2535 !important; }

    /* Page header */
    .page-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #1e2535;
    }
    .logo-text {
        font-size: 26px; font-weight: 900; color: #f1f5f9; letter-spacing: -0.03em;
    }
    .logo-accent { color: #3b82f6; }
    .header-badge {
        background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3);
        color: #60a5fa; padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 700; letter-spacing: 0.05em;
    }

    /* Status dot */
    .status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        margin-right: 6px; vertical-align: middle;
    }
    .dot-ok { background: #10b981; box-shadow: 0 0 6px #10b981; }
    .dot-warn { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
    .dot-err { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_data():
    try:
        conn = sqlite3.connect("outputs/findings.db")
        df = pd.read_sql_query("SELECT * FROM findings", conn)
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
    cls = {"Critical": "badge-critical", "Medium": "badge-medium", "Low": "badge-low"}.get(risk, "badge-medium")
    return f'<span class="badge {cls}">{risk}</span>'


def run_scan_background(cmd, log_key, status_key, done_key):
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=os.getcwd(), bufsize=1
        )
        for line in iter(process.stdout.readline, ""):
            st.session_state[log_key] = st.session_state.get(log_key, "") + line
        process.wait()
        st.session_state[status_key] = "done" if process.returncode == 0 else "error"
    except Exception as e:
        st.session_state[log_key] = st.session_state.get(log_key, "") + f"\nError: {e}"
        st.session_state[status_key] = "error"
    finally:
        st.session_state[done_key] = True


# Page header
st.markdown("""
<div class="page-header">
    <div>
        <div class="logo-text">PCI<span class="logo-accent">Guard</span></div>
        <div style="font-size:13px;color:#475569;margin-top:2px;">Autonomous Credit Card Data Discovery & Compliance System</div>
    </div>
    <div class="header-badge">PCI DSS v4.0</div>
</div>
""", unsafe_allow_html=True)

# --- Navigation ---
TABS = ["Overview", "Run Scan", "AI Analysis", "Executive Report"]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

nav_cols = st.columns(len(TABS))
for i, (col, name) in enumerate(zip(nav_cols, TABS)):
    with col:
        btn_type = "primary" if st.session_state.active_tab == i else "secondary"
        if st.button(name, key=f"nav_{i}", type=btn_type, use_container_width=True):
            st.session_state.active_tab = i
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

df = load_data()

# ── SHARED METRICS ─────────────────────────────────────────────────────────────
if not df.empty:
    total_findings = len(df)
    critical_count = len(df[df["risk_level"] == "Critical"])
    medium_count = len(df[df["risk_level"] == "Medium"])
    low_count = len(df[df["risk_level"] == "Low"])
    remediated_count = (
        len(df[df["remediation"].str.contains("Masked and saved", na=False)])
        if "remediation" in df.columns else 0
    )
    scan_date = df["scan_date"].max() if "scan_date" in df.columns else "N/A"

    mc = st.columns(5)
    cards = [
        ("metric-total",      str(total_findings),    "Total Findings"),
        ("metric-critical",   str(critical_count),    "Critical Risk"),
        ("metric-medium",     str(medium_count),      "Medium Risk"),
        ("metric-low",        str(low_count),         "Low Risk"),
        ("metric-remediated", str(remediated_count),  "Remediated"),
    ]
    for col, (cls, val, lbl) in zip(mc, cards):
        with col:
            st.markdown(f"""
            <div class="metric-card {cls}">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 0 – OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == 0:
    if df.empty:
        st.markdown("""
        <div style="text-align:center;padding:80px 0">
            <div style="font-size:48px;margin-bottom:16px">🔍</div>
            <div style="font-size:20px;font-weight:700;color:#f1f5f9;margin-bottom:8px">No scan results yet</div>
            <div style="color:#64748b">Head to the <b>Run Scan</b> tab to start your first compliance scan</div>
        </div>""", unsafe_allow_html=True)
    else:
        color_map = {"Critical": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
        chart_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", size=12),
            margin=dict(l=8, r=8, t=28, b=8),
        )

        r1c1, r1c2 = st.columns(2)

        with r1c1:
            st.markdown('<div class="section-header">Risk Distribution</div>', unsafe_allow_html=True)
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            fig = px.pie(
                risk_counts, values="Count", names="Risk Level",
                color="Risk Level", color_discrete_map=color_map, hole=0.55,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              textfont=dict(color="#fff", size=12))
            fig.update_layout(**chart_layout, legend=dict(
                orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True)

        with r1c2:
            st.markdown('<div class="section-header">Findings by File Extension</div>', unsafe_allow_html=True)
            df["extension"] = df["file"].str.extract(r"\.([^.]+)$").fillna("none")
            ext_counts = df["extension"].value_counts().head(8).reset_index()
            ext_counts.columns = ["Extension", "Count"]
            fig2 = px.bar(
                ext_counts, x="Extension", y="Count",
                color="Count", color_continuous_scale=[[0, "#1e3a5f"], [1, "#3b82f6"]],
            )
            fig2.update_layout(**chart_layout, showlegend=False,
                               xaxis=dict(gridcolor="#1e2535"),
                               yaxis=dict(gridcolor="#1e2535"))
            st.plotly_chart(fig2, use_container_width=True)

        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.markdown('<div class="section-header">Source Breakdown</div>', unsafe_allow_html=True)
            df["source"] = df["file"].apply(lambda x: "Cloud" if x.startswith("gdrive://") else "Local")
            source_counts = df["source"].value_counts().reset_index()
            source_counts.columns = ["Source", "Count"]
            fig3 = px.bar(
                source_counts, x="Source", y="Count",
                color="Source",
                color_discrete_map={"Local": "#3b82f6", "Cloud": "#f59e0b"},
            )
            fig3.update_layout(**chart_layout, showlegend=False,
                               xaxis=dict(gridcolor="#1e2535"),
                               yaxis=dict(gridcolor="#1e2535"))
            st.plotly_chart(fig3, use_container_width=True)

        with r2c2:
            st.markdown('<div class="section-header">Risk by File Category</div>', unsafe_allow_html=True)

            def categorize(path):
                p = path.lower()
                if "config" in p or p.endswith((".env", ".ini", ".conf")): return "Config"
                if "log" in p: return "Logs"
                if "backup" in p or p.endswith(".sql"): return "Backup"
                if p.endswith((".csv", ".json", ".xml")): return "Data"
                return "Other"

            df["file_cat"] = df["file"].apply(categorize)
            ftr = df.groupby(["file_cat", "risk_level"]).size().reset_index(name="count")
            fig4 = px.bar(
                ftr, x="file_cat", y="count", color="risk_level",
                color_discrete_map=color_map, barmode="stack",
            )
            fig4.update_layout(**chart_layout,
                               xaxis=dict(title="", gridcolor="#1e2535"),
                               yaxis=dict(title="", gridcolor="#1e2535"))
            st.plotly_chart(fig4, use_container_width=True)

        # --- Findings table ---
        st.markdown('<div class="section-header" style="margin-top:12px">Findings Table</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            search_q = st.text_input("Search by file path", placeholder="e.g. /logs/app.log", label_visibility="collapsed")
        with fc2:
            risk_opts = sorted(df["risk_level"].dropna().unique().tolist())
            selected_risks = st.multiselect("Risk filter", risk_opts, default=risk_opts, label_visibility="collapsed")

        filtered = df[df["risk_level"].isin(selected_risks)]
        if search_q:
            filtered = filtered[filtered["file"].str.contains(search_q, case=False, na=False)]

        display = filtered[["file", "card_number", "risk_level", "scan_date"]].copy()
        display["card_number"] = display["card_number"].apply(
            lambda x: f"{str(x)[:4]}{'*' * 8}{str(x)[-4:]}" if len(str(x)) >= 8 else x
        )
        if "remediation" in filtered.columns:
            display["status"] = filtered["remediation"].apply(
                lambda x: "Remediated" if "Masked and saved" in str(x) else "Pending"
            )

        st.dataframe(display, use_container_width=True, hide_index=True,
                     column_config={
                         "file": st.column_config.TextColumn("File Path", width="large"),
                         "card_number": st.column_config.TextColumn("Card (Masked)"),
                         "risk_level": st.column_config.TextColumn("Risk"),
                         "scan_date": st.column_config.TextColumn("Scan Date"),
                     })

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

    st.markdown('<div class="scan-title">Run Compliance Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="scan-subtitle">Configure your scan targets, then launch to detect PCI DSS violations</div>', unsafe_allow_html=True)

    # --- Source selection ---
    st.markdown('<div class="section-header">Scan Sources</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        use_local = st.checkbox("Local File System", value=True)
    with sc2:
        use_cloud = st.checkbox("Google Drive (Cloud)", value=False)
    with sc3:
        use_sample = st.checkbox("Use Sample Files", value=False)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # --- Path input ---
    if use_local and not use_sample:
        st.markdown('<div class="section-header">Local Paths</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="section-header" style="margin-top:12px">Cloud Configuration</div>', unsafe_allow_html=True)
        gdrive_col1, gdrive_col2 = st.columns(2)
        with gdrive_col1:
            creds_file = st.text_input("credentials.json path", value="cloud/credentials.json")
        with gdrive_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if not os.path.exists(creds_file):
                st.warning("credentials.json not found — Google Drive scan will be skipped")

    # --- Advanced options ---
    with st.expander("Advanced Options"):
        ac1, ac2 = st.columns(2)
        with ac1:
            min_confidence = st.slider("Presidio Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        with ac2:
            enable_remediation = st.checkbox("Enable Auto-Remediation (mask critical cards)", value=False)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
            st.markdown(
                '<span class="status-dot dot-warn"></span><span style="color:#f59e0b;font-weight:600">Scan in progress...</span>',
                unsafe_allow_html=True,
            )
        elif st.session_state.scan_status == "done":
            st.markdown(
                '<span class="status-dot dot-ok"></span><span style="color:#10b981;font-weight:600">Scan completed successfully</span>',
                unsafe_allow_html=True,
            )
        elif st.session_state.scan_status == "error":
            st.markdown(
                '<span class="status-dot dot-err"></span><span style="color:#ef4444;font-weight:600">Scan encountered an error</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-dot" style="background:#334155"></span><span style="color:#64748b">Idle — configure options above and click Launch</span>',
                unsafe_allow_html=True,
            )

    if launch:
        target_path = paths[0] if paths else "sample_files"
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
        st.markdown('<div class="section-header" style="margin-top:16px">Scan Output</div>', unsafe_allow_html=True)

        log_lines = st.session_state.scan_log.splitlines()
        colored = []
        for line in log_lines[-80:]:
            if any(k in line for k in ["✓", "complete", "Done", "success", "generated", "saved"]):
                colored.append(f'<span class="log-line-ok">{line}</span>')
            elif any(k in line for k in ["Error", "error", "fail", "Fail", "WARN"]):
                colored.append(f'<span class="log-line-err">{line}</span>')
            elif any(k in line for k in ["[", "Scanning", "Processing", "Classif", "Generat"]):
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
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        pa1, pa2 = st.columns(2)
        with pa1:
            if st.button("Refresh Dashboard", use_container_width=True):
                load_data.clear()
                st.session_state.scan_status = "idle"
                st.session_state.active_tab = 0
                st.rerun()
        with pa2:
            if st.button("Run Another Scan", use_container_width=True, type="secondary"):
                st.session_state.scan_status = "idle"
                st.session_state.scan_log = ""
                st.rerun()

    # --- Multiple paths UI hint ---
    if use_local and not use_sample and (not scan_running):
        if paths and len(paths) > 1:
            st.markdown(f"""
            <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.25);
                        border-radius:10px;padding:14px 16px;margin-top:12px">
                <span style="color:#60a5fa;font-weight:700">Multi-path mode:</span>
                <span style="color:#94a3b8"> {len(paths)} paths queued. Only the first path is passed to the scanner in this version.</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – AI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 2:
    if df.empty:
        st.info("No scan data available. Run a scan first.")
    else:
        st.markdown('<div class="section-header">AI Analysis per Finding</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#64748b;font-size:14px;margin-bottom:16px">LLM-powered contextual analysis for each credit card exposure</div>', unsafe_allow_html=True)

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            risk_opts = sorted(df["risk_level"].dropna().unique().tolist())
            risk_filter = st.multiselect("Risk Level", risk_opts, default=risk_opts)
        with fc2:
            source_filter = st.multiselect("Source", ["Local", "Cloud"], default=["Local", "Cloud"])
        with fc3:
            search_ai = st.text_input("Search file", placeholder="filter by path...")

        filtered_df = df[df["risk_level"].isin(risk_filter)].copy()
        if "Local" not in source_filter:
            filtered_df = filtered_df[filtered_df["file"].str.startswith("gdrive://")]
        if "Cloud" not in source_filter:
            filtered_df = filtered_df[~filtered_df["file"].str.startswith("gdrive://")]
        if search_ai:
            filtered_df = filtered_df[filtered_df["file"].str.contains(search_ai, case=False, na=False)]

        st.markdown(f'<div style="color:#64748b;font-size:13px;margin-bottom:12px">{len(filtered_df)} findings shown</div>', unsafe_allow_html=True)

        for _, row in filtered_df.iterrows():
            risk = row.get("risk_level", "Unknown")
            badge = get_badge(risk)
            label = f"{row['file']}  {badge}"

            with st.expander(row["file"]):
                left, right = st.columns([1, 3])
                with left:
                    card_str = str(row["card_number"])
                    masked = f"{card_str[:4]}{'*' * 8}{card_str[-4:]}" if len(card_str) >= 8 else card_str
                    st.markdown(f"**Card:** `{masked}`")
                    st.markdown(badge, unsafe_allow_html=True)
                    source_lbl = "Cloud" if str(row["file"]).startswith("gdrive://") else "Local"
                    st.markdown(f"**Source:** {source_lbl}")
                    if "remediation" in row and row["remediation"]:
                        is_done = "Masked and saved" in str(row["remediation"])
                        st.markdown(f"**Status:** {'Remediated' if is_done else 'Pending'}")
                with right:
                    analysis = clean_context_analysis(row.get("context_analysis", ""))
                    st.markdown(analysis)
                    if "remediation" in row and "Masked and saved" in str(row.get("remediation", "")):
                        st.success(row["remediation"])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 – EXECUTIVE REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == 3:
    st.markdown('<div class="section-header">Executive Compliance Report</div>', unsafe_allow_html=True)
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

        st.markdown("\n".join(filtered_lines))

        with open("outputs/report.txt", "r", encoding="utf-8") as f:
            raw = f.read()
        st.download_button(
            "Download Full Report",
            data=raw,
            file_name=f"pci_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )
    except Exception:
        st.error("No report found. Run a scan first to generate the executive report.")

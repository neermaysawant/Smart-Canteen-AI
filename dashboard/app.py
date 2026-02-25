import streamlit as st
import os
import pickle
import pandas as pd
import json
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess
import glob
import numpy as np

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CanteenIQ · Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary:   #080c10;
    --bg-panel:     #0d1117;
    --bg-card:      #111820;
    --bg-hover:     #161e28;
    --border:       #1e2d3d;
    --border-bright:#2a3f55;
    --accent-cyan:  #00d4ff;
    --accent-green: #00ff88;
    --accent-amber: #ffb800;
    --accent-red:   #ff4757;
    --accent-purple:#b04eff;
    --text-primary: #e8f0f8;
    --text-secondary:#7a9bb5;
    --text-dim:     #3d5166;
    --mono:         'IBM Plex Mono', monospace;
    --sans:         'IBM Plex Sans', sans-serif;
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: var(--sans) !important;
    color: var(--text-primary) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 2px; }

/* ── Main container ── */
.main .block-container {
    padding: 1rem 1.5rem 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--sans) !important; }

/* ── Header ── */
.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.2rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.dash-logo {
    font-family: var(--mono);
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--accent-cyan);
    letter-spacing: 0.05em;
}
.dash-logo span {
    color: var(--text-secondary);
    font-weight: 400;
}
.dash-tag {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.dash-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--accent-green);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent-green);
    box-shadow: 0 0 8px var(--accent-green);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: var(--bg-card);
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.cyan::before  { background: var(--accent-cyan); }
.kpi-card.green::before { background: var(--accent-green); }
.kpi-card.amber::before { background: var(--accent-amber); }
.kpi-card.purple::before{ background: var(--accent-purple); }
.kpi-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: var(--mono);
    font-size: 2rem;
    font-weight: 600;
    line-height: 1;
    color: var(--text-primary);
}
.kpi-value.cyan   { color: var(--accent-cyan); }
.kpi-value.green  { color: var(--accent-green); }
.kpi-value.amber  { color: var(--accent-amber); }
.kpi-value.purple { color: var(--accent-purple); }
.kpi-sub {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
    font-family: var(--mono);
}
.kpi-change {
    font-family: var(--mono);
    font-size: 0.65rem;
    margin-top: 0.3rem;
}
.kpi-change.pos { color: var(--accent-green); }
.kpi-change.neg { color: var(--accent-red); }

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 1.5rem 0 0.8rem 0;
}
.section-title {
    font-family: var(--mono);
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-secondary);
}
.section-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}
.section-badge {
    font-family: var(--mono);
    font-size: 0.55rem;
    padding: 2px 7px;
    border-radius: 2px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-live {
    background: rgba(0,255,136,0.1);
    color: var(--accent-green);
    border: 1px solid rgba(0,255,136,0.3);
}

/* ── Panel ── */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}

/* ── Prediction Result ── */
.pred-result {
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0.02) 100%);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 6px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
}
.pred-number {
    font-family: var(--mono);
    font-size: 3.5rem;
    font-weight: 600;
    color: var(--accent-cyan);
    line-height: 1;
}
.pred-label {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-top: 0.4rem;
}
.pred-menu-display {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--text-secondary);
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.6rem 0.9rem;
    margin: 0.7rem 0;
    word-break: break-word;
    line-height: 1.6;
}

/* ── Alert / Info boxes ── */
.alert-warn {
    background: rgba(255,184,0,0.07);
    border: 1px solid rgba(255,184,0,0.3);
    border-left: 3px solid var(--accent-amber);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--accent-amber);
    margin: 0.5rem 0;
}
.alert-success {
    background: rgba(0,255,136,0.07);
    border: 1px solid rgba(0,255,136,0.3);
    border-left: 3px solid var(--accent-green);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--accent-green);
    margin: 0.5rem 0;
}
.alert-info {
    background: rgba(0,212,255,0.07);
    border: 1px solid rgba(0,212,255,0.25);
    border-left: 3px solid var(--accent-cyan);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--accent-cyan);
    margin: 0.5rem 0;
}

/* ── Progress bar ── */
.retrain-bar-wrap {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 3px;
    height: 6px;
    margin-top: 0.4rem;
    overflow: hidden;
}
.retrain-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.4s ease;
}

/* ── Model leaderboard table ── */
.lb-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--mono);
    font-size: 0.75rem;
}
.lb-table th {
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    padding: 0.5rem 0.7rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
    font-weight: 500;
}
.lb-table td {
    padding: 0.55rem 0.7rem;
    color: var(--text-secondary);
    border-bottom: 1px solid rgba(30,45,61,0.5);
}
.lb-table tr:hover td { background: var(--bg-hover); }
.lb-table tr.best td { color: var(--text-primary); }
.lb-table td.rank { color: var(--text-dim); }
.lb-table td.model-name { color: var(--text-primary); font-weight: 500; }
.lb-table td.rmse-val { color: var(--accent-cyan); }
.lb-table td.best-rmse { color: var(--accent-green); }
.lb-mini-bar {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.mini-bar-track {
    flex: 1;
    height: 4px;
    background: var(--bg-panel);
    border-radius: 2px;
    overflow: hidden;
}
.mini-bar-fill {
    height: 100%;
    border-radius: 2px;
}

/* ── Selectbox & Inputs ── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
}
.stSelectbox > div > div:hover {
    border-color: var(--border-bright) !important;
}
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
}
label[data-testid="stWidgetLabel"] {
    font-family: var(--mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 4px !important;
    color: var(--text-primary) !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: var(--bg-hover) !important;
    border-color: var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.15) !important;
}
.stButton > button[kind="primary"] {
    background: rgba(0,212,255,0.1) !important;
    border-color: var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
}

/* ── Radio / Nav ── */
.stRadio > div {
    gap: 0.3rem !important;
}
.stRadio > div > label {
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    color: var(--text-secondary) !important;
    padding: 0.4rem 0.8rem !important;
    border-radius: 3px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
.stRadio > div > label:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
}

/* ── Horizontal divider ── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 1rem 0 !important; }

/* ── Plotly container ── */
.js-plotly-plot { border-radius: 4px; }

/* ── Sidebar nav ── */
.nav-item {
    font-family: var(--mono);
    font-size: 0.75rem;
    padding: 0.6rem 0.8rem;
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    letter-spacing: 0.05em;
}

/* ── Metrics strip ── */
.metrics-strip {
    display: flex;
    gap: 1px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.metric-chip {
    flex: 1;
    background: var(--bg-card);
    padding: 0.7rem 0.8rem;
    text-align: center;
}
.metric-chip .val {
    font-family: var(--mono);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}
.metric-chip .lbl {
    font-family: var(--mono);
    font-size: 0.55rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# ─── Paths ──────────────────────────────────────────────────────────────────────
base_dir = os.path.dirname(os.path.dirname(__file__))
models_dir = os.path.join(base_dir, 'models')
db_path = os.path.join(base_dir, 'database', 'canteen.db')

# ─── Load Model ─────────────────────────────────────────────────────────────────
model_files = sorted(glob.glob(os.path.join(models_dir, "model_v*.pkl")))
latest_model = model_files[-1]
metadata_path = latest_model.replace(".pkl", "_metadata.json")

with open(latest_model, "rb") as f:
    model = pickle.load(f)
with open(metadata_path, "r") as f:
    metadata = json.load(f)

# ─── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM canteen_data", conn)
    conn.close()
    return df

# ─── Plotly theme ───────────────────────────────────────────────────────────────
PLOT_BG   = "#0d1117"
PLOT_PAPER = "#0d1117"
GRID_CLR  = "#1e2d3d"
TICK_CLR  = "#3d5166"
FONT_CLR  = "#7a9bb5"
CYAN      = "#00d4ff"
GREEN     = "#00ff88"
AMBER     = "#ffb800"
RED       = "#ff4757"
PURPLE    = "#b04eff"

PALETTE = [CYAN, GREEN, AMBER, PURPLE, RED,
           "#ff6b35", "#40e0d0", "#e040fb", "#69f0ae", "#ffcc02"]

def apply_theme(fig, height=320):
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_PAPER,
        plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Mono", color=FONT_CLR, size=11),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID_CLR,
            font=dict(size=10)
        ),
        xaxis=dict(
            gridcolor=GRID_CLR, zerolinecolor=GRID_CLR,
            tickfont=dict(color=TICK_CLR, size=10),
            linecolor=GRID_CLR
        ),
        yaxis=dict(
            gridcolor=GRID_CLR, zerolinecolor=GRID_CLR,
            tickfont=dict(color=TICK_CLR, size=10),
            linecolor=GRID_CLR
        )
    )
    return fig

# ─── Menu Data ──────────────────────────────────────────────────────────────────
days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
breakfast_items = ["Idli","Medu Vada","Poha","Upma","Masala Dosa","Plain Dosa",
                   "Aloo Paratha","Paneer Paratha","Vegetable Sandwich","Pav Bhaji",
                   "Sabudana Khichdi","Sheera","Uttapam"]
dry_veg    = ["Bhindi Fry","Aloo Gobi","Beans Poriyal","Cabbage Sabzi","Aloo Methi",
              "Tinda Masala","Gajar Matar","Baingan Bharta Dry","Karela Fry"]
gravy_veg  = ["Mixed Veg Curry","Chana Masala","Veg Kofta","Malai Kofta","Rajma Masala",
              "Kadhi Pakoda","Aloo Dum","Mushroom Masala","Navratan Korma","Vegetable Kurma"]
rice_items = ["Jeera Rice","Plain Rice","Veg Pulao","Peas Pulao","Lemon Rice","Curd Rice","Tomato Rice"]
dal_items  = ["Dal Tadka","Sambar","Dal Fry","Moong Dal","Dal Makhani","Gujarati Dal"]
indian_bread = ["Roti","Chapati","Naan","Tandoori Roti","Phulka"]
beverages  = ["Curd","Tang","Lemonade","Lassi","Buttermilk","Jaljeera","Rose Milk"]
paneer_gravies  = ["Paneer Butter Masala","Shahi Paneer","Kadai Paneer","Palak Paneer",
                   "Matar Paneer","Paneer Lababdar","Paneer Do Pyaza","Paneer Tikka Masala"]
chicken_gravies = ["Chicken Curry","Butter Chicken","Chicken Masala","Chicken Do Pyaza",
                   "Chicken Kolhapuri","Chicken Handi","Chicken Kadai"]
egg_gravies    = ["Egg Curry","Anda Masala","Egg Bhurji Gravy","Egg Korma","Masala Egg Curry"]
sweets = ["Gulab Jamun","Kheer","Halwa","Rasmalai","Jalebi","Sheera","Rice Kheer","Moong Dal Halwa"]

# ─── Session State ──────────────────────────────────────────────────────────────
for key in ["prediction_made","predicted_val","selected_menu","selected_day",
            "selected_cat","selected_exam"]:
    if key not in st.session_state:
        st.session_state[key] = False if "made" in key else None

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #1e2d3d; margin-bottom: 1rem;'>
        <div style='font-family: IBM Plex Mono; font-size: 1.1rem; font-weight: 600; color: #00d4ff;'>
            CANTEEN<span style='color:#3d5166;'>IQ</span>
        </div>
        <div style='font-family: IBM Plex Mono; font-size: 0.58rem; letter-spacing: 0.2em;
                    text-transform: uppercase; color: #3d5166; margin-top: 2px;'>
            DEMAND INTELLIGENCE v2.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["⬡  Operations Hub", "⬡  Model Intelligence"],
        label_visibility="collapsed"
    )

    # Model info pill in sidebar
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#111820; border:1px solid #1e2d3d; border-radius:5px; padding:0.9rem;'>
        <div style='font-family:IBM Plex Mono; font-size:0.55rem; letter-spacing:0.15em;
                    text-transform:uppercase; color:#3d5166; margin-bottom:0.6rem;'>Active Model</div>
        <div style='font-family:IBM Plex Mono; font-size:0.85rem; font-weight:600; color:#e8f0f8;'>
            {metadata['model_name']}
        </div>
        <div style='font-family:IBM Plex Mono; font-size:0.7rem; color:#00d4ff; margin-top:3px;'>
            RMSE · {metadata['rmse']:.2f}
        </div>
        <div style='font-family:IBM Plex Mono; font-size:0.65rem; color:#3d5166; margin-top:3px;'>
            Version {metadata['version']} · {metadata.get('trained_at','—')[:10]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # System status
    df_sidebar = load_data()
    total = len(df_sidebar)
    updates_mod = total % 42
    pct = updates_mod / 42
    st.markdown(f"""
    <div style='background:#111820; border:1px solid #1e2d3d; border-radius:5px; padding:0.9rem;'>
        <div style='font-family:IBM Plex Mono; font-size:0.55rem; letter-spacing:0.15em;
                    text-transform:uppercase; color:#3d5166; margin-bottom:0.6rem;'>Retrain Status</div>
        <div style='font-family:IBM Plex Mono; font-size:0.7rem; color:#7a9bb5;'>
            {updates_mod}/42 updates
        </div>
        <div style='background:#0d1117; border-radius:2px; height:5px; margin-top:6px; overflow:hidden;'>
            <div style='height:100%; width:{pct*100:.0f}%; background:{"#ff4757" if pct > 0.85 else "#ffb800" if pct > 0.5 else "#00ff88"};
                        border-radius:2px;'></div>
        </div>
        <div style='font-family:IBM Plex Mono; font-size:0.6rem; color:#3d5166; margin-top:4px;'>
            {"⚠ RETRAIN REQUIRED" if updates_mod == 0 and total > 0 else f"{42 - updates_mod} updates until retrain"}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <div>
        <div class="dash-logo">CANTEEN<span>IQ</span> · Intelligence Platform</div>
        <div class="dash-tag">University Canteen · Demand Forecasting System</div>
    </div>
    <div class="dash-status">
        <div class="status-dot"></div>
        LIVE · MODEL ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: OPERATIONS HUB
# ══════════════════════════════════════════════════════════════════════════════
if "Operations" in page:

    df = load_data()

    # ─── KPI Row ──────────────────────────────────────────────────────────────
    avg_d  = int(df["plates_consumed"].mean())
    peak_d = int(df["plates_consumed"].max())
    total_r = len(df)
    exam_avg = int(df[df["is_exam_period"]==1]["plates_consumed"].mean()) if len(df[df["is_exam_period"]==1]) > 0 else 0
    normal_avg = int(df[df["is_exam_period"]==0]["plates_consumed"].mean()) if len(df[df["is_exam_period"]==0]) > 0 else 0
    diff_pct = round((normal_avg - exam_avg) / normal_avg * 100, 1) if normal_avg > 0 else 0

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card cyan">
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value cyan">{total_r:,}</div>
            <div class="kpi-sub">in database</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-label">Avg Daily Demand</div>
            <div class="kpi-value green">{avg_d}</div>
            <div class="kpi-sub">plates / service</div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-label">Peak Demand</div>
            <div class="kpi-value amber">{peak_d}</div>
            <div class="kpi-sub">all-time high</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-label">Exam Impact</div>
            <div class="kpi-value purple">-{diff_pct}%</div>
            <div class="kpi-sub">{normal_avg} → {exam_avg} plates</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Two-column layout: Prediction + Analytics ────────────────────────────
    left_col, right_col = st.columns([1, 1.6], gap="medium")

    with left_col:
        st.markdown("""
        <div class="section-header">
            <div class="section-title">Demand Forecast</div>
            <div class="section-line"></div>
            <div class="section-badge badge-live">PREDICT</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Configure Service Parameters</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            day = st.selectbox("Day of Week", days, key="day_sel")
        with c2:
            category = st.selectbox("Meal Category", ["Breakfast","Lunch","Dinner"], key="cat_sel")

        exam_choice = st.selectbox("Exam Period", ["No","Yes"], key="exam_sel")
        exam_period = 1 if exam_choice == "Yes" else 0

        if category == "Breakfast":
            menu_item = st.selectbox("Breakfast Item", breakfast_items)

        elif category == "Lunch":
            c1, c2 = st.columns(2)
            with c1:
                gravy = st.selectbox("Gravy Veg", gravy_veg)
                dry   = st.selectbox("Dry Veg", dry_veg)
                rice  = st.selectbox("Rice", rice_items)
            with c2:
                dal      = st.selectbox("Dal", dal_items)
                bread    = st.selectbox("Bread", indian_bread)
                beverage = st.selectbox("Beverage", beverages)
            menu_item = f"{gravy} + {dry} + {rice} + {dal} + {bread} + {beverage}"

        elif category == "Dinner":
            if day in ["Monday","Tuesday","Thursday","Saturday"]:
                gravy = st.selectbox("Veg Gravy", gravy_veg)
                menu_item = gravy
            elif day in ["Wednesday","Sunday"]:
                c1, c2 = st.columns(2)
                with c1:
                    chicken = st.selectbox("Chicken Gravy", chicken_gravies)
                with c2:
                    paneer  = st.selectbox("Paneer Gravy", paneer_gravies)
                menu_item = f"{chicken} + {paneer}"
            elif day == "Friday":
                c1, c2 = st.columns(2)
                with c1:
                    egg    = st.selectbox("Egg Gravy", egg_gravies)
                with c2:
                    paneer = st.selectbox("Paneer Gravy", paneer_gravies)
                menu_item = f"{egg} + {paneer}"

            c1, c2 = st.columns(2)
            with c1:
                rice  = st.selectbox("Rice", rice_items)
                dal   = st.selectbox("Dal", dal_items)
            with c2:
                bread = st.selectbox("Bread", indian_bread)
                sweet = st.selectbox("Sweet Dish", sweets)
            menu_item += f" + {rice} + {dal} + {bread} + {sweet}"

        st.markdown('</div>', unsafe_allow_html=True)

        # Predict button
        if st.button("⬡  RUN FORECAST", use_container_width=True):
            input_df = pd.DataFrame([{
                "day_of_week": day, "category": category,
                "menu_item": menu_item, "is_exam_period": exam_period
            }])
            pred = model.predict(input_df)
            st.session_state.prediction_made = True
            st.session_state.predicted_val   = int(pred[0])
            st.session_state.selected_menu   = menu_item
            st.session_state.selected_day    = day
            st.session_state.selected_cat    = category
            st.session_state.selected_exam   = exam_period

        # Prediction result
        if st.session_state.prediction_made and st.session_state.predicted_val:
            pv = st.session_state.predicted_val
            cat_avg = int(df[df["category"] == st.session_state.selected_cat]["plates_consumed"].mean())
            delta_pct = round((pv - cat_avg) / cat_avg * 100, 1)
            delta_color = GREEN if delta_pct >= 0 else RED
            delta_sign  = "+" if delta_pct >= 0 else ""

            st.markdown(f"""
            <div class="pred-result">
                <div class="pred-number">{pv}</div>
                <div class="pred-label">Predicted Plates · {st.session_state.selected_cat}</div>
                <div style='font-family:IBM Plex Mono; font-size:0.7rem;
                            color:{delta_color}; margin-top:0.4rem;'>
                    {delta_sign}{delta_pct}% vs category avg ({cat_avg})
                </div>
            </div>
            <div class="pred-menu-display">
                {st.session_state.selected_menu}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="section-header" style="margin-top:1rem;">
                <div class="section-title">Log Actual Consumption</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            actual = st.number_input("Actual Plates Served", min_value=0, key="actual_input")

            if st.button("⬡  COMMIT TO DATABASE", use_container_width=True):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO canteen_data(day_of_week,category,menu_item,is_exam_period,plates_consumed)
                    VALUES (?,?,?,?,?)
                """, (st.session_state.selected_day, st.session_state.selected_cat,
                      st.session_state.selected_menu, st.session_state.selected_exam, actual))
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM canteen_data")
                total_rows = cursor.fetchone()[0]
                conn.close()
                load_data.clear()

                accuracy = round((1 - abs(pv - actual) / max(actual, 1)) * 100, 1) if actual > 0 else 0
                updates_mod = total_rows % 42

                st.markdown(f"""
                <div class="alert-success">
                    ✓ Record committed · Forecast accuracy {accuracy}% · {total_rows:,} total records
                </div>
                """, unsafe_allow_html=True)

                if updates_mod == 0:
                    st.markdown("""
                    <div class="alert-warn">⚠ Threshold reached · Navigate to Model Intelligence to retrain</div>
                    """, unsafe_allow_html=True)
                else:
                    remaining = 42 - updates_mod
                    pct_fill = updates_mod / 42
                    bar_color = "#ff4757" if pct_fill > 0.85 else "#ffb800" if pct_fill > 0.5 else "#00ff88"
                    st.markdown(f"""
                    <div class="alert-info">
                        {remaining} updates until next retrain cycle
                        <div class="retrain-bar-wrap">
                            <div class="retrain-bar-fill"
                                 style="width:{pct_fill*100:.0f}%; background:{bar_color};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ─── Right column: Analytics ──────────────────────────────────────────────
    with right_col:
        st.markdown("""
        <div class="section-header">
            <div class="section-title">Live Analytics</div>
            <div class="section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        # ── ROW 1: Radial Meal Clock + Stacked Category Ribbon ────────────────
        ra1, ra2 = st.columns([1, 1.4])

        with ra1:
            # POLAR/RADIAL chart — demand by day as a clock face
            week_data = df.groupby("day_of_week")["plates_consumed"].mean().reindex(day_order).fillna(0)
            theta_vals = [d[:3] for d in day_order]

            fig = go.Figure()
            # Filled area
            fig.add_trace(go.Scatterpolar(
                r=list(week_data.values) + [week_data.values[0]],
                theta=theta_vals + [theta_vals[0]],
                fill="toself",
                fillcolor="rgba(0,212,255,0.10)",
                line=dict(color=CYAN, width=2.5),
                mode="lines+markers+text",
                marker=dict(color=CYAN, size=9, line=dict(color=PLOT_BG, width=2)),
                text=[f"{v:.0f}" for v in week_data.values] + [""],
                textposition="top center",
                textfont=dict(color=CYAN, size=9),
                showlegend=False
            ))
            # Exam overlay — exam-period avg per day
            exam_week = df[df["is_exam_period"]==1].groupby("day_of_week")["plates_consumed"].mean().reindex(day_order).fillna(0)
            fig.add_trace(go.Scatterpolar(
                r=list(exam_week.values) + [exam_week.values[0]],
                theta=theta_vals + [theta_vals[0]],
                fill="toself",
                fillcolor="rgba(255,71,87,0.07)",
                line=dict(color=RED, width=1.5, dash="dot"),
                mode="lines",
                showlegend=False
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(
                        visible=True, gridcolor=GRID_CLR,
                        tickfont=dict(color=TICK_CLR, size=8),
                        range=[0, week_data.max() * 1.25]
                    ),
                    angularaxis=dict(
                        gridcolor=GRID_CLR,
                        tickfont=dict(color=FONT_CLR, size=10),
                        direction="clockwise"
                    )
                ),
                title=dict(text="⬡  Weekly Demand Radar · Normal vs Exam", font=dict(color=FONT_CLR, size=11)),
                paper_bgcolor=PLOT_PAPER,
                plot_bgcolor=PLOT_BG,
                font=dict(family="IBM Plex Mono", color=FONT_CLR),
                margin=dict(l=20, r=20, t=40, b=20),
                height=320,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ra2:
            # STACKED AREA — category demand across days (normalised)
            cat_day = df.groupby(["day_of_week","category"])["plates_consumed"].mean().unstack(fill_value=0)
            cat_day = cat_day.reindex(day_order)
            categories  = cat_day.columns.tolist()
            cat_colors  = [CYAN, AMBER, PURPLE]
            short_days  = [d[:3] for d in day_order]

            fig = go.Figure()
            for i, cat in enumerate(categories):
                vals = cat_day[cat].values
                fig.add_trace(go.Scatter(
                    x=short_days,
                    y=vals,
                    name=cat,
                    stackgroup="one",
                    fill="tonexty",
                    line=dict(color=cat_colors[i % len(cat_colors)], width=1.5),
                    fillcolor=cat_colors[i % len(cat_colors)].replace("#","rgba(").replace("ff","ff,0.25)") if False
                             else f"rgba({int(cat_colors[i%len(cat_colors)][1:3],16)},"
                                  f"{int(cat_colors[i%len(cat_colors)][3:5],16)},"
                                  f"{int(cat_colors[i%len(cat_colors)][5:7],16)},0.20)",
                    mode="lines",
                    hovertemplate=f"<b>{cat}</b><br>%{{x}}: %{{y:.0f}} plates<extra></extra>"
                ))
            fig.update_layout(
                title=dict(text="⬡  Stacked Demand · Category × Day", font=dict(color=FONT_CLR, size=11)),
                legend=dict(
                    bgcolor="rgba(0,0,0,0)", bordercolor=GRID_CLR,
                    font=dict(size=9, color=FONT_CLR),
                    orientation="h", x=0, y=-0.15
                )
            )
            apply_theme(fig, 320)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── ROW 2: Bullet/Gauge + Violin + Sankey ─────────────────────────────
        rb1, rb2, rb3 = st.columns([1, 1, 1])

        with rb1:
            # BULLET GAUGE — utilisation % per meal vs peak
            cat_avgs = df.groupby("category")["plates_consumed"].mean()
            peak_val = df["plates_consumed"].max()
            cats_list    = ["Breakfast", "Lunch", "Dinner"]
            gauge_colors = [CYAN, GREEN, AMBER]

            fig = go.Figure()
            for i, (cat, col) in enumerate(zip(cats_list, gauge_colors)):
                avg_val = cat_avgs.get(cat, 0)
                pct = avg_val / peak_val
                y_pos = i * 0.33 + 0.05

                # background track
                fig.add_shape(type="rect",
                    x0=0, x1=1, y0=y_pos, y1=y_pos+0.18,
                    fillcolor="#1e2d3d", line=dict(color="rgba(0,0,0,0)"),
                    layer="below"
                )
                # filled bar
                fig.add_shape(type="rect",
                    x0=0, x1=pct, y0=y_pos, y1=y_pos+0.18,
                    fillcolor=col, opacity=0.85, line=dict(color="rgba(0,0,0,0)")
                )
                # label
                fig.add_annotation(
                    x=0.02, y=y_pos+0.09,
                    text=f"<b>{cat}</b>  {avg_val:.0f} / {peak_val}",
                    showarrow=False,
                    font=dict(color="white", size=10, family="IBM Plex Mono"),
                    xanchor="left"
                )
                fig.add_annotation(
                    x=min(pct + 0.02, 0.98), y=y_pos+0.09,
                    text=f"{pct*100:.0f}%",
                    showarrow=False,
                    font=dict(color=col, size=10, family="IBM Plex Mono"),
                    xanchor="left"
                )

            fig.update_layout(
                title=dict(text="⬡  Utilisation vs Peak Capacity", font=dict(color=FONT_CLR, size=11)),
                xaxis=dict(visible=False, range=[0,1.15]),
                yaxis=dict(visible=False, range=[0,1.1]),
                paper_bgcolor=PLOT_PAPER,
                plot_bgcolor=PLOT_BG,
                font=dict(family="IBM Plex Mono"),
                margin=dict(l=10, r=10, t=40, b=10),
                height=280
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with rb2:
            # VIOLIN — demand spread per category
            fig = go.Figure()
            vcolors = [CYAN, GREEN, AMBER]
            for cat, col in zip(["Breakfast","Lunch","Dinner"], vcolors):
                sub = df[df["category"]==cat]["plates_consumed"]
                fig.add_trace(go.Violin(
                    y=sub,
                    name=cat,
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.18)",
                    line_color=col,
                    points="outliers",
                    marker=dict(color=col, size=4, opacity=0.6),
                    box=dict(fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.3)", line=dict(color=col)),
                    meanline=dict(color="white", width=1.5)
                ))
            fig.update_layout(
                title=dict(text="⬡  Demand Spread · Violin Distribution", font=dict(color=FONT_CLR, size=11)),
                violingap=0.15,
                violinmode="overlay",
                showlegend=False
            )
            apply_theme(fig, 280)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with rb3:
            # WATERFALL — cumulative demand build across week
            week_vals = df.groupby("day_of_week")["plates_consumed"].sum().reindex(day_order).fillna(0)
            short_days = [d[:3] for d in day_order]
            changes = list(week_vals.values)
            wf_colors = [GREEN if v >= week_vals.mean() else AMBER for v in changes]

            fig = go.Figure(go.Waterfall(
                name="Weekly",
                orientation="v",
                measure=["relative"] * 7,
                x=short_days,
                y=changes,
                text=[f"{v:.0f}" for v in changes],
                textposition="outside",
                textfont=dict(size=9, color=FONT_CLR),
                connector=dict(line=dict(color=GRID_CLR, width=1, dash="dot")),
                increasing=dict(marker=dict(color=GREEN)),
                decreasing=dict(marker=dict(color=RED)),
                totals=dict(marker=dict(color=CYAN)),
            ))
            fig.update_layout(
                title=dict(text="⬡  Weekly Volume Waterfall", font=dict(color=FONT_CLR, size=11)),
                showlegend=False
            )
            apply_theme(fig, 280)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── ROW 3: Sankey Flow + Treemap ──────────────────────────────────────
        rc1, rc2 = st.columns([1.1, 1])

        with rc1:
            # SANKEY — flow: Day → Category → High/Low Demand
            day_cat = df.groupby(["day_of_week","category"])["plates_consumed"].mean().reset_index()
            threshold = df["plates_consumed"].mean()

            s_labels = day_order + ["Breakfast","Lunch","Dinner","High Demand","Low Demand"]
            label_idx = {l: i for i, l in enumerate(s_labels)}

            sources, targets, values, link_colors = [], [], [], []
            # Day → Category
            for _, r in day_cat.iterrows():
                if r["day_of_week"] in label_idx and r["category"] in label_idx:
                    sources.append(label_idx[r["day_of_week"]])
                    targets.append(label_idx[r["category"]])
                    values.append(r["plates_consumed"])
                    link_colors.append("rgba(0,212,255,0.12)")
            # Category → High/Low
            for cat in ["Breakfast","Lunch","Dinner"]:
                sub = df[df["category"]==cat]
                hi = sub[sub["plates_consumed"] >= threshold]["plates_consumed"].sum()
                lo = sub[sub["plates_consumed"] <  threshold]["plates_consumed"].sum()
                if hi > 0:
                    sources.append(label_idx[cat]); targets.append(label_idx["High Demand"])
                    values.append(hi); link_colors.append("rgba(0,255,136,0.15)")
                if lo > 0:
                    sources.append(label_idx[cat]); targets.append(label_idx["Low Demand"])
                    values.append(lo); link_colors.append("rgba(255,71,87,0.12)")

            node_colors = (
                [f"rgba(0,212,255,0.7)"] * 7 +
                [f"rgba(0,212,255,0.5)", f"rgba(255,184,0,0.5)", f"rgba(176,78,255,0.5)"] +
                [f"rgba(0,255,136,0.7)", f"rgba(255,71,87,0.7)"]
            )
            fig = go.Figure(go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=12, thickness=14,
                    line=dict(color=GRID_CLR, width=0.5),
                    label=s_labels,
                    color=node_colors,
                    hovertemplate="%{label}: %{value:.0f}<extra></extra>"
                ),
                link=dict(
                    source=sources, target=targets, value=values,
                    color=link_colors,
                    hovertemplate="Flow: %{value:.0f} plates<extra></extra>"
                )
            ))
            fig.update_layout(
                title=dict(text="⬡  Demand Flow · Day → Category → Volume Tier", font=dict(color=FONT_CLR, size=11)),
                font=dict(family="IBM Plex Mono", color=FONT_CLR, size=9),
                paper_bgcolor=PLOT_PAPER,
                margin=dict(l=10, r=10, t=40, b=10),
                height=330
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with rc2:
            # TREEMAP — menu item demand landscape
            top_menu = df.groupby(["category","menu_item"])["plates_consumed"].mean().reset_index()
            top_menu = top_menu.sort_values("plates_consumed", ascending=False)
            # keep top 20 menu items for readability
            top_items = top_menu.nlargest(20, "plates_consumed")

            fig = go.Figure(go.Treemap(
                labels=top_items["menu_item"].tolist() + top_items["category"].unique().tolist() + ["ALL"],
                parents=top_items["category"].tolist() + ["ALL"] * len(top_items["category"].unique()) + [""],
                values=top_items["plates_consumed"].tolist() + [0]*len(top_items["category"].unique()) + [0],
                branchvalues="remainder",
                marker=dict(
                    colors=top_items["plates_consumed"].tolist() + [0]*len(top_items["category"].unique()) + [0],
                    colorscale=[[0,"#111820"],[0.4, "#1e4d6b"],[0.7, CYAN],[1, GREEN]],
                    showscale=False,
                    line=dict(color=PLOT_BG, width=2)
                ),
                textfont=dict(family="IBM Plex Mono", size=9, color="white"),
                hovertemplate="<b>%{label}</b><br>Avg demand: %{value:.0f}<extra></extra>",
                tiling=dict(packing="squarify"),
                pathbar=dict(visible=False)
            ))
            fig.update_layout(
                title=dict(text="⬡  Menu Demand Landscape · Treemap", font=dict(color=FONT_CLR, size=11)),
                paper_bgcolor=PLOT_PAPER,
                font=dict(family="IBM Plex Mono", color=FONT_CLR),
                margin=dict(l=5, r=5, t=40, b=5),
                height=330
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── ROW 4: Dot-strip exam scatter + Rolling avg sparkline ─────────────
        rd1, rd2 = st.columns(2)

        with rd1:
            # STRIP PLOT — individual plate counts scattered by day, colored by exam
            jitter = np.random.uniform(-0.2, 0.2, len(df))
            day_num_map = {d: i for i, d in enumerate(day_order)}
            df_plot = df.copy()
            df_plot["day_num"] = df_plot["day_of_week"].map(day_num_map)
            df_plot["jittered"] = df_plot["day_num"] + jitter

            fig = go.Figure()
            for exam_val, col, label in [(0, CYAN, "Normal"), (1, RED, "Exam Period")]:
                sub = df_plot[df_plot["is_exam_period"] == exam_val]
                fig.add_trace(go.Scatter(
                    x=sub["jittered"],
                    y=sub["plates_consumed"],
                    mode="markers",
                    name=label,
                    marker=dict(
                        color=col, size=5, opacity=0.55,
                        line=dict(color="rgba(0,0,0,0)", width=0)
                    ),
                    hovertemplate=f"<b>{label}</b><br>%{{y:.0f}} plates<extra></extra>"
                ))
            # overlay mean line per day
            day_means = df.groupby("day_of_week")["plates_consumed"].mean().reindex(day_order)
            fig.add_trace(go.Scatter(
                x=list(range(7)),
                y=day_means.values,
                mode="lines+markers",
                name="Daily Mean",
                line=dict(color=AMBER, width=2.5),
                marker=dict(color=AMBER, size=8, symbol="diamond",
                            line=dict(color=PLOT_BG, width=2)),
                showlegend=True
            ))
            fig.update_layout(
                title=dict(text="⬡  Individual Records · Exam vs Normal Strip", font=dict(color=FONT_CLR, size=11)),
                xaxis=dict(
                    tickvals=list(range(7)),
                    ticktext=[d[:3] for d in day_order],
                    gridcolor=GRID_CLR
                ),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="h", x=0, y=-0.18)
            )
            apply_theme(fig, 290)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with rd2:
            # MULTI-LINE SPARKLINE — rolling 10-record avg per category
            fig = go.Figure()
            cat_colors_map = {"Breakfast": CYAN, "Lunch": GREEN, "Dinner": AMBER}
            for cat, col in cat_colors_map.items():
                sub = df[df["category"]==cat]["plates_consumed"].reset_index(drop=True)
                if len(sub) > 5:
                    rolled = sub.rolling(8, min_periods=1).mean()
                    fig.add_trace(go.Scatter(
                        y=rolled,
                        x=list(range(len(rolled))),
                        name=cat,
                        mode="lines",
                        line=dict(color=col, width=2),
                        fill="tozeroy",
                        fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.04)",
                        hovertemplate=f"<b>{cat}</b> record %{{x}}: %{{y:.0f}}<extra></extra>"
                    ))
                    # annotate last value
                    fig.add_annotation(
                        x=len(rolled)-1, y=float(rolled.iloc[-1]),
                        text=f"{rolled.iloc[-1]:.0f}",
                        showarrow=False,
                        font=dict(color=col, size=9, family="IBM Plex Mono"),
                        xanchor="left", xshift=4
                    )
            fig.update_layout(
                title=dict(text="⬡  Rolling Avg · Category Trend Over Records", font=dict(color=FONT_CLR, size=11)),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="h", x=0, y=-0.18)
            )
            apply_theme(fig, 290)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: MODEL INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif "Model" in page:

    model_perf = metadata.get("all_models_performance", {})

    if not model_perf:
        st.markdown("""
        <div class="alert-warn">No model comparison data available. Run full training to generate leaderboard.</div>
        """, unsafe_allow_html=True)
    else:
        perf_df = pd.DataFrame(list(model_perf.items()), columns=["Model","RMSE"])
        perf_df = perf_df.sort_values("RMSE").reset_index(drop=True)
        best_rmse = perf_df["RMSE"].min()
        worst_rmse = perf_df["RMSE"].max()
        perf_df["Rank"] = range(1, len(perf_df)+1)
        perf_df["Gap"] = perf_df["RMSE"] - best_rmse

        # Use 95th-percentile cap so outliers (e.g. GaussianProcess) don't
        # compress the entire competitive range into a flat 99-100 band.
        rmse_cap = perf_df["RMSE"].quantile(0.90)
        score_worst = min(worst_rmse, rmse_cap)
        score_range = score_worst - best_rmse if score_worst != best_rmse else 1
        perf_df["Score"] = ((score_worst - perf_df["RMSE"]).clip(lower=0) / score_range * 100).round(1).clip(0, 100)

        # KPI strip
        st.markdown(f"""
        <div class="section-header">
            <div class="section-title">Model Training Summary</div>
            <div class="section-line"></div>
        </div>
        <div class="metrics-strip">
            <div class="metric-chip">
                <div class="val" style="color:{CYAN}">{len(perf_df)}</div>
                <div class="lbl">Models Evaluated</div>
            </div>
            <div class="metric-chip">
                <div class="val" style="color:{GREEN}">{best_rmse:.2f}</div>
                <div class="lbl">Best RMSE</div>
            </div>
            <div class="metric-chip">
                <div class="val" style="color:{AMBER}">{perf_df['RMSE'].median():.2f}</div>
                <div class="lbl">Median RMSE</div>
            </div>
            <div class="metric-chip">
                <div class="val" style="color:{PURPLE}">{metadata['model_name']}</div>
                <div class="lbl">Champion Model</div>
            </div>
            <div class="metric-chip">
                <div class="val" style="color:{CYAN}">v{metadata['version']}</div>
                <div class="lbl">Model Version</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── Charts row 1 ─────────────────────────────────────────────────────
        ch1, ch2 = st.columns([1.4, 1])

        with ch1:
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Performance Leaderboard</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            # Color bars: best = green, top5 = cyan, rest = dim
            bar_colors = []
            for i, row in perf_df.iterrows():
                if row["Rank"] == 1:
                    bar_colors.append(GREEN)
                elif row["Rank"] <= 5:
                    bar_colors.append(CYAN)
                else:
                    bar_colors.append("#1e2d3d")

            fig = go.Figure(go.Bar(
                x=perf_df["Model"],
                y=perf_df["RMSE"],
                marker=dict(color=bar_colors, line=dict(color=PLOT_BG, width=0.5)),
                text=[f"{v:.2f}" for v in perf_df["RMSE"]],
                textposition="outside",
                textfont=dict(color=FONT_CLR, size=9)
            ))
            # Best model annotation
            best_model_name = perf_df.iloc[0]["Model"]
            fig.add_annotation(
                x=best_model_name, y=best_rmse,
                text=f"★ BEST",
                showarrow=True, arrowhead=2, arrowcolor=GREEN,
                font=dict(color=GREEN, size=10),
                ax=0, ay=-30
            )
            fig.update_layout(
                title=dict(text="All Models · RMSE Comparison (Lower = Better)",
                           font=dict(color=FONT_CLR, size=11)),
                xaxis=dict(tickangle=-35, tickfont=dict(size=9)),
            )
            apply_theme(fig, 340)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch2:
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Score Distribution</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            fig = go.Figure(go.Histogram(
                x=perf_df["RMSE"],
                nbinsx=12,
                marker=dict(color=CYAN, opacity=0.7, line=dict(color=PLOT_BG, width=0.8))
            ))
            fig.add_vline(x=best_rmse, line_dash="dash", line_color=GREEN, line_width=1.5,
                          annotation_text=f"Best {best_rmse:.2f}",
                          annotation_font_color=GREEN, annotation_font_size=9)
            fig.add_vline(x=perf_df["RMSE"].median(), line_dash="dot", line_color=AMBER, line_width=1.5,
                          annotation_text=f"Med",
                          annotation_font_color=AMBER, annotation_font_size=9)
            fig.update_layout(title=dict(text="RMSE Distribution", font=dict(color=FONT_CLR, size=11)))
            apply_theme(fig, 340)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ─── Charts row 2 ─────────────────────────────────────────────────────
        ch3, ch4 = st.columns([1, 1])

        with ch3:
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Gap From Champion</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            top10_gap = perf_df.head(12)
            gap_colors = [GREEN if i == 0 else CYAN if i < 5 else AMBER if i < 8 else RED
                          for i in range(len(top10_gap))]

            fig = go.Figure(go.Bar(
                x=top10_gap["Gap"],
                y=top10_gap["Model"],
                orientation="h",
                marker=dict(color=gap_colors, line=dict(color=PLOT_BG, width=0.5)),
                text=[f"+{v:.2f}" if v > 0 else "BEST" for v in top10_gap["Gap"]],
                textposition="outside",
                textfont=dict(color=FONT_CLR, size=9)
            ))
            fig.update_layout(
                title=dict(text="RMSE Gap vs Best Model (Top 12)", font=dict(color=FONT_CLR, size=11)),
                yaxis=dict(autorange="reversed", tickfont=dict(size=9))
            )
            apply_theme(fig, 360)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with ch4:
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Relative Performance Score</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            top8 = perf_df.head(8)
            fig = go.Figure(go.Scatterpolar(
                r=top8["Score"],
                theta=top8["Model"],
                fill="toself",
                fillcolor=f"rgba(0,212,255,0.08)",
                line=dict(color=CYAN, width=2),
                marker=dict(color=CYAN, size=7)
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(
                        visible=True, gridcolor=GRID_CLR,
                        tickfont=dict(color=TICK_CLR, size=9), range=[0, 105]
                    ),
                    angularaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=FONT_CLR, size=9))
                ),
                title=dict(text="Model Score · Top 8 (0-100)", font=dict(color=FONT_CLR, size=11))
            )
            apply_theme(fig, 360)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ─── Full Leaderboard Table ────────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
            <div class="section-title">Full Leaderboard</div>
            <div class="section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        # Build entire leaderboard table as one concatenated string.
        # Injecting a large HTML variable into an f-string triple-quote causes
        # Streamlit to escape the injected content — so we build & emit as one call.
        table_parts = []
        table_parts.append('<div class="panel">')
        table_parts.append('<table class="lb-table"><thead><tr>')
        table_parts.append('<th>Rank</th><th>Model</th><th>RMSE</th><th>Score (0-100)</th><th>Gap vs Best</th>')
        table_parts.append('</tr></thead><tbody>')

        for _, row in perf_df.iterrows():
            is_best     = row["Rank"] == 1
            score       = row["Score"]
            bar_width   = max(3, int(score))
            bar_color   = GREEN if is_best else (CYAN if score >= 80 else (AMBER if score >= 50 else "#ff4757"))
            score_color = bar_color
            rmse_class  = "best-rmse" if is_best else "rmse-val"
            row_class   = "best" if is_best else ""
            badge       = "&#9733; " if is_best else ""
            gap_color   = "#ff4757" if row["Gap"] > 5 else ("#ffb800" if row["Gap"] > 1 else "#00ff88")
            gap_str     = ("+" + str(round(row["Gap"], 4))) if row["Gap"] > 0 else "&mdash;"

            table_parts.append('<tr class="' + row_class + '">')
            table_parts.append('<td class="rank">#' + str(int(row["Rank"])) + '</td>')
            table_parts.append('<td class="model-name">' + badge + str(row["Model"]) + '</td>')
            table_parts.append('<td class="' + rmse_class + '">' + f"{row['RMSE']:.4f}" + '</td>')
            table_parts.append(
                '<td><div class="lb-mini-bar">'
                '<div class="mini-bar-track">'
                '<div class="mini-bar-fill" style="width:' + str(bar_width) + '%;background:' + bar_color + ';"></div>'
                '</div>'
                '<span style="font-size:0.65rem;color:' + score_color + ';min-width:30px;">' + f"{score:.0f}" + '</span>'
                '</div></td>'
            )
            table_parts.append('<td style="color:' + gap_color + ';font-size:0.7rem;">' + gap_str + '</td>')
            table_parts.append('</tr>')

        table_parts.append('</tbody></table></div>')
        st.markdown("".join(table_parts), unsafe_allow_html=True)

        # ─── Retrain Section ──────────────────────────────────────────────────
        st.markdown("""
        <div class="section-header" style="margin-top:1.5rem;">
            <div class="section-title">Model Lifecycle</div>
            <div class="section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        lc1, lc2 = st.columns([1, 2])

        with lc1:
            st.markdown(f"""
            <div class="panel">
                <div class="panel-title">Active Model Details</div>
                <div style="display:flex; flex-direction:column; gap:0.6rem;">
                    <div>
                        <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                    letter-spacing:0.12em; text-transform:uppercase; color:#3d5166;">
                            Algorithm
                        </div>
                        <div style="font-family:IBM Plex Mono; font-size:0.9rem;
                                    font-weight:600; color:#e8f0f8; margin-top:2px;">
                            {metadata['model_name']}
                        </div>
                    </div>
                    <div>
                        <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                    letter-spacing:0.12em; text-transform:uppercase; color:#3d5166;">
                            RMSE Score
                        </div>
                        <div style="font-family:IBM Plex Mono; font-size:0.9rem;
                                    font-weight:600; color:#00d4ff; margin-top:2px;">
                            {metadata['rmse']:.4f}
                        </div>
                    </div>
                    <div>
                        <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                    letter-spacing:0.12em; text-transform:uppercase; color:#3d5166;">
                            Version
                        </div>
                        <div style="font-family:IBM Plex Mono; font-size:0.9rem;
                                    font-weight:600; color:#b04eff; margin-top:2px;">
                            v{metadata['version']}
                        </div>
                    </div>
                    <div>
                        <div style="font-family:IBM Plex Mono; font-size:0.58rem;
                                    letter-spacing:0.12em; text-transform:uppercase; color:#3d5166;">
                            Trained At
                        </div>
                        <div style="font-family:IBM Plex Mono; font-size:0.75rem;
                                    color:#7a9bb5; margin-top:2px;">
                            {metadata.get('trained_at','—')[:19]}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⬡  RETRAIN MODEL", use_container_width=True):
                with st.spinner("Running full model training pipeline..."):
                    train_script = os.path.join(base_dir, "scripts", "train_models.py")
                    result = subprocess.run(["python", train_script], capture_output=True, text=True)
                st.markdown(f"""
                <div class="alert-success">
                    ✓ Training complete · New model version generated
                </div>
                """, unsafe_allow_html=True)
                st.rerun()

        with lc2:
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Top Models · RMSE Scatter</div>
                <div class="section-line"></div>
            </div>
            """, unsafe_allow_html=True)

            top15 = perf_df.head(15)
            fig = go.Figure()
            for i, row in top15.iterrows():
                color = GREEN if row["Rank"] == 1 else CYAN if row["Rank"] <= 5 else AMBER if row["Rank"] <= 10 else "#3d5166"
                size  = 18 if row["Rank"] == 1 else 12 if row["Rank"] <= 5 else 9
                fig.add_trace(go.Scatter(
                    x=[row["RMSE"]],
                    y=[row["Score"]],
                    mode="markers+text",
                    marker=dict(color=color, size=size,
                                line=dict(color=PLOT_BG, width=1.5)),
                    text=[row["Model"]],
                    textposition="top center",
                    textfont=dict(size=8, color=color),
                    name=row["Model"],
                    showlegend=False
                ))
            fig.update_layout(
                title=dict(text="RMSE vs Performance Score · Top 15",
                           font=dict(color=FONT_CLR, size=11)),
                xaxis_title="RMSE",
                yaxis_title="Score (0-100)"
            )
            apply_theme(fig, 300)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
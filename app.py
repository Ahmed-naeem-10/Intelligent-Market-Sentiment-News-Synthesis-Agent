"""
╔══════════════════════════════════════════════════════════════╗
║        Automated Market Intelligence System                  ║
║        Professional Streamlit UI — app.py                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.WARNING)

from agents import ResearcherAgent, AnalystAgent, ReporterAgent

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MarketPulse AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #0a0e1a !important;
    color: #e2e8f0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none; }

/* ══════════════════════════════════════════════
   NAVBAR
══════════════════════════════════════════════ */
.navbar {
    background: linear-gradient(135deg, #0d1117 0%, #161b27 100%);
    border-bottom: 1px solid #1e2d3d;
    padding: 18px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(12px);
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.navbar-logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #00d4aa, #0088ff);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 800;
}
.navbar-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
}
.navbar-subtitle {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 400;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.navbar-badge {
    background: linear-gradient(135deg, #00d4aa22, #0088ff22);
    border: 1px solid #00d4aa44;
    color: #00d4aa;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ══════════════════════════════════════════════
   HERO SECTION
══════════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%);
    padding: 64px 48px 48px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -100px; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse, #0088ff18 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-block;
    background: linear-gradient(135deg, #00d4aa22, #0088ff22);
    border: 1px solid #00d4aa33;
    color: #00d4aa;
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin: 0 0 16px;
}
.hero-title span {
    background: linear-gradient(135deg, #00d4aa, #0088ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 580px;
    margin: 0 auto 36px;
    line-height: 1.7;
    font-weight: 400;
}
.pipeline-badges {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.pipe-badge {
    background: #1e2d3d;
    border: 1px solid #2d3f55;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #94a3b8;
}
.pipe-arrow {
    color: #334155;
    font-size: 1.2rem;
}

/* ══════════════════════════════════════════════
   STAT CARDS
══════════════════════════════════════════════ */
.stats-row {
    display: flex;
    gap: 16px;
    padding: 0 48px 32px;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1;
    min-width: 160px;
    background: #111827;
    border: 1px solid #1e2d3d;
    border-radius: 14px;
    padding: 20px 22px;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: #2d3f55; }
.stat-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.stat-sub {
    font-size: 0.75rem;
    color: #475569;
    margin-top: 4px;
}

/* ══════════════════════════════════════════════
   CONTENT WRAPPER
══════════════════════════════════════════════ */
.content-wrap {
    padding: 0 48px 48px;
}

/* ══════════════════════════════════════════════
   SENTIMENT CARD
══════════════════════════════════════════════ */
.sentiment-card {
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}
.sentiment-bullish {
    background: linear-gradient(135deg, #052e16 0%, #0d2418 100%);
    border: 1px solid #166534;
}
.sentiment-bearish {
    background: linear-gradient(135deg, #2d0a0a 0%, #1f0d0d 100%);
    border: 1px solid #991b1b;
}
.sentiment-neutral {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
}
.sentiment-left { display: flex; align-items: center; gap: 20px; }
.sentiment-icon {
    width: 56px; height: 56px;
    border-radius: 14px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 28px;
}
.icon-bullish { background: #14532d44; }
.icon-bearish { background: #7f1d1d44; }
.icon-neutral { background: #1e293b44; }
.sentiment-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.sentiment-value {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1;
}
.bullish-text { color: #4ade80; }
.bearish-text { color: #f87171; }
.neutral-text  { color: #94a3b8; }
.confidence-wrap { text-align: right; }
.conf-label {
    font-size: 0.7rem; color: #64748b;
    text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 6px;
}
.conf-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1px;
}
.conf-max { font-size: 1rem; color: #475569; font-weight: 400; }
.conf-bar-bg {
    width: 160px;
    height: 6px;
    background: #1e293b;
    border-radius: 3px;
    margin-top: 8px;
    margin-left: auto;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #0088ff, #00d4aa);
}

/* ══════════════════════════════════════════════
   SECTION GRID
══════════════════════════════════════════════ */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

/* ══════════════════════════════════════════════
   INFO CARD
══════════════════════════════════════════════ */
.info-card {
    background: #111827;
    border: 1px solid #1e2d3d;
    border-radius: 14px;
    padding: 22px 24px;
    height: 100%;
}
.info-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid #1e2d3d;
}
.info-card-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 15px;
}
.icon-blue { background: #0088ff22; }
.icon-green { background: #00d4aa22; }
.icon-red { background: #ef444422; }
.icon-purple { background: #a855f722; }
.info-card-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ══════════════════════════════════════════════
   LIST ITEMS
══════════════════════════════════════════════ */
.list-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.875rem;
    line-height: 1.5;
    color: #cbd5e1;
    background: #0f172a;
    border: 1px solid #1e2d3d;
    transition: border-color 0.15s;
}
.list-item:hover { border-color: #2d3f55; }
.list-dot-blue  { color: #3b82f6; font-size: 1.2rem; line-height: 1; margin-top:2px; flex-shrink:0; }
.list-dot-red   { color: #ef4444; font-size: 1.2rem; line-height: 1; margin-top:2px; flex-shrink:0; }

/* ══════════════════════════════════════════════
   TICKER CHIPS
══════════════════════════════════════════════ */
.ticker-wrap { display: flex; flex-wrap: wrap; gap: 8px; padding-top: 4px; }
.ticker {
    background: linear-gradient(135deg, #0088ff18, #00d4aa18);
    border: 1px solid #0088ff33;
    color: #60a5fa;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    font-family: 'Courier New', monospace;
}

/* ══════════════════════════════════════════════
   SUMMARY CARD
══════════════════════════════════════════════ */
.summary-card {
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #1e2d3d;
    border-left: 4px solid #0088ff;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 20px;
    font-size: 1rem;
    color: #cbd5e1;
    line-height: 1.7;
    font-style: italic;
}
.summary-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #0088ff;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
    font-style: normal;
}

/* ══════════════════════════════════════════════
   ARTICLE LIST
══════════════════════════════════════════════ */
.article-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    background: #0f172a;
    border: 1px solid #1e2d3d;
    transition: border-color 0.15s, background 0.15s;
}
.article-item:hover {
    border-color: #2d3f55;
    background: #111827;
}
.article-num {
    min-width: 26px; height: 26px;
    background: #1e2d3d;
    border-radius: 6px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: #475569;
    flex-shrink: 0;
}
.article-title {
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.4;
}
.article-title a {
    color: #60a5fa;
    text-decoration: none;
}
.article-title a:hover { color: #93c5fd; text-decoration: underline; }
.article-source {
    font-size: 0.7rem;
    color: #475569;
    margin-top: 3px;
    font-weight: 500;
}

/* ══════════════════════════════════════════════
   STEP PROGRESS
══════════════════════════════════════════════ */
.step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 8px;
    border: 1px solid #1e2d3d;
    background: #0f172a;
}
.step-icon {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.step-pending  { background: #1e2d3d; }
.step-running  { background: #0088ff22; border: 1px solid #0088ff44; }
.step-done     { background: #00d4aa22; border: 1px solid #00d4aa44; }
.step-error    { background: #ef444422; border: 1px solid #ef444444; }
.step-text { flex: 1; }
.step-name { font-size: 0.85rem; font-weight: 600; color: #cbd5e1; }
.step-detail { font-size: 0.75rem; color: #475569; margin-top: 2px; }
.step-time {
    font-size: 0.75rem;
    color: #475569;
    font-variant-numeric: tabular-nums;
}

/* ══════════════════════════════════════════════
   DOWNLOAD BUTTON
══════════════════════════════════════════════ */
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #0088ff, #0066cc) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
    letter-spacing: 0.3px;
}
div[data-testid="stDownloadButton"] button:hover {
    opacity: 0.9 !important;
}

/* Run button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0088ff, #00d4aa) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 36px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════════ */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e2d3d, transparent);
    margin: 32px 0;
}

/* ══════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════ */
.footer {
    background: #0d1117;
    border-top: 1px solid #1e2d3d;
    padding: 24px 48px;
    text-align: center;
    color: #334155;
    font-size: 0.8rem;
}

/* ══════════════════════════════════════════════
   STREAMLIT OVERRIDES
══════════════════════════════════════════════ */
div[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 14px !important;
}
div[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* status widget */
div[data-testid="stStatusWidget"] {
    background: #111827 !important;
    border-color: #1e2d3d !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def sentiment_css(s):
    return {"Bullish": "bullish", "Bearish": "bearish"}.get(s, "neutral")

def sentiment_icon(s):
    return {"Bullish": "📈", "Bearish": "📉"}.get(s, "⚖️")

def conf_color(c):
    if c >= 70: return "#4ade80"
    if c >= 40: return "#facc15"
    return "#f87171"


# ══════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="navbar">
    <div class="navbar-brand">
        <div class="navbar-logo">M</div>
        <div>
            <div class="navbar-title">MarketPulse AI</div>
            <div class="navbar-subtitle">Intelligence System</div>
        </div>
    </div>
    <div class="navbar-badge">● LIVE</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════

today = datetime.now().strftime("%B %d, %Y")
weekday = datetime.now().strftime("%A")

st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered · Real-Time · {weekday}, {today}</div>
    <h1 class="hero-title">Market <span>Intelligence</span><br>at Your Fingertips</h1>
    <p class="hero-desc">
        A multi-agent pipeline that fetches live market news, runs LLM-powered
        sentiment analysis, and generates professional reports — automatically.
    </p>
    <div class="pipeline-badges">
        <div class="pipe-badge">🔍 News Fetch</div>
        <div class="pipe-arrow">→</div>
        <div class="pipe-badge">🧠 LLM Analysis</div>
        <div class="pipe-arrow">→</div>
        <div class="pipe-badge">📄 Report Generation</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# API KEY CHECK
# ══════════════════════════════════════════════════════════════

groq_key = os.getenv("GROQ_API_KEY", "")
if not groq_key or groq_key == "your_groq_api_key_here":
    st.markdown("""
    <div style="background:#2d0a0a;border:1px solid #991b1b;border-radius:14px;
                padding:20px 26px;margin:24px 48px;color:#fca5a5;">
        <strong>⚠️ Configuration Required</strong><br>
        <span style="color:#94a3b8;font-size:0.875rem;">
        GROQ_API_KEY is not set. Add it to your .env file or Streamlit Secrets to run live analysis.
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# STAT CARDS
# ══════════════════════════════════════════════════════════════

news_src = "NewsAPI + DuckDuckGo" if os.getenv("NEWS_API_KEY", "your_newsapi_key_here") != "your_newsapi_key_here" else "DuckDuckGo"

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">LLM Engine</div>
        <div class="stat-value" style="font-size:1.1rem;color:#60a5fa;">GPT-OSS 20B</div>
        <div class="stat-sub">via Groq · Ultra-fast inference</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">News Source</div>
        <div class="stat-value" style="font-size:1.1rem;color:#34d399;">{news_src}</div>
        <div class="stat-sub">Real-time headlines</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Articles Analyzed</div>
        <div class="stat-value">20</div>
        <div class="stat-sub">Per run · AI/Tech focus</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Output Formats</div>
        <div class="stat-value" style="font-size:1.1rem;color:#a78bfa;">PDF + MD</div>
        <div class="stat-sub">Professional reports</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Pipeline Agents</div>
        <div class="stat-value">3</div>
        <div class="stat-sub">Researcher · Analyst · Reporter</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# RUN BUTTON
# ══════════════════════════════════════════════════════════════

st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

col_btn, col_space = st.columns([1, 3])
with col_btn:
    run_btn = st.button("🚀  Run Analysis", type="primary", use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PIPELINE EXECUTION
# ══════════════════════════════════════════════════════════════

if run_btn:
    articles, analysis, pdf_path = [], {}, ""
    step_results = {}

    # ── Step 1 ────────────────────────────────────────────────
    with st.status("🔍 &nbsp; ResearcherAgent — fetching live market news...", expanded=False) as s1:
        r = ResearcherAgent().execute()
        if r.success:
            articles = r.data
            s1.update(label=f"✅ &nbsp; ResearcherAgent — {len(articles)} articles fetched in {r.execution_time_sec}s", state="complete")
            step_results["researcher"] = ("done", len(articles), r.execution_time_sec)
        else:
            s1.update(label="❌ &nbsp; ResearcherAgent — failed", state="error")
            st.markdown("""
            <div style="background:#2d0a0a;border:1px solid #991b1b;border-radius:12px;
                        padding:16px 20px;margin:8px 0;color:#fca5a5;">
                ❌ News fetch failed. Check your network connection.
            </div>""", unsafe_allow_html=True)
            st.stop()

    # ── Step 2 ────────────────────────────────────────────────
    with st.status("🧠 &nbsp; AnalystAgent — running LLM sentiment analysis...", expanded=False) as s2:
        r = AnalystAgent().execute(articles)
        if r.success:
            analysis = r.data
            s2.update(
                label=f"✅ &nbsp; AnalystAgent — {analysis.get('sentiment')} · {analysis.get('confidence')}% confidence · {r.execution_time_sec}s",
                state="complete"
            )
            step_results["analyst"] = ("done", analysis.get("sentiment"), r.execution_time_sec)
        else:
            s2.update(label="⚠️ &nbsp; AnalystAgent — using fallback", state="error")
            analysis = {
                "sentiment": "Neutral", "confidence": 0,
                "key_reasons": ["Analysis unavailable due to API error."],
                "top_movers": [], "risk_factors": ["Manual review recommended."],
                "one_line_summary": "Automated analysis could not be completed.",
            }

    # ── Step 3 ────────────────────────────────────────────────
    with st.status("📄 &nbsp; ReporterAgent — generating PDF + Markdown report...", expanded=False) as s3:
        r = ReporterAgent().execute(analysis, articles)
        if r.success:
            pdf_path = r.data["pdf"]
            s3.update(label=f"✅ &nbsp; ReporterAgent — reports saved in {r.execution_time_sec}s", state="complete")
        else:
            s3.update(label="❌ &nbsp; ReporterAgent — failed", state="error")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # RESULTS
    # ══════════════════════════════════════════════════════════

    sentiment  = analysis.get("sentiment", "Neutral")
    confidence = analysis.get("confidence", 0)
    css        = sentiment_css(sentiment)
    icon       = sentiment_icon(sentiment)
    bar_width  = confidence
    text_class = f"{css}-text"

    # ── Sentiment card ────────────────────────────────────────
    st.markdown(f"""
    <div class="sentiment-card sentiment-{css}">
        <div class="sentiment-left">
            <div class="sentiment-icon icon-{css}">{icon}</div>
            <div>
                <div class="sentiment-label">Overall Market Sentiment</div>
                <div class="sentiment-value {text_class}">{sentiment.upper()}</div>
            </div>
        </div>
        <div class="confidence-wrap">
            <div class="conf-label">Confidence Score</div>
            <div class="conf-value">{confidence}<span class="conf-max">/100</span></div>
            <div class="conf-bar-bg">
                <div class="conf-bar-fill" style="width:{bar_width}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Executive Summary ─────────────────────────────────────
    summary = analysis.get("one_line_summary", "")
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-label">📋 Executive Summary</div>
        {summary}
    </div>
    """, unsafe_allow_html=True)

    # ── Key Reasons + Top Movers ──────────────────────────────
    reasons = analysis.get("key_reasons", [])
    tickers = analysis.get("top_movers", [])

    reasons_html = "".join([
        f'<div class="list-item"><span class="list-dot-blue">›</span>{r}</div>'
        for r in reasons
    ])
    ticker_html = "".join([
        f'<span class="ticker">{t}</span>' for t in tickers
    ]) if tickers else '<span style="color:#475569;font-size:0.85rem;">No movers identified</span>'

    st.markdown(f"""
    <div class="grid-2">
        <div class="info-card">
            <div class="info-card-header">
                <div class="info-card-icon icon-blue">💡</div>
                <div class="info-card-title">Key Reasons</div>
            </div>
            {reasons_html}
        </div>
        <div class="info-card">
            <div class="info-card-header">
                <div class="info-card-icon icon-green">🏆</div>
                <div class="info-card-title">Top Movers / Stocks to Watch</div>
            </div>
            <div class="ticker-wrap">{ticker_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk Factors ──────────────────────────────────────────
    risks = analysis.get("risk_factors", [])
    risks_html = "".join([
        f'<div class="list-item"><span class="list-dot-red">›</span>{r}</div>'
        for r in risks
    ])

    st.markdown(f"""
    <div class="info-card" style="margin-bottom:20px;">
        <div class="info-card-header">
            <div class="info-card-icon icon-red">⚠️</div>
            <div class="info-card-title">Risk Factors</div>
        </div>
        {risks_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Source Articles ───────────────────────────────────────
    articles_html = "".join([
        f'''<div class="article-item">
            <div class="article-num">{i}</div>
            <div>
                <div class="article-title">
                    <a href="{a["url"]}" target="_blank">{a["title"]}</a>
                </div>
                <div class="article-source">{a["source"]}</div>
            </div>
        </div>'''
        for i, a in enumerate(articles, 1)
    ])

    with st.expander(f"📰 Source Articles Analyzed ({len(articles)})", expanded=False):
        st.markdown(articles_html, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────
    dl_col, meta_col = st.columns([1, 2])
    with dl_col:
        if pdf_path and Path(pdf_path).exists():
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️  Download PDF Report",
                    data=f,
                    file_name=f"MarketPulse_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    with meta_col:
        st.markdown(f"""
        <div style="padding-top:10px;">
            <span style="color:#475569;font-size:0.8rem;">
                Generated at <strong style="color:#64748b;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
                &nbsp;·&nbsp; {len(articles)} articles analyzed
                &nbsp;·&nbsp; Powered by Groq LLM
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── Idle state ────────────────────────────────────────────────
else:
    sample_path = Path("reports/sample/market_report_sample.pdf")

    st.markdown("""
    <div style="background:#111827;border:1px solid #1e2d3d;border-radius:16px;
                padding:40px;text-align:center;margin-bottom:24px;">
        <div style="font-size:3rem;margin-bottom:16px;">📊</div>
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;">
            Ready to Generate Your Report
        </div>
        <div style="font-size:0.9rem;color:#64748b;max-width:480px;margin:0 auto 24px;">
            Click <strong style="color:#60a5fa;">Run Analysis</strong> to fetch live market news,
            run AI sentiment analysis, and generate a professional PDF report — all in under 30 seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if sample_path.exists():
        st.markdown("""
        <div style="background:#0f172a;border:1px solid #1e2d3d;border-radius:14px;
                    padding:22px 26px;margin-bottom:8px;">
            <div style="font-size:0.7rem;font-weight:700;color:#475569;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
                📄 Sample Report
            </div>
            <div style="font-size:0.9rem;color:#64748b;">
                Preview a real generated report to see what the output looks like.
            </div>
        </div>
        """, unsafe_allow_html=True)
        with open(sample_path, "rb") as f:
            st.download_button(
                label="⬇️  Download Sample Report (PDF)",
                data=f,
                file_name="MarketPulse_Sample.pdf",
                mime="application/pdf",
            )

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="footer">
    MarketPulse AI &nbsp;·&nbsp; Built with Python, Groq LLM, fpdf2 &amp; Streamlit
    &nbsp;·&nbsp; Multi-agent architecture: Researcher → Analyst → Reporter
</div>
""", unsafe_allow_html=True)

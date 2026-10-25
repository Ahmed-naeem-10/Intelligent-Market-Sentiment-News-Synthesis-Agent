"""
╔══════════════════════════════════════════════════════════════╗
║        Automated Market Intelligence System                  ║
║        Streamlit Web UI — app.py                             ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Market Intelligence System",
    page_icon="📈",
    layout="centered",
)

# ── Suppress agent logs from polluting UI ─────────────────────
logging.basicConfig(level=logging.WARNING)

# ── Import agents ─────────────────────────────────────────────
from agents import ResearcherAgent, AnalystAgent, ReporterAgent

# ══════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main { max-width: 800px; }
    .sentiment-bullish {
        background: #e6f4ea; color: #1a7f3c;
        border-left: 5px solid #1a7f3c;
        padding: 16px 20px; border-radius: 8px;
        font-size: 1.3rem; font-weight: bold;
    }
    .sentiment-bearish {
        background: #fce8e6; color: #b31412;
        border-left: 5px solid #b31412;
        padding: 16px 20px; border-radius: 8px;
        font-size: 1.3rem; font-weight: bold;
    }
    .sentiment-neutral {
        background: #f1f3f4; color: #444;
        border-left: 5px solid #888;
        padding: 16px 20px; border-radius: 8px;
        font-size: 1.3rem; font-weight: bold;
    }
    .summary-box {
        background: #f8f9fa; border-radius: 8px;
        padding: 14px 18px; font-style: italic;
        color: #333; margin: 8px 0;
    }
    .ticker-chip {
        display: inline-block;
        background: #1a73e8; color: white;
        padding: 4px 12px; border-radius: 20px;
        margin: 3px; font-weight: bold; font-size: 0.9rem;
    }
    .risk-item {
        background: #fff3e0; border-left: 4px solid #e65100;
        padding: 8px 14px; border-radius: 4px; margin: 4px 0;
        color: #bf360c;
    }
    .reason-item {
        background: #f0f7ff; border-left: 4px solid #1a73e8;
        padding: 8px 14px; border-radius: 4px; margin: 4px 0;
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════

st.title("📈 Market Intelligence System")
st.markdown("**Multi-agent AI pipeline** · News Fetch → LLM Analysis → Report Generation")
st.markdown("---")

# ── API key check ─────────────────────────────────────────────
groq_key = os.getenv("GROQ_API_KEY", "")
if not groq_key or groq_key == "your_groq_api_key_here":
    st.warning("⚠️ GROQ_API_KEY not configured. Add it to your .env file or Streamlit secrets.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown("**News Source**")
    news_api_key = os.getenv("NEWS_API_KEY", "")
    if news_api_key and news_api_key != "your_newsapi_key_here":
        st.success("✅ NewsAPI connected")
    else:
        st.info("ℹ️ Using DuckDuckGo (no key needed)")

    st.markdown("**LLM**")
    st.success("✅ Groq (GPT-OSS 20B)")

    st.markdown("---")
    st.markdown("**Pipeline Steps**")
    st.markdown("1. 🔍 ResearcherAgent — fetch news")
    st.markdown("2. 🧠 AnalystAgent — LLM analysis")
    st.markdown("3. 📄 ReporterAgent — generate report")

    st.markdown("---")
    st.caption("Built with Python · Groq · fpdf2 · Streamlit")


# ══════════════════════════════════════════════════════════════
# MAIN — RUN BUTTON
# ══════════════════════════════════════════════════════════════

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Generate Today's Market Report")
    st.caption(f"Date: {datetime.now().strftime('%B %d, %Y')}")
with col2:
    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PIPELINE EXECUTION
# ══════════════════════════════════════════════════════════════

if run_btn:
    articles = []
    analysis = {}
    pdf_path = ""

    # ── Step 1: Researcher ────────────────────────────────────
    with st.status("🔍 Step 1/3 — Fetching market news...", expanded=False) as status:
        researcher = ResearcherAgent()
        result = researcher.execute()
        if result.success:
            articles = result.data
            status.update(
                label=f"✅ Step 1/3 — {len(articles)} articles fetched ({result.execution_time_sec}s)",
                state="complete"
            )
        else:
            status.update(label="❌ Step 1/3 — News fetch failed", state="error")
            st.error(f"ResearcherAgent failed: {result.error}")
            st.stop()

    # ── Step 2: Analyst ───────────────────────────────────────
    with st.status("🧠 Step 2/3 — Running LLM sentiment analysis...", expanded=False) as status:
        analyst = AnalystAgent()
        result = analyst.execute(articles)
        if result.success:
            analysis = result.data
            sentiment = analysis.get("sentiment", "N/A")
            confidence = analysis.get("confidence", 0)
            status.update(
                label=f"✅ Step 2/3 — Sentiment: {sentiment} ({confidence}% confidence) ({result.execution_time_sec}s)",
                state="complete"
            )
        else:
            status.update(label="⚠️ Step 2/3 — Analysis failed (using fallback)", state="error")
            analysis = {
                "sentiment": "Neutral", "confidence": 0,
                "key_reasons": ["Analysis unavailable due to API error."],
                "top_movers": [], "risk_factors": ["Manual review recommended."],
                "one_line_summary": "Automated analysis could not be completed.",
            }

    # ── Step 3: Reporter ──────────────────────────────────────
    with st.status("📄 Step 3/3 — Generating reports...", expanded=False) as status:
        reporter = ReporterAgent()
        result = reporter.execute(analysis, articles)
        if result.success:
            paths = result.data
            pdf_path = paths["pdf"]
            status.update(
                label=f"✅ Step 3/3 — Reports saved ({result.execution_time_sec}s)",
                state="complete"
            )
        else:
            status.update(label="❌ Step 3/3 — Report generation failed", state="error")
            st.error(f"ReporterAgent failed: {result.error}")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # RESULTS DISPLAY
    # ══════════════════════════════════════════════════════════

    sentiment = analysis.get("sentiment", "Neutral")
    confidence = analysis.get("confidence", 0)

    # ── Sentiment badge ───────────────────────────────────────
    emoji_map = {"Bullish": "📈", "Bearish": "📉", "Neutral": "⚖️"}
    css_map   = {"Bullish": "bullish", "Bearish": "bearish", "Neutral": "neutral"}
    emoji = emoji_map.get(sentiment, "⚖️")
    css   = css_map.get(sentiment, "neutral")

    st.markdown(
        f'<div class="sentiment-{css}">{emoji} Overall Sentiment: {sentiment.upper()} &nbsp;|&nbsp; Confidence: {confidence}/100</div>',
        unsafe_allow_html=True
    )

    # confidence bar
    filled = round(confidence / 10)
    bar = "█" * filled + "░" * (10 - filled)
    st.caption(f"Confidence: {bar}  {confidence}%")
    st.markdown("")

    # ── Executive Summary ─────────────────────────────────────
    st.markdown("#### 📋 Executive Summary")
    st.markdown(
        f'<div class="summary-box">{analysis.get("one_line_summary", "")}</div>',
        unsafe_allow_html=True
    )

    # ── Two columns: reasons + movers ─────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 💡 Key Reasons")
        for reason in analysis.get("key_reasons", []):
            st.markdown(f'<div class="reason-item">• {reason}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("#### 🏆 Top Movers")
        tickers = analysis.get("top_movers", [])
        if tickers:
            chips = " ".join([f'<span class="ticker-chip">{t}</span>' for t in tickers])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No movers identified")

    st.markdown("")

    # ── Risk Factors ──────────────────────────────────────────
    st.markdown("#### ⚠️ Risk Factors")
    for risk in analysis.get("risk_factors", []):
        st.markdown(f'<div class="risk-item">⚠️ {risk}</div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Source Articles ───────────────────────────────────────
    with st.expander(f"📰 Source Articles Analyzed ({len(articles)})"):
        for i, a in enumerate(articles, 1):
            st.markdown(f"**{i}.** [{a['title']}]({a['url']}) — *{a['source']}*")

    st.markdown("---")

    # ── Download PDF ──────────────────────────────────────────
    if pdf_path and Path(pdf_path).exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=f,
                file_name=f"market_report_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

    st.caption(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ══════════════════════════════════════════════════════════════
# FOOTER — show sample if not yet run
# ══════════════════════════════════════════════════════════════

else:
    st.info("👆 Click **Run Analysis** to generate today's market intelligence report.")

    sample_path = Path("reports/sample/market_report_sample.pdf")
    if sample_path.exists():
        st.markdown("#### 📄 Sample Report Preview")
        st.caption("This is a previously generated report so you can see what the output looks like.")
        with open(sample_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Sample Report (PDF)",
                data=f,
                file_name="market_report_sample.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

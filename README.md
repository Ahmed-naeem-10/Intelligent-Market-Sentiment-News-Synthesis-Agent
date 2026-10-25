# 🤖 Automated Market Intelligence System

> A multi-agent AI pipeline that fetches live market news, runs LLM-powered sentiment analysis, and auto-generates professional PDF + Markdown reports — daily, on schedule.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Groq](https://img.shields.io/badge/LLM-Groq%20%28GPT--OSS%2020B%29-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📊 Sample Report Output

See a real generated report: [`reports/sample/market_report_sample.pdf`](reports/sample/market_report_sample.pdf)

---

## 🏗️ Architecture

```
Orchestrator (main.py)
    │
    ├── 1. ResearcherAgent   → Fetches top AI/tech stock news
    │       ├── Primary  : NewsAPI
    │       └── Fallback : DuckDuckGo (no API key needed)
    │
    ├── 2. AnalystAgent      → LLM sentiment analysis via Groq
    │       └── Returns: Sentiment, Confidence, Key Reasons, Top Movers, Risk Factors
    │
    └── 3. ReporterAgent     → Generates PDF + Markdown reports
            └── Saves to: reports/YYYY-MM-DD/
```

---

## ✨ Features

- **Multi-agent pipeline** — clean separation of concerns
- **Automatic fallback** — DuckDuckGo when NewsAPI is unavailable
- **Graceful degradation** — pipeline never fully crashes
- **Retry logic** — 3 attempts with exponential backoff on every agent
- **Daily scheduling** — runs automatically at configured time
- **Dual output** — professional PDF + Markdown report every run
- **Full logging** — daily log files for every run

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Ahmed-naeem-10/Intelligent-Market-Sentiment-News-Synthesis-Agent.git
cd Intelligent-Market-Sentiment-News-Synthesis-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
copy .env.example .env
# Edit .env — add your GROQ_API_KEY (required)

# 4. Run once
python main.py

# 5. Run on daily schedule (stays alive, runs at 7 AM)
python main.py --schedule
```

---

## 🔑 Get API Keys

| Key | Required | Where to get | Cost |
|-----|----------|--------------|------|
| `GROQ_API_KEY` | ✅ Yes | [console.groq.com/keys](https://console.groq.com/keys) | Free |
| `NEWS_API_KEY` | ❌ Optional | [newsapi.org/register](https://newsapi.org/register) | Free (100 req/day) |

> If `NEWS_API_KEY` is not set, the system automatically uses DuckDuckGo as the news source.

---

## 📁 Project Structure

```
├── main.py                  ← Orchestrator — start here
├── agents/
│   ├── base_agent.py        ← Retry logic + logging (inherited by all agents)
│   ├── researcher.py        ← Agent 1: Fetches news (NewsAPI + DuckDuckGo)
│   ├── analyst.py           ← Agent 2: LLM sentiment analysis (Groq)
│   └── reporter.py          ← Agent 3: PDF + Markdown report generator
├── reports/
│   └── sample/              ← Sample report for preview
├── logs/                    ← Auto-created daily log files
├── .env.example             ← Template for environment variables
└── requirements.txt
```

---

## 📄 Report Output

Each run generates two files in `reports/YYYY-MM-DD/`:

| File | Description |
|------|-------------|
| `market_report.md` | Markdown version with sentiment, reasons, movers |
| `market_report_HHMMSS.pdf` | Formatted PDF with color-coded sentiment badge |

**Report sections:**
- Overall Sentiment (Bullish / Bearish / Neutral) with confidence score
- Executive Summary (one-line AI-generated insight)
- Key Reasons (citing specific news articles)
- Top Movers / Stocks to Watch
- Risk Factors
- Full list of source articles analyzed

---

## ➕ Adding a New Agent

1. Create `agents/your_agent.py` inheriting `BaseAgent`
2. Implement `run(self, ...)` method
3. Import and add a step in `main.py` `Orchestrator.run_pipeline()`

```python
# Example skeleton
from .base_agent import BaseAgent

class EmailSenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="EmailSender")

    def run(self, pdf_path: str):
        # your logic here
        pass
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Inference | [Groq](https://groq.com) — GPT-OSS 20B |
| News Source 1 | [NewsAPI](https://newsapi.org) |
| News Source 2 | [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) |
| PDF Generation | [fpdf2](https://py-pdf.github.io/fpdf2/) |
| Scheduling | [schedule](https://github.com/dbader/schedule) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

*Built with Python · Powered by Groq LLM*

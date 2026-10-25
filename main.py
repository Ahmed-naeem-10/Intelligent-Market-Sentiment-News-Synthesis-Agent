"""
╔══════════════════════════════════════════════════════════════╗
║        Automated Market Intelligence System                  ║
║        Orchestrator — main.py                                ║
╚══════════════════════════════════════════════════════════════╝

Architecture:
    Orchestrator  →  ResearcherAgent
                  →  AnalystAgent
                  →  ReporterAgent
                  →  [EmailSenderAgent]  ← future extension slot

Run modes:
    python main.py           → Run once immediately
    python main.py --schedule → Run daily at configured time (default 7:00 AM)
"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

import schedule
import time
from dotenv import load_dotenv

# ── Load environment variables from .env ──────────────────────────────────────
load_dotenv()

# ── Setup logging ─────────────────────────────────────────────────────────────
import os

LOGS_DIR = os.getenv("LOGS_DIR", "logs")
Path(LOGS_DIR).mkdir(exist_ok=True)

log_file = os.path.join(LOGS_DIR, f"run_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),           # Console output
        logging.FileHandler(log_file, encoding="utf-8"),  # File log
    ],
)
logger = logging.getLogger("orchestrator")

# ── Import Agents ──────────────────────────────────────────────────────────────
from agents import ResearcherAgent, AnalystAgent, ReporterAgent


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR CLASS
# ══════════════════════════════════════════════════════════════════════════════

class Orchestrator:
    """
    Central controller that manages the agent pipeline.

    Adding a new agent is simple:
    1. Create agents/your_agent.py inheriting BaseAgent
    2. Import it here
    3. Add a step in `run_pipeline()`
    """

    def __init__(self):
        self.researcher = ResearcherAgent()
        self.analyst    = AnalystAgent()
        self.reporter   = ReporterAgent()
        # Future: self.email_sender = EmailSenderAgent()

    def run_pipeline(self) -> bool:
        """
        Executes the full Researcher → Analyst → Reporter pipeline.
        Returns True on success, False if any critical step fails.
        """
        run_start = datetime.now()
        logger.info("=" * 60)
        logger.info(f"  PIPELINE START  |  {run_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        # ── STEP 1: RESEARCHER ─────────────────────────────────────────────
        logger.info("► Step 1/3 | ResearcherAgent: Fetching market news...")
        research_result = self.researcher.execute()

        if not research_result.success:
            logger.error(f"✗ ResearcherAgent failed: {research_result.error}")
            logger.error("Pipeline aborted — cannot proceed without news data.")
            return False

        articles = research_result.data
        logger.info(f"✓ ResearcherAgent done | {len(articles)} articles fetched "
                    f"in {research_result.execution_time_sec}s")

        # ── STEP 2: ANALYST ────────────────────────────────────────────────
        logger.info("► Step 2/3 | AnalystAgent: Running sentiment analysis...")
        analysis_result = self.analyst.execute(articles)

        if not analysis_result.success:
            logger.error(f"✗ AnalystAgent failed: {analysis_result.error}")
            logger.warning("Pipeline continuing with fallback analysis...")
            # Graceful degradation: use a minimal fallback so Reporter can still run
            analysis = self._fallback_analysis()
        else:
            analysis = analysis_result.data
            logger.info(
                f"✓ AnalystAgent done | Sentiment: {analysis['sentiment']} "
                f"({analysis['confidence']}% confidence) "
                f"in {analysis_result.execution_time_sec}s"
            )

        # ── STEP 3: REPORTER ───────────────────────────────────────────────
        logger.info("► Step 3/3 | ReporterAgent: Generating reports...")
        report_result = self.reporter.execute(analysis, articles)

        if not report_result.success:
            logger.error(f"✗ ReporterAgent failed: {report_result.error}")
            return False

        paths = report_result.data
        logger.info(f"✓ ReporterAgent done in {report_result.execution_time_sec}s")

        # ── PIPELINE SUMMARY ───────────────────────────────────────────────
        elapsed = round((datetime.now() - run_start).total_seconds(), 2)
        logger.info("=" * 60)
        logger.info("  PIPELINE COMPLETE")
        logger.info(f"  Total time      : {elapsed}s")
        logger.info(f"  Sentiment       : {analysis['sentiment']} @ {analysis['confidence']}% confidence")
        logger.info(f"  Markdown report : {paths['markdown']}")
        logger.info(f"  PDF report      : {paths['pdf']}")
        logger.info("=" * 60)

        # ── FUTURE EXTENSION SLOT ──────────────────────────────────────────
        # Uncomment when EmailSenderAgent is ready:
        # logger.info("► Step 4/4 | EmailSenderAgent: Sending report...")
        # self.email_sender.execute(paths['pdf'])

        return True

    @staticmethod
    def _fallback_analysis() -> dict:
        """
        Agar AnalystAgent fail ho jaaye, toh report khaali nahi jaati.
        Ek basic structure return hota hai taaki Reporter kaam kar sake.
        """
        return {
            "sentiment": "Neutral",
            "confidence": 0,
            "key_reasons": ["Analysis unavailable due to API error."],
            "top_movers": [],
            "risk_factors": ["Manual review recommended for today."],
            "one_line_summary": "Automated analysis could not be completed. Please review source articles manually.",
        }


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINTS
# ══════════════════════════════════════════════════════════════════════════════

def run_once():
    """Single run — use this for manual execution or cron jobs."""
    orchestrator = Orchestrator()
    success = orchestrator.run_pipeline()
    sys.exit(0 if success else 1)


def run_scheduled():
    """
    Keeps the process alive and runs the pipeline once per day
    at the configured time (default 07:00).
    """
    run_hour   = int(os.getenv("RUN_HOUR", "7"))
    run_minute = int(os.getenv("RUN_MINUTE", "0"))
    run_time   = f"{run_hour:02d}:{run_minute:02d}"

    logger.info(f"Scheduler mode active. Pipeline will run daily at {run_time}.")
    logger.info("Press Ctrl+C to stop.\n")

    orchestrator = Orchestrator()

    schedule.every().day.at(run_time).do(orchestrator.run_pipeline)

    # Run immediately on startup so you don't wait until tomorrow
    logger.info("Running pipeline immediately on startup...")
    orchestrator.run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(30)  # check every 30 seconds


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated Market Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                  Run once right now
  python main.py --schedule       Run daily at configured time (see .env)
        """
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Keep running and execute pipeline daily at configured time",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        run_once()

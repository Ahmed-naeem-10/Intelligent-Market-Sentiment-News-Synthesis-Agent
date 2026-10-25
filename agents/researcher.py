"""
Agent 1: Researcher
-------------------
Kaam: Tech/AI stocks se related top news headlines fetch karna.
Primary source  : NewsAPI
Fallback source : DuckDuckGo Search (agar NewsAPI key nahi hai ya limit hit ho)
"""

import os
import requests
from typing import List, Dict
from .base_agent import BaseAgent

# DuckDuckGo — zero API key required
try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False


SEARCH_QUERIES = [
    "AI stocks market news today",
    "tech stocks NVIDIA Apple Microsoft sentiment",
    "artificial intelligence investment news",
    "semiconductor stocks analysis today",
]

MAX_ARTICLES = 20  # total articles to collect


class ResearcherAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="Researcher")
        self.news_api_key = os.getenv("NEWS_API_KEY", "")

    def run(self) -> List[Dict]:
        """
        Returns list of article dicts:
        [{"title": ..., "description": ..., "url": ..., "source": ...}, ...]
        """
        articles = []

        if self.news_api_key and self.news_api_key != "your_newsapi_key_here":
            self.logger.info("Using NewsAPI as primary source...")
            articles = self._fetch_from_newsapi()
        
        # Fallback ya supplement: DuckDuckGo
        if len(articles) < 5:
            self.logger.info("Switching to DuckDuckGo fallback...")
            articles += self._fetch_from_ddg()

        if not articles:
            raise ValueError("No articles fetched from any source. Check API keys or network.")

        self.logger.info(f"Total articles collected: {len(articles)}")
        return articles[:MAX_ARTICLES]

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _fetch_from_newsapi(self) -> List[Dict]:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "AI stocks OR tech stocks OR NVIDIA OR semiconductor",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": MAX_ARTICLES,
            "apiKey": self.news_api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw = response.json().get("articles", [])
        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
            }
            for a in raw
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]

    def _fetch_from_ddg(self) -> List[Dict]:
        if not DDG_AVAILABLE:
            self.logger.warning("duckduckgo_search not installed. Skipping DDG fallback.")
            return []

        results = []
        with DDGS() as ddgs:
            for query in SEARCH_QUERIES:
                try:
                    hits = list(ddgs.news(query, max_results=5))
                    for h in hits:
                        results.append({
                            "title": h.get("title", ""),
                            "description": h.get("body", ""),
                            "url": h.get("url", ""),
                            "source": h.get("source", "DuckDuckGo"),
                        })
                except Exception as e:
                    self.logger.warning(f"DDG query '{query}' failed: {e}")
        return results

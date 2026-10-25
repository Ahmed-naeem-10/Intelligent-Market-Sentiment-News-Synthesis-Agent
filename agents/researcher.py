"""
Agent 1: Researcher
-------------------
Kaam: Tech/AI stocks se related top news headlines fetch karna.

Source priority:
  1. NewsAPI       — best quality, needs API key
  2. GNews API     — free, no key needed, cloud-friendly
  3. DuckDuckGo    — local fallback
"""

import os
import time
import requests
from typing import List, Dict
from .base_agent import BaseAgent

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False


SEARCH_QUERIES = [
    "AI stocks market news",
    "tech stocks NVIDIA Apple Microsoft",
    "artificial intelligence investment",
    "semiconductor stocks analysis",
]

MAX_ARTICLES = 20

# GNews topics — free, no key, works on cloud servers
GNEWS_QUERIES = [
    "AI stocks",
    "tech stocks market",
    "NVIDIA Apple Microsoft stock",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class ResearcherAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="Researcher")
        self.news_api_key = os.getenv("NEWS_API_KEY", "")

    def run(self) -> List[Dict]:
        articles = []

        # ── Source 1: NewsAPI ──────────────────────────────────
        if self.news_api_key and self.news_api_key != "your_newsapi_key_here":
            self.logger.info("Using NewsAPI as primary source...")
            try:
                articles = self._fetch_from_newsapi()
                self.logger.info(f"NewsAPI returned {len(articles)} articles")
            except Exception as e:
                self.logger.warning(f"NewsAPI failed: {e}")

        # ── Source 2: GNews (free, cloud-safe) ────────────────
        if len(articles) < 5:
            self.logger.info("Trying GNews API...")
            try:
                gnews_articles = self._fetch_from_gnews()
                articles += gnews_articles
                self.logger.info(f"GNews returned {len(gnews_articles)} articles")
            except Exception as e:
                self.logger.warning(f"GNews failed: {e}")

        # ── Source 3: DuckDuckGo (local fallback) ─────────────
        if len(articles) < 5:
            self.logger.info("Trying DuckDuckGo fallback...")
            try:
                ddg_articles = self._fetch_from_ddg()
                articles += ddg_articles
                self.logger.info(f"DDG returned {len(ddg_articles)} articles")
            except Exception as e:
                self.logger.warning(f"DDG failed: {e}")

        # ── Source 4: RSS feeds (always available) ─────────────
        if len(articles) < 5:
            self.logger.info("Trying RSS feeds as last resort...")
            try:
                rss_articles = self._fetch_from_rss()
                articles += rss_articles
                self.logger.info(f"RSS returned {len(rss_articles)} articles")
            except Exception as e:
                self.logger.warning(f"RSS failed: {e}")

        # Deduplicate by title
        seen, unique = set(), []
        for a in articles:
            t = a.get("title", "").strip().lower()
            if t and t not in seen:
                seen.add(t)
                unique.append(a)

        if not unique:
            raise ValueError("No articles fetched from any source.")

        self.logger.info(f"Total unique articles: {len(unique)}")
        return unique[:MAX_ARTICLES]

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
        r = requests.get(url, params=params, timeout=12, headers=HEADERS)
        r.raise_for_status()
        raw = r.json().get("articles", [])
        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description", "") or "",
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
            }
            for a in raw
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]

    def _fetch_from_gnews(self) -> List[Dict]:
        """
        GNews public API — free tier, no key needed for basic use,
        works reliably from cloud servers.
        """
        results = []
        gnews_key = os.getenv("GNEWS_API_KEY", "")

        for query in GNEWS_QUERIES:
            try:
                if gnews_key:
                    url = "https://gnews.io/api/v4/search"
                    params = {
                        "q": query,
                        "lang": "en",
                        "max": 5,
                        "apikey": gnews_key,
                    }
                else:
                    # Use the free RSS-based endpoint
                    url = f"https://news.google.com/rss/search"
                    params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}

                r = requests.get(url, params=params, timeout=10, headers=HEADERS)
                if r.status_code == 200:
                    if gnews_key:
                        for art in r.json().get("articles", []):
                            results.append({
                                "title": art.get("title", ""),
                                "description": art.get("description", "") or "",
                                "url": art.get("url", ""),
                                "source": art.get("source", {}).get("name", "GNews"),
                            })
                    else:
                        # Parse RSS XML
                        rss_results = self._parse_rss_xml(r.text, "Google News")
                        results.extend(rss_results[:5])
                time.sleep(0.3)
            except Exception as e:
                self.logger.warning(f"GNews query '{query}' failed: {e}")

        return results

    def _fetch_from_rss(self) -> List[Dict]:
        """Fetch from reliable public RSS feeds — always cloud-safe."""
        feeds = [
            ("https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA,AAPL,MSFT,META&region=US&lang=en-US", "Yahoo Finance"),
            ("https://www.investing.com/rss/news_301.rss", "Investing.com"),
            ("https://feeds.marketwatch.com/marketwatch/topstories/", "MarketWatch"),
        ]
        results = []
        for feed_url, source_name in feeds:
            try:
                r = requests.get(feed_url, timeout=10, headers=HEADERS)
                if r.status_code == 200:
                    items = self._parse_rss_xml(r.text, source_name)
                    results.extend(items[:6])
            except Exception as e:
                self.logger.warning(f"RSS {source_name} failed: {e}")
        return results

    def _parse_rss_xml(self, xml_text: str, source: str) -> List[Dict]:
        """Simple RSS XML parser without external dependencies."""
        import re
        results = []
        items = re.findall(r"<item>(.*?)</item>", xml_text, re.DOTALL)
        for item in items:
            title_m = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", item, re.DOTALL)
            link_m  = re.search(r"<link>(.*?)</link>|<guid>(.*?)</guid>", item, re.DOTALL)
            desc_m  = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>", item, re.DOTALL)

            title = (title_m.group(1) or title_m.group(2) or "").strip() if title_m else ""
            link  = (link_m.group(1) or link_m.group(2) or "").strip() if link_m else ""
            desc  = (desc_m.group(1) or desc_m.group(2) or "").strip() if desc_m else ""

            # Strip HTML tags from description
            desc = re.sub(r"<[^>]+>", "", desc).strip()

            if title and len(title) > 10:
                results.append({
                    "title": title,
                    "description": desc[:300],
                    "url": link,
                    "source": source,
                })
        return results

    def _fetch_from_ddg(self) -> List[Dict]:
        if not DDG_AVAILABLE:
            return []
        results = []
        with DDGS(headers=HEADERS) as ddgs:
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
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"DDG query '{query}' failed: {e}")
        return results

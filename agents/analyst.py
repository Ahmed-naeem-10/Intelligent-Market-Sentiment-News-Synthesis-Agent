"""
Agent 2: Analyst
----------------
Kaam: Researcher ke articles ko Groq (Llama 3.1) ke paas bhejkar
      structured sentiment analysis lena.

Output:
{
  "sentiment": "Bullish" | "Bearish" | "Neutral",
  "confidence": 0-100,
  "key_reasons": ["reason1", "reason2", ...],
  "top_movers": ["NVDA", "AAPL", ...],
  "risk_factors": ["risk1", ...],
  "one_line_summary": "..."
}
"""

import os
import json
import re
from typing import Dict, List
from .base_agent import BaseAgent

from groq import Groq


ANALYSIS_PROMPT_TEMPLATE = """
You are a senior equity analyst at a top investment firm.

Below are today's top news headlines and descriptions related to tech stocks and AI industry.
Analyze them collectively and return a JSON object — nothing else, just valid JSON.

NEWS DATA:
{news_text}

Return this exact JSON structure:
{{
  "sentiment": "<Bullish|Bearish|Neutral>",
  "confidence": <integer 0-100>,
  "key_reasons": ["<reason 1>", "<reason 2>", "<reason 3>"],
  "top_movers": ["<TICKER or company name>", ...],
  "risk_factors": ["<risk 1>", "<risk 2>"],
  "one_line_summary": "<One crisp executive sentence>"
}}

Rules:
- confidence 70+ means strong signal, 40-69 is moderate, below 40 is weak/uncertain
- key_reasons must cite specific news items
- Be concise and factual
- Return ONLY valid JSON, no extra text
"""


class AnalystAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="Analyst")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in environment.")
        self.client = Groq(api_key=api_key)

    def run(self, articles: List[Dict]) -> Dict:
        """
        articles: output from ResearcherAgent
        Returns: structured analysis dict
        """
        news_text = self._format_articles(articles)
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(news_text=news_text)

        self.logger.info(f"Sending {len(articles)} articles to Groq (Llama) for analysis...")

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a professional equity analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        raw_text = response.choices[0].message.content.strip()
        analysis = self._parse_json_response(raw_text)
        self.logger.info(f"Sentiment: {analysis['sentiment']} | Confidence: {analysis['confidence']}%")
        return analysis

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _format_articles(self, articles: List[Dict]) -> str:
        lines = []
        for i, a in enumerate(articles, 1):
            lines.append(
                f"{i}. [{a['source']}] {a['title']}\n"
                f"   {a.get('description', 'No description')}\n"
                f"   URL: {a['url']}"
            )
        return "\n\n".join(lines)

    def _parse_json_response(self, raw: str) -> Dict:
        """
        Strip markdown code fences if present and parse JSON.
        """
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse failed. Raw response:\n{raw}")
            raise ValueError(f"Groq returned invalid JSON: {e}") from e

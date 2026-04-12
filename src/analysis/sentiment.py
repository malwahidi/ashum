"""
AI News Sentiment Analysis
===========================
Uses Claude API to analyze Arabic financial news and determine
sentiment (bullish/bearish/neutral) for Saudi stocks.
"""

import logging
import json
from datetime import date, datetime

from config.settings import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

# Sentiment cache: {ticker: {date, sentiment, score, summary}}
_sentiment_cache = {}

SENTIMENT_BULLISH_SCORE = 20
SENTIMENT_BEARISH_SCORE = -20
SENTIMENT_NEUTRAL_SCORE = 0


class StockSentiment:
    """Sentiment analysis result for a stock."""

    def __init__(self, ticker: str, sentiment: str, score: int,
                 summary: str, confidence: float):
        self.ticker = ticker
        self.sentiment = sentiment  # "bullish", "bearish", "neutral"
        self.score = score  # +20, -20, or 0
        self.summary = summary  # Arabic summary
        self.confidence = confidence  # 0.0 - 1.0

    def to_arabic(self) -> str:
        icons = {"bullish": "\U0001f7e2", "bearish": "\U0001f534", "neutral": "\U0001f7e1"}
        labels = {"bullish": "إيجابي", "bearish": "سلبي", "neutral": "محايد"}
        icon = icons.get(self.sentiment, "\U0001f7e1")
        label = labels.get(self.sentiment, "محايد")
        return f"{icon} المشاعر: {label} ({self.confidence:.0%})\n  {self.summary}"


async def analyze_stock_sentiment(ticker: str, stock_name: str) -> StockSentiment | None:
    """
    Analyze news sentiment for a stock using Claude API.
    Results are cached for 1 day per stock.

    Args:
        ticker: Tadawul ticker number
        stock_name: Company name for search

    Returns:
        StockSentiment or None if API unavailable.
    """
    if not ANTHROPIC_API_KEY:
        return None

    # Check cache
    today = date.today()
    cache_key = ticker
    if cache_key in _sentiment_cache:
        cached = _sentiment_cache[cache_key]
        if cached.get("date") == today:
            return cached.get("result")

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""أنت محلل مالي متخصص في السوق السعودي (تداول).

حلل الوضع الحالي لسهم {stock_name} (رمز {ticker}.SR) في السوق السعودي.

بناءً على معرفتك العامة بالسوق والشركة، قيّم:
1. هل الاتجاه العام للسهم إيجابي أم سلبي أم محايد؟
2. هل هناك عوامل أساسية تدعم الشراء أو البيع؟

أجب بصيغة JSON فقط:
{{
  "sentiment": "bullish" أو "bearish" أو "neutral",
  "confidence": رقم بين 0.0 و 1.0,
  "summary_ar": "ملخص قصير بالعربي (جملة واحدة)"
}}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Parse JSON from response
        # Handle potential markdown code blocks
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        data = json.loads(response_text)

        sentiment = data.get("sentiment", "neutral")
        confidence = float(data.get("confidence", 0.5))
        summary = data.get("summary_ar", "لا يتوفر تحليل")

        # Map sentiment to score
        score_map = {
            "bullish": SENTIMENT_BULLISH_SCORE,
            "bearish": SENTIMENT_BEARISH_SCORE,
            "neutral": SENTIMENT_NEUTRAL_SCORE,
        }
        score = score_map.get(sentiment, 0)

        # Apply confidence weighting
        score = int(score * confidence)

        result = StockSentiment(ticker, sentiment, score, summary, confidence)

        # Cache
        _sentiment_cache[cache_key] = {"date": today, "result": result}

        logger.info(f"Sentiment for {ticker}: {sentiment} ({confidence:.0%}) score={score}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse sentiment response for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {ticker}: {e}")
        return None


def get_cached_sentiment(ticker: str) -> StockSentiment | None:
    """Get cached sentiment without making API call."""
    today = date.today()
    cached = _sentiment_cache.get(ticker)
    if cached and cached.get("date") == today:
        return cached.get("result")
    return None

"""
AI News Sentiment Analysis
===========================
Uses Gemini (free) for daily analysis, Claude API ready for live trading phase.
Analyzes Arabic financial sentiment for Saudi stocks.
"""

import logging
import json
from datetime import date

from config.settings import GEMINI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

# Sentiment cache: {ticker: {date, result}}
_sentiment_cache = {}

SENTIMENT_BULLISH_SCORE = 20
SENTIMENT_BEARISH_SCORE = -20
SENTIMENT_NEUTRAL_SCORE = 0

# Which AI provider to use: "gemini" (free) or "claude" (paid, for live trading)
AI_PROVIDER = "gemini"


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


def _build_prompt(ticker: str, stock_name: str, news_headlines: list[str] = None) -> str:
    """Build the analysis prompt with real news if available."""
    if news_headlines:
        headlines_text = "\n".join(f"- {h}" for h in news_headlines)
        return f"""أنت محلل مالي متخصص في السوق السعودي (تداول).

حلل سهم {stock_name} (رمز {ticker}.SR) بناءً على الأخبار التالية:

{headlines_text}

بناءً على هذه الأخبار الحقيقية:
1. هل تأثير الأخبار إيجابي أم سلبي أم محايد على السهم؟
2. ما مدى تأثير هذه الأخبار على سعر السهم؟

أجب بصيغة JSON فقط:
{{
  "sentiment": "bullish" أو "bearish" أو "neutral",
  "confidence": رقم بين 0.0 و 1.0,
  "summary_ar": "ملخص قصير بالعربي (جملة واحدة) يوضح تأثير الأخبار"
}}"""
    else:
        return f"""أنت محلل مالي متخصص في السوق السعودي (تداول).

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


def _parse_response(response_text: str) -> dict:
    """Parse JSON from AI response, handling code blocks."""
    text = response_text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


async def _analyze_with_gemini(ticker: str, stock_name: str, news_headlines: list[str] = None) -> StockSentiment | None:
    """Analyze sentiment using Google Gemini with real news."""
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set")
        return None

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = _build_prompt(ticker, stock_name, news_headlines)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        data = _parse_response(response.text)

        sentiment = data.get("sentiment", "neutral")
        confidence = float(data.get("confidence", 0.5))
        summary = data.get("summary_ar", "لا يتوفر تحليل")

        score_map = {
            "bullish": SENTIMENT_BULLISH_SCORE,
            "bearish": SENTIMENT_BEARISH_SCORE,
            "neutral": SENTIMENT_NEUTRAL_SCORE,
        }
        score = int(score_map.get(sentiment, 0) * confidence)

        return StockSentiment(ticker, sentiment, score, summary, confidence)

    except Exception as e:
        logger.error(f"Gemini sentiment failed for {ticker}: {e}")
        return None


# ============================================================
# Claude API — commented out, ready for live trading phase
# To activate: change AI_PROVIDER = "claude" and set ANTHROPIC_API_KEY
# ============================================================
#
# async def _analyze_with_claude(ticker: str, stock_name: str) -> StockSentiment | None:
#     """Analyze sentiment using Claude API (paid, higher quality)."""
#     if not ANTHROPIC_API_KEY:
#         return None
#
#     try:
#         import anthropic
#
#         client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
#         prompt = _build_prompt(ticker, stock_name)
#
#         message = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=300,
#             messages=[{"role": "user", "content": prompt}]
#         )
#
#         data = _parse_response(message.content[0].text)
#
#         sentiment = data.get("sentiment", "neutral")
#         confidence = float(data.get("confidence", 0.5))
#         summary = data.get("summary_ar", "لا يتوفر تحليل")
#
#         score_map = {
#             "bullish": SENTIMENT_BULLISH_SCORE,
#             "bearish": SENTIMENT_BEARISH_SCORE,
#             "neutral": SENTIMENT_NEUTRAL_SCORE,
#         }
#         score = int(score_map.get(sentiment, 0) * confidence)
#
#         return StockSentiment(ticker, sentiment, score, summary, confidence)
#
#     except Exception as e:
#         logger.error(f"Claude sentiment failed for {ticker}: {e}")
#         return None


async def analyze_stock_sentiment(ticker: str, stock_name: str) -> StockSentiment | None:
    """
    Analyze sentiment for a stock using real news + AI.
    1. Fetch real news headlines from Argaam/MarketAux
    2. Send to Gemini for analysis
    Results are cached for 1 day per stock.
    """
    # Check cache
    today = date.today()
    if ticker in _sentiment_cache:
        cached = _sentiment_cache[ticker]
        if cached.get("date") == today:
            return cached.get("result")

    # Fetch real news for this stock
    from src.analysis.news import get_stock_news
    news_headlines = get_stock_news(ticker, stock_name)

    if news_headlines:
        logger.info(f"Found {len(news_headlines)} news items for {ticker}")
    else:
        logger.info(f"No specific news for {ticker}, using general analysis")

    # Analyze with Gemini (with real news if available)
    result = await _analyze_with_gemini(ticker, stock_name, news_headlines)

    # To switch to Claude later, uncomment:
    # if AI_PROVIDER == "claude":
    #     result = await _analyze_with_claude(ticker, stock_name)
    # else:
    #     result = await _analyze_with_gemini(ticker, stock_name)

    if result:
        _sentiment_cache[ticker] = {"date": today, "result": result}
        logger.info(f"Sentiment for {ticker}: {result.sentiment} ({result.confidence:.0%}) score={result.score}")

    return result


def get_cached_sentiment(ticker: str) -> StockSentiment | None:
    """Get cached sentiment without making API call."""
    today = date.today()
    cached = _sentiment_cache.get(ticker)
    if cached and cached.get("date") == today:
        return cached.get("result")
    return None

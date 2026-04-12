"""
Real-Time News Fetching for Saudi Stocks
=========================================
Fetches actual news from Argaam RSS feeds and MarketAux API.
Returns today's headlines for sentiment analysis.
"""

import logging
from datetime import date, datetime, timedelta

import feedparser
import requests

logger = logging.getLogger(__name__)

# Argaam RSS Feeds (free, Arabic)
ARGAAM_FEEDS = {
    "breaking": "https://www.argaam.com/en/rss/breaking-news?sectionid=1584",
    "latest": "https://www.argaam.com/en/rss/ho-main-news?sectionid=1524",
    "disclosures": "https://www.argaam.com/en/rss/ho-company-disclosures?sectionid=244",
}

# Also fetch Arabic feeds
ARGAAM_AR_FEEDS = {
    "latest_ar": "https://www.argaam.com/ar/rss/ho-main-news?sectionid=138",
    "disclosures_ar": "https://www.argaam.com/ar/rss/ho-company-disclosures?sectionid=244",
}

# News cache: {date: {ticker: [headlines]}}
_news_cache = {}
_cache_date = None


def fetch_argaam_news() -> list[dict]:
    """
    Fetch latest news from Argaam RSS feeds.
    Returns list of {title, summary, published, link}.
    """
    all_news = []

    for name, url in {**ARGAAM_FEEDS, **ARGAAM_AR_FEEDS}.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:  # Last 20 per feed
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])

                all_news.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:200],
                    "published": published,
                    "link": entry.get("link", ""),
                    "source": "Argaam",
                })
        except Exception as e:
            logger.error(f"Failed to fetch Argaam feed {name}: {e}")

    logger.info(f"Fetched {len(all_news)} news items from Argaam")
    return all_news


def fetch_marketaux_news(ticker: str = None) -> list[dict]:
    """
    Fetch Saudi stock news from MarketAux API (free, 100 req/day).
    """
    try:
        params = {
            "countries": "sa",
            "filter_entities": "true",
            "language": "ar,en",
            "limit": 10,
        }
        if ticker:
            params["search"] = f"{ticker}.SR"

        # MarketAux free tier (no API key needed for basic)
        url = "https://api.marketaux.com/v1/news/all"
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            news = []
            for item in data.get("data", []):
                news.append({
                    "title": item.get("title", ""),
                    "summary": item.get("description", "")[:200],
                    "published": item.get("published_at"),
                    "link": item.get("url", ""),
                    "source": "MarketAux",
                    "sentiment_score": item.get("sentiment_score"),
                })
            return news
        else:
            logger.warning(f"MarketAux returned {resp.status_code}")
            return []

    except Exception as e:
        logger.error(f"MarketAux fetch failed: {e}")
        return []


def get_stock_news(ticker: str, stock_name: str) -> list[str]:
    """
    Get recent news headlines relevant to a specific stock.

    Args:
        ticker: Tadawul ticker number (e.g., "2222")
        stock_name: Company name for matching (e.g., "Saudi Aramco")

    Returns:
        List of relevant headline strings.
    """
    global _news_cache, _cache_date

    today = date.today()

    # Refresh cache once per day
    if _cache_date != today:
        _news_cache = {"all_news": fetch_argaam_news()}
        _cache_date = today

    all_news = _news_cache.get("all_news", [])

    # Match headlines to this stock
    search_terms = [
        ticker,
        f"{ticker}.SR",
        stock_name.lower(),
    ]

    # Add common name variations
    name_parts = stock_name.lower().split()
    if len(name_parts) > 1:
        search_terms.extend(name_parts)

    relevant = []
    for item in all_news:
        title = item["title"].lower()
        summary = item.get("summary", "").lower()
        text = f"{title} {summary}"

        for term in search_terms:
            if term.lower() in text:
                headline = item["title"]
                if headline not in relevant:
                    relevant.append(headline)
                break

    # If no specific news found, try MarketAux
    if not relevant:
        mx_news = fetch_marketaux_news(ticker)
        for item in mx_news:
            if item["title"] not in relevant:
                relevant.append(item["title"])

    # Limit to 5 most relevant
    return relevant[:5]


def get_market_news_summary() -> list[str]:
    """Get top market-wide headlines (not stock-specific)."""
    global _news_cache, _cache_date

    today = date.today()
    if _cache_date != today:
        _news_cache = {"all_news": fetch_argaam_news()}
        _cache_date = today

    all_news = _news_cache.get("all_news", [])

    # Return top 5 most recent headlines
    headlines = [item["title"] for item in all_news[:5]]
    return headlines

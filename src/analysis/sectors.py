"""
Sector Strength Analysis
========================
Ranks sectors by recent performance. Boosts signals from strong sectors,
suppresses signals from weak sectors.
"""

import logging
from datetime import date

import pandas as pd

from src.data.tickers import TADAWUL_STOCKS, get_tickers_by_sector, get_all_sectors

logger = logging.getLogger(__name__)

# Cached sector rankings
_cached_rankings = None
_cached_date = None

STRONG_SECTOR_BOOST = 10   # Score boost for top sectors
WEAK_SECTOR_PENALTY = -10  # Score penalty for bottom sectors
TOP_N = 3                  # Number of top/bottom sectors


class SectorRanking:
    """Sector strength rankings."""

    def __init__(self, rankings: list[dict]):
        self.rankings = rankings  # [{sector, avg_return, rank, strength}]
        self._strong = set()
        self._weak = set()

        if rankings:
            for r in rankings[:TOP_N]:
                if r["avg_return"] > 0:
                    self._strong.add(r["sector"])
            for r in rankings[-TOP_N:]:
                if r["avg_return"] < 0:
                    self._weak.add(r["sector"])

    def get_score_adjustment(self, sector: str) -> int:
        """Get score adjustment for a stock's sector."""
        if sector in self._strong:
            return STRONG_SECTOR_BOOST
        elif sector in self._weak:
            return WEAK_SECTOR_PENALTY
        return 0

    def get_strength(self, sector: str) -> str:
        """Get sector strength label."""
        if sector in self._strong:
            return "STRONG"
        elif sector in self._weak:
            return "WEAK"
        return "NEUTRAL"

    def to_arabic(self) -> str:
        """Arabic summary for Telegram."""
        if not self.rankings:
            return "لا تتوفر بيانات القطاعات"

        msg = "\U0001f4ca <b>أقوى القطاعات (20 يوم):</b>\n"
        for r in self.rankings[:3]:
            icon = "\U0001f7e2" if r["avg_return"] > 0 else "\U0001f534"
            msg += f"  {icon} {r['sector']}: {r['avg_return']:+.1f}%\n"

        msg += "\n<b>أضعف القطاعات:</b>\n"
        for r in self.rankings[-3:]:
            icon = "\U0001f534" if r["avg_return"] < 0 else "\U0001f7e1"
            msg += f"  {icon} {r['sector']}: {r['avg_return']:+.1f}%\n"

        return msg


def calculate_sector_rankings(stock_data: dict[str, pd.DataFrame]) -> SectorRanking:
    """
    Calculate sector performance rankings from stock data.

    Args:
        stock_data: Dict of ticker -> OHLCV DataFrame (already fetched)

    Returns:
        SectorRanking object with ranked sectors.
    """
    global _cached_rankings, _cached_date

    today = date.today()
    if _cached_rankings and _cached_date == today:
        return _cached_rankings

    sector_returns = {}  # sector -> [returns]

    for ticker, df in stock_data.items():
        if len(df) < 20:
            continue

        stock_info = TADAWUL_STOCKS.get(ticker)
        if not stock_info:
            continue

        sector = stock_info["sector"]

        # Calculate 20-day return
        current = float(df["Close"].iloc[-1])
        past = float(df["Close"].iloc[-20])
        if past > 0:
            ret = ((current - past) / past) * 100
            if sector not in sector_returns:
                sector_returns[sector] = []
            sector_returns[sector].append(ret)

    # Calculate average return per sector
    rankings = []
    for sector, returns in sector_returns.items():
        if len(returns) >= 2:  # Need at least 2 stocks to be meaningful
            avg_ret = sum(returns) / len(returns)
            rankings.append({
                "sector": sector,
                "avg_return": round(avg_ret, 2),
                "stock_count": len(returns),
            })

    # Sort by return (best first)
    rankings.sort(key=lambda x: x["avg_return"], reverse=True)

    # Add rank
    for i, r in enumerate(rankings):
        r["rank"] = i + 1

    result = SectorRanking(rankings)

    # Cache
    _cached_rankings = result
    _cached_date = today

    logger.info(f"Sector rankings: top={[r['sector'] for r in rankings[:3]]}, bottom={[r['sector'] for r in rankings[-3:]]}")

    return result

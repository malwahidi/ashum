"""
Market Regime Detection
=======================
Detects if the overall Saudi market (TASI index) is in a crash, correction,
or healthy state. Prevents buying during market-wide selloffs.
"""

import logging
from datetime import date

import pandas as pd

from src.data.fetcher import fetch_tasi_index
from src.analysis.technical import compute_indicators, get_latest_indicators
from config.indicators import RSI_PERIOD

logger = logging.getLogger(__name__)

# Regime thresholds
CRASH_DROP_PCT = 3.0       # TASI drops >3% in 5 days = DANGER
CORRECTION_DROP_PCT = 1.5  # TASI drops >1.5% in 5 days = CAUTION
OVERSOLD_RSI = 30          # TASI RSI <30 = oversold (contrarian opportunity)

# Cached regime (updated once per scan)
_cached_regime = None
_cached_date = None


class MarketRegime:
    """Current state of the overall Saudi market."""

    def __init__(self, status: str, tasi_price: float, tasi_change_5d: float,
                 tasi_rsi: float, description: str):
        self.status = status  # "HEALTHY", "CAUTION", "DANGER", "OVERSOLD"
        self.tasi_price = tasi_price
        self.tasi_change_5d = tasi_change_5d
        self.tasi_rsi = tasi_rsi
        self.description = description

    @property
    def allow_buy(self) -> bool:
        """Should we allow BUY signals?"""
        return self.status in ("HEALTHY", "OVERSOLD")

    @property
    def allow_sell(self) -> bool:
        """Should we allow SELL signals?"""
        return True  # Always allow selling

    @property
    def score_adjustment(self) -> int:
        """Adjust signal score based on market regime."""
        if self.status == "HEALTHY":
            return 0
        elif self.status == "CAUTION":
            return -10  # Reduce buy confidence
        elif self.status == "DANGER":
            return -20  # Strong reduction
        elif self.status == "OVERSOLD":
            return 10  # Contrarian boost for buys
        return 0

    def to_arabic(self) -> str:
        """Arabic description for Telegram."""
        status_map = {
            "HEALTHY": "\U0001f7e2 السوق صحي",
            "CAUTION": "\U0001f7e1 السوق حذر - تراجع طفيف",
            "DANGER": "\U0001f534 السوق خطر - تراجع قوي (لا شراء)",
            "OVERSOLD": "\U0001f7e2 السوق في تشبع بيعي - فرصة شراء محتملة",
        }
        status_text = status_map.get(self.status, self.status)
        return (
            f"{status_text}\n"
            f"  TASI: {self.tasi_price:,.0f} | تغير 5 أيام: {self.tasi_change_5d:+.1f}%\n"
            f"  RSI: {self.tasi_rsi:.0f}"
        )


def detect_market_regime(tasi_df: pd.DataFrame = None) -> MarketRegime:
    """
    Detect current market regime from TASI index data.

    Args:
        tasi_df: Optional pre-fetched TASI DataFrame. If None, fetches fresh data.

    Returns:
        MarketRegime object with status and details.
    """
    global _cached_regime, _cached_date

    # Return cached if same day
    today = date.today()
    if _cached_regime and _cached_date == today:
        return _cached_regime

    # Fetch TASI data
    if tasi_df is None:
        tasi_df = fetch_tasi_index(period="3mo")

    if tasi_df.empty or len(tasi_df) < 20:
        logger.warning("Insufficient TASI data for regime detection")
        return MarketRegime("HEALTHY", 0, 0, 50, "لا توجد بيانات كافية")

    # Compute indicators on TASI
    analyzed = compute_indicators(tasi_df) if len(tasi_df) >= 200 else tasi_df

    # Get current values
    current_price = float(tasi_df["Close"].iloc[-1])

    # Calculate 5-day change
    if len(tasi_df) >= 6:
        price_5d_ago = float(tasi_df["Close"].iloc[-6])
        change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
    else:
        change_5d = 0

    # Get RSI (compute manually if not enough data for full indicators)
    tasi_rsi = 50  # Default
    if len(analyzed) >= 200:
        indicators = get_latest_indicators(analyzed)
        tasi_rsi = indicators.get(f"RSI_{RSI_PERIOD}", 50)
    else:
        # Simple RSI calculation for short data
        from ta.momentum import RSIIndicator
        rsi_calc = RSIIndicator(close=tasi_df["Close"], window=14)
        rsi_values = rsi_calc.rsi()
        if not rsi_values.empty and pd.notna(rsi_values.iloc[-1]):
            tasi_rsi = float(rsi_values.iloc[-1])

    # Determine regime
    if change_5d <= -CRASH_DROP_PCT:
        if tasi_rsi < OVERSOLD_RSI:
            status = "OVERSOLD"
            desc = "السوق تراجع بشدة لكن وصل لمستوى تشبع بيعي - فرصة محتملة"
        else:
            status = "DANGER"
            desc = "السوق يتراجع بقوة - تجنب الشراء حتى يستقر"
    elif change_5d <= -CORRECTION_DROP_PCT:
        status = "CAUTION"
        desc = "السوق يتراجع - كن حذراً في الشراء"
    else:
        status = "HEALTHY"
        desc = "السوق مستقر أو صاعد - ظروف طبيعية للتداول"

    regime = MarketRegime(status, current_price, change_5d, tasi_rsi, desc)

    # Cache
    _cached_regime = regime
    _cached_date = today

    logger.info(f"Market regime: {status} | TASI: {current_price:.0f} | 5d: {change_5d:+.1f}% | RSI: {tasi_rsi:.0f}")

    return regime

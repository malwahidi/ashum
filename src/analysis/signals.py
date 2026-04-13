import logging
from datetime import date

import pandas as pd

from config.indicators import (
    RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, SMA_SHORT, SMA_LONG,
    EMA_FAST, EMA_SLOW, VOLUME_SPIKE_MULTIPLIER,
    SCORE_RSI_MACD, SCORE_TREND, SCORE_BB_BOUNCE,
    SCORE_VOLUME, SCORE_EMA_CROSS,
)
from config.settings import (
    SIGNAL_THRESHOLD, STRONG_THRESHOLD, MODERATE_THRESHOLD,
    STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT,
)
from src.data.tickers import TADAWUL_STOCKS, get_stock_info
from src.analysis.technical import compute_indicators, get_latest_indicators

logger = logging.getLogger(__name__)


def get_signal_grade(strength: int) -> str:
    """Categorize signal strength into a safety grade."""
    if strength >= STRONG_THRESHOLD:
        return "STRONG"
    elif strength >= MODERATE_THRESHOLD:
        return "MODERATE"
    else:
        return "WEAK"


def calculate_stop_loss(price: float, signal_type: str) -> dict:
    """Calculate stop-loss and take-profit levels to protect your money."""
    if signal_type == "BUY":
        stop_loss = round(price * (1 - STOP_LOSS_PERCENT / 100), 2)
        take_profit = round(price * (1 + TAKE_PROFIT_PERCENT / 100), 2)
        max_loss_per_share = round(price - stop_loss, 2)
        max_gain_per_share = round(take_profit - price, 2)
    else:  # SELL
        stop_loss = round(price * (1 + STOP_LOSS_PERCENT / 100), 2)
        take_profit = round(price * (1 - TAKE_PROFIT_PERCENT / 100), 2)
        max_loss_per_share = round(stop_loss - price, 2)
        max_gain_per_share = round(price - take_profit, 2)

    return {
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "max_loss_per_share": max_loss_per_share,
        "max_gain_per_share": max_gain_per_share,
        "risk_reward_ratio": "1:2",
    }


def get_market_status(indicators: dict) -> str:
    """Get a simple plain-English status of a stock."""
    close = indicators.get("close", 0)
    rsi = indicators.get(f"RSI_{RSI_PERIOD}", 50)
    sma_long = indicators.get(f"SMA_{SMA_LONG}", 0)
    ema_fast = indicators.get(f"EMA_{EMA_FAST}", 0)
    ema_slow = indicators.get(f"EMA_{EMA_SLOW}", 0)

    parts = []

    # Trend
    if sma_long and close > sma_long:
        parts.append("Long-term trend: UP")
    elif sma_long:
        parts.append("Long-term trend: DOWN")

    # Short-term momentum
    if ema_fast and ema_slow:
        if ema_fast > ema_slow:
            parts.append("Short-term momentum: Bullish")
        else:
            parts.append("Short-term momentum: Bearish")

    # RSI status
    if rsi < 30:
        parts.append("RSI: Oversold (potential bounce)")
    elif rsi > 70:
        parts.append("RSI: Overbought (potential pullback)")
    elif rsi > 50:
        parts.append("RSI: Healthy")
    else:
        parts.append("RSI: Weak")

    return "\n".join(parts)


def generate_signal(ticker: str, df: pd.DataFrame) -> dict | None:
    """
    Analyze a stock and generate a trading signal.

    Args:
        ticker: Tadawul ticker number
        df: OHLCV DataFrame

    Returns:
        Signal dict or None if score is below threshold.
    """
    if df.empty or len(df) < 200:
        return None

    # Compute all indicators
    analyzed = compute_indicators(df)
    if analyzed.empty:
        return None

    indicators = get_latest_indicators(analyzed)
    if not indicators:
        return None

    # Calculate BUY score
    buy_score = 0
    buy_reasons = []

    sell_score = 0
    sell_reasons = []

    close = indicators.get("close", 0)
    rsi = indicators.get(f"RSI_{RSI_PERIOD}")
    vol_ratio = indicators.get("Volume_Ratio")
    sma_long = indicators.get(f"SMA_{SMA_LONG}")
    bb_lower = indicators.get(f"BBL_{BB_PERIOD}_{BB_STD}")
    bb_upper = indicators.get(f"BBU_{BB_PERIOD}_{BB_STD}")

    sma_short = indicators.get(f"SMA_{SMA_SHORT}")
    ema_fast = indicators.get(f"EMA_{EMA_FAST}")
    ema_slow = indicators.get(f"EMA_{EMA_SLOW}")
    macd_hist = indicators.get(f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}")

    # --- إشارات شراء ---

    # 1. RSI
    if rsi is not None:
        if rsi < RSI_OVERSOLD:
            if indicators.get("MACD_Cross_Up"):
                buy_score += SCORE_RSI_MACD
                buy_reasons.append(f"RSI في منطقة التشبع البيعي ({rsi:.1f}) + تقاطع MACD إيجابي")
            else:
                buy_score += 20
                buy_reasons.append(f"RSI في منطقة التشبع البيعي ({rsi:.1f}) - احتمال ارتداد")
        elif rsi < 40:
            buy_score += 10
            buy_reasons.append(f"RSI منخفض ({rsi:.1f}) - يقترب من التشبع البيعي")

    # 2. السعر فوق متوسط 200
    if sma_long and close > sma_long:
        buy_score += SCORE_TREND
        buy_reasons.append(f"اتجاه صاعد: السعر فوق متوسط {SMA_LONG} يوم")

    # 3. السعر فوق متوسط 50
    if sma_short and close > sma_short:
        buy_score += 10
        buy_reasons.append(f"السعر فوق متوسط {SMA_SHORT} يوم - إيجابي متوسط المدى")

    # 4. زخم إيجابي
    if ema_fast and ema_slow and ema_fast > ema_slow:
        buy_score += 10
        buy_reasons.append(f"زخم صاعد: EMA({EMA_FAST}) أعلى من EMA({EMA_SLOW})")

    # 5. السعر قرب بولنجر السفلي
    if bb_lower and close > 0:
        bb_distance = (close - bb_lower) / close
        if bb_distance < 0.03:
            buy_score += SCORE_BB_BOUNCE
            buy_reasons.append(f"السعر قرب حد بولنجر السفلي (منطقة ارتداد)")

    # 6. ارتفاع الحجم مع صعود
    if vol_ratio and vol_ratio > VOLUME_SPIKE_MULTIPLIER:
        if len(df) >= 2 and df["Close"].iloc[-1] >= df["Close"].iloc[-2]:
            buy_score += SCORE_VOLUME
            buy_reasons.append(f"ارتفاع حجم التداول مع صعود: {vol_ratio:.1f}x من المتوسط")

    # 7. MACD إيجابي
    if macd_hist and macd_hist > 0:
        buy_score += 10
        buy_reasons.append(f"زخم MACD إيجابي")

    # 8. تقاطع EMA اليوم
    if indicators.get("EMA_Cross_Up"):
        buy_score += SCORE_EMA_CROSS
        buy_reasons.append(f"تقاطع EMA({EMA_FAST}) فوق EMA({EMA_SLOW}) اليوم")

    # 9. التقاطع الذهبي
    if indicators.get("Golden_Cross"):
        buy_score += 10
        buy_reasons.append(f"التقاطع الذهبي: متوسط {SMA_SHORT} تجاوز متوسط {SMA_LONG}")

    # --- إشارات بيع ---

    # 1. RSI
    if rsi is not None:
        if rsi > RSI_OVERBOUGHT:
            if indicators.get("MACD_Cross_Down"):
                sell_score += SCORE_RSI_MACD
                sell_reasons.append(f"RSI في منطقة التشبع الشرائي ({rsi:.1f}) + تقاطع MACD سلبي")
            else:
                sell_score += 20
                sell_reasons.append(f"RSI في منطقة التشبع الشرائي ({rsi:.1f}) - احتمال تصحيح")
        elif rsi > 65:
            sell_score += 10
            sell_reasons.append(f"RSI مرتفع ({rsi:.1f}) - يقترب من التشبع الشرائي")

    # 2. السعر تحت متوسط 200
    if sma_long and close < sma_long:
        sell_score += SCORE_TREND
        sell_reasons.append(f"اتجاه هابط: السعر تحت متوسط {SMA_LONG} يوم")

    # 3. السعر تحت متوسط 50
    if sma_short and close < sma_short:
        sell_score += 10
        sell_reasons.append(f"السعر تحت متوسط {SMA_SHORT} يوم - سلبي متوسط المدى")

    # 4. زخم سلبي
    if ema_fast and ema_slow and ema_fast < ema_slow:
        sell_score += 10
        sell_reasons.append(f"زخم هابط: EMA({EMA_FAST}) أقل من EMA({EMA_SLOW})")

    # 5. السعر قرب بولنجر العلوي
    if bb_upper and close > 0:
        bb_distance = (bb_upper - close) / close
        if bb_distance < 0.03:
            sell_score += SCORE_BB_BOUNCE
            sell_reasons.append(f"السعر قرب حد بولنجر العلوي (منطقة تشبع شرائي)")

    # 6. ارتفاع الحجم مع هبوط
    if vol_ratio and vol_ratio > VOLUME_SPIKE_MULTIPLIER:
        if len(df) >= 2 and df["Close"].iloc[-1] < df["Close"].iloc[-2]:
            sell_score += SCORE_VOLUME
            sell_reasons.append(f"بيع بحجم مرتفع: {vol_ratio:.1f}x من المتوسط")

    # 7. MACD سلبي
    if macd_hist and macd_hist < 0:
        sell_score += 10
        sell_reasons.append(f"زخم MACD سلبي")

    # 8. تقاطع EMA سلبي
    if indicators.get("EMA_Cross_Down"):
        sell_score += SCORE_EMA_CROSS
        sell_reasons.append(f"تقاطع EMA({EMA_FAST}) تحت EMA({EMA_SLOW}) اليوم")

    # 9. تقاطع الموت
    if indicators.get("Death_Cross"):
        sell_score += 10
        sell_reasons.append(f"تقاطع الموت: متوسط {SMA_SHORT} كسر متوسط {SMA_LONG}")

    # Determine signal type
    buy_score = int(min(buy_score, 100))
    sell_score = int(min(sell_score, 100))

    stock_info = get_stock_info(ticker) or {}
    market_status = get_market_status(indicators)

    if buy_score >= SIGNAL_THRESHOLD and buy_score > sell_score:
        risk = calculate_stop_loss(close, "BUY")
        return {
            "ticker": ticker,
            "stock_name": stock_info.get("name_ar", stock_info.get("name", ticker)),
            "sector": stock_info.get("sector", "Unknown"),
            "date": date.today(),
            "signal_type": "BUY",
            "strength": buy_score,
            "grade": get_signal_grade(buy_score),
            "price": close,
            "stop_loss": risk["stop_loss"],
            "take_profit": risk["take_profit"],
            "risk_reward": risk["risk_reward_ratio"],
            "market_status": market_status,
            "indicators": indicators,
            "reasons": buy_reasons,
        }
    elif sell_score >= SIGNAL_THRESHOLD and sell_score > buy_score:
        risk = calculate_stop_loss(close, "SELL")
        return {
            "ticker": ticker,
            "stock_name": stock_info.get("name_ar", stock_info.get("name", ticker)),
            "sector": stock_info.get("sector", "Unknown"),
            "date": date.today(),
            "signal_type": "SELL",
            "strength": sell_score,
            "grade": get_signal_grade(sell_score),
            "price": close,
            "stop_loss": risk["stop_loss"],
            "take_profit": risk["take_profit"],
            "risk_reward": risk["risk_reward_ratio"],
            "market_status": market_status,
            "indicators": indicators,
            "reasons": sell_reasons,
        }

    return None


def scan_all_stocks(stock_data: dict[str, pd.DataFrame]) -> list[dict]:
    """
    Scan all stocks and generate signals.

    Args:
        stock_data: Dict mapping ticker -> OHLCV DataFrame

    Returns:
        List of signal dicts, sorted by strength (descending).
    """
    signals = []

    for ticker, df in stock_data.items():
        try:
            signal = generate_signal(ticker, df)
            if signal:
                signals.append(signal)
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            continue

    # Sort by strength (strongest first)
    signals.sort(key=lambda s: s["strength"], reverse=True)

    buy_count = sum(1 for s in signals if s["signal_type"] == "BUY")
    sell_count = sum(1 for s in signals if s["signal_type"] == "SELL")
    logger.info(f"Scan complete: {buy_count} BUY, {sell_count} SELL signals from {len(stock_data)} stocks")

    return signals


def get_top_signals(
    signals: list[dict],
    signal_type: str = "BUY",
    limit: int = 10,
) -> list[dict]:
    """Get top N signals of a given type."""
    filtered = [s for s in signals if s["signal_type"] == signal_type]
    return filtered[:limit]

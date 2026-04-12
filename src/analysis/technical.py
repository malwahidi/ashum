import logging

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

from config.indicators import (
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, SMA_SHORT, SMA_LONG,
    EMA_FAST, EMA_SLOW, VOLUME_AVG_PERIOD,
)

logger = logging.getLogger(__name__)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all technical indicators for a stock DataFrame.

    Args:
        df: DataFrame with columns Open, High, Low, Close, Volume (index=Date)

    Returns:
        DataFrame with all indicator columns added.
    """
    if df.empty or len(df) < SMA_LONG:
        logger.warning(f"Insufficient data: {len(df)} rows (need {SMA_LONG})")
        return df

    result = df.copy()
    close = result["Close"]
    volume = result["Volume"].astype(float)

    # RSI
    rsi = RSIIndicator(close=close, window=RSI_PERIOD)
    result[f"RSI_{RSI_PERIOD}"] = rsi.rsi()

    # MACD
    macd = MACD(close=close, window_slow=MACD_SLOW, window_fast=MACD_FAST, window_sign=MACD_SIGNAL)
    result[f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"] = macd.macd()
    result[f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"] = macd.macd_signal()
    result[f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"] = macd.macd_diff()

    # Bollinger Bands
    bb = BollingerBands(close=close, window=BB_PERIOD, window_dev=BB_STD)
    result[f"BBU_{BB_PERIOD}_{BB_STD}"] = bb.bollinger_hband()
    result[f"BBM_{BB_PERIOD}_{BB_STD}"] = bb.bollinger_mavg()
    result[f"BBL_{BB_PERIOD}_{BB_STD}"] = bb.bollinger_lband()

    # Simple Moving Averages
    result[f"SMA_{SMA_SHORT}"] = SMAIndicator(close=close, window=SMA_SHORT).sma_indicator()
    result[f"SMA_{SMA_LONG}"] = SMAIndicator(close=close, window=SMA_LONG).sma_indicator()

    # Exponential Moving Averages
    result[f"EMA_{EMA_FAST}"] = EMAIndicator(close=close, window=EMA_FAST).ema_indicator()
    result[f"EMA_{EMA_SLOW}"] = EMAIndicator(close=close, window=EMA_SLOW).ema_indicator()

    # Volume Moving Average
    result[f"Volume_SMA_{VOLUME_AVG_PERIOD}"] = SMAIndicator(
        close=volume, window=VOLUME_AVG_PERIOD
    ).sma_indicator()

    # Volume Ratio (current vs average)
    vol_sma_col = f"Volume_SMA_{VOLUME_AVG_PERIOD}"
    result["Volume_Ratio"] = result["Volume"] / result[vol_sma_col]

    # MACD histogram direction change (for crossover detection)
    macd_hist_col = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    if macd_hist_col in result.columns:
        result["MACD_Cross_Up"] = (
            (result[macd_hist_col] > 0) &
            (result[macd_hist_col].shift(1) <= 0)
        )
        result["MACD_Cross_Down"] = (
            (result[macd_hist_col] < 0) &
            (result[macd_hist_col].shift(1) >= 0)
        )

    # EMA Crossover
    ema_fast_col = f"EMA_{EMA_FAST}"
    ema_slow_col = f"EMA_{EMA_SLOW}"
    result["EMA_Cross_Up"] = (
        (result[ema_fast_col] > result[ema_slow_col]) &
        (result[ema_fast_col].shift(1) <= result[ema_slow_col].shift(1))
    )
    result["EMA_Cross_Down"] = (
        (result[ema_fast_col] < result[ema_slow_col]) &
        (result[ema_fast_col].shift(1) >= result[ema_slow_col].shift(1))
    )

    # Golden Cross / Death Cross (SMA 50/200)
    sma_short_col = f"SMA_{SMA_SHORT}"
    sma_long_col = f"SMA_{SMA_LONG}"
    result["Golden_Cross"] = (
        (result[sma_short_col] > result[sma_long_col]) &
        (result[sma_short_col].shift(1) <= result[sma_long_col].shift(1))
    )
    result["Death_Cross"] = (
        (result[sma_short_col] < result[sma_long_col]) &
        (result[sma_short_col].shift(1) >= result[sma_long_col].shift(1))
    )

    return result


def get_latest_indicators(df: pd.DataFrame) -> dict:
    """
    Extract the latest indicator values from a computed DataFrame.

    Returns:
        Dict with all current indicator values.
    """
    if df.empty:
        return {}

    last = df.iloc[-1]

    indicators = {
        "close": round(last["Close"], 2),
        "volume": int(last["Volume"]) if pd.notna(last["Volume"]) else 0,
    }

    # Extract indicator values safely
    indicator_keys = [
        f"RSI_{RSI_PERIOD}",
        f"SMA_{SMA_SHORT}", f"SMA_{SMA_LONG}",
        f"EMA_{EMA_FAST}", f"EMA_{EMA_SLOW}",
        "Volume_Ratio",
        f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
        f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
        f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
        f"BBL_{BB_PERIOD}_{BB_STD}", f"BBM_{BB_PERIOD}_{BB_STD}",
        f"BBU_{BB_PERIOD}_{BB_STD}",
    ]

    for key in indicator_keys:
        if key in last.index and pd.notna(last[key]):
            indicators[key] = round(float(last[key]), 4)

    # Boolean crossovers
    for key in ["MACD_Cross_Up", "MACD_Cross_Down",
                "EMA_Cross_Up", "EMA_Cross_Down",
                "Golden_Cross", "Death_Cross"]:
        if key in last.index:
            indicators[key] = bool(last[key])

    return indicators

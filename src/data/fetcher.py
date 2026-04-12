import logging
from datetime import date

import pandas as pd
import yfinance as yf

from src.data.tickers import TADAWUL_STOCKS, get_yf_ticker, TASI_INDEX
from config.settings import HISTORY_PERIOD

logger = logging.getLogger(__name__)


def fetch_stock_history(ticker: str, period: str = HISTORY_PERIOD) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a single Tadawul stock.

    Args:
        ticker: Tadawul ticker number (e.g., "2222")
        period: yfinance period string (e.g., "1y", "2y", "max")

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    yf_ticker = get_yf_ticker(ticker)
    try:
        stock = yf.Ticker(yf_ticker)
        df = stock.history(period=period)
        if df.empty:
            logger.warning(f"No data returned for {yf_ticker}")
            return pd.DataFrame()

        # Clean up: remove timezone info, keep only OHLCV
        df.index = df.index.tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.index.name = "Date"
        return df

    except Exception as e:
        logger.error(f"Error fetching {yf_ticker}: {e}")
        return pd.DataFrame()


def fetch_multiple_stocks(
    tickers: list[str] | None = None,
    period: str = HISTORY_PERIOD
) -> dict[str, pd.DataFrame]:
    """
    Fetch historical data for multiple stocks.

    Args:
        tickers: List of Tadawul ticker numbers. None = all stocks.
        period: yfinance period string.

    Returns:
        Dict mapping ticker -> DataFrame
    """
    if tickers is None:
        tickers = list(TADAWUL_STOCKS.keys())

    results = {}
    yf_tickers = [get_yf_ticker(t) for t in tickers]

    logger.info(f"Fetching {len(yf_tickers)} stocks...")

    try:
        # Batch download is much faster than individual requests
        data = yf.download(
            yf_tickers,
            period=period,
            group_by="ticker",
            threads=True,
            progress=False,
        )

        if data.empty:
            logger.warning("Batch download returned empty data")
            return results

        for ticker in tickers:
            yf_t = get_yf_ticker(ticker)
            try:
                if len(yf_tickers) == 1:
                    df = data[["Open", "High", "Low", "Close", "Volume"]].copy()
                else:
                    df = data[yf_t][["Open", "High", "Low", "Close", "Volume"]].copy()

                df = df.dropna(how="all")
                if not df.empty:
                    if df.index.tz is not None:
                        df.index = df.index.tz_localize(None)
                    results[ticker] = df
            except (KeyError, TypeError):
                logger.warning(f"No data for {ticker} in batch result")
                continue

    except Exception as e:
        logger.error(f"Batch download failed: {e}. Falling back to individual fetch.")
        for ticker in tickers:
            df = fetch_stock_history(ticker, period)
            if not df.empty:
                results[ticker] = df

    logger.info(f"Successfully fetched {len(results)}/{len(tickers)} stocks")
    return results


def fetch_tasi_index(period: str = HISTORY_PERIOD) -> pd.DataFrame:
    """Fetch TASI index data."""
    try:
        tasi = yf.Ticker(TASI_INDEX)
        df = tasi.history(period=period)
        if not df.empty:
            df.index = df.index.tz_localize(None)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
        return df
    except Exception as e:
        logger.error(f"Error fetching TASI index: {e}")
        return pd.DataFrame()


def get_latest_price(ticker: str) -> dict | None:
    """Get the latest price info for a stock."""
    yf_t = get_yf_ticker(ticker)
    try:
        stock = yf.Ticker(yf_t)
        info = stock.info
        return {
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange"),
            "change_pct": info.get("regularMarketChangePercent"),
            "volume": info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
        }
    except Exception as e:
        logger.error(f"Error getting latest price for {ticker}: {e}")
        return None

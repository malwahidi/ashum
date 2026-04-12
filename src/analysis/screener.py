import logging
from datetime import date, datetime

from src.data.fetcher import fetch_multiple_stocks
from src.data.tickers import TADAWUL_STOCKS
from src.data.repository import save_signal, save_scan_result
from src.analysis.signals import scan_all_stocks, get_top_signals
from config.settings import TOP_SIGNALS_COUNT, HISTORY_PERIOD

logger = logging.getLogger(__name__)


def run_market_scan(
    tickers: list[str] | None = None,
    period: str = HISTORY_PERIOD,
    save_to_db: bool = True,
) -> dict:
    """
    Run a full market scan: fetch data, analyze, generate signals.

    Args:
        tickers: List of tickers to scan. None = all Tadawul stocks.
        period: History period for analysis.
        save_to_db: Whether to persist results to database.

    Returns:
        Dict with scan results: top_buys, top_sells, all_signals, stats.
    """
    if tickers is None:
        tickers = list(TADAWUL_STOCKS.keys())

    logger.info(f"Starting market scan: {len(tickers)} stocks, period={period}")

    # 1. Fetch data
    stock_data = fetch_multiple_stocks(tickers, period=period)
    if not stock_data:
        logger.error("No stock data fetched. Scan aborted.")
        return {"top_buys": [], "top_sells": [], "all_signals": [], "stats": {}}

    # 2. Generate signals
    all_signals = scan_all_stocks(stock_data)

    # 3. Get top signals
    top_buys = get_top_signals(all_signals, "BUY", TOP_SIGNALS_COUNT)
    top_sells = get_top_signals(all_signals, "SELL", TOP_SIGNALS_COUNT)

    # 4. Save to database
    if save_to_db:
        for signal in all_signals:
            save_signal(signal)

        save_scan_result({
            "date": date.today(),
            "scan_time": datetime.utcnow(),
            "total_stocks": len(stock_data),
            "buy_signals": sum(1 for s in all_signals if s["signal_type"] == "BUY"),
            "sell_signals": sum(1 for s in all_signals if s["signal_type"] == "SELL"),
            "top_buys": [
                {"ticker": s["ticker"], "name": s["stock_name"],
                 "strength": s["strength"], "price": s["price"]}
                for s in top_buys
            ],
            "top_sells": [
                {"ticker": s["ticker"], "name": s["stock_name"],
                 "strength": s["strength"], "price": s["price"]}
                for s in top_sells
            ],
        })

    stats = {
        "total_scanned": len(stock_data),
        "total_signals": len(all_signals),
        "buy_signals": sum(1 for s in all_signals if s["signal_type"] == "BUY"),
        "sell_signals": sum(1 for s in all_signals if s["signal_type"] == "SELL"),
        "scan_time": datetime.now().isoformat(),
    }

    logger.info(
        f"Scan complete: {stats['buy_signals']} BUY, "
        f"{stats['sell_signals']} SELL from {stats['total_scanned']} stocks"
    )

    return {
        "top_buys": top_buys,
        "top_sells": top_sells,
        "all_signals": all_signals,
        "stats": stats,
    }


def scan_single_stock(ticker: str, period: str = HISTORY_PERIOD) -> dict | None:
    """Quick scan of a single stock."""
    from src.data.fetcher import fetch_stock_history
    from src.analysis.signals import generate_signal

    df = fetch_stock_history(ticker, period)
    if df.empty:
        return None

    return generate_signal(ticker, df)

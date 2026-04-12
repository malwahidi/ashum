import logging
from datetime import date, datetime

from src.data.fetcher import fetch_multiple_stocks
from src.data.tickers import TADAWUL_STOCKS, get_naqi_tickers
from src.data.repository import save_signal, save_scan_result
from src.analysis.signals import scan_all_stocks, get_top_signals
from src.analysis.market_regime import detect_market_regime
from src.analysis.sectors import calculate_sector_rankings
from config.settings import TOP_SIGNALS_COUNT, HISTORY_PERIOD

logger = logging.getLogger(__name__)


def run_market_scan(
    tickers: list[str] | None = None,
    period: str = HISTORY_PERIOD,
    save_to_db: bool = True,
) -> dict:
    """
    Run a full market scan with AI intelligence layers:
    1. Detect market regime (crash/healthy)
    2. Calculate sector strength rankings
    3. Generate signals with adjustments

    Returns:
        Dict with scan results + market_regime + sector_ranking.
    """
    if tickers is None:
        tickers = get_naqi_tickers()  # Only pure stocks (Al-Osaimi)

    logger.info(f"Starting smart scan (naqi only): {len(tickers)} stocks")

    # 1. Fetch data
    stock_data = fetch_multiple_stocks(tickers, period=period)
    if not stock_data:
        logger.error("No stock data fetched. Scan aborted.")
        return {"top_buys": [], "top_sells": [], "all_signals": [], "stats": {}}

    # 2. Detect market regime (TASI analysis)
    market_regime = detect_market_regime()

    # 3. Calculate sector rankings
    sector_ranking = calculate_sector_rankings(stock_data)

    # 4. Generate signals with intelligence layers
    all_signals = scan_all_stocks(stock_data)

    # 5. Apply market regime filter
    if not market_regime.allow_buy:
        # Block BUY signals during market danger
        before_count = len(all_signals)
        all_signals = [s for s in all_signals if s["signal_type"] != "BUY"]
        blocked = before_count - len(all_signals)
        if blocked > 0:
            logger.info(f"Market regime DANGER: blocked {blocked} BUY signals")

    # 6. Apply sector + regime score adjustments
    for signal in all_signals:
        sector = signal.get("sector", "")

        # Sector adjustment
        sector_adj = sector_ranking.get_score_adjustment(sector)
        if sector_adj != 0:
            signal["strength"] = max(0, min(100, signal["strength"] + sector_adj))
            sector_str = sector_ranking.get_strength(sector)
            if sector_adj > 0:
                signal["reasons"].append(f"قطاع قوي: {sector} ({sector_str})")
            else:
                signal["reasons"].append(f"قطاع ضعيف: {sector} ({sector_str})")

        # Market regime adjustment
        regime_adj = market_regime.score_adjustment
        if regime_adj != 0 and signal["signal_type"] == "BUY":
            signal["strength"] = max(0, min(100, signal["strength"] + regime_adj))

        # Update grade after adjustments
        from src.analysis.signals import get_signal_grade
        signal["grade"] = get_signal_grade(signal["strength"])

    # Re-sort after adjustments
    all_signals.sort(key=lambda s: s["strength"], reverse=True)

    # 7. Get top signals
    top_buys = get_top_signals(all_signals, "BUY", TOP_SIGNALS_COUNT)
    top_sells = get_top_signals(all_signals, "SELL", TOP_SIGNALS_COUNT)

    # 8. Save to database
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
        f"Smart scan complete: {stats['buy_signals']} BUY, "
        f"{stats['sell_signals']} SELL | Market: {market_regime.status}"
    )

    return {
        "top_buys": top_buys,
        "top_sells": top_sells,
        "all_signals": all_signals,
        "stats": stats,
        "market_regime": market_regime,
        "sector_ranking": sector_ranking,
    }


def scan_single_stock(ticker: str, period: str = HISTORY_PERIOD) -> dict | None:
    """Quick scan of a single stock."""
    from src.data.fetcher import fetch_stock_history
    from src.analysis.signals import generate_signal

    df = fetch_stock_history(ticker, period)
    if df.empty:
        return None

    return generate_signal(ticker, df)

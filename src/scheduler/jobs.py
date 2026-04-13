import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import (
    MARKET_TIMEZONE, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR,
    SCAN_DELAY_MINUTES, INTRADAY_INTERVAL_MINUTES,
)

logger = logging.getLogger(__name__)


# Trading rules
MAX_BUYS_PER_DAY = 3
MAX_OPEN_POSITIONS = 5
MIN_GRADE = "STRONG"  # Only buy STRONG signals (70+)

# Track daily buys to enforce limit
_today_buys = {"date": None, "count": 0, "tickers_sold_today": set()}


def _can_buy_today() -> bool:
    """Check if we can still buy today."""
    from datetime import date
    today = date.today()
    if _today_buys["date"] != today:
        _today_buys["date"] = today
        _today_buys["count"] = 0
        _today_buys["tickers_sold_today"] = set()
    return _today_buys["count"] < MAX_BUYS_PER_DAY


def _record_buy():
    _today_buys["count"] += 1


def _record_sell(ticker: str):
    _today_buys["tickers_sold_today"].add(ticker)


def _was_sold_today(ticker: str) -> bool:
    from datetime import date
    if _today_buys["date"] != date.today():
        return False
    return ticker in _today_buys["tickers_sold_today"]


async def _auto_buy_strong_signals(result: dict):
    """
    Intelligent auto-buy: STRONG signals only, max 3/day, max 5 total.
    Works for both morning and intraday scans.
    """
    from src.trading.paper_trader import open_trade, get_portfolio

    portfolio = get_portfolio()
    open_count = portfolio["num_positions"]

    top_buys = result.get("top_buys", [])
    strong_buys = [s for s in top_buys if s.get("grade") == MIN_GRADE]

    if not strong_buys:
        return 0

    opened = 0
    for signal in strong_buys:
        # Check all limits
        if not _can_buy_today():
            break
        if open_count + opened >= MAX_OPEN_POSITIONS:
            break
        if _was_sold_today(signal["ticker"]):
            continue  # Don't rebuy a stock sold today

        trade = open_trade(signal)
        if trade:
            opened += 1
            _record_buy()

    if opened > 0:
        from src.notifications.telegram import send_message
        await send_message(
            f"\U0001f4bc <b>تم فتح {opened} صفقة افتراضية (إشارات قوية فقط)</b>\n"
            f"اكتب /portfolio للتفاصيل."
        )

    return opened


async def morning_scan_job():
    """Run after market open — full market scan with notifications."""
    logger.info("Running morning scan job...")
    try:
        from src.analysis.screener import run_market_scan
        from src.data.fetcher import fetch_multiple_stocks
        from src.notifications.telegram import send_scan_results

        result = run_market_scan()

        # Fetch data for charts
        top_tickers = [s["ticker"] for s in result.get("top_buys", [])[:3]]
        stock_data = {}
        if top_tickers:
            stock_data = fetch_multiple_stocks(top_tickers, period="6mo")

        await send_scan_results(result, stock_data)

        # Auto-buy STRONG signals only
        await _auto_buy_strong_signals(result)

        # Check if naqi list needs updating
        from src.data.tickers import check_naqi_update_needed
        naqi_reminder = check_naqi_update_needed()
        if naqi_reminder:
            from src.notifications.telegram import send_message
            await send_message(naqi_reminder)

        logger.info("Morning scan completed and sent.")

    except Exception as e:
        logger.error(f"Morning scan failed: {e}", exc_info=True)


async def intraday_scan_job():
    """Run during market hours — check positions + auto-buy new STRONG signals."""
    logger.info("Running intraday scan job...")
    try:
        # 1. Check paper trading positions for SL/TP
        from src.trading.paper_trader import check_positions
        closed = check_positions()
        if closed:
            from src.notifications.telegram import send_message
            for trade in closed:
                icon = "\U0001f7e2" if trade["final_pnl"] > 0 else "\U0001f534"
                _record_sell(trade["ticker"])
                await send_message(
                    f"{icon} <b>صفقة افتراضية مغلقة:</b> {trade['ticker']}\n"
                    f"السبب: {trade['exit_reason']}\n"
                    f"P&L: {trade['final_pnl']:+,.0f} ريال ({trade['final_pnl_pct']:+.1f}%)"
                )

        # 2. Scan for new signals
        from src.analysis.screener import run_market_scan
        result = run_market_scan(save_to_db=True)

        # 3. Auto-buy new STRONG signals (same rules as morning)
        opened = await _auto_buy_strong_signals(result)

        # 4. Notify about strong signals even if not bought (at max positions)
        strong_buys = [s for s in result.get("all_signals", [])
                       if s["strength"] >= 70 and s["signal_type"] == "BUY"]
        strong_sells = [s for s in result.get("all_signals", [])
                        if s["strength"] >= 70 and s["signal_type"] == "SELL"]

        if strong_buys or strong_sells:
            from src.notifications.telegram import send_message
            msg = f"\u26a1 <b>إشارات قوية ({len(strong_buys)} شراء، {len(strong_sells)} بيع):</b>\n\n"
            for s in (strong_buys + strong_sells)[:5]:
                icon = "\U0001f7e2" if s["signal_type"] == "BUY" else "\U0001f534"
                action = "شراء" if s["signal_type"] == "BUY" else "بيع"
                msg += f"{icon} <b>{s['ticker']}</b> ({s.get('stock_name', '')}) — {action} [{s['strength']}/100]\n"
            await send_message(msg)

        logger.info(f"Intraday: {len(strong_buys)} strong buys, {opened} auto-bought")

    except Exception as e:
        logger.error(f"Intraday scan failed: {e}", exc_info=True)


async def end_of_day_job():
    """Run after market close — daily summary."""
    logger.info("Running end-of-day summary job...")
    try:
        from src.data.repository import get_latest_signals
        from src.notifications.telegram import send_message

        today_signals = get_latest_signals(limit=50)

        buy_count = sum(1 for s in today_signals if s["signal_type"] == "BUY")
        sell_count = sum(1 for s in today_signals if s["signal_type"] == "SELL")

        msg = (
            f"\U0001f4ca <b>End of Day Summary</b>\n"
            f"\U0001f4c5 {datetime.now().strftime('%Y-%m-%d')}\n"
            f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"\U0001f7e2 Buy signals today: {buy_count}\n"
            f"\U0001f534 Sell signals today: {sell_count}\n\n"
            f"\U0001f6d1 Market closed. See you tomorrow!\n"
            f"\u26a0\ufe0f <i>Not financial advice.</i>"
        )

        await send_message(msg)
        logger.info("End-of-day summary sent.")

    except Exception as e:
        logger.error(f"End-of-day job failed: {e}", exc_info=True)


def create_scheduler() -> AsyncIOScheduler:
    """
    Create APScheduler with all trading jobs.

    Tadawul hours: Sun-Thu, 10:00 AM - 3:00 PM (Asia/Riyadh)
    """
    scheduler = AsyncIOScheduler(timezone=MARKET_TIMEZONE)

    # Morning scan: 15 min after market open (10:15 AM, Sun-Thu)
    scheduler.add_job(
        morning_scan_job,
        CronTrigger(
            day_of_week="sun,mon,tue,wed,thu",
            hour=MARKET_OPEN_HOUR,
            minute=SCAN_DELAY_MINUTES,
            timezone=MARKET_TIMEZONE,
        ),
        id="morning_scan",
        name="Morning Market Scan",
        replace_existing=True,
    )

    # Intraday scans: every 30 min from 10:30 to 14:30
    scheduler.add_job(
        intraday_scan_job,
        CronTrigger(
            day_of_week="sun,mon,tue,wed,thu",
            hour=f"{MARKET_OPEN_HOUR}-{MARKET_CLOSE_HOUR - 1}",
            minute=f"0,{INTRADAY_INTERVAL_MINUTES}",
            timezone=MARKET_TIMEZONE,
        ),
        id="intraday_scan",
        name="Intraday Scan",
        replace_existing=True,
    )

    # End of day: 15 min after market close (3:15 PM)
    scheduler.add_job(
        end_of_day_job,
        CronTrigger(
            day_of_week="sun,mon,tue,wed,thu",
            hour=MARKET_CLOSE_HOUR,
            minute=SCAN_DELAY_MINUTES,
            timezone=MARKET_TIMEZONE,
        ),
        id="end_of_day",
        name="End of Day Summary",
        replace_existing=True,
    )

    return scheduler

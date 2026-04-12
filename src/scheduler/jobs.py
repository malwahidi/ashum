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


async def morning_scan_job():
    """Run after market open — full market scan with notifications."""
    logger.info("Running morning scan job...")
    try:
        from src.analysis.screener import run_market_scan
        from src.data.fetcher import fetch_multiple_stocks
        from src.notifications.telegram import send_scan_results

        result = run_market_scan()

        # Fetch data again for charts (or reuse from scan)
        top_tickers = [s["ticker"] for s in result.get("top_buys", [])[:3]]
        stock_data = {}
        if top_tickers:
            from src.data.fetcher import fetch_multiple_stocks
            stock_data = fetch_multiple_stocks(top_tickers, period="6mo")

        await send_scan_results(result, stock_data)

        # Auto-open paper trades for top BUY signals
        from src.trading.paper_trader import open_trade
        top_buys = result.get("top_buys", [])
        opened = 0
        for signal in top_buys[:3]:  # Top 3 BUY signals
            if signal.get("grade") in ("STRONG", "MODERATE"):
                trade = open_trade(signal)
                if trade:
                    opened += 1
        if opened > 0:
            from src.notifications.telegram import send_message
            await send_message(f"\U0001f4bc تم فتح {opened} صفقة افتراضية تلقائياً. اكتب /portfolio للتفاصيل.")

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
    """Run during market hours — check for new signals + paper positions."""
    logger.info("Running intraday scan job...")
    try:
        # Check paper trading positions
        from src.trading.paper_trader import check_positions
        closed = check_positions()
        if closed:
            from src.notifications.telegram import send_message
            for trade in closed:
                icon = "\U0001f7e2" if trade["final_pnl"] > 0 else "\U0001f534"
                await send_message(
                    f"{icon} <b>صفقة افتراضية مغلقة:</b> {trade['ticker']}.SR\n"
                    f"السبب: {trade['exit_reason']}\n"
                    f"P&L: {trade['final_pnl']:+,.0f} ريال ({trade['final_pnl_pct']:+.1f}%)"
                )

        from src.analysis.screener import run_market_scan
        from src.notifications.telegram import send_message

        result = run_market_scan(save_to_db=True)

        # Only notify for very strong signals (>= 75)
        strong_signals = [
            s for s in result.get("all_signals", [])
            if s["strength"] >= 75
        ]

        if strong_signals:
            from src.notifications.telegram import send_message
            header = f"\u26a1 <b>Strong signals detected ({len(strong_signals)}):</b>\n\n"
            for s in strong_signals[:5]:
                icon = "\U0001f7e2" if s["signal_type"] == "BUY" else "\U0001f534"
                header += (
                    f"{icon} <b>{s['ticker']}.SR</b> ({s.get('stock_name', '')}) "
                    f"- {s['strength']}/100\n"
                )
            await send_message(header)

        logger.info(f"Intraday scan: {len(strong_signals)} strong signals")

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

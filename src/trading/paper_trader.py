"""
Paper Trading — Virtual Trade Tracking
=======================================
Tracks signals as virtual trades with virtual 100K SAR.
Stores everything in a simple JSON file.
"""

import json
import logging
import os
from datetime import date, datetime
from pathlib import Path

from config.settings import STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, MAX_HOLDING_DAYS

logger = logging.getLogger(__name__)

TRADES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "paper_trades.json")
INITIAL_CAPITAL = 100_000  # 100K SAR virtual
MAX_POSITIONS = 5  # Max simultaneous virtual positions
POSITION_SIZE_PCT = 10  # 10% of capital per trade


def _load_data() -> dict:
    """Load trades data from JSON file."""
    if os.path.exists(TRADES_FILE):
        try:
            with open(TRADES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "capital": INITIAL_CAPITAL,
        "open_positions": [],
        "closed_trades": [],
        "transaction_log": [],
        "total_pnl": 0,
    }


def _save_data(data: dict):
    """Save trades data to JSON file."""
    try:
        with open(TRADES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save trades: {e}")


def open_trade(signal: dict) -> dict | None:
    """
    Open a virtual trade based on a signal.
    Returns trade dict or None if can't open.
    """
    data = _load_data()

    # Check max positions
    if len(data["open_positions"]) >= MAX_POSITIONS:
        return None

    # Check if already in this stock
    for pos in data["open_positions"]:
        if pos["ticker"] == signal["ticker"]:
            return None

    price = signal.get("price", 0)
    if price <= 0:
        return None

    position_size = data["capital"] * (POSITION_SIZE_PCT / 100)
    shares = int(position_size / price)
    if shares <= 0:
        return None

    trade = {
        "ticker": signal["ticker"],
        "stock_name": signal.get("stock_name", signal["ticker"]),
        "signal_type": signal.get("signal_type", "BUY"),
        "strength": signal.get("strength", 0),
        "grade": signal.get("grade", "WEAK"),
        "entry_price": price,
        "entry_date": str(date.today()),
        "shares": shares,
        "position_value": round(shares * price, 2),
        "stop_loss": signal.get("stop_loss", round(price * 0.97, 2)),
        "take_profit": signal.get("take_profit", round(price * 1.06, 2)),
        "current_price": price,
        "current_pnl": 0,
        "current_pnl_pct": 0,
    }

    data["open_positions"].append(trade)

    # Log transaction
    if "transaction_log" not in data:
        data["transaction_log"] = []
    data["transaction_log"].append({
        "action": "شراء",
        "ticker": signal["ticker"],
        "stock_name": signal.get("stock_name", signal["ticker"]),
        "price": price,
        "shares": shares,
        "strength": signal.get("strength", 0),
        "grade": signal.get("grade", ""),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    _save_data(data)

    logger.info(f"Paper trade opened: {signal['signal_type']} {signal['ticker']} @ {price}")
    return trade


def check_positions() -> list[dict]:
    """
    Check all open positions against current prices.
    Closes positions that hit SL, TP, or max holding days.
    Returns list of closed trades.
    """
    from src.data.fetcher import get_latest_price

    data = _load_data()
    closed = []
    still_open = []

    for pos in data["open_positions"]:
        ticker = pos["ticker"]

        # Get current price
        latest = get_latest_price(ticker)
        if not latest or not latest.get("price"):
            still_open.append(pos)
            continue

        current_price = latest["price"]
        entry_price = pos["entry_price"]
        shares = pos["shares"]

        # Update current values
        if pos["signal_type"] == "BUY":
            pnl = (current_price - entry_price) * shares
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl = (entry_price - current_price) * shares
            pnl_pct = ((entry_price - current_price) / entry_price) * 100

        pos["current_price"] = current_price
        pos["current_pnl"] = round(pnl, 2)
        pos["current_pnl_pct"] = round(pnl_pct, 2)

        # Check exit conditions
        entry_date = datetime.strptime(pos["entry_date"], "%Y-%m-%d").date()
        days_held = (date.today() - entry_date).days
        exit_reason = None

        if pos["signal_type"] == "BUY":
            if current_price <= pos["stop_loss"]:
                exit_reason = "وقف الخسارة"
            elif current_price >= pos["take_profit"]:
                exit_reason = "وصل الهدف"
            elif days_held >= MAX_HOLDING_DAYS:
                exit_reason = "انتهاء المدة"
        else:
            if current_price >= pos["stop_loss"]:
                exit_reason = "وقف الخسارة"
            elif current_price <= pos["take_profit"]:
                exit_reason = "وصل الهدف"
            elif days_held >= MAX_HOLDING_DAYS:
                exit_reason = "انتهاء المدة"

        if exit_reason:
            closed_trade = {
                **pos,
                "exit_price": current_price,
                "exit_date": str(date.today()),
                "exit_reason": exit_reason,
                "final_pnl": round(pnl, 2),
                "final_pnl_pct": round(pnl_pct, 2),
                "days_held": days_held,
            }
            closed.append(closed_trade)
            data["closed_trades"].append(closed_trade)
            data["total_pnl"] = round(data["total_pnl"] + pnl, 2)
            data["capital"] = round(data["capital"] + pnl, 2)

            # Log transaction
            if "transaction_log" not in data:
                data["transaction_log"] = []
            data["transaction_log"].append({
                "action": "بيع",
                "ticker": ticker,
                "stock_name": pos.get("stock_name", ticker),
                "price": current_price,
                "shares": shares,
                "reason": exit_reason,
                "pnl": round(pnl, 2),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

            logger.info(f"Paper trade closed: {ticker} {exit_reason} P&L: {pnl:+.0f}")
        else:
            still_open.append(pos)

    data["open_positions"] = still_open
    _save_data(data)

    return closed


def get_portfolio() -> dict:
    """Get current portfolio status."""
    data = _load_data()

    total_invested = sum(p["position_value"] for p in data["open_positions"])
    total_unrealized = sum(p.get("current_pnl", 0) for p in data["open_positions"])

    return {
        "capital": data["capital"],
        "open_positions": data["open_positions"],
        "num_positions": len(data["open_positions"]),
        "total_invested": round(total_invested, 2),
        "total_unrealized_pnl": round(total_unrealized, 2),
        "portfolio_value": round(data["capital"] + total_unrealized, 2),
    }


def get_performance() -> dict:
    """Get overall trading performance."""
    data = _load_data()
    closed = data["closed_trades"]

    if not closed:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "total_return_pct": 0,
            "capital": data["capital"],
            "open_positions": len(data["open_positions"]),
        }

    wins = [t for t in closed if t["final_pnl"] > 0]
    losses = [t for t in closed if t["final_pnl"] <= 0]

    return {
        "total_trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins) / len(closed) * 100, 1),
        "total_pnl": data["total_pnl"],
        "total_return_pct": round(data["total_pnl"] / INITIAL_CAPITAL * 100, 1),
        "avg_win": round(sum(t["final_pnl"] for t in wins) / len(wins), 0) if wins else 0,
        "avg_loss": round(sum(t["final_pnl"] for t in losses) / len(losses), 0) if losses else 0,
        "best_trade": max(closed, key=lambda t: t["final_pnl"]) if closed else None,
        "worst_trade": min(closed, key=lambda t: t["final_pnl"]) if closed else None,
        "capital": data["capital"],
        "initial_capital": INITIAL_CAPITAL,
        "open_positions": len(data["open_positions"]),
    }


def format_portfolio_arabic() -> str:
    """Format portfolio for Telegram in Arabic."""
    portfolio = get_portfolio()

    msg = (
        f"\U0001f4bc <b>المحفظة الافتراضية</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4b0 رأس المال: {portfolio['capital']:,.0f} ريال\n"
        f"\U0001f4ca قيمة المحفظة: {portfolio['portfolio_value']:,.0f} ريال\n"
        f"\U0001f4c8 الربح/الخسارة غير المحققة: {portfolio['total_unrealized_pnl']:+,.0f} ريال\n"
        f"\U0001f4cb الصفقات المفتوحة: {portfolio['num_positions']}/{MAX_POSITIONS}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    )

    if portfolio["open_positions"]:
        for i, pos in enumerate(portfolio["open_positions"], 1):
            pnl = pos.get("current_pnl", 0)
            pnl_pct = pos.get("current_pnl_pct", 0)
            icon = "\U0001f7e2" if pnl >= 0 else "\U0001f534"

            msg += (
                f"{icon} <b>{pos['ticker']}</b> ({pos['stock_name']})\n"
                f"  {pos['signal_type']} | دخول: {pos['entry_price']:.2f}\n"
                f"  الحالي: {pos.get('current_price', pos['entry_price']):.2f} | "
                f"P&L: {pnl:+,.0f} ({pnl_pct:+.1f}%)\n"
                f"  وقف: {pos['stop_loss']:.2f} | هدف: {pos['take_profit']:.2f}\n\n"
            )
    else:
        msg += "\U0001f4a4 لا توجد صفقات مفتوحة حالياً\n\n"

    msg += "<i>هذه محفظة افتراضية للتجربة — لا تستخدم أموال حقيقية.</i>"
    return msg


def format_performance_arabic() -> str:
    """Format performance stats for Telegram in Arabic."""
    perf = get_performance()

    if perf["total_trades"] == 0:
        return (
            "\U0001f4ca <b>أداء التداول الافتراضي</b>\n\n"
            "لا توجد صفقات مغلقة بعد.\n"
            "البوت سيبدأ التداول الافتراضي مع أول مسح للسوق.\n\n"
            f"\U0001f4bc صفقات مفتوحة: {perf['open_positions']}\n"
            f"\U0001f4b0 رأس المال: {perf['capital']:,.0f} ريال"
        )

    pnl_icon = "\U0001f7e2" if perf["total_pnl"] >= 0 else "\U0001f534"

    msg = (
        f"\U0001f4ca <b>أداء التداول الافتراضي</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"{pnl_icon} الربح/الخسارة الكلي: <b>{perf['total_pnl']:+,.0f} ريال</b> ({perf['total_return_pct']:+.1f}%)\n"
        f"\U0001f4b0 رأس المال: {perf['initial_capital']:,.0f} → {perf['capital']:,.0f} ريال\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4c8 إجمالي الصفقات: {perf['total_trades']}\n"
        f"\U0001f7e2 رابحة: {perf['wins']}\n"
        f"\U0001f534 خاسرة: {perf['losses']}\n"
        f"\U0001f3af نسبة الفوز: <b>{perf['win_rate']}%</b>\n"
        f"\U0001f4b5 متوسط الربح: {perf['avg_win']:+,.0f} ريال\n"
        f"\U0001f4b8 متوسط الخسارة: {perf['avg_loss']:+,.0f} ريال\n"
    )

    best = perf.get("best_trade")
    worst = perf.get("worst_trade")
    if best:
        msg += f"\U0001f947 أفضل صفقة: {best['ticker']} ({best['final_pnl']:+,.0f} ريال)\n"
    if worst:
        msg += f"\U0001f4a5 أسوأ صفقة: {worst['ticker']} ({worst['final_pnl']:+,.0f} ريال)\n"

    msg += (
        f"\n\U0001f4bc صفقات مفتوحة: {perf['open_positions']}\n\n"
        f"<i>هذه نتائج افتراضية — لا تمثل أداء حقيقي.</i>"
    )

    return msg

"""
Performance metrics for backtesting results.
"""

import math


def calculate_metrics(trades: list, initial_capital: float) -> dict:
    """
    Calculate comprehensive performance metrics from trade results.

    Args:
        trades: List of Trade objects (with .pnl, .pnl_pct, etc.)
        initial_capital: Starting capital in SAR

    Returns:
        Dict with all performance metrics.
    """
    if not trades:
        return _empty_metrics()

    # Basic counts
    total_trades = len(trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    win_count = len(wins)
    loss_count = len(losses)

    # Win rate
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

    # P&L
    total_pnl = sum(t.pnl for t in trades)
    total_return_pct = (total_pnl / initial_capital) * 100

    # Average win/loss
    avg_win = sum(t.pnl for t in wins) / win_count if win_count > 0 else 0
    avg_loss = sum(t.pnl for t in losses) / loss_count if loss_count > 0 else 0
    avg_win_pct = sum(t.pnl_pct for t in wins) / win_count if win_count > 0 else 0
    avg_loss_pct = sum(t.pnl_pct for t in losses) / loss_count if loss_count > 0 else 0

    # Profit factor
    gross_profit = sum(t.pnl for t in wins) if wins else 0
    gross_loss = abs(sum(t.pnl for t in losses)) if losses else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # Best/worst trade
    best_trade = max(trades, key=lambda t: t.pnl)
    worst_trade = min(trades, key=lambda t: t.pnl)

    # Average holding period
    avg_holding_days = sum(t.holding_days for t in trades) / total_trades

    # Max drawdown
    max_drawdown, max_drawdown_pct = _calculate_max_drawdown(trades, initial_capital)

    # Sharpe ratio (simplified: annualized)
    sharpe = _calculate_sharpe(trades, initial_capital)

    # Exit reason breakdown
    exit_reasons = {}
    for t in trades:
        reason = t.exit_reason or "unknown"
        exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

    # By signal type
    buy_trades = [t for t in trades if t.signal_type == "BUY"]
    sell_trades = [t for t in trades if t.signal_type == "SELL"]

    buy_win_rate = (
        sum(1 for t in buy_trades if t.pnl > 0) / len(buy_trades) * 100
        if buy_trades else 0
    )
    sell_win_rate = (
        sum(1 for t in sell_trades if t.pnl > 0) / len(sell_trades) * 100
        if sell_trades else 0
    )

    # By grade
    grade_stats = {}
    for grade in ["STRONG", "MODERATE", "WEAK"]:
        grade_trades = [t for t in trades if t.grade == grade]
        if grade_trades:
            grade_wins = sum(1 for t in grade_trades if t.pnl > 0)
            grade_stats[grade] = {
                "count": len(grade_trades),
                "win_rate": grade_wins / len(grade_trades) * 100,
                "avg_pnl": sum(t.pnl for t in grade_trades) / len(grade_trades),
            }

    return {
        "total_trades": total_trades,
        "wins": win_count,
        "losses": loss_count,
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_return_pct, 1),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "avg_win_pct": round(avg_win_pct, 2),
        "avg_loss_pct": round(avg_loss_pct, 2),
        "profit_factor": round(profit_factor, 2),
        "best_trade_pnl": round(best_trade.pnl, 2),
        "best_trade_ticker": best_trade.ticker,
        "worst_trade_pnl": round(worst_trade.pnl, 2),
        "worst_trade_ticker": worst_trade.ticker,
        "avg_holding_days": round(avg_holding_days, 1),
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 1),
        "sharpe_ratio": round(sharpe, 2),
        "exit_reasons": exit_reasons,
        "buy_trades": len(buy_trades),
        "buy_win_rate": round(buy_win_rate, 1),
        "sell_trades": len(sell_trades),
        "sell_win_rate": round(sell_win_rate, 1),
        "grade_stats": grade_stats,
        "initial_capital": initial_capital,
        "final_capital": round(initial_capital + total_pnl, 2),
    }


def _calculate_max_drawdown(trades: list, initial_capital: float) -> tuple[float, float]:
    """Calculate maximum drawdown from peak equity."""
    equity = initial_capital
    peak = equity
    max_dd = 0
    max_dd_pct = 0

    for trade in trades:
        equity += trade.pnl
        if equity > peak:
            peak = equity
        dd = peak - equity
        dd_pct = (dd / peak * 100) if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
            max_dd_pct = dd_pct

    return max_dd, max_dd_pct


def _calculate_sharpe(trades: list, initial_capital: float, risk_free_rate: float = 0.05) -> float:
    """Calculate simplified Sharpe ratio."""
    if len(trades) < 2:
        return 0.0

    returns = [t.pnl_pct / 100 for t in trades]
    avg_return = sum(returns) / len(returns)
    std_dev = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1))

    if std_dev == 0:
        return 0.0

    # Annualize (assume ~250 trading days, avg trade every few days)
    trades_per_year = 250 / max(1, sum(t.holding_days for t in trades) / len(trades))
    annualized_return = avg_return * trades_per_year
    annualized_std = std_dev * math.sqrt(trades_per_year)

    return (annualized_return - risk_free_rate) / annualized_std


def _empty_metrics() -> dict:
    return {
        "total_trades": 0, "wins": 0, "losses": 0,
        "win_rate": 0, "total_pnl": 0, "total_return_pct": 0,
        "avg_win": 0, "avg_loss": 0, "profit_factor": 0,
        "max_drawdown": 0, "max_drawdown_pct": 0, "sharpe_ratio": 0,
        "initial_capital": 0, "final_capital": 0,
    }

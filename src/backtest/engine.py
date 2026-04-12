"""
Ashum Backtesting Engine
========================
Tests the signal strategy on historical data to measure performance.
Answers: "Would following these signals have made money?"
"""

import logging
from datetime import date, timedelta

import pandas as pd

from src.analysis.technical import compute_indicators
from src.analysis.signals import generate_signal
from src.data.fetcher import fetch_multiple_stocks, fetch_stock_history
from src.data.tickers import get_stock_info
from config.settings import (
    STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, SIGNAL_THRESHOLD,
    MIN_HISTORY_DAYS, TRAILING_STOP_ACTIVATION, TRAILING_STOP_DISTANCE,
    MAX_HOLDING_DAYS,
)

logger = logging.getLogger(__name__)

# Backtest defaults
DEFAULT_INITIAL_CAPITAL = 100_000  # 100K SAR
DEFAULT_POSITION_SIZE_PCT = 10  # 10% of capital per trade
MAX_OPEN_POSITIONS = 10


class Trade:
    """Represents a single simulated trade."""

    def __init__(self, ticker: str, stock_name: str, signal_type: str,
                 strength: int, grade: str, entry_date: date,
                 entry_price: float, stop_loss: float, take_profit: float,
                 position_size: float):
        self.ticker = ticker
        self.stock_name = stock_name
        self.signal_type = signal_type
        self.strength = strength
        self.grade = grade
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_size = position_size
        self.shares = int(position_size / entry_price)
        self.highest_price = entry_price  # For trailing stop
        self.trailing_active = False

        # Filled on exit
        self.exit_date = None
        self.exit_price = None
        self.exit_reason = None  # "stop_loss", "take_profit", "timeout"
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.holding_days = 0

    def close(self, exit_date: date, exit_price: float, exit_reason: str):
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.holding_days = (exit_date - self.entry_date).days

        if self.signal_type == "BUY":
            self.pnl = (exit_price - self.entry_price) * self.shares
            self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL (short)
            self.pnl = (self.entry_price - exit_price) * self.shares
            self.pnl_pct = ((self.entry_price - exit_price) / self.entry_price) * 100

    @property
    def is_win(self) -> bool:
        return self.pnl > 0

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "stock_name": self.stock_name,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "grade": self.grade,
            "entry_date": str(self.entry_date),
            "entry_price": self.entry_price,
            "exit_date": str(self.exit_date),
            "exit_price": self.exit_price,
            "exit_reason": self.exit_reason,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "pnl": round(self.pnl, 2),
            "pnl_pct": round(self.pnl_pct, 2),
            "holding_days": self.holding_days,
            "shares": self.shares,
            "is_win": self.is_win,
        }


class BacktestEngine:
    """
    Backtests the Ashum signal strategy on historical data.

    How it works:
    1. Load historical data for selected stocks
    2. For each trading day, compute indicators and generate signals
    3. If signal → open virtual trade at next day's open
    4. Track each trade: did it hit stop-loss or take-profit first?
    5. Calculate overall performance stats
    """

    def __init__(
        self,
        tickers: list[str],
        period: str = "2y",
        initial_capital: float = DEFAULT_INITIAL_CAPITAL,
        position_size_pct: float = DEFAULT_POSITION_SIZE_PCT,
    ):
        self.tickers = tickers
        self.period = period
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position_size_pct = position_size_pct

        self.trades: list[Trade] = []
        self.open_trades: dict[str, Trade] = {}  # ticker → Trade
        self.equity_curve: list[dict] = []  # [{date, equity}]
        self.stock_data: dict[str, pd.DataFrame] = {}

    def run(self) -> dict:
        """Run the full backtest. Returns results dict."""
        logger.info(f"بدء الاختبار الرجعي: {len(self.tickers)} سهم، الفترة={self.period}")

        # 1. Fetch historical data
        if len(self.tickers) == 1:
            # Single stock: use fetch_stock_history (more reliable)
            df = fetch_stock_history(self.tickers[0], period=self.period)
            if not df.empty:
                self.stock_data = {self.tickers[0]: df}
            else:
                self.stock_data = {}
        else:
            self.stock_data = fetch_multiple_stocks(self.tickers, period=self.period)

        if not self.stock_data:
            logger.error("No data fetched. Backtest aborted.")
            return {"trades": [], "metrics": {}}

        logger.info(f"تم تحميل {len(self.stock_data)} سهم")

        # 2. Find common date range across all stocks
        all_dates = set()
        for df in self.stock_data.values():
            all_dates.update(df.index.date if hasattr(df.index, 'date') else df.index)

        sorted_dates = sorted(all_dates)

        if len(sorted_dates) < MIN_HISTORY_DAYS + 10:
            logger.error(f"بيانات غير كافية: {len(sorted_dates)} يوم")
            return {"trades": [], "metrics": {}}

        # 3. Iterate through each trading day (skip first 200 for indicator warmup)
        start_idx = MIN_HISTORY_DAYS
        check_dates = sorted_dates[start_idx:]

        logger.info(f"فحص {len(check_dates)} يوم تداول...")

        for i, current_date in enumerate(check_dates):
            # Check open trades for exit conditions
            self._check_open_trades(current_date)

            # Skip if max positions reached
            if len(self.open_trades) >= MAX_OPEN_POSITIONS:
                self._record_equity(current_date)
                continue

            # Scan stocks for signals on this date
            for ticker, full_df in self.stock_data.items():
                # Skip if already in a trade for this stock
                if ticker in self.open_trades:
                    continue

                # Get data up to current date
                if hasattr(full_df.index, 'date'):
                    mask = full_df.index.date <= current_date
                else:
                    mask = full_df.index <= pd.Timestamp(current_date)

                df_slice = full_df[mask]

                if len(df_slice) < MIN_HISTORY_DAYS:
                    continue

                # Generate signal using same logic as live bot
                signal = generate_signal(ticker, df_slice)

                if signal and signal["strength"] >= SIGNAL_THRESHOLD:
                    # Find next trading day for entry
                    next_day = self._get_next_trading_day(
                        ticker, current_date, sorted_dates
                    )
                    if next_day is None:
                        continue

                    # Open trade at next day's open price
                    self._open_trade(signal, next_day)

                    # Respect max positions
                    if len(self.open_trades) >= MAX_OPEN_POSITIONS:
                        break

            self._record_equity(current_date)

        # 4. Close any remaining open trades at last price
        self._close_all_remaining(sorted_dates[-1])

        # 5. Calculate metrics
        from src.backtest.metrics import calculate_metrics
        metrics = calculate_metrics(self.trades, self.initial_capital)

        logger.info(
            f"اكتمل الاختبار: {len(self.trades)} صفقة، "
            f"نسبة الفوز: {metrics.get('win_rate', 0):.1f}%، "
            f"العائد: {metrics.get('total_return_pct', 0):.1f}%"
        )

        return {
            "trades": [t.to_dict() for t in self.trades],
            "metrics": metrics,
            "equity_curve": self.equity_curve,
            "config": {
                "tickers": self.tickers,
                "period": self.period,
                "initial_capital": self.initial_capital,
                "stop_loss_pct": STOP_LOSS_PERCENT,
                "take_profit_pct": TAKE_PROFIT_PERCENT,
                "signal_threshold": SIGNAL_THRESHOLD,
                "max_holding_days": MAX_HOLDING_DAYS,
            },
        }

    def _open_trade(self, signal: dict, entry_date):
        """Open a virtual trade."""
        ticker = signal["ticker"]
        full_df = self.stock_data[ticker]

        # Get entry price (open of next day)
        if hasattr(full_df.index, 'date'):
            mask = full_df.index.date == entry_date
        else:
            mask = full_df.index == pd.Timestamp(entry_date)

        entry_bar = full_df[mask]
        if entry_bar.empty:
            return

        entry_price = float(entry_bar["Open"].iloc[0])
        if entry_price <= 0:
            return

        position_size = self.capital * (self.position_size_pct / 100)

        trade = Trade(
            ticker=ticker,
            stock_name=signal.get("stock_name", ticker),
            signal_type=signal["signal_type"],
            strength=signal["strength"],
            grade=signal.get("grade", "WEAK"),
            entry_date=entry_date,
            entry_price=entry_price,
            stop_loss=signal["stop_loss"],
            take_profit=signal["take_profit"],
            position_size=position_size,
        )

        self.open_trades[ticker] = trade

    def _check_open_trades(self, current_date):
        """Check all open trades for exit conditions."""
        to_close = []

        for ticker, trade in self.open_trades.items():
            full_df = self.stock_data.get(ticker)
            if full_df is None:
                continue

            # Get current day's bar
            if hasattr(full_df.index, 'date'):
                mask = full_df.index.date == current_date
            else:
                mask = full_df.index == pd.Timestamp(current_date)

            bar = full_df[mask]
            if bar.empty:
                continue

            high = float(bar["High"].iloc[0])
            low = float(bar["Low"].iloc[0])
            close = float(bar["Close"].iloc[0])

            # Check days held
            days_held = (current_date - trade.entry_date).days

            if trade.signal_type == "BUY":
                # Update highest price for trailing stop
                if high > trade.highest_price:
                    trade.highest_price = high

                # Activate trailing stop when profit exceeds activation threshold
                gain_pct = (trade.highest_price - trade.entry_price) / trade.entry_price * 100
                if gain_pct >= TRAILING_STOP_ACTIVATION:
                    trade.trailing_active = True
                    trailing_sl = trade.highest_price * (1 - TRAILING_STOP_DISTANCE / 100)
                    # Move stop-loss up (never down)
                    if trailing_sl > trade.stop_loss:
                        trade.stop_loss = trailing_sl

                # Check stop-loss (price went below SL)
                if low <= trade.stop_loss:
                    exit_reason = "trailing_stop" if trade.trailing_active else "stop_loss"
                    to_close.append((ticker, current_date, trade.stop_loss, exit_reason))
                # Check take-profit (price went above TP)
                elif high >= trade.take_profit:
                    to_close.append((ticker, current_date, trade.take_profit, "take_profit"))
                # Check timeout
                elif days_held >= MAX_HOLDING_DAYS:
                    to_close.append((ticker, current_date, close, "timeout"))
            else:  # SELL
                # Update lowest price for trailing stop
                if low < trade.highest_price or trade.highest_price == trade.entry_price:
                    trade.highest_price = min(low, trade.highest_price) if trade.highest_price < trade.entry_price else low

                gain_pct = (trade.entry_price - trade.highest_price) / trade.entry_price * 100
                if gain_pct >= TRAILING_STOP_ACTIVATION:
                    trade.trailing_active = True
                    trailing_sl = trade.highest_price * (1 + TRAILING_STOP_DISTANCE / 100)
                    if trailing_sl < trade.stop_loss:
                        trade.stop_loss = trailing_sl

                if high >= trade.stop_loss:
                    exit_reason = "trailing_stop" if trade.trailing_active else "stop_loss"
                    to_close.append((ticker, current_date, trade.stop_loss, exit_reason))
                elif low <= trade.take_profit:
                    to_close.append((ticker, current_date, trade.take_profit, "take_profit"))
                elif days_held >= MAX_HOLDING_DAYS:
                    to_close.append((ticker, current_date, close, "timeout"))

        # Close trades
        for ticker, exit_date, exit_price, reason in to_close:
            trade = self.open_trades.pop(ticker)
            trade.close(exit_date, exit_price, reason)
            self.trades.append(trade)
            self.capital += trade.pnl

    def _close_all_remaining(self, last_date):
        """Close all open trades at the end of backtest."""
        for ticker in list(self.open_trades.keys()):
            trade = self.open_trades.pop(ticker)
            full_df = self.stock_data.get(ticker)
            if full_df is not None and not full_df.empty:
                close_price = float(full_df["Close"].iloc[-1])
            else:
                close_price = trade.entry_price
            trade.close(last_date, close_price, "end_of_test")
            self.trades.append(trade)
            self.capital += trade.pnl

    def _get_next_trading_day(self, ticker, current_date, all_dates):
        """Get the next available trading day after current_date."""
        for d in all_dates:
            if d > current_date:
                # Check if we have data for this ticker on that day
                full_df = self.stock_data[ticker]
                if hasattr(full_df.index, 'date'):
                    mask = full_df.index.date == d
                else:
                    mask = full_df.index == pd.Timestamp(d)
                if not full_df[mask].empty:
                    return d
        return None

    def _record_equity(self, current_date):
        """Record current equity for equity curve."""
        # Calculate unrealized P&L from open trades
        unrealized = 0
        for ticker, trade in self.open_trades.items():
            full_df = self.stock_data.get(ticker)
            if full_df is None:
                continue
            if hasattr(full_df.index, 'date'):
                mask = full_df.index.date == current_date
            else:
                mask = full_df.index == pd.Timestamp(current_date)
            bar = full_df[mask]
            if not bar.empty:
                current_price = float(bar["Close"].iloc[0])
                if trade.signal_type == "BUY":
                    unrealized += (current_price - trade.entry_price) * trade.shares
                else:
                    unrealized += (trade.entry_price - current_price) * trade.shares

        self.equity_curve.append({
            "date": str(current_date),
            "equity": round(self.capital + unrealized, 2),
        })


def run_backtest(
    tickers: list[str] | None = None,
    period: str = "2y",
    initial_capital: float = DEFAULT_INITIAL_CAPITAL,
) -> dict:
    """
    Quick function to run a backtest.

    Args:
        tickers: List of Tadawul tickers. None = top 20 major stocks.
        period: History period (e.g., "2y", "3y").
        initial_capital: Starting capital in SAR.

    Returns:
        Results dict with trades, metrics, and equity curve.
    """
    if tickers is None:
        tickers = [
            "2222", "1120", "2010", "7010", "2280",
            "1180", "1150", "2082", "1050", "1060",
            "4190", "2350", "1010", "7020", "4013",
            "2050", "1211", "4001", "5110", "1111",
        ]

    engine = BacktestEngine(
        tickers=tickers,
        period=period,
        initial_capital=initial_capital,
    )

    return engine.run()

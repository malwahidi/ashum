import io
import logging

import pandas as pd
import mplfinance as mpf
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend

from config.indicators import (
    SMA_SHORT, SMA_LONG, BB_PERIOD, BB_STD,
    EMA_FAST, EMA_SLOW,
)

logger = logging.getLogger(__name__)

# Custom Tadawul-themed style
ASHUM_STYLE = mpf.make_mpf_style(
    base_mpf_style="nightclouds",
    marketcolors=mpf.make_marketcolors(
        up="#00c853",     # Green for up
        down="#ff1744",   # Red for down
        edge="inherit",
        wick="inherit",
        volume="in",
    ),
    figcolor="#1a1a2e",
    facecolor="#16213e",
    gridcolor="#0f3460",
    gridstyle="--",
    gridaxis="both",
    y_on_right=True,
)


def generate_stock_chart(
    df: pd.DataFrame,
    ticker: str,
    stock_name: str,
    signal_type: str | None = None,
    signal_strength: int | None = None,
    days: int = 60,
) -> io.BytesIO | None:
    """
    Generate a candlestick chart with indicators.

    Args:
        df: DataFrame with OHLCV + computed indicators
        ticker: Ticker number
        stock_name: Company name
        signal_type: "BUY" or "SELL" (for title)
        signal_strength: Signal score (for title)
        days: Number of days to show on chart

    Returns:
        BytesIO buffer with PNG image, or None on error.
    """
    if df.empty or len(df) < days:
        days = len(df)

    if days < 10:
        logger.warning(f"Too little data for chart: {ticker}")
        return None

    try:
        # Take last N days
        chart_df = df.tail(days).copy()

        # Ensure proper index
        if not isinstance(chart_df.index, pd.DatetimeIndex):
            chart_df.index = pd.to_datetime(chart_df.index)

        # Build additional plots (overlays)
        add_plots = []

        # SMA lines
        sma_short_col = f"SMA_{SMA_SHORT}"
        sma_long_col = f"SMA_{SMA_LONG}"

        if sma_short_col in chart_df.columns:
            add_plots.append(mpf.make_addplot(
                chart_df[sma_short_col], color="#ffd700", width=1.2,
                linestyle="-", label=f"SMA {SMA_SHORT}"
            ))

        if sma_long_col in chart_df.columns:
            add_plots.append(mpf.make_addplot(
                chart_df[sma_long_col], color="#ff6b6b", width=1.2,
                linestyle="-", label=f"SMA {SMA_LONG}"
            ))

        # Bollinger Bands
        bb_upper = f"BBU_{BB_PERIOD}_{BB_STD}"
        bb_lower = f"BBL_{BB_PERIOD}_{BB_STD}"

        if bb_upper in chart_df.columns:
            add_plots.append(mpf.make_addplot(
                chart_df[bb_upper], color="#4fc3f7", width=0.8,
                linestyle="--"
            ))
        if bb_lower in chart_df.columns:
            add_plots.append(mpf.make_addplot(
                chart_df[bb_lower], color="#4fc3f7", width=0.8,
                linestyle="--"
            ))

        # Build title
        signal_text = ""
        if signal_type and signal_strength:
            emoji = "BUY" if signal_type == "BUY" else "SELL"
            signal_text = f" | {emoji} Signal: {signal_strength}/100"

        title = f"{ticker}.SR - {stock_name}{signal_text}"

        # Generate chart
        buf = io.BytesIO()

        fig, axes = mpf.plot(
            chart_df,
            type="candle",
            style=ASHUM_STYLE,
            volume=True,
            addplot=add_plots if add_plots else None,
            title=title,
            figsize=(12, 8),
            tight_layout=True,
            returnfig=True,
        )

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0)

        matplotlib.pyplot.close(fig)

        return buf

    except Exception as e:
        logger.error(f"Error generating chart for {ticker}: {e}")
        return None

import logging
from datetime import date, datetime

import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.data.models import (
    StockPrice, Signal, ScanResult, SignalType,
    get_session, init_db
)

logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database tables."""
    init_db()
    logger.info("Database tables created/verified.")


def save_stock_prices(ticker: str, df: pd.DataFrame):
    """
    Save OHLCV DataFrame to database. Upserts on (ticker, date).

    Args:
        ticker: Tadawul ticker number
        df: DataFrame with OHLCV data (index=Date)
    """
    if df.empty:
        return

    session = get_session()
    try:
        records = []
        for dt, row in df.iterrows():
            records.append({
                "ticker": ticker,
                "date": dt.date() if isinstance(dt, datetime) else dt,
                "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                "high": float(row["High"]) if pd.notna(row["High"]) else None,
                "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
            })

        if records:
            stmt = pg_insert(StockPrice).values(records)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_ticker_date",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume,
                }
            )
            session.execute(stmt)
            session.commit()
            logger.debug(f"Saved {len(records)} price records for {ticker}")

    except Exception as e:
        session.rollback()
        logger.error(f"Error saving prices for {ticker}: {e}")
    finally:
        session.close()


def save_signal(signal_data: dict):
    """
    Save a trading signal to the database.

    Args:
        signal_data: dict with keys: ticker, stock_name, sector, date,
                     signal_type, strength, price, indicators, reasons
    """
    session = get_session()
    try:
        signal = Signal(
            ticker=signal_data["ticker"],
            stock_name=signal_data.get("stock_name"),
            sector=signal_data.get("sector"),
            date=signal_data["date"],
            signal_type=SignalType(signal_data["signal_type"]),
            strength=signal_data["strength"],
            price=signal_data.get("price"),
            indicators=signal_data.get("indicators"),
            reasons=signal_data.get("reasons"),
        )
        session.add(signal)
        session.commit()
        logger.debug(f"Saved signal: {signal}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving signal: {e}")
    finally:
        session.close()


def save_scan_result(scan_data: dict):
    """Save a market scan result summary."""
    session = get_session()
    try:
        result = ScanResult(
            date=scan_data["date"],
            scan_time=scan_data.get("scan_time", datetime.utcnow()),
            total_stocks=scan_data["total_stocks"],
            buy_signals=scan_data["buy_signals"],
            sell_signals=scan_data["sell_signals"],
            top_buys=scan_data.get("top_buys"),
            top_sells=scan_data.get("top_sells"),
        )
        session.add(result)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving scan result: {e}")
    finally:
        session.close()


def get_stock_prices(ticker: str, days: int = 365) -> pd.DataFrame:
    """Load stock prices from DB as DataFrame."""
    session = get_session()
    try:
        stmt = (
            select(StockPrice)
            .where(StockPrice.ticker == ticker)
            .order_by(StockPrice.date.desc())
            .limit(days)
        )
        rows = session.execute(stmt).scalars().all()

        if not rows:
            return pd.DataFrame()

        data = [{
            "Date": r.date,
            "Open": r.open,
            "High": r.high,
            "Low": r.low,
            "Close": r.close,
            "Volume": r.volume,
        } for r in rows]

        df = pd.DataFrame(data).set_index("Date").sort_index()
        return df

    finally:
        session.close()


def get_latest_signals(
    signal_type: str | None = None,
    limit: int = 20
) -> list[dict]:
    """Get the most recent signals."""
    session = get_session()
    try:
        stmt = select(Signal).order_by(Signal.created_at.desc())

        if signal_type:
            stmt = stmt.where(Signal.signal_type == SignalType(signal_type))

        stmt = stmt.limit(limit)
        rows = session.execute(stmt).scalars().all()

        return [{
            "ticker": r.ticker,
            "stock_name": r.stock_name,
            "sector": r.sector,
            "date": r.date.isoformat(),
            "signal_type": r.signal_type.value,
            "strength": r.strength,
            "price": r.price,
            "indicators": r.indicators,
            "reasons": r.reasons,
        } for r in rows]

    finally:
        session.close()

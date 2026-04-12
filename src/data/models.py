from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, String, Float, Integer, BigInteger,
    Date, DateTime, JSON, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
import enum

from config.settings import DATABASE_URL


class Base(DeclarativeBase):
    pass


class SignalType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_ticker_date"),
        Index("ix_stock_prices_ticker_date", "ticker", "date"),
    )

    def __repr__(self):
        return f"<StockPrice {self.ticker} {self.date} C:{self.close}>"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    stock_name = Column(String(100))
    sector = Column(String(50))
    date = Column(Date, nullable=False)
    signal_type = Column(SAEnum(SignalType), nullable=False)
    strength = Column(Integer, nullable=False)  # 0-100
    price = Column(Float)
    indicators = Column(JSON)  # Snapshot of indicator values
    reasons = Column(JSON)  # List of reasons for the signal
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_signals_date_type", "date", "signal_type"),
        Index("ix_signals_ticker_date", "ticker", "date"),
    )

    def __repr__(self):
        return f"<Signal {self.signal_type.value} {self.ticker} {self.strength}/100>"


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    scan_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_stocks = Column(Integer)
    buy_signals = Column(Integer)
    sell_signals = Column(Integer)
    top_buys = Column(JSON)  # [{ticker, name, strength, price}, ...]
    top_sells = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    return SessionLocal()

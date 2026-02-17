from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.database.engine import Base

class AssetType(enum.Enum):
    STOCK_DOMESTIC = "STOCK_DOMESTIC"
    STOCK_OVERSEAS = "STOCK_OVERSEAS"
    CASH_KRW = "CASH_KRW"
    CASH_USD = "CASH_USD"
    CRYPTO = "CRYPTO"
    MANUAL = "MANUAL"  # Real estate, etc.

# ──────────────────────────────────────────────
# Instrument Master (normalized)
# ──────────────────────────────────────────────
class Instrument(Base):
    """
    Master table for all financial instruments.
    Stocks, crypto, RP, FX, manual assets — all tracked here.
    """
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=True, index=True)        # e.g., AAPL, 005930, BTC — null for 부동산 등
    name = Column(String, nullable=False)                      # e.g., Apple Inc., 삼성전자, Bitcoin
    asset_type = Column(Enum(AssetType), nullable=False)
    currency = Column(String, default="KRW")                   # KRW, USD
    brokerage = Column(String, nullable=True)                  # null for crypto, manual
    exchange = Column(String, nullable=True)                   # KRX, NASD, NYSE — null for RP, FX, crypto
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    snapshots = relationship("DailyPortfolioSnapshot", back_populates="instrument")


# ──────────────────────────────────────────────
# Daily Portfolio Snapshot (replaces asset_snapshots)
# ──────────────────────────────────────────────
class DailyPortfolioSnapshot(Base):
    """
    One row per instrument per date. Recorded at market close.
    Uses UPSERT to ensure no duplicates.
    """
    __tablename__ = "daily_portfolio_snapshot"
    __table_args__ = (
        UniqueConstraint('date', 'instrument_id', name='uq_date_instrument'),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False, index=True)
    snapshot_time = Column(DateTime, nullable=False)           # Exact capture time
    quantity = Column(Float, default=0.0)
    close_price = Column(Float, default=0.0)                   # Closing price (or latest at snapshot)
    avg_buy_price = Column(Float, default=0.0)                 # Average purchase price
    exchange_rate = Column(Float, default=1.0)                 # FX rate to KRW
    value_krw = Column(Float, nullable=False)                  # Total value in KRW
    profit_loss_krw = Column(Float, default=0.0)               # P&L in KRW

    instrument = relationship("Instrument", back_populates="snapshots")


# ──────────────────────────────────────────────
# Daily Summary (enhanced)
# ──────────────────────────────────────────────
class DailySummary(Base):
    """Aggregated daily portfolio summary for quick period-return queries."""
    __tablename__ = "daily_summary"

    date = Column(Date, primary_key=True, index=True)
    snapshot_time = Column(DateTime, nullable=True)
    total_asset_krw = Column(Float, default=0.0)
    total_cost_krw = Column(Float, default=0.0)                # Total invested amount
    profit_loss_krw = Column(Float, default=0.0)
    return_rate_pct = Column(Float, default=0.0)               # (asset - cost) / cost * 100
    net_investment_krw = Column(Float, default=0.0)            # Cumulative deposits - withdrawals
    
    # Benchmark indices for comparison
    kospi_close = Column(Float, nullable=True)                 # KOSPI closing price
    sp500_close = Column(Float, nullable=True)                 # S&P 500 closing price


# ──────────────────────────────────────────────
# Deposit History (unchanged)
# ──────────────────────────────────────────────
class DepositHistory(Base):
    """Tracks deposits and withdrawals for net investment calculation."""
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Positive=Deposit, Negative=Withdrawal
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────
# Trade Log (unchanged)
# ──────────────────────────────────────────────
class TradeLog(Base):
    """Record of executed trades."""
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    asset_type = Column(Enum(AssetType), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    result_msg = Column(String, nullable=True)


# ──────────────────────────────────────────────
# Manual Asset (unchanged — kept for manual asset CRUD)
# ──────────────────────────────────────────────
class ManualAsset(Base):
    """
    Assets manually added by the user (e.g., crypto, real estate).
    These are also registered in `instruments` for snapshot tracking.
    """
    __tablename__ = "manual_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    asset_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)
    buy_price = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, nullable=False, default=0.0)
    currency = Column(String, default="KRW")
    brokerage = Column(String, nullable=False, default="Manual")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

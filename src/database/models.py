from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.database.engine import Base

class AssetType(enum.Enum):
    STOCK_DOMESTIC = "STOCK_DOMESTIC"
    STOCK_OVERSEAS = "STOCK_OVERSEAS"
    CASH_KRW = "CASH_KRW"
    CASH_USD = "CASH_USD"
    CRYPTO = "CRYPTO" # Future use
    MANUAL = "MANUAL" # Real estate, etc.

class DepositHistory(Base):
    """Tracks deposits and withdrawals for net investment calculation."""
    __tablename__ = "deposits"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False) # KRW based. Positive=Deposit, Negative=Withdrawal
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetSnapshot(Base):
    """Daily snapshot of individual asset holdings."""
    __tablename__ = "asset_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    symbol = Column(String, nullable=True) # e.g., AAPL, 005930
    name = Column(String, nullable=True)
    quantity = Column(Float, default=0.0)
    price = Column(Float, default=0.0) # Unit price
    currency = Column(String, default="KRW")
    exchange_rate = Column(Float, default=1.0) # Exchange rate to KRW
    value_krw = Column(Float, nullable=False) # Converted to KRW
    
class DailySummary(Base):
    """Aggregated daily portfolio summary for quick graphing."""
    __tablename__ = "daily_summary"
    
    date = Column(Date, primary_key=True, index=True)
    total_asset_krw = Column(Float, default=0.0)
    net_investment_krw = Column(Float, default=0.0) # Total deposits - withdrawals until this date
    profit_loss_krw = Column(Float, default=0.0)
    return_rate_percentage = Column(Float, default=0.0) # Simple return: (Total / Net) - 1

class TradeLog(Base):
    """Record of executed trades."""
    __tablename__ = "trade_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    asset_type = Column(Enum(AssetType), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False) # BUY, SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    result_msg = Column(String, nullable=True)

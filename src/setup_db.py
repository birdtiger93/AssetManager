import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.engine import engine, Base
from src.database.models import Instrument, DailyPortfolioSnapshot, DepositHistory, DailySummary, TradeLog, ManualAsset

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")
    print(f"Database file located at: {engine.url}")

if __name__ == "__main__":
    init_db()

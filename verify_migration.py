"""Quick verification of the migration results."""
import sqlite3, os

DB_PATH = os.path.join("data", "assets.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. List all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)

# 2. Check instruments
c.execute("SELECT count(*) FROM instruments")
print(f"\nInstruments count: {c.fetchone()[0]}")
c.execute("SELECT id, symbol, name, asset_type, currency, brokerage, exchange FROM instruments LIMIT 5")
for r in c.fetchall():
    print(f"  {r}")

# 3. Check snapshots
c.execute("SELECT count(*) FROM daily_portfolio_snapshot")
print(f"\nSnapshots count: {c.fetchone()[0]}")
c.execute("SELECT id, date, instrument_id, quantity, close_price, value_krw FROM daily_portfolio_snapshot LIMIT 5")
for r in c.fetchall():
    print(f"  {r}")

# 4. Verify old table is gone
print(f"\nasset_snapshots exists: {'asset_snapshots' in tables}")
print(f"instruments exists: {'instruments' in tables}")
print(f"daily_portfolio_snapshot exists: {'daily_portfolio_snapshot' in tables}")

conn.close()

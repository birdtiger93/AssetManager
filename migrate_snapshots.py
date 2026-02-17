"""
Migration script: Restructure asset_snapshots into normalized schema.

1. Create `instruments` table
2. Create `daily_portfolio_snapshot` table
3. Migrate data from `asset_snapshots` (deduplicate per date+symbol)
4. Update `daily_summary` table schema
5. Drop old `asset_snapshots` table

Run from project root:
    python migrate_snapshots.py
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "assets.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # ── Step 1: Create `instruments` table ──
        print("[1/5] Creating instruments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instruments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                currency TEXT DEFAULT 'KRW',
                brokerage TEXT,
                exchange TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Step 2: Create `daily_portfolio_snapshot` table ──
        print("[2/5] Creating daily_portfolio_snapshot table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_portfolio_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                instrument_id INTEGER NOT NULL,
                snapshot_time TIMESTAMP NOT NULL,
                quantity REAL DEFAULT 0.0,
                close_price REAL DEFAULT 0.0,
                avg_buy_price REAL DEFAULT 0.0,
                exchange_rate REAL DEFAULT 1.0,
                value_krw REAL NOT NULL,
                profit_loss_krw REAL DEFAULT 0.0,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id),
                UNIQUE(date, instrument_id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_daily_snapshot_date ON daily_portfolio_snapshot(date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_daily_snapshot_instrument ON daily_portfolio_snapshot(instrument_id)
        """)

        # ── Step 3: Migrate data from asset_snapshots ──
        # Check if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asset_snapshots'")
        old_table_exists = cursor.fetchone() is not None

        if old_table_exists:
            print("[3/5] Migrating data from asset_snapshots...")

            # Extract unique instruments from old snapshots
            cursor.execute("""
                SELECT DISTINCT symbol, name, asset_type, currency, exchange_rate
                FROM asset_snapshots
                WHERE symbol IS NOT NULL
            """)
            old_instruments = cursor.fetchall()
            
            instrument_map = {}  # (symbol, asset_type) -> instrument_id
            for symbol, name, asset_type, currency, _ in old_instruments:
                # Check if instrument already exists
                cursor.execute(
                    "SELECT id FROM instruments WHERE symbol = ? AND asset_type = ?",
                    (symbol, asset_type)
                )
                existing = cursor.fetchone()
                if existing:
                    instrument_map[(symbol, asset_type)] = existing[0]
                else:
                    brokerage = "Korea Investment"  # Default for KIS API assets
                    exchange = None
                    if asset_type == "STOCK_DOMESTIC":
                        exchange = "KRX"
                    elif asset_type == "STOCK_OVERSEAS":
                        exchange = "NASD"  # Default, could be NYSE
                    
                    cursor.execute("""
                        INSERT INTO instruments (symbol, name, asset_type, currency, brokerage, exchange)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (symbol, name or symbol, asset_type, currency or "KRW", brokerage, exchange))
                    instrument_map[(symbol, asset_type)] = cursor.lastrowid
            
            print(f"    Created {len(instrument_map)} instruments from old data.")

            # Migrate snapshots — deduplicate by keeping last entry per (date, symbol, asset_type)
            cursor.execute("""
                SELECT date, asset_type, symbol, quantity, price, currency, exchange_rate, value_krw
                FROM asset_snapshots
                ORDER BY id ASC
            """)
            old_snapshots = cursor.fetchall()

            # Group and deduplicate: keep last snapshot per (date, symbol, asset_type)
            dedup = {}
            for row in old_snapshots:
                date, asset_type, symbol, quantity, price, currency, exchange_rate, value_krw = row
                key = (date, symbol, asset_type)
                dedup[key] = row  # Overwrites with the latest

            migrated = 0
            for key, row in dedup.items():
                date, asset_type, symbol, quantity, price, currency, exchange_rate, value_krw = row
                instrument_id = instrument_map.get((symbol, asset_type))
                if instrument_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO daily_portfolio_snapshot
                        (date, instrument_id, snapshot_time, quantity, close_price, avg_buy_price, exchange_rate, value_krw, profit_loss_krw)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date,
                        instrument_id,
                        datetime.utcnow().isoformat(),  # We don't have the original time
                        quantity,
                        price,
                        0.0,   # avg_buy_price not available in old data
                        exchange_rate,
                        value_krw,
                        0.0    # P&L not available in old data
                    ))
                    migrated += 1

            print(f"    Migrated {migrated} snapshots (deduplicated from {len(old_snapshots)}).")
        else:
            print("[3/5] No old asset_snapshots table found. Skipping data migration.")

        # ── Step 4: Update daily_summary table ──
        print("[4/5] Updating daily_summary table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_summary'")
        summary_exists = cursor.fetchone() is not None

        if summary_exists:
            # Check existing columns
            cursor.execute("PRAGMA table_info(daily_summary)")
            existing_cols = {row[1] for row in cursor.fetchall()}

            if "snapshot_time" not in existing_cols:
                cursor.execute("ALTER TABLE daily_summary ADD COLUMN snapshot_time TIMESTAMP")
            if "total_cost_krw" not in existing_cols:
                cursor.execute("ALTER TABLE daily_summary ADD COLUMN total_cost_krw REAL DEFAULT 0.0")
        else:
            cursor.execute("""
                CREATE TABLE daily_summary (
                    date DATE PRIMARY KEY,
                    snapshot_time TIMESTAMP,
                    total_asset_krw REAL DEFAULT 0.0,
                    total_cost_krw REAL DEFAULT 0.0,
                    profit_loss_krw REAL DEFAULT 0.0,
                    return_rate_pct REAL DEFAULT 0.0,
                    net_investment_krw REAL DEFAULT 0.0
                )
            """)

        # ── Step 5: Drop old table ──
        if old_table_exists:
            print("[5/5] Dropping old asset_snapshots table...")
            cursor.execute("DROP TABLE IF EXISTS asset_snapshots")
        else:
            print("[5/5] Nothing to drop.")

        conn.commit()
        print("\n[OK] Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()

"""
Migration: Fix column name mismatch in daily_summary
Changes:
- Rename return_rate_percentage to return_rate_pct
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "assets.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Fixing daily_summary column names...")
    
    try:
        # Check if return_rate_percentage exists
        c.execute("PRAGMA table_info(daily_summary)")
        columns = {row[1]: row for row in c.fetchall()}
        
        if 'return_rate_percentage' in columns and 'return_rate_pct' not in columns:
            print("  Renaming return_rate_percentage to return_rate_pct...")
            # SQLite doesn't support RENAME COLUMN directly in older versions
            # We need to recreate the table
            c.execute("""
                CREATE TABLE daily_summary_new (
                    date DATE PRIMARY KEY,
                    snapshot_time TIMESTAMP,
                    total_asset_krw FLOAT DEFAULT 0.0,
                    total_cost_krw FLOAT DEFAULT 0.0,
                    profit_loss_krw FLOAT DEFAULT 0.0,
                    return_rate_pct FLOAT DEFAULT 0.0,
                    net_investment_krw FLOAT DEFAULT 0.0,
                    kospi_close REAL,
                    sp500_close REAL
                )
            """)
            
            # Copy data
            c.execute("""
                INSERT INTO daily_summary_new 
                SELECT date, snapshot_time, total_asset_krw, total_cost_krw, 
                       profit_loss_krw, return_rate_percentage, net_investment_krw,
                       kospi_close, sp500_close
                FROM daily_summary
            """)
            
            # Drop old table and rename
            c.execute("DROP TABLE daily_summary")
            c.execute("ALTER TABLE daily_summary_new RENAME TO daily_summary")
            
            print("  [OK] Column renamed successfully")
        else:
            print("  [SKIP] Column already has correct name")
        
        conn.commit()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

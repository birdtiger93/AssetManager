"""Add benchmark columns to daily_summary table."""
import sqlite3
import os

DB_PATH = os.path.join("data", "assets.db")

def migrate():
    print("Adding benchmark columns to daily_summary...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Add kospi_close column
        c.execute("ALTER TABLE daily_summary ADD COLUMN kospi_close REAL")
        print("  Added kospi_close column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  kospi_close column already exists")
        else:
            raise
    
    try:
        # Add sp500_close column
        c.execute("ALTER TABLE daily_summary ADD COLUMN sp500_close REAL")
        print("  Added sp500_close column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  sp500_close column already exists")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("[OK] Migration completed successfully!")

if __name__ == "__main__":
    migrate()

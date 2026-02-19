from sqlalchemy import create_engine, inspect
import os
import sys

# Setup path
sys.path.append(os.getcwd())

from src.database.engine import DB_URL

def check_tables():
    print(f"Connecting to: {DB_URL}")
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables found:", tables)
    
    if "manual_assets" in tables:
        print("[OK] manual_assets table exists.")
    else:
        print("[ERROR] manual_assets table MISSING!")

if __name__ == "__main__":
    check_tables()

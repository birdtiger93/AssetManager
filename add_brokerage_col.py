import sqlite3

DB_PATH = "data/assets.db"

def add_brokerage_column():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Checking if 'brokerage' column exists in 'manual_assets'...")
        cursor.execute("PRAGMA table_info(manual_assets)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "brokerage" not in columns:
            print("Adding 'brokerage' column...")
            cursor.execute("ALTER TABLE manual_assets ADD COLUMN brokerage VARCHAR DEFAULT 'Manual'")
            conn.commit()
            print("Column added successfully.")
        else:
            print("'brokerage' column already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_brokerage_column()

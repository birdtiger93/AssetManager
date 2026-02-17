import json
import os
from src.api.domestic import DomesticAPI

def save_account_balance():
    api = DomesticAPI()
    print("Fetching account balance...")
    result = api.get_account_balance()
    
    if result:
        file_path = "account_balance.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved account balance to {file_path}")
        return result
    else:
        print("Failed to fetch account balance.")
        return None

if __name__ == "__main__":
    save_account_balance()

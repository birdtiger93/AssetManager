import os
import sys

# 프로젝트 루트 경로를 PYTHONPATH에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.engine import SessionLocal
from src.database.models import AssetSnapshot, DailySummary, DepositHistory, TradeLog, AssetType
import code

def launch_shell():
    db = SessionLocal()
    print("--- KIS AssetManager DB Shell ---")
    print("Available Objects: db, AssetSnapshot, DailySummary, DepositHistory, TradeLog, AssetType")
    print("Example: db.query(AssetSnapshot).all()")
    
    # 대화형 쉘 실행
    local_vars = {
        "db": db,
        "AssetSnapshot": AssetSnapshot,
        "DailySummary": DailySummary,
        "DepositHistory": DepositHistory,
        "TradeLog": TradeLog,
        "AssetType": AssetType
    }
    
    code.interact(local=local_vars)

if __name__ == "__main__":
    launch_shell()

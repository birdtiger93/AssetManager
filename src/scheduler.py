from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import datetime
from src.database.engine import SessionLocal
from src.database.models import AssetSnapshot, AssetType
from src.api.domestic import DomesticAPI
from src.api.overseas import OverseasAPI

def snapshot_assets():
    """Fetches current balance and saves a snapshot to DB."""
    print(f"[{datetime.datetime.now()}] Starting Asset Snapshot...")
    db = SessionLocal()
    
    try:
        # 1. Overseas
        ov_api = OverseasAPI()
        ov_res = ov_api.get_balance_present()
        
        usd_rate = 1200.0 # Default fallback
        
        if ov_res and ov_res.get("rt_cd") == "0":
            # Extract Exchange Rate from output2
            for curr in ov_res.get("output2", []):
                if curr.get("crcy_cd") == "USD":
                    try:
                        usd_rate = float(curr.get("frst_bltn_exrt", 1200))
                    except:
                        pass
                    break
            
            for item in ov_res.get("output1", []):
                qty = float(item.get("ccld_qty_smtl1", 0))
                if qty > 0:
                    price_usd = float(item.get("ovrs_now_pric1", 0))
                    snapshot = AssetSnapshot(
                        date=datetime.date.today(),
                        asset_type=AssetType.STOCK_OVERSEAS,
                        symbol=item.get("pdno"),
                        name=item.get("prdt_name"),
                        quantity=qty,
                        price=price_usd,
                        currency="USD",
                        exchange_rate=usd_rate,
                        value_krw=price_usd * qty * usd_rate
                    )
                    db.add(snapshot)
        
        # 2. Domestic
        dom_api = DomesticAPI()
        dom_res = dom_api.get_balance()
        if dom_res and dom_res.get("rt_cd") == "0":
             for item in dom_res.get("output1", []):
                qty = float(item.get("hldg_qty", 0))
                if qty > 0:
                     price_krw = float(item.get("prpr", 0))
                     snapshot = AssetSnapshot(
                        date=datetime.date.today(),
                        asset_type=AssetType.STOCK_DOMESTIC,
                        symbol=item.get("pdno"),
                        name=item.get("prdt_name"),
                        quantity=qty,
                        price=price_krw,
                        currency="KRW",
                        exchange_rate=1.0,
                        value_krw=float(item.get("evlu_amt", 0))
                    )
                     db.add(snapshot)
        
        db.commit()
        print(f"[{datetime.datetime.now()}] Snapshot saved.")
        
    except Exception as e:
        print(f"[ERROR] Snapshot failed: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule snapshot every 30 minutes during day? 
    # Or just once a day for closing price?
    # User said "Realtime monitor", so maybe more frequent?
    # But API rate limits exist.
    # Let's do every 1 hour for now, and a fixed one at market close.
    
    scheduler.add_job(snapshot_assets, 'interval', minutes=60, id='hourly_snapshot')
    
    # Domestic market close (approx 15:40)
    scheduler.add_job(snapshot_assets, CronTrigger(hour=15, minute=40), id='domestic_close')
    
    # US market close (approx 06:00 KST)
    scheduler.add_job(snapshot_assets, CronTrigger(hour=6, minute=10), id='overseas_close')
    
    scheduler.start()
    print("Scheduler started.")
    
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()

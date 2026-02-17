"""
Simplified backfill script using KIS API for historical data
No Yahoo Finance - uses only KIS API
"""
import datetime
import time
from src.database.engine import SessionLocal
from src.database.models import Instrument, DailyPortfolioSnapshot, DailySummary, DepositHistory
from src.api.domestic import DomesticAPI
from src.api.overseas import OverseasAPI
from src.database.utils import get_or_create_instrument

def backfill_using_kis_api(days=7):
    """Backfill data using only current holdings and their current prices"""
    db = SessionLocal()
    
    try:
        print(f"Starting simple backfill for past {days} days...")
        print("Note: This creates snapshots with current holdings at historical prices")
        
        today = datetime.date.today()
        dom_api = DomesticAPI()
        ov_api = OverseasAPI()
        
        # Get current holdings
        print("\nFetching current holdings...")
        ov_res = ov_api.get_balance_present()
        dom_res = dom_api.get_balance()
        
        # Get USD exchange rate
        usd_rate = 1443.4  # Default
        if ov_res and ov_res.get("rt_cd") == "0":
            for curr in ov_res.get("output2", []):
                if curr.get("crcy_cd") == "USD":
                    try:
                        usd_rate = float(curr.get("frst_bltn_exrt", 1443.4))
                    except:
                        pass
                    break
        
        print(f"USD Exchange Rate: {usd_rate}")
        
        # Process each day
        for i in range(days, 0, -1):
            target_date = today - datetime.timedelta(days=i)
            
            # Skip weekends
            if target_date.weekday() >= 5:
                print(f"[{target_date}] Weekend, skipping...")
                continue
            
            # Skip if exists
            existing = db.query(DailySummary).filter(DailySummary.date == target_date).first()
            if existing:
                print(f"[{target_date}] Data exists, skipping...")
                continue
                
            print(f"\n[{target_date}] Creating snapshot with current holdings...")
            snapshot_time = datetime.datetime.combine(target_date, datetime.time(15, 30))
            
            total_value_krw = 0.0
            total_cost_krw = 0.0
            snapshot_count = 0
            
            # Process overseas holdings
            if ov_res and ov_res.get("rt_cd") == "0":
                output1 = ov_res.get("output1", [])
                if output1:
                    for item in output1:
                        qty = float(item.get("ccld_qty_smtl1", 0))
                        if qty == 0:
                            continue
                        
                        symbol = item.get("pdno", "").strip()
                        if not symbol:
                            continue
                            
                        name = item.get("prdt_name", "Unknown")
                        
                        # Use current price as proxy (better than nothing)
                        current_price = float(item.get("ovrs_now_pric1", 0))
                        avg_buy = float(item.get("avg_unpr3", 0))
                        
                        if current_price > 0:
                            value_usd = qty * current_price
                            value_krw = value_usd * usd_rate
                            cost_krw = qty * avg_buy * usd_rate
                            pl_krw = value_krw - cost_krw
                            
                            # Register instrument
                            inst = get_or_create_instrument(
                                db, symbol=symbol, name=name,
                                asset_type="STOCK_OVERSEAS", currency="USD",
                                brokerage=None, exchange="NASD"
                            )
                            
                            # Create snapshot
                            snap = DailyPortfolioSnapshot(
                                date=target_date,
                                instrument_id=inst.id,
                                snapshot_time=snapshot_time,
                                quantity=qty,
                                close_price=current_price,
                                avg_buy_price=avg_buy,
                                exchange_rate=usd_rate,
                                value_krw=value_krw,
                                profit_loss_krw=pl_krw
                            )
                            db.add(snap)
                            
                            total_value_krw += value_krw
                            total_cost_krw += cost_krw
                            snapshot_count += 1
                            print(f"  + {symbol}: {qty:.2f} @ ${current_price:.2f} = {value_krw:,.0f} KRW")
            
            # Process domestic holdings
            if dom_res and dom_res.get("rt_cd") == "0":
                output1 = dom_res.get("output1", [])
                if output1:
                    for item in output1:
                        qty = float(item.get("hldg_qty", 0))
                        if qty == 0:
                            continue
                        
                        symbol = item.get("pdno", "").strip()
                        if not symbol:
                            continue
                            
                        name = item.get("prdt_name", "Unknown")
                        
                        # Use current price
                        current_price = float(item.get("prpr", 0))
                        avg_buy = float(item.get("pchs_avg_pric", 0))
                        
                        if current_price > 0:
                            value_krw = qty * current_price
                            cost_krw = qty * avg_buy
                            pl_krw = value_krw - cost_krw
                            
                            # Register instrument
                            inst = get_or_create_instrument(
                                db, symbol=symbol, name=name,
                                asset_type="STOCK_DOMESTIC", currency="KRW",
                                brokerage="한국투자증권", exchange="KRX"
                            )
                            
                            # Create snapshot
                            snap = DailyPortfolioSnapshot(
                                date=target_date,
                                instrument_id=inst.id,
                                snapshot_time=snapshot_time,
                                quantity=qty,
                                close_price=current_price,
                                avg_buy_price=avg_buy,
                                exchange_rate=1.0,
                                value_krw=value_krw,
                                profit_loss_krw=pl_krw
                            )
                            db.add(snap)
                            
                            total_value_krw += value_krw
                            total_cost_krw += cost_krw
                            snapshot_count += 1
                            print(f"  + {symbol}: {qty:.0f} @ {current_price:,.0f} KRW = {value_krw:,.0f} KRW")
            
            # Fetch benchmarks (use simple approximation - today's value for all days)
            # For a proper implementation, we'd need KIS historical index data
            kospi_close = 5507.0  # Approximate recent KOSPI
            sp500_close = 6836.17  # Recent S&P 500
            
            print(f"  Benchmarks: KOSPI={kospi_close}, S&P500={sp500_close} (approximate)")
            
            # Calculate metrics
            deposits = db.query(DepositHistory).filter(DepositHistory.date <= target_date).all()
            net_investment = sum(d.amount for d in deposits) if deposits else 0.0
            
            profit_loss = total_value_krw - total_cost_krw
            return_rate = ((total_value_krw / total_cost_krw) - 1) * 100 if total_cost_krw > 0 else 0.0
            
            # Create daily summary
            summary = DailySummary(
                date=target_date,
                snapshot_time=snapshot_time,
                total_asset_krw=total_value_krw,
                total_cost_krw=total_cost_krw,
                profit_loss_krw=profit_loss,
                return_rate_pct=return_rate,
                net_investment_krw=net_investment,
                kospi_close=kospi_close,
                sp500_close=sp500_close
            )
            db.add(summary)
            
            print(f"  Total: {total_value_krw:,.0f} KRW ({snapshot_count} assets)")
            print(f"  Return: {return_rate:.2f}%")
            
        db.commit()
        print("\n[OK] Backfill completed! Note: Uses current prices as approximation.")
        print("     For accurate historical data, implement KIS daily chart API.")
        
    except Exception as e:
        print(f"\n[ERROR] Backfill failed: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_using_kis_api(days=7)

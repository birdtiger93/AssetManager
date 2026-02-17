"""
Backfill script to populate historical data for the past 7 days
"""
import datetime
from src.database.engine import SessionLocal
from src.database.models import Instrument, DailyPortfolioSnapshot, DailySummary, DepositHistory
from src.api.domestic import DomesticAPI
from src.api.overseas import OverseasAPI
from src.database.utils import get_or_create_instrument
import yfinance as yf

def fetch_kospi_historical(date):
    """Fetch KOSPI for a specific date using yfinance"""
    try:
        kospi = yf.Ticker("^KS11")  # Correct KOSPI symbol
        hist = kospi.history(start=date, end=date + datetime.timedelta(days=1))
        if not hist.empty:
            return float(hist['Close'].iloc[0])
    except Exception as e:
        print(f"  Error fetching KOSPI for {date}: {e}")
    return None

def fetch_sp500_historical(date):
    """Fetch S&P 500 for a specific date"""
    try:
        sp500 = yf.Ticker("^GSPC")
        hist = sp500.history(start=date, end=date + datetime.timedelta(days=1))
        if not hist.empty:
            return float(hist['Close'].iloc[0])
    except Exception as e:
        print(f"  Error fetching S&P 500 for {date}: {e}")
    return None

def backfill_historical_data(days=7):
    """Backfill data for the past N days"""
    db = SessionLocal()
    
    try:
        print(f"Starting backfill for past {days} days...")
        
        # Get current date
        today = datetime.date.today()
        
        # Initialize APIs
        dom_api = DomesticAPI()
        ov_api = OverseasAPI()
        
        # Get current balance to know which assets we have
        ov_res = ov_api.get_balance_present()
        dom_res = dom_api.get_balance()
        
        # Default exchange rate
        usd_rate = 1200.0
        
        # Extract USD rate if available
        if ov_res and ov_res.get("rt_cd") == "0":
            for curr in ov_res.get("output2", []):
                if curr.get("crcy_cd") == "USD":
                    try:
                        usd_rate = float(curr.get("frst_bltn_exrt", 1200))
                    except:
                        pass
                    break
        
        # Process each day
        for i in range(days, 0, -1):
            target_date = today - datetime.timedelta(days=i)
            
            # Skip if data already exists
            existing = db.query(DailySummary).filter(DailySummary.date == target_date).first()
            if existing:
                print(f"[{target_date}] Data already exists, skipping...")
                continue
            
            print(f"\n[{target_date}] Processing...")
            snapshot_time = datetime.datetime.combine(target_date, datetime.time(15, 30))
            
            total_value_krw = 0.0
            total_cost_krw = 0.0
            snapshot_count = 0
            
            # Process overseas stocks
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
                        
                        # Get historical price using yfinance
                        try:
                            ticker = yf.Ticker(symbol)
                            hist = ticker.history(start=target_date, end=target_date + datetime.timedelta(days=1))
                            
                            if not hist.empty:
                                close_price = float(hist['Close'].iloc[0])
                                avg_buy = float(item.get("avg_unpr3", 0))
                                
                                value_usd = qty * close_price
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
                                    close_price=close_price,
                                    avg_buy_price=avg_buy,
                                    exchange_rate=usd_rate,
                                    value_krw=value_krw,
                                    profit_loss_krw=pl_krw
                                )
                                db.add(snap)
                                
                                total_value_krw += value_krw
                                total_cost_krw += cost_krw
                                snapshot_count += 1
                                print(f"  + {symbol}: {qty} @ ${close_price:.2f} = {value_krw:,.0f} KRW")
                        except Exception as e:
                            print(f"  ! Error processing {symbol}: {e}")
            
            # Process domestic stocks
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
                        
                        # Get historical price using yfinance (Korean stocks)
                        try:
                            # Korean stocks on yfinance need .KS or .KQ suffix
                            yf_symbol = f"{symbol}.KS"
                            ticker = yf.Ticker(yf_symbol)
                            hist = ticker.history(start=target_date, end=target_date + datetime.timedelta(days=1))
                            
                            if hist.empty:
                                # Try KOSDAQ
                                yf_symbol = f"{symbol}.KQ"
                                ticker = yf.Ticker(yf_symbol)
                                hist = ticker.history(start=target_date, end=target_date + datetime.timedelta(days=1))
                            
                            if not hist.empty:
                                close_price = float(hist['Close'].iloc[0])
                                avg_buy = float(item.get("pchs_avg_pric", 0))
                                
                                value_krw = qty * close_price
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
                                    close_price=close_price,
                                    avg_buy_price=avg_buy,
                                    exchange_rate=1.0,
                                    value_krw=value_krw,
                                    profit_loss_krw=pl_krw
                                )
                                db.add(snap)
                                
                                total_value_krw += value_krw
                                total_cost_krw += cost_krw
                                snapshot_count += 1
                                print(f"  + {symbol}: {qty} @ {close_price:,.0f} KRW = {value_krw:,.0f} KRW")
                        except Exception as e:
                            print(f"  ! Error processing {symbol}: {e}")
            
            # Fetch benchmark indices
            kospi = fetch_kospi_historical(target_date)
            sp500 = fetch_sp500_historical(target_date)
            
            print(f"  Benchmarks: KOSPI={kospi}, S&P500={sp500}")
            
            # Calculate net investment
            deposits = db.query(DepositHistory).filter(DepositHistory.date <= target_date).all()
            net_investment = sum(d.amount for d in deposits) if deposits else 0.0
            
            # Calculate return
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
                kospi_close=kospi,
                sp500_close=sp500
            )
            db.add(summary)
            
            print(f"  Total: {total_value_krw:,.0f} KRW ({snapshot_count} assets)")
            print(f"  Return: {return_rate:.2f}%")
        
        db.commit()
        print("\n[OK] Backfill completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Error during backfill: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_historical_data(days=7)

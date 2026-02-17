from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import datetime
from sqlalchemy import and_
from src.database.engine import SessionLocal
from src.database.models import Instrument, DailyPortfolioSnapshot, DailySummary, AssetType
from src.api.domestic import DomesticAPI
from src.api.overseas import OverseasAPI


from src.database.utils import get_or_create_instrument


def fetch_kospi_close():
    """Fetch KOSPI closing price using KIS API."""
    try:
        dom_api = DomesticAPI()
        result = dom_api.get_current_price("0001")  # KOSPI index code
        if result and result.get("rt_cd") == "0":
            kospi_price = float(result["output"]["stck_prpr"])
            return kospi_price
    except Exception as e:
        print(f"Error fetching KOSPI: {e}")
    return None


def fetch_sp500_close():
    """Fetch S&P 500 closing price using yfinance."""
    try:
        import yfinance as yf
        sp500 = yf.Ticker("^GSPC")
        hist = sp500.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"Error fetching S&P 500: {e}")
    return None


def upsert_snapshot(db, date, instrument_id, snapshot_time, quantity, close_price,
                    avg_buy_price, exchange_rate, value_krw, profit_loss_krw):
    """Insert or update a daily snapshot for an instrument."""
    existing = db.query(DailyPortfolioSnapshot).filter(
        and_(
            DailyPortfolioSnapshot.date == date,
            DailyPortfolioSnapshot.instrument_id == instrument_id
        )
    ).first()

    if existing:
        existing.snapshot_time = snapshot_time
        existing.quantity = quantity
        existing.close_price = close_price
        existing.avg_buy_price = avg_buy_price
        existing.exchange_rate = exchange_rate
        existing.value_krw = value_krw
        existing.profit_loss_krw = profit_loss_krw
    else:
        snapshot = DailyPortfolioSnapshot(
            date=date,
            instrument_id=instrument_id,
            snapshot_time=snapshot_time,
            quantity=quantity,
            close_price=close_price,
            avg_buy_price=avg_buy_price,
            exchange_rate=exchange_rate,
            value_krw=value_krw,
            profit_loss_krw=profit_loss_krw
        )
        db.add(snapshot)


def update_daily_summary(db, date, snapshot_time):
    """Aggregate all snapshots for the given date into a DailySummary."""
    snapshots = db.query(DailyPortfolioSnapshot).filter(
        DailyPortfolioSnapshot.date == date
    ).all()

    total_asset = sum(s.value_krw for s in snapshots)
    total_cost = sum(s.avg_buy_price * s.quantity * s.exchange_rate for s in snapshots)
    profit_loss = total_asset - total_cost

    # Calculate net investment from deposits
    from src.database.models import DepositHistory
    deposits = db.query(DepositHistory).filter(DepositHistory.date <= date).all()
    net_investment = sum(d.amount for d in deposits) if deposits else 0.0

    return_rate = ((total_asset / total_cost) - 1) * 100 if total_cost > 0 else 0.0

    # Fetch benchmark indices
    kospi = fetch_kospi_close()
    sp500 = fetch_sp500_close()
    
    # Upsert daily summary
    summary = db.query(DailySummary).filter(DailySummary.date == date).first()
    if summary:
        summary.snapshot_time = snapshot_time
        summary.total_asset_krw = total_asset
        summary.total_cost_krw = total_cost
        summary.profit_loss_krw = profit_loss
        summary.return_rate_pct = return_rate
        summary.net_investment_krw = net_investment
        summary.kospi_close = kospi
        summary.sp500_close = sp500
    else:
        summary = DailySummary(
            date=date,
            snapshot_time=snapshot_time,
            total_asset_krw=total_asset,
            total_cost_krw=total_cost,
            profit_loss_krw=profit_loss,
            return_rate_pct=return_rate,
            net_investment_krw=net_investment,
            kospi_close=kospi,
            sp500_close=sp500
        )
        db.add(summary)


def snapshot_assets():
    """Fetches current balance and saves a closing-price snapshot to DB."""
    now = datetime.datetime.now()
    today = datetime.date.today()
    print(f"[{now}] Starting Asset Snapshot (closing price)...")
    db = SessionLocal()

    try:
        # ── 1. Overseas Stocks ──
        ov_api = OverseasAPI()
        ov_res = ov_api.get_balance_present()

        usd_rate = 1200.0  # Default fallback

        if ov_res and ov_res.get("rt_cd") == "0":
            # Extract exchange rate
            for curr in ov_res.get("output2", []):
                if curr.get("crcy_cd") == "USD":
                    try:
                        usd_rate = float(curr.get("frst_bltn_exrt", 1200))
                    except (ValueError, TypeError):
                        pass
                    break

            for item in ov_res.get("output1", []):
                qty = float(item.get("ccld_qty_smtl1", 0))
                if qty > 0:
                    symbol = item.get("pdno", "")
                    name = item.get("prdt_name", symbol)
                    close_price = float(item.get("ovrs_now_pric1", 0))
                    avg_buy = float(item.get("avg_unpr3", 0))
                    eval_amt = close_price * qty * usd_rate
                    pl_krw = float(item.get("ovrs_rlzt_pfls_amt2", 0))

                    instrument = get_or_create_instrument(
                        db, symbol=symbol, name=name,
                        asset_type=AssetType.STOCK_OVERSEAS,
                        currency="USD", brokerage="Korea Investment", exchange="NASD"
                    )
                    upsert_snapshot(
                        db, date=today, instrument_id=instrument.id,
                        snapshot_time=now, quantity=qty,
                        close_price=close_price, avg_buy_price=avg_buy,
                        exchange_rate=usd_rate, value_krw=eval_amt,
                        profit_loss_krw=pl_krw
                    )

        # ── 2. Domestic Stocks ──
        dom_api = DomesticAPI()
        dom_res = dom_api.get_balance()
        if dom_res and dom_res.get("rt_cd") == "0":
            for item in dom_res.get("output1", []):
                qty = float(item.get("hldg_qty", 0))
                if qty > 0:
                    symbol = item.get("pdno", "")
                    name = item.get("prdt_name", symbol)
                    close_price = float(item.get("prpr", 0))
                    avg_buy = float(item.get("pchs_avg_pric", 0))
                    eval_amt = float(item.get("evlu_amt", 0))
                    pl_krw = float(item.get("evlu_pfls_amt", 0))

                    instrument = get_or_create_instrument(
                        db, symbol=symbol, name=name,
                        asset_type=AssetType.STOCK_DOMESTIC,
                        currency="KRW", brokerage="Korea Investment", exchange="KRX"
                    )
                    upsert_snapshot(
                        db, date=today, instrument_id=instrument.id,
                        snapshot_time=now, quantity=qty,
                        close_price=close_price, avg_buy_price=avg_buy,
                        exchange_rate=1.0, value_krw=eval_amt,
                        profit_loss_krw=pl_krw
                    )

            # ── 3. Cash / RP from domestic balance ──
            for summary in dom_res.get("output2", []):
                # CMA/RP balance
                rp_amt = float(summary.get("cma_evlu_amt", 0))
                if rp_amt > 0:
                    instrument = get_or_create_instrument(
                        db, symbol="RP_MMW", name="RP/어음",
                        asset_type=AssetType.CASH_KRW,
                        currency="KRW", brokerage="Korea Investment"
                    )
                    upsert_snapshot(
                        db, date=today, instrument_id=instrument.id,
                        snapshot_time=now, quantity=1, close_price=rp_amt,
                        avg_buy_price=rp_amt, exchange_rate=1.0,
                        value_krw=rp_amt, profit_loss_krw=0.0
                    )

        # ── 4. Manual Assets ──
        from src.database.models import ManualAsset
        manual_assets = db.query(ManualAsset).all()
        for ma in manual_assets:
            # Determine asset_type enum
            type_map = {
                "STOCK": AssetType.STOCK_DOMESTIC,
                "STOCK_DOMESTIC": AssetType.STOCK_DOMESTIC,
                "STOCK_OVERSEAS": AssetType.STOCK_OVERSEAS,
                "CRYPTO": AssetType.CRYPTO,
                "REAL_ESTATE": AssetType.MANUAL,
                "CASH": AssetType.CASH_KRW,
            }
            a_type = type_map.get(ma.asset_type, AssetType.MANUAL)

            instrument = get_or_create_instrument(
                db, symbol=ma.symbol, name=ma.name,
                asset_type=a_type,
                currency=ma.currency,
                brokerage=ma.brokerage if ma.brokerage != "Manual" else None
            )

            ex_rate = usd_rate if ma.currency == "USD" else 1.0
            value_krw = ma.current_price * ma.quantity * ex_rate
            cost_krw = ma.buy_price * ma.quantity * ex_rate

            upsert_snapshot(
                db, date=today, instrument_id=instrument.id,
                snapshot_time=now, quantity=ma.quantity,
                close_price=ma.current_price, avg_buy_price=ma.buy_price,
                exchange_rate=ex_rate, value_krw=value_krw,
                profit_loss_krw=value_krw - cost_krw
            )

        # ── 5. Update Daily Summary ──
        update_daily_summary(db, today, now)

        db.commit()
        print(f"[{datetime.datetime.now()}] Snapshot saved successfully.")

    except Exception as e:
        print(f"[ERROR] Snapshot failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Market-close snapshots only (no hourly)
    # Domestic market close (~15:30 → snapshot at 15:40)
    scheduler.add_job(snapshot_assets, CronTrigger(hour=15, minute=40), id='domestic_close')

    # US market close (~06:00 KST → snapshot at 06:10)
    scheduler.add_job(snapshot_assets, CronTrigger(hour=6, minute=10), id='overseas_close')

    scheduler.start()
    print("Scheduler started (market-close snapshots only).")

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()

"""Period returns API with benchmark comparison."""
from datetime import datetime, timedelta, date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database.engine import get_db
from src.database.models import DailySummary, DailyPortfolioSnapshot, Instrument
from src.api.fetch_benchmarks import get_kospi_history, get_sp500_history, get_nasdaq_history

# ... imports ...

router = APIRouter(prefix="/api/returns", tags=["returns"])

@router.get("/period")
def get_period_returns(
    period: str = Query("1M", description="Period: 1D, 1W, 1M, 3M, YTD, 1Y, custom"),
    start_date: Optional[str] = Query(None, description="Start date for custom period (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for custom period (YYYY-MM-DD)"),
    group_by: str = Query("total", description="Group by: total, instrument, brokerage"),
    benchmark: str = Query("both", description="Benchmark: kospi, sp500, nasdaq, both, all, none"), # Updated description
    db: Session = Depends(get_db)
):
    """
    Get period returns with benchmark comparison.
    Iterates through the full requested period to show benchmark data even if portfolio data is missing.
    """
    try:
        start, end = get_period_dates(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 1. Fetch Portfolio Data
    summaries = db.query(DailySummary).filter(
        DailySummary.date.between(start, end)
    ).order_by(DailySummary.date).all()
    
    # Map portfolio data by date string
    portfolio_map = {str(s.date): s for s in summaries}
    
    # Determine portfolio start/end values IF data exists
    start_value = 0
    end_value = 0
    profit_loss = 0
    portfolio_return_pct = 0
    
    if summaries:
        start_value = summaries[0].total_asset_krw
        end_value = summaries[-1].total_asset_krw
        profit_loss = end_value - start_value
        portfolio_return_pct = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0

    # Calculate portfolio start/end dates from actual data found
    portfolio_start_date = str(summaries[0].date) if summaries else None
    
    # 2. Fetch Benchmark Data (Real-time / Cached) for FULL period
    full_start_date = str(start)
    full_end_date = str(end)
    
    kospi_data = None
    sp500_data = None
    nasdaq_data = None
    
    # helper to find closest value on or before date
    def get_value_on_or_before(data, target_date_str):
        if data is None or data.empty: return None
        if target_date_str in data.index:
             return data[target_date_str]
        # Filter dates <= target
        past_data = data[data.index <= target_date_str]
        if not past_data.empty:
            return past_data.iloc[-1]
        # If no past data, try finding first future data? 
        # Or just return first available (might be slightly after)
        return data.iloc[0]

    # Always fetch all if not 'none' to support flexible frontend toggling
    if benchmark != "none":
        try:
            kospi_data = get_kospi_history(full_start_date, full_end_date)
        except Exception as e:
            print(f"KOSPI fetch error: {e}")
            
        try:
            sp500_data = get_sp500_history(full_start_date, full_end_date)
        except Exception as e:
            print(f"S&P500 fetch error: {e}")

        try:
            nasdaq_data = get_nasdaq_history(full_start_date, full_end_date)
        except Exception as e:
            print(f"NASDAQ fetch error: {e}")

    # 3. Prepare Response Structure
    response = {
        "period": {
            "start": full_start_date,
            "end": full_end_date
        },
        "portfolio": {
            "start_value": start_value,
            "end_value": end_value,
            "profit_loss": profit_loss,
            "return_pct": portfolio_return_pct
        },
        "benchmarks": {},
        "breakdown": []
    }

    # Helper to calculate return stats for benchmarks (relative to PERIOD START)
    def add_benchmark_stat(key, data):
        if data is not None and not data.empty:
            # Base value at PERIOD START
            start_val = get_value_on_or_before(data, full_start_date)
            # End value at PERIOD END
            end_val = get_value_on_or_before(data, full_end_date)
            
            if start_val and end_val and start_val > 0:
                response["benchmarks"][key] = {
                    "start_value": start_val,
                    "end_value": end_val,
                    "return_pct": ((end_val / start_val) - 1) * 100
                }

    add_benchmark_stat("kospi", kospi_data)
    add_benchmark_stat("sp500", sp500_data)
    add_benchmark_stat("nasdaq", nasdaq_data)

    # 4. Generate Daily Series for Full Period
    daily_series = []
    
    # Generate list of dates from start to end
    current_date = start
    date_list = []
    while current_date <= end:
        date_list.append(current_date)
        current_date += timedelta(days=1)
        
    # Pre-calculate base values for benchmarks (at period start)
    kospi_base = get_value_on_or_before(kospi_data, full_start_date)
    sp500_base = get_value_on_or_before(sp500_data, full_start_date)
    nasdaq_base = get_value_on_or_before(nasdaq_data, full_start_date)

    # Portfolio base: First available summary value (relative to its own start)
    # This means portfolio line starts at 0% when it appears.
    portfolio_base = summaries[0].total_asset_krw if summaries else None

    for d in date_list:
        date_str = str(d)
        daily_point = {"date": date_str}
        
        # Portfolio Data
        if date_str in portfolio_map:
            summary = portfolio_map[date_str]
            daily_point["portfolio_value"] = summary.total_asset_krw
            if portfolio_base and portfolio_base > 0:
                daily_point["portfolio_return"] = ((summary.total_asset_krw / portfolio_base) - 1) * 100
        else:
            # No portfolio data for this day
            daily_point["portfolio_value"] = None
            daily_point["portfolio_return"] = None

        # Benchmark Data
        def add_bench_point(key, data, base):
            if data is not None and base and base > 0:
                if date_str in data.index:
                    val = data[date_str]
                    daily_point[f"{key}_return"] = ((val / base) - 1) * 100
                else:
                    # Optional: Fill forward for weekends implicitly? 
                    # Or rely on Recharts connectNulls if we want continuous lines.
                    # But actually Recharts line chart with missing data points simply draws line between existing points if connectNulls is true?
                    # Or if we omit the key?
                    # If we set "kospi_return" key only when data exists.
                    pass
        
        add_bench_point("kospi", kospi_data, kospi_base)
        add_bench_point("sp500", sp500_data, sp500_base)
        add_bench_point("nasdaq", nasdaq_data, nasdaq_base)
        
        # Only add point if we have at least some data (portfolio or any benchmark)
        # This filters out weekends/holidays where no market was open
        has_data = False
        if daily_point.get("portfolio_value") is not None: has_data = True
        if "kospi_return" in daily_point: has_data = True
        if "sp500_return" in daily_point: has_data = True
        if "nasdaq_return" in daily_point: has_data = True
        
        if has_data:
            daily_series.append(daily_point)
    
    response["daily_series"] = daily_series

    # Add breakdown if requested
    if group_by == "instrument":
        response["breakdown"] = get_instrument_breakdown(db, start, end)
    elif group_by == "brokerage":
        response["breakdown"] = get_brokerage_breakdown(db, start, end)
        
    return response




def get_period_dates(period: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Calculate start/end dates based on period type."""
    today = date.today()
    
    if period == "custom":
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="custom period requires start_date and end_date")
        return datetime.strptime(start_date, "%Y-%m-%d").date(), \
               datetime.strptime(end_date, "%Y-%m-%d").date()
    
    period_map = {
        "1D": timedelta(days=1),
        "1W": timedelta(weeks=1),
        "1M": timedelta(days=30),
        "3M": timedelta(days=90),
        "6M": timedelta(days=180),
        "1Y": timedelta(days=365),
    }
    
    if period == "YTD":
        return date(today.year, 1, 1), today
    elif period == "MTD":
        return date(today.year, today.month, 1), today
    else:
        delta = period_map.get(period, timedelta(days=30))
        return today - delta, today


def get_instrument_breakdown(db: Session, start: date, end: date):
    """Get per-instrument breakdown for the period."""
    # Get first and last snapshot for each instrument
    instruments = db.query(Instrument).all()
    breakdown = []
    
    for inst in instruments:
        start_snap = db.query(DailyPortfolioSnapshot).filter(
            DailyPortfolioSnapshot.instrument_id == inst.id,
            DailyPortfolioSnapshot.date >= start
        ).order_by(DailyPortfolioSnapshot.date).first()
        
        end_snap = db.query(DailyPortfolioSnapshot).filter(
            DailyPortfolioSnapshot.instrument_id == inst.id,
            DailyPortfolioSnapshot.date <= end
        ).order_by(DailyPortfolioSnapshot.date.desc()).first()
        
        if start_snap and end_snap:
            start_value = start_snap.value_krw
            end_value = end_snap.value_krw
            profit_loss = end_value - start_value
            return_pct = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0
            
            breakdown.append({
                "name": inst.name,
                "symbol": inst.symbol,
                "start_value": start_value,
                "end_value": end_value,
                "profit_loss": profit_loss,
                "return_pct": return_pct
            })
    
    return sorted(breakdown, key=lambda x: x['return_pct'], reverse=True)


def get_brokerage_breakdown(db: Session, start: date, end: date):
    """Get per-brokerage breakdown for the period."""
    # Group snapshots by brokerage
    brokerages = db.query(Instrument.brokerage).distinct().all()
    breakdown = []
    
    for (brokerage,) in brokerages:
        if not brokerage:
            continue
            
        # Get all instruments for this brokerage
        inst_ids = [i.id for i in db.query(Instrument).filter(Instrument.brokerage == brokerage).all()]
        
        # Sum up start and end values
        start_value = sum([
            snap.value_krw for snap in db.query(DailyPortfolioSnapshot).filter(
                DailyPortfolioSnapshot.instrument_id.in_(inst_ids),
                DailyPortfolioSnapshot.date >= start
            ).order_by(DailyPortfolioSnapshot.date).limit(len(inst_ids)).all()
        ])
        
        end_value = sum([
            snap.value_krw for snap in db.query(DailyPortfolioSnapshot).filter(
                DailyPortfolioSnapshot.instrument_id.in_(inst_ids),
                DailyPortfolioSnapshot.date <= end
            ).order_by(DailyPortfolioSnapshot.date.desc()).limit(len(inst_ids)).all()
        ])
        
        if start_value > 0:
            profit_loss = end_value - start_value
            return_pct = ((end_value / start_value) - 1) * 100
            
            breakdown.append({
                "name": brokerage,
                "start_value": start_value,
                "end_value": end_value,
                "profit_loss": profit_loss,
                "return_pct": return_pct
            })
    
    return sorted(breakdown, key=lambda x: x['return_pct'], reverse=True)


@router.get("/period")
def get_period_returns(
    period: str = Query("1M", description="Period: 1D, 1W, 1M, 3M, YTD, 1Y, custom"),
    start_date: Optional[str] = Query(None, description="Start date for custom period (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for custom period (YYYY-MM-DD)"),
    group_by: str = Query("total", description="Group by: total, instrument, brokerage"),
    benchmark: str = Query("both", description="Benchmark: kospi, sp500, both, none"),
    db: Session = Depends(get_db)
):
    """
    Get period returns with benchmark comparison.
    
    Returns:
        - period: start and end dates
        - portfolio: portfolio summary (start/end value, return %)
        - benchmarks: KOSPI and S&P 500 returns
        - breakdown: per-instrument or per-brokerage breakdown
        - daily_series: daily data for charting
    """
    try:
        start, end = get_period_dates(period, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Get daily summary for total portfolio
    summaries = db.query(DailySummary).filter(
        DailySummary.date.between(start, end)
    ).order_by(DailySummary.date).all()
    
    if not summaries:
        raise HTTPException(status_code=404, detail="No data available for the specified period")
    
    start_value = summaries[0].total_asset_krw
    end_value = summaries[-1].total_asset_krw
    profit_loss = end_value - start_value
    portfolio_return_pct = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0
    
    # Prepare response
    response = {
        "period": {
            "start": str(start),
            "end": str(end)
        },
        "portfolio": {
            "start_value": start_value,
            "end_value": end_value,
            "profit_loss": profit_loss,
            "return_pct": portfolio_return_pct
        }
    }
    
    # Add benchmark data if requested
    if benchmark != "none":
        benchmarks = {}
        
        if benchmark in ["kospi", "both"]:
            kospi_start = summaries[0].kospi_close
            kospi_end = summaries[-1].kospi_close
            if kospi_start and kospi_end:
                benchmarks["kospi"] = {
                    "start_value": kospi_start,
                    "end_value": kospi_end,
                    "return_pct": ((kospi_end / kospi_start) - 1) * 100
                }
        
        if benchmark in ["sp500", "both"]:
            sp500_start = summaries[0].sp500_close
            sp500_end = summaries[-1].sp500_close
            if sp500_start and sp500_end:
                benchmarks["sp500"] = {
                    "start_value": sp500_start,
                    "end_value": sp500_end,
                    "return_pct": ((sp500_end / sp500_start) - 1) * 100
                }
        
        response["benchmarks"] = benchmarks
    
    # Add breakdown if requested
    if group_by == "instrument":
        response["breakdown"] = get_instrument_breakdown(db, start, end)
    elif group_by == "brokerage":
        response["breakdown"] = get_brokerage_breakdown(db, start, end)
    
    # Build daily series for charting
    daily_series = []
    for summary in summaries:
        daily_point = {
            "date": str(summary.date),
            "portfolio_value": summary.total_asset_krw,
            "portfolio_return": ((summary.total_asset_krw / start_value) - 1) * 100 if start_value > 0 else 0
        }
        
        if benchmark in ["kospi", "both"] and summary.kospi_close and summaries[0].kospi_close:
            daily_point["kospi_return"] = ((summary.kospi_close / summaries[0].kospi_close) - 1) * 100
        
        if benchmark in ["sp500", "both"] and summary.sp500_close and summaries[0].sp500_close:
            daily_point["sp500_return"] = ((summary.sp500_close / summaries[0].sp500_close) - 1) * 100
        
        daily_series.append(daily_point)
    
    response["daily_series"] = daily_series
    
    return response

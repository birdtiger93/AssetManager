from datetime import date
from sqlalchemy import func

def calculate_simple_return(current_value, invested_capital):
    if invested_capital == 0:
        return 0.0
    return (current_value - invested_capital) / invested_capital * 100.0

def calculate_twr(daily_records):
    """
    Calculate Time-Weighted Return (TWR) from a list of DailySummary records.
    daily_records: list of dict or object having 'total_asset_krw', 'net_investment_krw', 'prev_total' (inferred)
    
    Formula: TWR = (1 + r1) * (1 + r2) * ... * (1 + rn) - 1
    where ri = (Vi - (Vi-1 + CFi)) / (Vi-1 + CFi)  (Simple Dietz per period where flow happens at start)
    Or more accurately: ri = (Vi - Vi-1 - CFi) / (Vi-1) if flow happens at end?
    
    Standard approach: Chain periodic returns.
    """
    if not daily_records:
        return 0.0
        
    twr = 1.0
    
    # Sort by date
    sorted_records = sorted(daily_records, key=lambda x: x.date)
    
    prev_val = 0.0
    prev_invest = 0.0

    for i, rec in enumerate(sorted_records):
        curr_val = rec.total_asset_krw
        curr_invest = rec.net_investment_krw
        
        # Cash Flow = Change in Net Investment
        cash_flow = curr_invest - prev_invest
        
        if prev_val == 0:
            # First day, return is 0 or undefined. Start tracking from here.
            pass
        else:
            # Calculate daily return excluding cash flow
            # Assumption: Cash flow happens at start of day (denominator increases)
            # return = (EndValue - StartValue - CashFlow) / (StartValue + CashFlow)
            # Or if Cash flow happens at end: (EndValue - CashFlow - StartValue) / StartValue
            
            # Let's use: Return = (V_end - V_start - CF) / (V_start + (CF * weight))
            # For daily data, usually safe to assume CF at start or end.
            # If we assume CF at START of day:
            # ri = (V_end - (V_prev + CF)) / (V_prev + CF)
            #    = (V_end / (V_prev + CF)) - 1
            
            denom = prev_val + cash_flow
            if denom != 0:
                r_i = (curr_val / denom) - 1
                twr *= (1 + r_i)
        
        prev_val = curr_val
        prev_invest = curr_invest
        
    return (twr - 1) * 100.0

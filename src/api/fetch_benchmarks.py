import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache

# Cache for 1 hour
@lru_cache(maxsize=4)
def get_benchmark_history(symbol: str, start_date: str, end_date: str):
    """
    Fetch historical data for a benchmark symbol using yfinance.
    Returns a pandas Series of closing prices indexed by date (string YYYY-MM-DD).
    """
    try:
        # Fetch data
        print(f"Fetching benchmark data for {symbol} from {start_date} to {end_date}")
        
        # yfinance expects YYYY-MM-DD
        # Add buffer to start date to ensure we have the start value
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        buffered_start = (start_dt - timedelta(days=5)).strftime("%Y-%m-%d")
        
        # Convert end_date to inclusive (yfinance end is exclusive)
        # Add buffer for time zone differences
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        buffered_end = (end_dt + timedelta(days=2)).strftime("%Y-%m-%d")

        data = yf.download(symbol, start=buffered_start, end=buffered_end, progress=False)
        
        if data.empty:
            print(f"No data found for {symbol}")
            return pd.Series(dtype=float)
        
        # Handle data structure (yfinance recent update returns MultiIndex columns)
        close_data = None
        if isinstance(data.columns, pd.MultiIndex):
            # Try to find ('Close', symbol)
            if ('Close', symbol) in data.columns:
                close_data = data[('Close', symbol)]
            elif 'Close' in data.columns.levels[0]:
                 # Maybe just 'Close' level exists but symbol mismatch? unlikely for single download
                 try:
                    close_data = data['Close'][symbol]
                 except:
                    close_data = data['Close'].iloc[:, 0] # Fallback to first column
        elif 'Close' in data.columns:
            close_data = data['Close']
        else:
            # Maybe just one column if 'Adj Close' wasn't requested?
            close_data = data.iloc[:, 0]

        if close_data is None:
            return pd.Series(dtype=float)

        # Standardize index to string YYYY-MM-DD
        close_data.index = close_data.index.strftime("%Y-%m-%d")
        
        # Filter for requested range (strict)
        # But we need previous close for calculation? Just return range covering request
        return close_data

    except Exception as e:
        print(f"Error fetching benchmark {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return pd.Series(dtype=float)

def get_kospi_history(start_date: str, end_date: str):
    # KOSPI symbol in Yahoo Finance: ^KS11
    return get_benchmark_history("^KS11", start_date, end_date)

def get_sp500_history(start_date: str, end_date: str):
    # S&P 500 symbol in Yahoo Finance: ^GSPC
    return get_benchmark_history("^GSPC", start_date, end_date)

def get_nasdaq_history(start_date: str, end_date: str):
    # NASDAQ Composite symbol in Yahoo Finance: ^IXIC
    return get_benchmark_history("^IXIC", start_date, end_date)

if __name__ == "__main__":
    # Test
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print("Testing KOSPI...")
    kospi = get_kospi_history(week_ago, today)
    print(kospi)
    
    print("\nTesting S&P 500...")
    sp500 = get_sp500_history(week_ago, today)
    print(sp500)

    print("\nTesting NASDAQ...")
    nasdaq = get_nasdaq_history(week_ago, today)
    print(nasdaq)

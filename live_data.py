import yfinance as yf
import pandas as pd
import os

def fetch_and_clean(ticker, period="1y"): 
    """
    Fetches data for a SINGLE ticker, cleans it, and saves/returns it.
    Now supports dynamic time horizons (e.g., '1mo', '1y', '5y').
    """
    print(f"--- Fetching data for {ticker} (Period: {period}) ---")
    try:
        # Fetch data using the dynamic period requested by the user
        data = yf.download(ticker, period=period, interval="1d")
        
        if data.empty:
            return None
        
        # Handling MultiIndex if yfinance returns it
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten columns
            data.columns = data.columns.droplevel(1) 
            
        data = data.reset_index()
        
        # Standardize Columns
        required_cols = {'Date', 'Close', 'Volume', 'Open', 'High', 'Low'}
        data.rename(columns={'Date': 'Date', 'Close': 'Close', 'Volume': 'Volume', 'Open':'Open', 'High':'High', 'Low':'Low'}, inplace=True)
        
        # Check if we have the columns we need
        if not required_cols.issubset(data.columns):
            print(f"Missing columns for {ticker}")
            return None

        # Clean
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date')
        
        # Save to CSV for the Risk Engine to read later
        filename = f"cleaned_{ticker.replace('-','_')}_daily_data.csv"
        data.to_csv(filename, index=False)
        return filename

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None
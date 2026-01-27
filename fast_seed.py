import requests
import time
import live_data
import risk_engine
import concurrent.futures
import socket
import sys

def is_connected():
    """Checks for active internet connection"""
    try:
        # Try to connect to Google's DNS server to test connection
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Optimized for speed: uses threading to fetch data in parallel
def fetch_and_analyze_wrapper(ticker):
    """Wrapper to run fetch and analyze in a single thread"""
    try:
        # 1. Fetch
        if live_data.fetch_and_clean(ticker, period="1y"):
            # 2. Analyze
            risk_engine.run_analysis(ticker)
            return f"✅ {ticker}"
    except Exception:
        return f"❌ {ticker}"
    return f"⚠️ {ticker} (No Data)"

def get_dynamic_top_coins(limit=12):
    """Fast fetch from CoinGecko with hard timeout"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit, "page": 1}
        response = requests.get(url, params=params, timeout=2) 
        data = response.json()
        return [f"{coin['symbol'].upper()}-USD" for coin in data]
    except:
        print("   (API Slow/Down - Using Backup List for Speed)")
        return ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", 
                "ADA-USD", "AVAX-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "SHIB-USD"]

if __name__ == "__main__":
    print("--- ⚡ SEED INITIATED ---")
    
    # 1. ROBUST INTERNET CHECK
    if not is_connected():
        print("\n" + "="*50)
        print("❌ CRITICAL ERROR: NO INTERNET CONNECTION")
        print("="*50)
        print("The system cannot fetch live market data without internet.")
        print("Please connect to Wi-Fi and try again.")
        print("="*50)
        # This input() pauses the script, stopping the .bat file from proceeding
        input("\nPress Enter to Exit...") 
        sys.exit(1) # Helper code to tell the computer 'we failed'

    start_time = time.time()
    
    # 2. Get List (Fast)
    tickers = get_dynamic_top_coins()
    
    # 3. Parallel Processing
    print(f"   🔥 Processing {len(tickers)} assets in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(fetch_and_analyze_wrapper, tickers))
    
    elapsed = time.time() - start_time
    print(f"--- 🚀 DONE in {elapsed:.2f} seconds! ---")
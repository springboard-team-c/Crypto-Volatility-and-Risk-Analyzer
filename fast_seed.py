import requests
import time
import live_data
import risk_engine
import concurrent.futures

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
        # Strict 2-second timeout. If CoinGecko is slow, we use the backup list instantly.
        response = requests.get(url, params=params, timeout=2) 
        data = response.json()
        return [f"{coin['symbol'].upper()}-USD" for coin in data]
    except:
        print("   (API Slow/Down - Using Backup List for Speed)")
        return ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", 
                "ADA-USD", "AVAX-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "SHIB-USD"]

if __name__ == "__main__":
    start_time = time.time()
    print("--- ⚡ INSTANT SEED INITIATED ---")
    
    # 1. Get List (Fast)
    tickers = get_dynamic_top_coins()
    
    # 2. Parallel Processing (The Secret to <4s speed)
    print(f"   🔥 Processing {len(tickers)} assets in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(fetch_and_analyze_wrapper, tickers))
    
    elapsed = time.time() - start_time
    print(f"--- 🚀 DONE in {elapsed:.2f} seconds! ---")
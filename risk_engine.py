import pandas as pd
import numpy as np
import glob
from sklearn.cluster import KMeans

# Define "Baseline" coins that define the market structure
BASELINE_COINS = ["cleaned_BTC_USD_daily_data.csv", "cleaned_ETH_USD_daily_data.csv"]

def calculate_single_metrics(file_path):
    """Calculates volatility, drawdown, var for a single CSV"""
    try:
        df = pd.read_csv(file_path)
        df['Daily_Return'] = df['Close'].pct_change()
        df = df.dropna()
        
        # 1. Volatility
        volatility = df['Daily_Return'].std() * np.sqrt(365)
        
        # 2. Max Drawdown
        cumulative = (1 + df['Daily_Return']).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        
        # 3. VaR 95%
        var_95 = np.percentile(df['Daily_Return'], 5)
        
        return volatility, max_drawdown, var_95
    except Exception as e:
        print(f"Error calculating metrics for {file_path}: {e}")
        return 0, 0, 0

def run_analysis(target_ticker):
    """
    1. Loads baseline data.
    2. Loads target ticker data.
    3. Runs ML Clustering on the combined set.
    4. Returns the specific stats for the target ticker.
    """
    # Identify the target file
    target_file = f"cleaned_{target_ticker.replace('-','_')}_daily_data.csv"
    
    # Gather all available CSVs (Baseline + The New One)
    all_files = list(set(glob.glob("cleaned_*_daily_data.csv") + [target_file]))
    
    results = []
    
    # Calculate metrics for ALL coins (to build the cluster map)
    for file in all_files:
        asset_name = file.replace("cleaned_", "").replace("_daily_data.csv", "").replace("_", "-")
        vol, dd, var = calculate_single_metrics(file)
        
        # Score Logic
        score = (vol * 30) + (abs(dd) * 40) + (abs(var) * 100 * 5)
        risk_score = min(score, 100)
        
        results.append({
            "Asset": asset_name,
            "Volatility_Ann": vol,
            "Max_Drawdown": dd,
            "VaR_95": var,
            "Risk_Score": risk_score
        })

    df = pd.DataFrame(results)
    
    # --- ML CLUSTERING ---
    # We need at least 3 coins to form clusters. 
    if len(df) >= 3:
        features = df[['Volatility_Ann', 'Max_Drawdown', 'VaR_95']]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['Cluster_Group'] = kmeans.fit_predict(features)
    else:
        df['Cluster_Group'] = 0

    # Logic: Math to English
    def interpret(row):
        if row['Risk_Score'] > 75: return "High Risk / Speculative"
        if row['Risk_Score'] > 40: return "Medium Risk / Balanced"
        return "Low Risk / Conservative"
    
    df['Risk_Category'] = df.apply(interpret, axis=1)
    
    # Save globally for the dashboard
    df.to_csv("crypto_risk_scored.csv", index=False)
    
    # Return ONLY the target coin's data
    target_data = df[df['Asset'] == target_ticker]
    if not target_data.empty:
        return target_data.to_dict(orient='records')[0]
    return None
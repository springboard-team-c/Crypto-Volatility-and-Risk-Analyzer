import pandas as pd
import numpy as np
import glob
from sklearn.cluster import KMeans

# Define "Baseline" coins that define the market structure
BASELINE_COINS = ["cleaned_BTC_USD_daily_data.csv", "cleaned_ETH_USD_daily_data.csv"]

def calculate_single_metrics(file_path):
    """Calculates Core & Risk-Adjusted Metrics"""
    try:
        df = pd.read_csv(file_path)
        df['Daily_Return'] = df['Close'].pct_change()
        df = df.dropna()
        
        # --- 1. CORE METRICS ---
        volatility = df['Daily_Return'].std() * np.sqrt(365) # Annualized Volatility
        
        cumulative = (1 + df['Daily_Return']).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min() # Max Drawdown
        
        var_95 = np.percentile(df['Daily_Return'], 5) # Value at Risk (95%)
        
        # --- 2. RISK-ADJUSTED METRICS (NEW) ---
        # Sharpe Ratio: (Return - RiskFree) / Volatility
        # We assume Risk Free rate is ~4% (0.04)
        avg_annual_return = df['Daily_Return'].mean() * 365
        risk_free_rate = 0.04 
        sharpe_ratio = (avg_annual_return - risk_free_rate) / volatility if volatility != 0 else 0
        
        return volatility, max_drawdown, var_95, sharpe_ratio, avg_annual_return
        
    except Exception as e:
        print(f"Error calculating metrics for {file_path}: {e}")
        return 0, 0, 0, 0, 0

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
        vol, dd, var, sharpe, ret = calculate_single_metrics(file)
        
        # Score Logic
        score = (vol * 30) + (abs(dd) * 40) + (abs(var) * 100 * 5)
        risk_score = min(score, 100)
        
        results.append({
            "Asset": asset_name,
            "Volatility_Ann": round(vol, 4),
            "Max_Drawdown": round(dd, 4),
            "VaR_95": round(var, 4),
            "Sharpe_Ratio": round(sharpe, 2),        # <--- NEW METRIC
            "Annual_Return": round(ret, 2),          # <--- CONTEXT
            "Risk_Score": round(risk_score, 2)
        })

    df = pd.DataFrame(results)
    
    # --- ML CLUSTERING ---
    # We need at least 3 coins to form clusters. 
    if len(df) >= 3:
        # We now include Sharpe Ratio in the clustering logic (Smarter grouping)
        features = df[['Volatility_Ann', 'Max_Drawdown', 'Sharpe_Ratio']]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['Cluster_Group'] = kmeans.fit_predict(features)
    else:
        df['Cluster_Group'] = 0

    # Logic: Math to English (INSIGHTS EXPLANATION ENGINE)
    def interpret(row):
        insights = []
        
        # 1. THE VERDICT (The "What")
        if row['Risk_Score'] > 75:
            insights.append(f"<b>VERDICT: HIGH RISK.</b> This coin is highly speculative and unstable.")
        elif row['Risk_Score'] > 40:
            insights.append(f"<b>VERDICT: BALANCED.</b> This coin shows a mix of stability and growth potential.")
        else:
            insights.append(f"<b>VERDICT: CONSERVATIVE.</b> This is one of the safest assets in the crypto market.")

        # 2. VOLATILITY EXPLANATION (The "Why")
        vol_pct = row['Volatility_Ann'] * 100
        if row['Volatility_Ann'] > 1.0:
            insights.append(f"It is experiencing wild price swings ({vol_pct:.0f}% annualized). Be prepared for the price to double or crash within weeks.")
        elif row['Volatility_Ann'] > 0.5:
             insights.append(f"The price moves significantly ({vol_pct:.0f}% annualized), offering good trading opportunities but higher risk.")
        else:
             insights.append(f"It is relatively calm compared to other cryptos, making it suitable for steady holding.")

        # 3. CRASH HISTORY (The Warning)
        drawdown_pct = abs(row['Max_Drawdown']) * 100
        if row['Max_Drawdown'] < -0.70:
            insights.append(f"<b>Caution:</b> It has a history of crashing hard, having lost {drawdown_pct:.0f}% of its value in the past. Only invest what you can afford to lose.")
        elif row['Max_Drawdown'] > -0.30:
            insights.append("It has proven resilient, recovering well even during market dips.")

        # 4. SHARPE RATIO CONTEXT (Risk-Adjusted Return)
        if row['Sharpe_Ratio'] > 1.5:
             insights.append(f"<b>Good News:</b> It has an excellent Sharpe Ratio ({row['Sharpe_Ratio']}), meaning you are getting high returns for the risk you take.")
        elif row['Sharpe_Ratio'] < 0:
             insights.append(f"<b>Note:</b> The risk-adjusted performance is poor (Sharpe: {row['Sharpe_Ratio']}); it is currently losing money relative to its volatility.")

        return " ".join(insights)

    df['Risk_Category'] = df.apply(interpret, axis=1)
    
    # Save globally for the dashboard
    df.to_csv("crypto_risk_scored.csv", index=False)
    
    # Return ONLY the target coin's data
    target_data = df[df['Asset'] == target_ticker]
    if not target_data.empty:
        return target_data.to_dict(orient='records')[0]
    return None
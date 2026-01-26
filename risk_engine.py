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
        # Annualized Volatility (Standard Deviation * sqrt(365))
        volatility = df['Daily_Return'].std() * np.sqrt(365)
        
        # Max Drawdown (Peak to Trough)
        cumulative = (1 + df['Daily_Return']).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% Confidence)
        var_95 = np.percentile(df['Daily_Return'], 5)
        
        # --- 2. RISK-ADJUSTED METRICS ---
        # Sharpe Ratio: (Return - RiskFree) / Volatility
        # We assume a standard Risk Free rate of ~4% (0.04)
        avg_annual_return = df['Daily_Return'].mean() * 365
        risk_free_rate = 0.04 
        sharpe_ratio = (avg_annual_return - risk_free_rate) / volatility if volatility != 0 else 0
        
        return volatility, max_drawdown, var_95, sharpe_ratio, avg_annual_return
        
    except Exception as e:
        print(f"Error calculating metrics for {file_path}: {e}")
        # BUG FIX: Must return 5 values to match the unpack expectation below
        return 0, 0, 0, 0, 0

def run_analysis(target_ticker):
    """
    Runs the full Risk Pipeline: Data Load -> Math -> Clustering -> Narrative
    """
    target_file = f"cleaned_{target_ticker.replace('-','_')}_daily_data.csv"
    
    # Gather all available CSVs (Baseline + The New One)
    all_files = list(set(glob.glob("cleaned_*_daily_data.csv") + [target_file]))
    
    results = []
    
    for file in all_files:
        asset_name = file.replace("cleaned_", "").replace("_daily_data.csv", "").replace("_", "-")
        
        # Unpack the 5 metrics calculated above
        vol, dd, var, sharpe, ret = calculate_single_metrics(file)
        
        # Score Logic (Weighted Average)
        score = (vol * 30) + (abs(dd) * 40) + (abs(var) * 100 * 5)
        risk_score = min(score, 100)
        
        results.append({
            "Asset": asset_name,
            "Volatility_Ann": round(vol, 4),
            "Max_Drawdown": round(dd, 4),
            "VaR_95": round(var, 4),
            "Sharpe_Ratio": round(sharpe, 2),
            "Annual_Return": round(ret, 2),
            "Risk_Score": round(risk_score, 2)
        })

    df = pd.DataFrame(results)
    
    # --- ML CLUSTERING ---
    # We need at least 3 coins to form meaningful clusters
    if len(df) >= 3:
        features = df[['Volatility_Ann', 'Max_Drawdown', 'Sharpe_Ratio']]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['Cluster_Group'] = kmeans.fit_predict(features)
    else:
        df['Cluster_Group'] = 0

  # ==============================================================================
    #  THE "BEGINNER-FRIENDLY" NARRATIVE ENGINE (Markdown Version)
    # ==============================================================================
    def interpret(row):
        insights = []
        
        # 1. THE VERDICT (The Headline)
        if row['Risk_Score'] > 75:
            insights.append(f"**VERDICT: HIGH RISK.** This asset is highly speculative.")
        elif row['Risk_Score'] > 40:
            insights.append(f"**VERDICT: BALANCED.** This asset shows moderate stability.")
        else:
            insights.append(f"**VERDICT: CONSERVATIVE.** This is a relatively safe asset.")

        # 2. SHARPE RATIO (Efficiency)
        sharpe = row['Sharpe_Ratio']
        if sharpe > 1.5:
             insights.append(f"**Sharpe Ratio ({sharpe}):** This metric tells you if the returns are worth the risk. A high score (>1.5) like this means you are getting excellent returns for every unit of risk you take.")
        elif sharpe > 0:
             insights.append(f"**Sharpe Ratio ({sharpe}):** This metric tells you if the returns are worth the risk. This score is decent, meaning you are being fairly compensated for the volatility.")
        else:
             insights.append(f"**Sharpe Ratio ({sharpe}):** This metric compares return vs. risk. A negative score means the asset is currently underperforming—you are taking risk but losing money.")

        # 3. VOLATILITY (The Jitters)
        vol_pct = row['Volatility_Ann'] * 100
        if row['Volatility_Ann'] > 1.0:
            insights.append(f"**Annual Volatility ({vol_pct:.0f}%):** This measures how violently the price moves. This is extremely high, meaning the price could double or crash in a very short time.")
        else:
             insights.append(f"**Annual Volatility ({vol_pct:.0f}%):** This measures price stability. This asset is relatively calm compared to the rest of the crypto market.")

        # 4. DRAWDOWN (The Worst Case)
        drawdown_pct = abs(row['Max_Drawdown']) * 100
        if row['Max_Drawdown'] < -0.50:
            insights.append(f"**Max Drawdown (-{drawdown_pct:.0f}%):** This shows the biggest crash this asset has ever suffered. A drop this large indicates it has collapsed before, so invest carefully.")
        
        return " ".join(insights)

    df['Risk_Category'] = df.apply(interpret, axis=1)
    
    # Save globally for the dashboard
    df.to_csv("crypto_risk_scored.csv", index=False)
    
    # Return ONLY the target coin's data
    target_data = df[df['Asset'] == target_ticker]
    if not target_data.empty:
        return target_data.to_dict(orient='records')[0]
    return None
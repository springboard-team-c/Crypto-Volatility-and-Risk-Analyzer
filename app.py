from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import glob
import os
import live_data   
import risk_engine 

app = Flask(__name__)
CORS(app)

# ================== HELPER FUNCTIONS ==================
def load_risk_data():
    if os.path.exists("crypto_risk_scored.csv"):
        return pd.read_csv("crypto_risk_scored.csv")
    return pd.DataFrame()

def build_correlation_matrix():
    """Reads all CSVs and calculates how assets move together (PDF Page 12)"""
    files = glob.glob("cleaned_*_daily_data.csv")
    if not files: return None
    
    combined_df = pd.DataFrame()
    
    for file in files:
        ticker = file.replace("cleaned_", "").replace("_daily_data.csv", "").replace("_", "-")
        df = pd.read_csv(file)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # We only care about Close price for correlation
        combined_df[ticker] = df['Close']
    
    # Calculate Correlation Matrix (Returns values between -1 and 1)
    return combined_df.pct_change().corr()

# ================== API ENDPOINTS ==================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Backend Active (100% Completed)", 
        "endpoints": ["/api/analyze", "/api/metrics", "/api/stress-test", "/api/correlation"]
    })

@app.route("/api/analyze", methods=["POST"])
def analyze_coin():
    """Triggers the full Live Data -> Risk Engine -> ML Pipeline"""
    data = request.get_json()
    ticker = data.get("ticker", "").upper()
    if not ticker: return jsonify({"error": "No ticker provided"}), 400

    print(f"--- Analyzing {ticker} ---")
    if live_data.fetch_and_clean(ticker):
        result = risk_engine.run_analysis(ticker)
        return jsonify({"success": True, "data": result})
    
    return jsonify({"error": "Fetch failed"}), 500

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Returns the Risk Leaderboard"""
    df = load_risk_data()
    return jsonify(df.to_dict(orient="records"))
    
@app.route("/api/stress-test", methods=["GET", "POST"])
def stress_test():
    """
    (PDF Page 13) Simulates portfolio crash.
    Supports POST (JSON) and GET (Browser defaults).
    """
    # 1. Handle Input (GET or POST)
    if request.method == "POST":
        data = request.get_json()
    else:
        # If accessing via Browser (GET), use defaults or URL params
        data = {
            "investment": request.args.get("investment", 1000),
            "drop_percentage": request.args.get("drop_percentage", 0.20)
        }
        
    investment = float(data.get("investment", 1000))
    drop = float(data.get("drop_percentage", 0.20))
    
    # 2. Run Simulation
    df = load_risk_data()
    if df.empty:
        return jsonify({"error": "No data found. Run /api/analyze first."}), 404

    results = []
    
    for _, row in df.iterrows():
        # High Volatility assets (Cluster 2) suffer 1.5x more in a crash
        multiplier = 1.5 if row.get('Cluster_Group') == 2 else 1.0
        
        actual_loss_pct = drop * multiplier
        loss_amount = investment * actual_loss_pct
        
        results.append({
            "Asset": row['Asset'],
            "Scenario_Drop": f"{drop*100}%",
            "Projected_Loss": round(loss_amount, 2),
            "Remaining_Value": round(investment - loss_amount, 2),
            "Risk_Multiplier": multiplier
        })
    
    return jsonify(results)

@app.route("/api/correlation", methods=["GET"])
def get_correlation():
    """(PDF Page 12) Returns the correlation matrix as JSON"""
    matrix = build_correlation_matrix()
    if matrix is not None:
        # Convert to a format suitable for Heatmaps (JSON)
        return jsonify(matrix.to_dict())
    return jsonify({"error": "Not enough data"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
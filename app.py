from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# ================== LOAD FINAL TEAM OUTPUT ==================
CSV_FILE = "crypto_risk_scored.csv"

def load_data():
    df = pd.read_csv(CSV_FILE)
    return df

# ================== ENDPOINTS ==================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Crypto Volatility and Risk Analyzer Backend is running",
        "status": "All endpoints are connected successfully",
         "available_endpoints": {
            "Health Check": "/health",
            "All Metrics": "/metrics",
            "Asset Metrics": "/metrics?asset=BTC",
            "Asset Risk": "/asset-risk?asset=ETH"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "message": "Backend health check successful"
    })

@app.route("/metrics", methods=["GET"])
def metrics():
    df = load_data()
    return jsonify(df.to_dict(orient="records"))

@app.route("/asset-risk", methods=["GET"])
def asset_risk():
    df = load_data()
    return jsonify(dict(zip(df["Asset"], df["Risk_Category"])))

@app.route("/risk-score", methods=["GET"])
def risk_score():
    df = load_data()
    return jsonify(dict(zip(df["Asset"], df["Risk_Score"])))

# ================== RUN ==================
if __name__ == "__main__":
    print("Backend running | All endpoints connected")
    app.run(debug=True)

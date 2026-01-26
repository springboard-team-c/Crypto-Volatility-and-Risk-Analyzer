import streamlit as st
import requests
import pandas as pd
import time

# CONFIGURATION
API_URL = "http://127.0.0.1:5000/api"
st.set_page_config(page_title="Crypto Risk Analyzer", layout="wide")

# TITLE
st.title("🚀 Crypto Volatility & Risk Analyzer")
st.markdown("### Team C | Infosys Springboard Internship")

# SIDEBAR - SELECTION
st.sidebar.header("⚙️ Analysis Settings")

# 1. PREDEFINED LIST OF CRYPTOS (As you requested)
ticker_options = [
    "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "ADA-USD", 
    "XRP-USD", "BNB-USD", "DOT-USD", "MATIC-USD", "LTC-USD"
]

# Allow user to select or type their own
selected_ticker = st.sidebar.selectbox("Select Crypto Asset", ticker_options)
custom_ticker = st.sidebar.text_input("Or type a custom ticker (e.g. PEPE-USD)")

# Final logic: Use custom if typed, otherwise use dropdown
ticker = custom_ticker.upper() if custom_ticker else selected_ticker

# Time Horizon
period = st.sidebar.select_slider(
    "Select Time Horizon", 
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
    value="1y"
)

# ANALYZE BUTTON
if st.sidebar.button("🚀 Analyze Risk"):
    with st.spinner(f"Fetching data and calculating risk for {ticker}..."):
        try:
            # CALL FLASK API
            payload = {"ticker": ticker, "period": period}
            response = requests.post(f"{API_URL}/analyze", json=payload)
            
            if response.status_code == 200:
                data = response.json()['data']
                
                # --- SECTION 1: KEY METRICS ---
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Risk Score", f"{data['Risk_Score']}/100")
                col2.metric("Sharpe Ratio", data['Sharpe_Ratio'])
                col3.metric("Annual Volatility", f"{data['Volatility_Ann']*100:.1f}%")
                col4.metric("Max Drawdown", f"{data['Max_Drawdown']*100:.1f}%")
                
                # --- SECTION 2: AI VERDICT ---
                st.subheader("🧠 The Risk Decoder") 
                st.caption("We translated the complex math into plain English for you.")
                
                # Color code the verdict box
                # Note: Streamlit will now automatically render the **bold** markdown correctly
                if data['Risk_Score'] > 75:
                    st.error(data['Risk_Category'], icon="🔥") # Red box with Fire icon
                elif data['Risk_Score'] > 40:
                    st.warning(data['Risk_Category'], icon="⚠️") # Yellow box with Warning icon
                else:
                    st.success(data['Risk_Category'], icon="✅") # Green box with Check icon

                # --- SECTION 3: CHARTS ---
                st.subheader("📈 Visual Analysis")
                chart_col1, chart_col2 = st.columns(2)
                
                # Get History Data for Line Chart
                hist_response = requests.post(f"{API_URL}/history", json={"ticker": ticker})
                if hist_response.status_code == 200:
                    hist_data = pd.DataFrame(hist_response.json())
                    hist_data['Date'] = pd.to_datetime(hist_data['Date'])
                    hist_data.set_index('Date', inplace=True)
                    
                    with chart_col1:
                        st.markdown("**Price History**")
                        st.line_chart(hist_data['Close'])

                # Get Cluster Data for Scatter Plot
                metrics_response = requests.get(f"{API_URL}/metrics")
                if metrics_response.status_code == 200:
                    cluster_data = pd.DataFrame(metrics_response.json())
                    with chart_col2:
                        st.markdown("**Market Risk Map (Clusters)**")
                        st.scatter_chart(
                            cluster_data, 
                            x='Volatility_Ann', 
                            y='Risk_Score', 
                            color='Cluster_Group'
                        )

            else:
                st.error("Error analyzing ticker. Check if the ticker symbol is correct.")

        except Exception as e:
            st.error(f"Connection Error. Is 'app.py' running? \nDetails: {e}")

# --- SECTION 4: STRESS TEST ---
st.divider()
st.header("⚡ Portfolio Stress Test")
st.markdown("Simulate a market crash to see how this asset performs.")

c1, c2, c3 = st.columns(3)
invest_amt = c1.number_input("Investment Amount ($)", value=1000)
drop_pct = c2.selectbox("Scenario", [
    ("Market Correction (-10%)", 0.10),
    ("Bear Market (-20%)", 0.20),
    ("Crash (-50%)", 0.50),
    ("Crypto Winter (-75%)", 0.75)
], format_func=lambda x: x[0])

if c3.button("🔥 Run Simulation"):
    # Call Stress Test API
    st_payload = {"investment": invest_amt, "drop_percentage": drop_pct[1]}
    st_res = requests.post(f"{API_URL}/stress-test", json=st_payload)
    
    if st_res.status_code == 200:
        st_data = pd.DataFrame(st_res.json())
        st.dataframe(st_data, hide_index=True, use_container_width=True)
    else:
        st.error("Could not run stress test. Analyze an asset first.")
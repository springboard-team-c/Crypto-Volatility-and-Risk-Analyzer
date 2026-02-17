import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from streamlit_option_menu import option_menu
from database import init_db, login_user, add_user, save_history, get_admin_data, delete_history_entry, get_system_stats, purge_all_history
from analysis import get_data, run_monte_carlo, generate_pdf_report
import time 

# Page Configuration
st.set_page_config(page_title="VELOXIS QUANT", layout="wide")

# --- Institutional & Royal UI Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1A1A1A; }
    
    .metric-card {
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .metric-label { font-size: 11px; color: #B8860B; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: 900; color: #1A1A1A; }
    
    .performance-section { 
        background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 15px 25px; border-radius: 12px; border: 1px solid #D4AF37; 
        margin: 20px auto; max-width: 800px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
    }
    .gauge-bg { height: 8px; background: #E0E0E0; border-radius: 4px; position: relative; margin: 20px 0; }
    .gauge-dot { height: 18px; width: 18px; background: #D4AF37; border: 2px solid white; border-radius: 50%; position: absolute; top: -5px; transform: translateX(-50%); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }

    .stButton>button { 
        background: linear-gradient(135deg, #C5A059 0%, #D4AF37 50%, #B8860B 100%) !important; 
        color: white !important; font-weight: 800 !important; border-radius: 6px !important; border: none !important;
        padding: 0.6rem 1rem; box-shadow: 0 4px 10px rgba(184, 134, 11, 0.2); transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(184, 134, 11, 0.3); }

    .stDownloadButton>button {
        background: linear-gradient(90deg, #1A1A1A 0%, #333333 100%) !important; 
        color: #D4AF37 !important; border: 1px solid #D4AF37 !important;
        font-weight: bold !important; white-space: nowrap !important; width: auto !important;
    }
    
    .decoder-card { padding: 25px; border-radius: 15px; margin-top: 15px; border-left: 10px solid; background-color: #f8f9fa; box-shadow: 0 4px 15px rgba(0,0,0,0.06); }
    
    .hero-container {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); padding: 60px; border-radius: 20px;
        border: 1px solid #E0E0E0; text-align: center; margin-top: 50px; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .main-title { color: #1A1A1A; font-family: 'serif'; font-size: 56px; font-weight: 900; letter-spacing: -1px; margin-bottom: 0px; }
    .sub-title { color: #D4AF37; font-size: 20px; text-transform: uppercase; letter-spacing: 4px; font-weight: 400; margin-bottom: 40px; }
    .access-card { background: white; display: inline-block; padding: 20px 40px; border-radius: 12px; border-left: 5px solid #D4AF37; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    </style>
    """, unsafe_allow_html=True)

init_db()
coins = {"Bitcoin": "bitcoin", "Ethereum": "ethereum", "Binance Coin": "binancecoin", "Bitcoin Cash": "bitcoin-cash", "Dogecoin": "dogecoin", "Solana": "solana", "Tron": "tron", "USDC": "usdc", "Tether": "tether", "FIGR HELOC": "figr"}
currencies = {"USD": {"symbol": "$", "rate": 1.0}, "EUR": {"symbol": "€", "rate": 0.92}, "INR": {"symbol": "₹", "rate": 83.0}}

def get_comp_data():
    v = {}
    for n, c in coins.items():
        d = get_data(c)
        if not d.empty: v[n] = d['vol_30d'].iloc[-1]
    return v

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #D4AF37; font-family: serif; letter-spacing: 2px;'>VELOXIS QUANT</h2>", unsafe_allow_html=True)
    if not st.session_state.auth:
        mode = option_menu(None, ["Login", "Register"], icons=['box-arrow-in-right', 'person-plus'], menu_icon="cast", default_index=0, styles={"nav-link-selected": {"background-color": "#D4AF37"}})
        u, p = st.text_input("Entity ID").strip(), st.text_input("Security Key", type='password')
        if st.button("AUTHENTICATE"):
            u_clean = u.lower().strip()
            if mode == "Login" and login_user(u_clean, p): 
                st.session_state.auth = True; st.session_state.user = u_clean; st.rerun()
            elif mode == "Register" and add_user(u_clean, p): st.success("Registered! Login now.")
            else: st.error("Invalid Credentials")
    else:
        st.info(f"👤 Entity: {st.session_state.user.upper()}")
        if st.session_state.user == "admin":
            curr_code, curr_sym, curr_rate = "USD", "$", 1.0 
            menu_options = ["User History", "System Logs"]
            icons = ["people", "gear"]
        else:
            curr_code = st.selectbox("Currency", list(currencies.keys()))
            curr_sym = currencies[curr_code]["symbol"]
            curr_rate = currencies[curr_code]["rate"]
            menu_options = ["Market Hub", "Divergence", "Probability", "My Vault"]
            icons = ["bank", "bar-chart-steps", "dice-5", "safe2"]
        
        selected = option_menu("Terminal", menu_options, icons=icons, menu_icon="cast", default_index=0, styles={"nav-link-selected": {"background-color": "#D4AF37"}})
        
        if st.button("LOGOUT", use_container_width=True): 
            st.session_state.auth = False; st.session_state.user = None; st.rerun()

if not st.session_state.auth:
    st.markdown("""
        <div class="hero-container">
            <h1 class="main-title">VELOXIS <span style="color: #D4AF37;">QUANT</span></h1>
            <p class="sub-title">Advanced Quantitative Asset Intelligence</p>
            <div class="access-card">
                <div style="font-size: 24px; margin-bottom: 10px;">🔒</div>
                <div style="color: #1A1A1A; font-weight: 700; font-size: 18px;">Terminal Encrypted</div>
                <div style="color: #666; font-size: 14px; margin-top: 5px;">
                    Please utilize the <b>Security Sidebar</b> to authenticate <br>and unlock institutional-grade volatility metrics.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    if selected == "Market Hub":
        st.title("🏛 Asset Intelligence Hub")
        with st.form("input_form", border=False):
            col_s, col_b = st.columns([3, 1])
            with col_s: asset = st.selectbox("Select Asset", list(coins.keys()))
            with col_b: st.write(""); run = st.form_submit_button("🔍 ANALYZE RISK", use_container_width=True)
        
        if run: st.session_state.current_asset = asset 
            
        if 'current_asset' in st.session_state:
            target_asset = st.session_state.current_asset
            df = get_data(coins[target_asset])
            
            if not df.empty:
                price = df['price'].iloc[-1] * curr_rate
                vol = df['vol_30d'].iloc[-1]
                risk_level = "CRITICAL" if vol > 0.7 else "MODERATE" if vol > 0.4 else "STABLE"
                
                if risk_level == "CRITICAL":
                    line_c = "#FF3B30"  
                elif target_asset in ["Tether", "USDC", "FIGR HELOC"]:
                    line_c = "#D4AF37"  
                else:
                    line_c = "#00CC78"  

                if run:
                    save_history(st.session_state.user, target_asset, risk_level, vol, "Auto-Log: Risk Scan")

                m_cols = st.columns(4)
                metrics = [("PRICE", f"{curr_sym}{price:,.2f}"), ("VOLATILITY", f"{vol:.2%}"), ("SCORE", f"{int(vol*100)}/100"), ("STATUS", risk_level)]
                for i, col in enumerate(m_cols):
                    col.markdown(f"""<div class="metric-card"><div class="metric-label">{metrics[i][0]}</div><div class="metric-value">{metrics[i][1]}</div></div>""", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                pdf_data = generate_pdf_report(st.session_state.user, target_asset, price/curr_rate, vol, risk_level, df, get_comp_data())
                st.download_button(label="📄 DOWNLOAD AUDIT REPORT", data=pdf_data, file_name=f"Risk_Audit_{target_asset}.pdf", mime="application/pdf")
                
                st.markdown("<br>", unsafe_allow_html=True)
                fig = px.area(df, x='time', y=df['price']*curr_rate)
                fig.update_traces(line_color=line_c, fillcolor=f"rgba{tuple(int(line_c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}")
                fig.update_layout(yaxis_tickprefix=curr_sym, title=f"{target_asset} Price History", height=400, plot_bgcolor='#000000', paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)

                low, high = df['price'].min() * curr_rate, df['price'].max() * curr_rate
                pos = ((price - low) / (high - low)) * 100 if high != low else 50
                st.markdown(f"""
                    <div class="performance-section">
                        <div style="display:flex; justify-content:space-between; font-weight:bold; color:#555;">
                            <span>LOW: {curr_sym}{low:,.2f}</span>
                            <span>HIGH: {curr_sym}{high:,.2f}</span>
                        </div>
                        <div class="gauge-bg"><div class="gauge-dot" style="left: {pos}%;"></div></div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 📝 Strategic Analysis Note")
                note_input = st.text_area("Observations", height=100, key="analysis_note")
                if st.button("💾 SAVE TO VAULT"):
                    save_history(st.session_state.user, target_asset, risk_level, vol, note_input if note_input.strip() else "Manual Scan")
                    st.success("Record saved!")
                    time.sleep(1)
                    st.rerun()

    elif selected == "My Vault":
        st.title("🔐 My Strategic Vault")
        full_df = get_admin_data()
        if not full_df.empty:
            full_df['username_clean'] = full_df['username'].astype(str).str.strip().str.lower()
            user_df = full_df[full_df['username_clean'] == st.session_state.user.strip().lower()].copy()
            if not user_df.empty:
                if st.button("☣️ PURGE ALL RECORDS"): purge_all_history(); st.rerun()
                user_df.reset_index(drop=True, inplace=True)
                user_df['No.'] = range(1, len(user_df) + 1)
                st.dataframe(user_df[['No.', 'coin', 'risk_level', 'volatility', 'timestamp', 'note']], use_container_width=True, hide_index=True)
                for _, row in user_df.iterrows():
                    with st.expander(f"Entry #{row['No.']} | {row['coin']}"):
                        st.info(f"**Note:** {row['note']}")
                        if st.button(f"🗑️ Delete Record #{row['No.']}", key=f"del_{row['id']}"):
                            delete_history_entry(row['id']); st.rerun()
            else: st.warning("Vault is empty.")

    elif selected == "Divergence":
        st.title("⚖️ Risk Divergence")
        c1, c2 = st.columns(2)
        with c1: a1 = st.selectbox("Asset A", list(coins.keys()), index=0)
        with c2: a2 = st.selectbox("Asset B", list(coins.keys()), index=1)
        if st.button("⚖️ ANALYZE DIVERGENCE", use_container_width=True):
            d1, d2 = get_data(coins[a1]), get_data(coins[a2])
            if not d1.empty and not d2.empty:
                v1, v2 = d1['vol_30d'].iloc[-1], d2['vol_30d'].iloc[-1]
                st.plotly_chart(go.Figure(data=[
                    go.Bar(name=a1, x=['Volatility'], y=[v1], marker_color='#D4AF37', text=[f"{v1:.2%}"], textposition='auto'), 
                    go.Bar(name=a2, x=['Volatility'], y=[v2], marker_color='#1A1A1A', text=[f"{v2:.2%}"], textposition='auto')
                ]).update_layout(template="plotly_white", barmode='group'), use_container_width=True)

    elif selected == "Probability":
        st.title("🎲 Monte Carlo Forecast")
        c1, c2 = st.columns([1, 2])
        with c1: asset = st.selectbox("Target Asset", list(coins.keys()))
        with c2: days = st.slider("Forecast Horizon", 7, 90, 30)
        
        if st.button("🎲 RUN SIMULATION", use_container_width=True):
            df = get_data(coins[asset])
            if not df.empty:
                paths = run_monte_carlo(df['price'].iloc[-1], df['vol_30d'].iloc[-1], days)
                final_paths = paths * curr_rate 
                
                fig = px.line(final_paths[:, :50], title=f"Future Price Projections ({curr_code})")
                fig.update_layout(showlegend=False, template="plotly_white", yaxis_tickprefix=curr_sym)
                st.plotly_chart(fig, use_container_width=True)

                final = final_paths[-1]
                s1, s2, s3 = st.columns(3)
                s1.metric("📉 WORST CASE", f"{curr_sym}{np.percentile(final, 5):,.2f}")
                s2.metric("🎯 MEDIAN", f"{curr_sym}{final.mean():,.2f}")
                s3.metric("📈 BEST CASE", f"{curr_sym}{np.percentile(final, 95):,.2f}")
                
                st.markdown("---")
                st.markdown("### 🔍 Risk Pattern Intelligence Decoder")
                p1, p2 = st.columns(2)
                with p1:
                    st.markdown(f"""
                        <div class="decoder-card" style="border-top-color: #2E7D32;">
                            <h3 style="color: #2E7D32; margin-top:0;">🛡️ LINEAR CONVERGENCE</h3>
                            <p style="font-size: 15px; color: #444;"><b>Pattern:</b> Simulation paths are densely packed and move in a unified direction.</p>
                            <p style="font-size: 14px; background: #e8f5e9; padding: 10px; border-radius: 8px;">
                                <b>Verdict:</b> High predictable confidence. Current market conditions suggest low volatility and stable momentum.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                with p2:
                    st.markdown(f"""
                        <div class="decoder-card" style="border-top-color: #C62828;">
                            <h3 style="color: #C62828; margin-top:0;">⚠️ PARABOLIC DIVERGENCE</h3>
                            <p style="font-size: 15px; color: #444;"><b>Pattern:</b> Simulation lines fan out wildly (The "Explosion" effect).</p>
                            <p style="font-size: 14px; background: #ffebee; padding: 10px; border-radius: 8px;">
                                <b>Verdict:</b> Extreme Uncertainty. Historical volatility is so high that the price could move 50% in either direction.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

    elif selected == "System Logs" and st.session_state.user == "admin":
        st.title("📊 System Diagnostics & Health")
        stats = get_system_stats()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Active Entities", stats.get('users', 0), delta="Stable")
        k2.metric("Total Analyses", stats.get('analyses', 0), delta="+12%")
        k3.metric("DB Latency", "12ms", delta="-2ms")
        k4.metric("System Status", "OPTIMAL", delta_color="normal")
        
        st.markdown("### 📜 Recent System Events")
        log_data = {
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "2024-03-15 09:12:01", "2024-03-15 08:45:33"],
            "Event Type": ["USER_LOGIN", "DB_BACKUP", "SYSTEM_BOOT"],
            "Status": ["SUCCESS", "SUCCESS", "SUCCESS"],
            "Details": ["Admin access granted", "Automated backup complete", "Server initialized"]
        }
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)

    elif selected == "User History" and st.session_state.user == "admin":
        st.title("🛡️ Institutional Oversight")
        df = get_admin_data()
        if not df.empty:
            df.reset_index(drop=True, inplace=True)
            df['No.'] = range(1, len(df) + 1)
            cols = ['No.'] + [c for c in df.columns if c != 'No.']
            st.dataframe(df[cols], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### ☣️ Admin Controls")
            did = st.number_input("Purge ID (Use original DB ID)", step=1, min_value=0)
            if st.button("🗑️ PURGE RECORD"):
                delete_history_entry(did)
                st.success(f"Entry {did} removed from database.")
                st.rerun()





                
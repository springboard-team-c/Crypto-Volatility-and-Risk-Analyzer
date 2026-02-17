import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import os
from fpdf import FPDF
import streamlit as st
import matplotlib
matplotlib.use('Agg')

@st.cache_data(ttl=600)
def get_data(coin_id):
    file_map = {
        'bitcoin': 'cleaned_BTC_USD_daily_data.csv', 'ethereum': 'cleaned_ETH_USD_daily_data.csv',
        'binancecoin': 'cleaned_BNB_USD_daily_data.csv', 'bitcoin-cash': 'cleaned_BCH_USD_daily_data.csv',
        'dogecoin': 'cleaned_DOGE_USD_daily_data.csv', 'solana': 'cleaned_SOL_USD_daily_data.csv',
        'tron': 'cleaned_TRX_USD_daily_data.csv', 'usdc': 'cleaned_USDC_USD_daily_data.csv',
        'tether': 'cleaned_USDT_USD_daily_data.csv', 'figr': 'cleaned_FIGR_HELOC_USD_daily_data.csv'
    }
    filename = file_map.get(coin_id)
    target_col = coin_id # Placeholder, logic handles column finding
    
    if not filename or not os.path.exists(filename): return pd.DataFrame()
    try:
        df = pd.read_csv(filename)
        date_col = 'Date' if 'Date' in df.columns else df.columns[0]
        # Smart Column Selection
        if 'Close' in df.columns: actual_col = 'Close'
        elif 'Close.1' in df.columns: actual_col = 'Close.1' # Common in merged files
        else: actual_col = df.columns[1] # Fallback to 2nd column
        
        # Specific overrides for your merged file structure if needed
        col_map = {
            'binancecoin': 'Close', 'bitcoin-cash': 'Close', 'ethereum': 'Close.1', 'bitcoin': 'Close.1',
            'solana': 'Close.2', 'dogecoin': 'Close.3', 'tron': 'Close.3', 'usdc': 'Close.4',
            'tether': 'Close.4', 'figr': 'Close.5'
        }
        if coin_id in col_map and col_map[coin_id] in df.columns:
            actual_col = col_map[coin_id]

        sub_df = df[[date_col, actual_col]].copy()
        sub_df.columns = ['time', 'price']
        sub_df['time'] = pd.to_datetime(sub_df['time'], errors='coerce')
        sub_df['price'] = pd.to_numeric(sub_df['price'], errors='coerce')
        sub_df = sub_df.dropna().sort_values('time')
        
        sub_df['returns'] = sub_df['price'].pct_change()
        sub_df['vol_30d'] = sub_df['returns'].rolling(30, min_periods=1).std() * np.sqrt(365)
        return sub_df[['time', 'price', 'vol_30d']].fillna(0)
    except: return pd.DataFrame()

def run_monte_carlo(current_price, vol, days=30, sims=1000):
    vol = max(vol, 0.01)
    daily_vol = vol / np.sqrt(365)
    results = np.zeros((days, sims))
    for i in range(sims):
        prices = [current_price]
        for _ in range(days-1): prices.append(prices[-1] * (1 + np.random.normal(0, daily_vol)))
        results[:, i] = prices
    return results

def calculate_max_drawdown(df):
    roll_max = df['price'].cummax()
    return (df['price'] / roll_max - 1.0).min()

def generate_pdf_report(user, coin, price, vol, risk, history_df, comparison_data):
    try:
        pdf = FPDF()
        
        # --- PAGE 1 ---
        pdf.add_page()
        # Header
        pdf.set_fill_color(20, 30, 40); pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_font("helvetica", "B", 20); pdf.set_text_color(212, 175, 55)
        pdf.cell(190, 15, "OFFICIAL RISK INTELLIGENCE REPORT", ln=True, align='C')
        
        # Info
        pdf.ln(20); pdf.set_text_color(0, 0, 0); pdf.set_font("helvetica", "B", 11)
        pdf.cell(190, 7, f"Account Holder: {str(user).upper()}", ln=True)
        pdf.cell(190, 7, f"Asset Analyzed: {str(coin).upper()}", ln=True)
        pdf.cell(190, 7, f"Data Range: {history_df['time'].iloc[0].date()} to {history_df['time'].iloc[-1].date()}", ln=True)
        
        # Metrics Table (Yellow Header)
        pdf.ln(5); pdf.set_font("helvetica", "B", 12); pdf.cell(190, 8, "RISK QUANTIFICATION SUMMARY", ln=True)
        pdf.set_fill_color(212, 175, 55); pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 10)
        pdf.cell(95, 9, "METRIC", 1, 0, 'C', 1); pdf.cell(95, 9, "VALUE", 1, 1, 'C', 1)
        pdf.set_text_color(0, 0, 0); pdf.set_font("helvetica", "", 10)
        
        mdd = calculate_max_drawdown(history_df)
        metrics = [("Current Market Price", f"${price:,.2f}"), ("Annualized Volatility", f"{vol:.2%}"), ("Max Drawdown (1Y)", f"{mdd:.2%}"), ("Risk Assessment", risk)]
        for l, v in metrics:
            pdf.cell(95, 9, l, 1); pdf.cell(95, 9, v, 1, 1)

        # Graph Heading
        pdf.ln(10); pdf.set_font("helvetica", "B", 13)
        pdf.cell(190, 8, "DETAILED PRICE ACTION TREND", ln=True)
        
        # Graph (Fills rest of page)
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(history_df['time'], history_df['price'], color='#D4AF37', linewidth=1.5)
        ax.set_title(f"{coin} Historical Performance", fontsize=10); ax.grid(True, alpha=0.3)
        buf = io.BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); pdf.image(buf, x=10, w=185); plt.close(fig)

        # --- PAGE 2 ---
        pdf.add_page(); pdf.set_font("helvetica", "B", 16); pdf.set_text_color(20, 30, 40)
        pdf.cell(190, 15, "MARKET RISK COMPARISON", ln=True, align='L'); pdf.ln(10)
        
        names, values = list(comparison_data.keys()), list(comparison_data.values())
        fig, ax = plt.subplots(figsize=(10, 5.5))
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#D4AF37']
        ax.bar(names, values, color=colors[:len(names)])
        ax.set_title("Annualized Volatility Benchmark", fontsize=12); plt.xticks(rotation=30, ha='right'); ax.grid(axis='y', alpha=0.3)
        buf = io.BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight'); buf.seek(0); pdf.image(buf, x=10, w=185); plt.close(fig)

        pdf.set_y(-15); pdf.set_font("helvetica", "I", 8); pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, "CONFIDENTIAL: Generated by BITRISK ELITE.", align='C')
        return bytes(pdf.output())
    except Exception as e:
        return f"Error: {e}".encode()
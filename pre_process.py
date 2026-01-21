import pandas as pd
import numpy as np
import os

DATA_FOLDER = "."          # current folder
OUTPUT_FOLDER = "preprocessed"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def preprocess_crypto_csv(file_path, output_path):
    df = pd.read_csv(file_path)

    print("Columns:", df.columns)

    # If column name is 'time' instead of 'Date'
    if 'time' in df.columns:
        df.rename(columns={'time': 'Date'}, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df = df.drop_duplicates(subset=['Date'])

    price_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[price_cols] = df[price_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    df['Daily_Return'] = df['Close'].pct_change()
    df['Rolling_Volatility_30'] = df['Daily_Return'].rolling(30).std()
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    df = df.dropna()

    df.to_csv(output_path, index=False)
    print(f"Processed: {file_path}")

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        input_path = os.path.join(DATA_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, f"cleaned_{file}")
        preprocess_crypto_csv(input_path, output_path)
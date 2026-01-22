import matplotlib.pyplot as plt
import yfinance as yf
import polars as pl
import numpy as np

## Globální proměnné
TICKER = "SPY"
FAST = 50
SLOW = 200
LOOKBACK = 1000 


def get_data():
    df = yf.download(TICKER)
    df.columns = df.columns.get_level_values(0)

    return df.iloc[-LOOKBACK:, :]

# def moving_averages(df, fast, slow):
if __name__ == "__main__":
    data = get_data()

    #Catch blok
    if data is None or data.empty:
        print("Data wasnt loaded. Check TICKER")
        exit() 

    print(f"Data for {TICKER} loaded ({len(data)} records).")
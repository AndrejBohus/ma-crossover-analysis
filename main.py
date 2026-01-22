import matplotlib.pyplot as plt
import yfinance as yf
import polars as pl
import numpy as np

## Globální proměnné
TICKER = "SPY"
FAST = 50
SLOW = 200
LOOKBACK = 10000


def get_data():
    df = yf.download(TICKER)
    df.columns = df.columns.get_level_values(0)

    return df.iloc[-LOOKBACK:, :]

def moving_averages(df, fast, slow):
    df[f"{FAST}_ma"] = df["Close"].rolling(fast).mean
    df[f"{SLOW}_ma"] = df["Close"].rolling(slow).mean

    plt.plot(df["Close"])
    plt.plot(df[f"{FAST}_ma"])
    plt.plot(df[f"{SLOW}_ma"])
    plt.legend(['Close', f'{FAST}_ma', f'{SLOW}_ma'])
    plt.title("Moving Average Crossover")
    return df.dropna()

def strategy(df, fast, slow):
    # long když FAST > SLOW, short
    df["Strategy"] = np.where(df[f"{fast}_ma"] > df[f"{slow}_ma"], 1, -1)
    df["Strategy"] = df["Strategy"].shift(1)
    return df

def test_strategy(df, ticker, fast,slow):
    df["Asset_Returns"] = (1 + df["Close"].pct_change()).cumprod() - 1
    df["Strategy_Returns"] = (1 + df["Close"].pct_change() * df["Strategy"]).cumprod() - 1

    plt.figure()
    plt.plot(df["Asset_Returns"])
    plt.plot(df["Strategy_Returns"])
    plt.legend(f'{ticker} Cumulative Returns', f'{fast}- {slow} Crossover strategy returns')
    plt.title("Moving Average Crossovers")
    return df.dropna()

df = get_data()
df = moving_averages(df, FAST, SLOW)
df = strategy(df, FAST, SLOW)
df = test_strategy(df, TICKER, FAST,SLOW)

df
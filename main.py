import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter

## Globální proměnné (Feel free to modify) 
# Golden cross (50/200 SMA)
# Swing trading (20/50 SMA)
# Aggressive day trading (10/20 SMA)
TICKER = "BTC-USD"
FAST = 5
SLOW = 20
LOOKBACK = 500


def get_data():
    try:
        df = yf.download(TICKER, period="max")
        if df.empty:
            raise ValueError(f"No data returned for ticker {TICKER}")
        df.columns = df.columns.get_level_values(0)
        return df.iloc[-LOOKBACK:, :]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {TICKER}: {str(e)}")

def moving_averages(df, fast, slow):
    try:
        if df is None or df.empty:
            raise ValueError("Input dataframe is empty")
        
        df[f"{FAST}_ma"] = df["Close"].rolling(fast).mean()
        df[f"{SLOW}_ma"] = df["Close"].rolling(slow).mean()
        
        df_clean = df.dropna()
        
        plt.figure(figsize=(12, 6))
        plt.plot(df_clean.index, df_clean["Close"], label='Close', linewidth=1.5)
        plt.plot(df_clean.index, df_clean[f"{FAST}_ma"], label=f'{FAST}-day MA', linewidth=1.5)
        plt.plot(df_clean.index, df_clean[f"{SLOW}_ma"], label=f'{SLOW}-day MA', linewidth=1.5)
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.title("Moving Average Crossover")
        plt.grid(alpha=0.3)
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("moving_averages.png", dpi=100, bbox_inches='tight')
        plt.close()
        return df_clean
    except Exception as e:
        raise RuntimeError(f"Error calculating moving averages: {str(e)}")

def strategy(df, fast, slow):
    try:
        if df is None or df.empty:
            raise ValueError("Input dataframe is empty")
        
        if f"{fast}_ma" not in df.columns or f"{slow}_ma" not in df.columns:
            raise ValueError(f"Missing moving average columns: {fast}_ma or {slow}_ma")
        
        # long když FAST > SLOW, short
        df["Strategy"] = np.where(df[f"{fast}_ma"] > df[f"{slow}_ma"], 1, -1)
        df["Strategy"] = df["Strategy"].shift(1)
        return df
    except Exception as e:
        raise RuntimeError(f"Error calculating strategy: {str(e)}")

def test_strategy(df, ticker, fast,slow):
    try:
        if df is None or df.empty:
            raise ValueError("Input dataframe is empty")
        
        if "Strategy" not in df.columns:
            raise ValueError("Strategy column not found in dataframe")
        
        df["Asset_Returns"] = (1 + df["Close"].pct_change()).cumprod() - 1
        df["Strategy_Returns"] = (1 + df["Close"].pct_change() * df["Strategy"]).cumprod() - 1
        
        # buy/sell signals
        df["Signal_Change"] = df["Strategy"].diff() != 0
        buy_signals = df[df["Signal_Change"] & (df["Strategy"] == 1)].copy()
        sell_signals = df[df["Signal_Change"] & (df["Strategy"] == -1)].copy()

        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df["Asset_Returns"] * 100, label=f'{ticker} Cumulative Returns', linewidth=2)
        plt.plot(df.index, df["Strategy_Returns"] * 100, label=f'{fast}-{slow} Crossover Strategy', linewidth=2)
        
        # buy signals (green upward triangles) - strategy line
        if len(buy_signals) > 0:
            plt.scatter(buy_signals.index, buy_signals["Strategy_Returns"] * 100, 
                        color='green', marker='^', s=150, label='BUY Signal (LONG)', zorder=5, edgecolors='darkgreen', linewidth=1.5)
        
        # sell signals (red downward triangles) - strategy line
        if len(sell_signals) > 0:
            plt.scatter(sell_signals.index, sell_signals["Strategy_Returns"] * 100, 
                        color='red', marker='v', s=150, label='SELL Signal (SHORT)', zorder=5, edgecolors='darkred', linewidth=1.5)
        
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns (%)')
        plt.legend(loc='best', fontsize=10)
        plt.title("Moving Average Crossover Strategy Returns")
        plt.grid(alpha=0.3)
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.yaxis.set_major_formatter(PercentFormatter(decimals=1))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("strategy_returns.png", dpi=100, bbox_inches='tight')
        plt.close()
        return df.dropna()
    except Exception as e:
        raise RuntimeError(f"Error in test_strategy: {str(e)}")

try:
    df = get_data()
    df = moving_averages(df, FAST, SLOW)
    df = strategy(df, FAST, SLOW)
    df = test_strategy(df, TICKER, FAST, SLOW)
    print("Graphs saved: moving_averages.png and strategy_returns.png")
except RuntimeError as e:
    print(f"RuntimeError: {str(e)}")
    exit(1)
except ValueError as e:
    print(f"ValueError: {str(e)}")
    exit(1)
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    exit(1)
# import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# import seaborn as sns

import pandas as pd
import yfinance as yf
import pandas as pd
from pathlib import Path

startDate = '2025-09-01'
endDate = '2026-05-12'

def download_and_save_csv(
    tickers,
    start="2025-09-01",
    end=None,
    filename=f"output/nasdaq_history_{startDate}_{endDate}.csv",
    auto_adjust=True
):
    """
    Download historical stock data from Yahoo Finance and save to CSV (long format).

    Parameters
    ----------
    tickers : list[str]
        List of stock tickers, e.g. ["AAPL", "MSFT"]
    start : str
        Start date, e.g. "2015-01-01"
    end : str or None
        End date, e.g. "2024-12-31"
    filename : str
        Output CSV file name
    auto_adjust : bool
        Whether to auto-adjust prices
    """

    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list, e.g. ['AAPL', 'MSFT']")

    # Fix tickers like BRK.B → BRK-B
    tickers = [t.replace(".", "-") for t in tickers]

    print(f"Downloading {len(tickers)} tickers...")
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=auto_adjust,
        group_by="ticker",
        threads=True,
        progress=True
    )

    if data.empty:
        raise ValueError("No data downloaded. Check tickers or date range.")

    # ---- normalize to long format ----
    if len(tickers) > 1:
        df = (
            data
            .stack(level=0)
            .reset_index()
            .rename(columns={"level_1": "Ticker"})
        )
    else:
        df = data.reset_index()
        df["Ticker"] = tickers[0]

    # Reorder columns
    cols = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    df = df[cols]

    # Save
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filename, index=False)

    print(f"Saved to {filename}")
    return df

def getting_nasdaq_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500 = pd.read_excel("output/sp500.xlsx")
    tickers = sp500["Symbol"].tolist()
    # tickers = [t.replace('.', '-') for t in tickers]

    df = download_and_save_csv(
        tickers,
        start=startDate,
        end=endDate,
        filename=f"output/nasdaq_sample_{startDate}_{endDate}.csv"
    )

def calculate_ma_for_nasdaq_data():
    # 1. Read CSV
    df = pd.read_csv(f"output/nasdaq_sample_{startDate}_{endDate}.csv")

    # 2. Ensure date is datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # 3. Sort by stock + date (VERY IMPORTANT)
    df = df.sort_values(['Ticker', 'Date'])

    # 4. Calculate moving averages per stock
    df['MA5'] = (
        df.groupby('Ticker')['Close']
        .rolling(window=5)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df['MA20'] = (
        df.groupby('Ticker')['Close']
        .rolling(window=20)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df['MA60'] = (
        df.groupby('Ticker')['Close']
        .rolling(window=60)
        .mean()
        .reset_index(level=0, drop=True)
    )
    df.to_csv(f"output/nasdaq_sample_with_ma_{startDate}_{endDate}.csv", index=False)
    print(f"✅ 成功保存 nasdaq_sample_with_ma_{startDate}_{endDate}.csv")

    return df

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="C:/Windows/Fonts/simhei.ttf")
def filter_stocks_and_plot(all_stock_dfs):
    selected_stocks = []
    ma5_list = []
    ma20_list = []
    ma60_list = []
    selected_stocks = all_stock_dfs[(all_stock_dfs["Date"]==endDate)&(all_stock_dfs["MA5"]>=all_stock_dfs["MA20"])&(all_stock_dfs["MA20"]>=all_stock_dfs["MA60"])] 
   #&(all_stock_dfs["收盘"]>=all_stock_dfs["MA5"])
    # 畫圖
    x = range(len(selected_stocks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar([i - width for i in x], selected_stocks["MA5"], width=width, label='MA5')
    ax.bar(x, selected_stocks["MA20"], width=width, label='MA20')
    ax.bar([i + width for i in x], selected_stocks["MA60"], width=width, label='MA60')

    ax.set_xticks(x)
    ax.set_xticklabels(selected_stocks["Ticker"], rotation=45, ha='right', fontproperties=font)
    ax.set_ylabel("均線數值", fontproperties=font)
    ax.set_title("符合 MA5 > MA20 > MA60 的股票", fontproperties=font)
    ax.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    getting_nasdaq_data()
    df = calculate_ma_for_nasdaq_data()
    filter_stocks_and_plot(df)
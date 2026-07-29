# import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# import seaborn as sns
import akshare as ak
import time

import pandas as pd
import yfinance as yf
import pandas as pd
from pathlib import Path
import numpy as np
startDate = '2026-01-01'
endDate = '2026-07-26'
as_of_date = '2026-07-27'

def download_and_save_csv(
    stock_list,
    tickers,
    start=startDate,
    end=endDate,
    filename=f"output/hs300_history_{startDate}_{endDate}.csv",
    adjust="qfq",   # "qfq", "hfq", or ""
):
    """
    Download historical A-share data from AKShare and save to CSV.

    Parameters
    ----------
    stock_list : DataFrame
        Must contain:
            stock_code_full
            成分券代码
            成分券名称

    tickers : list[str]
        Example:
            ["000001", "600519"]

    start : str
        Format: YYYYMMDD

    end : str
        Format: YYYYMMDD

    adjust : str
        "", "qfq", or "hfq"
    """

    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list.")

    print(f"Downloading {len(tickers)} stocks...")

    all_data = []

    # import akshare as ak

    # df = ak.stock_zh_a_hist(
    #     symbol="000001",
    #     period="daily",
    #     start_date="20240101",
    #     end_date="20241231",
    #     adjust="qfq"
    # )

    # print(df.head())
    # print(df.shape)


    for symbol in tickers:
        print(f"Downloading {symbol}...")
        print(f"Start: {start}, End: {end}, Adjust: {adjust}")

        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start,
                end_date=end,
                adjust=adjust,
            )

            if df.empty:
                print(f"No data for {symbol}")
                continue

            # Rename columns to match yfinance output
            df = df.rename(
                columns={
                    "日期": "Date",
                    "开盘": "Open",
                    "最高": "High",
                    "最低": "Low",
                    "收盘": "Close",
                    "成交量": "Volume",
                }
            )

            df["Ticker"] = symbol

            all_data.append(
                df[
                    [
                        "Date",
                        "Ticker",
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume",
                    ]
                ]
            )

            print(f"Downloaded {symbol} ({len(df)} rows)")

            # Prevent rate limiting
            time.sleep(0.2)

        except Exception as e:
            print(f"Failed {symbol}: {e}")

    if not all_data:
        raise ValueError("No data downloaded.")

    df = pd.concat(all_data, ignore_index=True)

    # Merge with stock names
    df_merged = pd.merge(
        df,
        stock_list,
        left_on="Ticker",
        right_on="stock_code_full",
        how="left",
    )

    cols = [
        "Date",
        "Ticker",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "成分券代码",
        "成分券名称",
    ]

    df_merged = df_merged[cols]

    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"Saved to {filename}")

    return df_merged

def getting_hs300_data():
    # url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    # sp500 = pd.read_excel("output/sp500.xlsx")
    stock_list = pd.read_csv('output/hs300_list_new.csv', dtype={'成分券代码': str})
    # stock_list['stock_code_full'] = np.where(
    # stock_list['交易所英文名称'] == "Shanghai Stock Exchange", 
    # stock_list['成分券代码'] + ".SS", 
    # stock_list['成分券代码'] + ".SZ")
    stock_list['stock_code_full'] = stock_list['成分券代码']

    tickers = stock_list["stock_code_full"].tolist()
   
    # tickers = [t.replace('.', '-') for t in tickers]
    start = startDate.replace("-", "")
    end = endDate.replace("-", "")

    df = download_and_save_csv(
        stock_list,
        tickers,
        start=start,
        end=end,
        filename=f"output/hs300_sample_{startDate}_{endDate}.csv"
    )

def calculate_ma_for_hs300_data():
    # 1. Read CSV
    df = pd.read_csv(f"output/hs300_sample_{startDate}_{endDate}.csv")

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
    df.to_csv(f"output/hs300_sample_with_ma_{startDate}_{endDate}.csv", index=False)
    print(f"✅ 成功保存 hs300_sample_with_ma_{startDate}_{endDate}.csv")

    return df

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="C:/Windows/Fonts/simhei.ttf")
def _ma_filter_mask(df, as_of_date=as_of_date):
    # d = pd.to_datetime(df["Date"]).dt.normalize()
    print(df["Date"])
    print(as_of_date)
    # selected_stocks = all_stock_dfs[(all_stock_dfs["Date"]=="2026-02-06")&(all_stock_dfs["MA5"]>=all_stock_dfs["MA20"])&(all_stock_dfs["MA20"]>=all_stock_dfs["MA60"])] 
   
    return (df["Date"] == as_of_date) & (df["MA5"] >= df["MA20"]) & (df["MA20"] >= df["MA60"])


def _daily_to_weekly(daily: pd.DataFrame) -> pd.DataFrame:
    """Resample single-ticker daily OHLC to weekly (week ending Friday)."""
    x = daily.sort_values("Date").set_index("Date")
    w = x.resample("W-FRI").agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
    )
    return w.dropna(subset=["Open", "High", "Low", "Close"]).reset_index()


def _candlestick_weekly(ax, weekly: pd.DataFrame, title: str):
    """Draw OHLC candles on ax; weekly has columns Date, Open, High, Low, Close."""
    o = weekly["Open"].to_numpy()
    h = weekly["High"].to_numpy()
    l = weekly["Low"].to_numpy()
    c = weekly["Close"].to_numpy()
    xs = np.arange(len(weekly))
    for xi, oi, hi, li, ci in zip(xs, o, h, l, c):
        color = "#26a69a" if ci >= oi else "#ef5350"
        ax.plot([xi, xi], [li, hi], color="black", linewidth=0.7)
        bottom = min(oi, ci)
        top = max(oi, ci)
        ax.bar(xi, top - bottom, bottom=bottom, width=0.65, color=color, edgecolor="black", linewidth=0.4)
    ax.set_xticks(xs[:: max(1, len(xs) // 6)])
    ax.set_xticklabels(
        [pd.Timestamp(t).strftime("%Y-%m-%d") for t in weekly["Date"].iloc[:: max(1, len(xs) // 6)]],
        rotation=35,
        ha="right",
        fontsize=7,
    )
    ax.set_title(title, fontproperties=font, fontsize=10)
    ax.grid(True, alpha=0.25)


def _candlestick_daily(ax, daily: pd.DataFrame, title: str):
    """Draw OHLC candles on ax; daily has columns Date, Open, High, Low, Close."""
    o = daily["Open"].to_numpy()
    h = daily["High"].to_numpy()
    l = daily["Low"].to_numpy()
    c = daily["Close"].to_numpy()
    xs = np.arange(len(daily))
    for xi, oi, hi, li, ci in zip(xs, o, h, l, c):
        color = "#26a69a" if ci >= oi else "#ef5350"
        ax.plot([xi, xi], [li, hi], color="black", linewidth=0.7)
        bottom = min(oi, ci)
        top = max(oi, ci)
        ax.bar(xi, top - bottom, bottom=bottom, width=0.65, color=color, edgecolor="black", linewidth=0.4)
    ax.set_xticks(xs[:: max(1, len(xs) // 6)])
    ax.set_xticklabels(
        [pd.Timestamp(t).strftime("%Y-%m-%d") for t in daily["Date"].iloc[:: max(1, len(xs) // 6)]],
        rotation=35,
        ha="right",
        fontsize=7,
    )
    ax.set_title(title, fontproperties=font, fontsize=10)
    ax.grid(True, alpha=0.25)


def filter_stocks_and_plot():
    all_stock_dfs = pd.read_csv(f"output/hs300_sample_with_ma_{startDate}_{endDate}.csv")
    all_stock_dfs["Date"] = pd.to_datetime(all_stock_dfs["Date"])
    selected_stocks = []
    ma5_list = []
    ma20_list = []
    ma60_list = []
    selected_stocks = all_stock_dfs[_ma_filter_mask(all_stock_dfs)]
   #&(all_stock_dfs["收盘"]>=all_stock_dfs["MA5"])
    # 畫圖
    x = range(len(selected_stocks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar([i - width for i in x], selected_stocks["MA5"], width=width, label='MA5')
    ax.bar(x, selected_stocks["MA20"], width=width, label='MA20')
    ax.bar([i + width for i in x], selected_stocks["MA60"], width=width, label='MA60')

    ax.set_xticks(x)
    ax.set_xticklabels(selected_stocks["成分券名称"], rotation=45, ha='right', fontproperties=font)
    ax.set_ylabel("均線數值", fontproperties=font)
    ax.set_title("符合 MA5 > MA20 > MA60 的股票", fontproperties=font)
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_ma5_trends_weekly(as_of_date=as_of_date):
    """Weekly candlestick chart for every ticker that passes the MA filter on as_of_date."""
    all_stock_dfs = pd.read_csv(f"output/hs300_sample_with_ma_{startDate}_{endDate}.csv")
    all_stock_dfs["Date"] = pd.to_datetime(all_stock_dfs["Date"])
    selected_stocks = all_stock_dfs[_ma_filter_mask(all_stock_dfs, as_of_date=as_of_date)]
    tickers = selected_stocks["成分券名称"].drop_duplicates().tolist()
    if not tickers:
        print("No tickers selected; check as_of_date and MA filters.")
        return

    n = len(tickers)
    ncols = min(4, n)
    nrows = int(np.ceil(n / ncols))
    # figsize in inches: increase 5.5 / 4.5 for larger subplots (was 4.2 / 3.4)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 4.5 * nrows), squeeze=False)
    fig.suptitle("Weekly candlesticks (MA5 ≥ MA20 ≥ MA60 on " + str(as_of_date) + ")", fontproperties=font, fontsize=12)

    for idx, ticker in enumerate(tickers):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        daily = all_stock_dfs[all_stock_dfs["成分券名称"] == ticker][["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        daily = daily.dropna(subset=["Open", "High", "Low", "Close"])
        weekly = _daily_to_weekly(daily)
        if weekly.empty:
            ax.set_visible(False)
            continue
        _candlestick_weekly(ax, weekly, str(ticker))

    for j in range(n, nrows * ncols):
        r, c = divmod(j, ncols)
        axes[r][c].set_visible(False)

    plt.tight_layout()
    plt.show()

def plot_ma5_trends_daily(as_of_date=as_of_date):
    """Weekly candlestick chart for every ticker that passes the MA filter on as_of_date."""
    all_stock_dfs = pd.read_csv(f"output/hs300_sample_with_ma_{startDate}_{endDate}.csv")
    all_stock_dfs["Date"] = pd.to_datetime(all_stock_dfs["Date"])
    selected_stocks = all_stock_dfs[_ma_filter_mask(all_stock_dfs, as_of_date=as_of_date)]
    tickers = selected_stocks["成分券名称"].drop_duplicates().tolist()
    if not tickers:
        print("No tickers selected; check as_of_date and MA filters.")
        return

    n = len(tickers)
    ncols = min(4, n)
    nrows = int(np.ceil(n / ncols))
    # figsize in inches: increase 5.5 / 4.5 for larger subplots (was 4.2 / 3.4)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 4.5 * nrows), squeeze=False)
    fig.suptitle("Weekly candlesticks (MA5 ≥ MA20 ≥ MA60 on " + str(as_of_date) + ")", fontproperties=font, fontsize=12)

    for idx, ticker in enumerate(tickers):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        daily = all_stock_dfs[all_stock_dfs["成分券名称"] == ticker][["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        daily = daily.dropna(subset=["Open", "High", "Low", "Close"])
        if daily.empty:
            ax.set_visible(False)
            continue
        _candlestick_daily(ax, daily, str(ticker))

    for j in range(n, nrows * ncols):
        r, c = divmod(j, ncols)
        axes[r][c].set_visible(False)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    getting_hs300_data()
    calculate_ma_for_hs300_data()
    # filter_stocks_and_plot()
    # can only run this after you get the data and calculate the ma 
    # plot_ma5_trends_weekly()
    plot_ma5_trends_daily()



    
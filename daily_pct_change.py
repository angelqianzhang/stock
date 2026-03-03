import pandas as pd
# import akshare as ak
import time
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import adata
# 获取平安银行2021年至今日线（自动前复权）

# Chinese-capable font for plot labels (Windows: Microsoft YaHei / SimHei)
font = FontProperties(family=['Microsoft YaHei', 'SimHei', 'sans-serif'])

 

# Set your date range here (format: YYYYMMDD)
START_DATE = '2025-09-02'
END_DATE = '2026-02-13'

# Read stock list

def get_month_k_with_ma(stock_code, stock_name):
    # 取月K線
    print(stock_code)
    df = adata.stock.market.get_market(stock_code=str(stock_code), k_type=1, start_date=START_DATE)
    if df.empty:
        return None
    
    # 按日期排序
    df = df.sort_values('trade_date')
    
    # 計算5/20/60均線
    df['MA5'] = df['pre_close'].rolling(window=5).mean()
    df['MA20'] = df['pre_close'].rolling(window=20).mean()
    df['MA60'] = df['pre_close'].rolling(window=60).mean()
    
    # 加上股票代碼
    df['stock_name'] = stock_name
    return df 


def get_stock_list():
    stock_list = pd.read_csv('hs300_list_new.csv', dtype={'成分券代码': str})
  
    all_results = pd.DataFrame()

    for i, row in stock_list.iterrows():
        stock_code = row['成分券代码']
        stock_name = row['成分券名称']
        df = get_month_k_with_ma(stock_code, stock_name)
        all_results = pd.concat([all_results, df], ignore_index=True)
        print(stock_name)
        time.sleep(0.5)

    all_results.to_csv('hs300_month_k_with_ma_'+START_DATE+'_'+END_DATE+'.csv', index=False, encoding='utf-8-sig')
    print('Saved to /hs300_month_k_with_ma_'+START_DATE+'_'+END_DATE+'.csv')

# --- Plotting Section ---
    
def filter_stocks_and_plot():
    selected_stocks = []
    ma5_list = []
    ma20_list = []
    ma60_list = []
    all_stock_dfs = pd.read_csv('hs300_month_k_with_ma_'+START_DATE+'_'+END_DATE+'.csv', dtype={'stock_code': str})
    selected_stocks =all_stock_dfs[(all_stock_dfs["stock_code"]!='600519')&(all_stock_dfs["trade_date"]==END_DATE)&(all_stock_dfs["MA5"]>=all_stock_dfs["MA20"])&(all_stock_dfs["MA20"]>=all_stock_dfs["MA60"])] 
 
    x = range(len(selected_stocks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar([i - width for i in x], selected_stocks["MA5"], width=width, label='MA5')
    ax.bar(x, selected_stocks["MA20"], width=width, label='MA20')
    ax.bar([i + width for i in x], selected_stocks["MA60"], width=width, label='MA60')

    ax.set_xticks(x)
    ax.set_xticklabels(selected_stocks["stock_name"], rotation=45, ha='right', fontproperties=font)
    ax.set_ylabel("均線數值", fontproperties=font)
    ax.set_title("符合 MA5 > MA20 > MA60 的股票", fontproperties=font)
    ax.legend()
    plt.tight_layout()
    plt.show()

def pct_change_above_1_by_stock():
    """Read CSV and compute, for each stock, the percentage of days where change_pct > 1."""
    df = pd.read_csv('hs300_month_k_with_ma_'+START_DATE+'_'+END_DATE+'.csv', dtype={'stock_code': str})
    # Compute change_pct within each stock (first day per stock is NaN)
    df = df.sort_values(['stock_code', 'trade_date'])
    # For each stock: count rows with change_pct > 1 and total valid change_pct rows
    valid = df.dropna(subset=['change_pct'])
    stats = valid.groupby('stock_code').agg(
        count_above_1=('change_pct', lambda s: (s > 3).sum()),
        total_days=('change_pct', 'count'),
    ).reset_index()
    stats['pct_above_1'] = (stats['count_above_1'] / stats['total_days'] * 100).round(2)
    # Attach stock_name from first row of each stock
    names = df.groupby('stock_code')['stock_name'].first().reset_index()
    stats = stats.merge(names, on='stock_code')
    return stats


def plot_pct_above_1_bar_chart(pct_df):
    """Bar chart: percentage of days where change_pct > 1 for each stock."""
    fig, ax = plt.subplots(figsize=(max(14, len(pct_df) * 0.2), 6))
    x = range(len(pct_df))
    bars = ax.bar(x, pct_df['pct_above_1'], color='steelblue', edgecolor='navy', alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(pct_df['stock_name'], rotation=45, ha='right', fontproperties=font)
    ax.set_ylabel('Percentage of days with change_pct > 1 (%)', fontproperties=font)
    ax.set_title('Percentage of days where change_pct > 1 by stock', fontproperties=font)
    ax.set_ylim(0, None)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # get_stock_list()
    # filter_stocks_and_plot()
    # Percentage of days with change_pct > 1 for each stock
    pct_df = pct_change_above_1_by_stock()
    print(pct_df)
    pct_df.to_csv('hs300_pct_above_1_'+START_DATE+'_'+END_DATE+'.csv', index=False, encoding='utf-8-sig')
    # Only plot stocks with percentage >= 40
    plot_pct_above_1_bar_chart(pct_df[pct_df['pct_above_1'] >= 23])
 
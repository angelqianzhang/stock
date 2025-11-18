import pandas as pd
import akshare as ak
import time
import matplotlib.pyplot as plt

# Set your date range here (format: YYYYMMDD)
START_DATE = '20240901'
END_DATE = '202505022'

# Read stock list
def get_stock_list():
    stock_list = pd.read_csv('hs300_list_new.csv', dtype={'成分券代码': str})
  
    all_results = []

    for i, row in stock_list.iterrows():
        stock_code = row['成分券代码']
        stock_name = row['成分券名称']
        # Determine exchange suffix
        if stock_code.startswith('6'):
            symbol = stock_code + '.SH'
        else:
            symbol = stock_code + '.SZ'
        try:
            print(f"[{i+1}/{len(stock_list)}] {stock_name} ({symbol})")
            df = ak.stock_zh_a_hist(symbol=stock_code[:6], period='daily', start_date=START_DATE, end_date=END_DATE, adjust='qfq')
            if df.empty:
                continue
            df = df.sort_values('日期')
            df['pct_change'] = df['收盘'].pct_change() * 100
            df['stock_code'] = stock_code
            df['stock_name'] = stock_name
            all_results.append(df[['stock_code', 'stock_name', '日期', '收盘', 'pct_change']])
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {stock_name} ({symbol}): {e}")

    if all_results:
        result_df = pd.concat(all_results, ignore_index=True)
        result_df.to_csv('hs300_daily_pct_change.csv', index=False, encoding='utf-8-sig')
        print('✅ Saved to /hs300_daily_pct_change.csv')
    else:
        print('❌ No data fetched.')

# --- Plotting Section ---

def plot_pct_change(stock_code):
    df = pd.read_csv('hs300_daily_pct_change.csv', dtype={'stock_code': str})
    stock_df = df[df['stock_code'] == stock_code]
    if stock_df.empty:
        print(f"No data found for stock code: {stock_code}")
        return
    plt.figure(figsize=(12, 6))
    plt.plot(stock_df['日期'], stock_df['pct_change'], marker='o')
    plt.title(f"Daily Percentage Change for {stock_code}")
    plt.xlabel('Date')
    plt.ylabel('Percentage Change (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# get_stock_list()
user_code = input('Enter a stock code to plot its daily percentage change (e.g., 000001): ')
plot_pct_change(user_code) 
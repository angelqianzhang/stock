import akshare as ak
import pandas as pd
import time

import pandas as pd
import requests
import json

startDate = '20240901'
endDate = '202505021'
def get_hs300_list():
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "500",          # 一次抓500條（夠了，因為只有300支）
        "fid": "f3",
        "fs": "b:MK0010",     # BK0707就是滬深300
        "fields": "f12,f14"   # f12=股票代碼，f14=股票名稱
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    stocks = data['data']['diff']
     
    stock_list = []
    for stock in stocks:
        stock_code = stocks[stock]['f12']
        stock_name = stocks[stock]['f14']
        # 判斷是滬市還是深市
        if stock_code.startswith('6'):
            stock_code_full =  stock_code + ".SH"
        else:
            stock_code_full = stock_code + ".SZ"
        stock_list.append({
            "stock_code_full": stock_code_full,
            "stock_name": stock_name
        })
    
    df = pd.DataFrame(stock_list)
    return df

# 直接取
hs300_df = ak.index_stock_cons_csindex(symbol="000300")  
# hs300_df = get_hs300_list()

# 保存成csv
# hs300_df.to_csv("hs300_list_new.csv", index=False, encoding="utf-8-sig")

# 2. 提取單隻股票的月K線並計算均線
def get_month_k_with_ma(stock_code, stock_name):
    # 取月K線
    df = ak.stock_zh_a_hist(symbol=stock_code[:6], period="daily", start_date=startDate, end_date=endDate, adjust="qfq")  # 選擇前复权

    if df.empty:
        return None
    
    # 按日期排序
    df = df.sort_values('日期')
    
    # 計算5/20/60均線
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    df['MA60'] = df['收盘'].rolling(window=60).mean()
    
    # 加上股票代碼
    df['stock_code'] = stock_code
    df['stock_name'] = stock_name
    return df[['stock_code', 'stock_name', '日期', '收盘', 'MA5', 'MA20', 'MA60']]

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="C:/Windows/Fonts/simhei.ttf")
def filter_stocks_and_plot(all_stock_dfs):
    selected_stocks = []
    ma5_list = []
    ma20_list = []
    ma60_list = []
    selected_stocks = all_stock_dfs[(all_stock_dfs["stock_code"]!=600519)&(all_stock_dfs["日期"]=="2025-05-20")&(all_stock_dfs["MA5"]>=all_stock_dfs["MA20"])&(all_stock_dfs["MA20"]>=all_stock_dfs["MA60"])] 
   #&(all_stock_dfs["收盘"]>=all_stock_dfs["MA5"])
    # 畫圖
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

# 3. 主程式
def main():
    # stock_list = hs300_df #get_hs300_list()
    stock_list = pd.read_csv("hs300_list_new.csv",dtype={"成分券代码": str})
    all_data = []
    
    for i, row in stock_list.iterrows():  # 正確是 iterrows()
        try:
            stock_code_full = row['成分券代码']
            stock_name = row['成分券名称']
            print(stock_code_full)
            
            print(f"[{i+1}/{len(stock_list)}] 正在處理 {stock_name}")
            df = get_month_k_with_ma(stock_code_full, stock_name)
            
            if df is not None:
                all_data.append(df)
            
            time.sleep(0.5)  # 避免請求過快
        
        except Exception as e:
            print(f"錯誤：{stock_name}, {e}")
    
    if all_data:  # 檢查一下有沒有成功抓到資料
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('hs300_monthly_ma_akshare.csv', index=False, encoding='utf-8-sig')
        print("✅ 成功保存 hs300_monthly_ma_akshare.csv")
        filter_stocks_and_plot(final_df)
    else:
        print("❌ 沒有任何資料被抓取")

####################
# main()
####################
final_df = pd.read_csv('hs300_monthly_ma_akshare.csv')
filter_stocks_and_plot(final_df)
####################
# df = ak.stock_zh_a_hist("000001", period="monthly", start_date="20250101", end_date="20250426", adjust="qfq")
# print(df)
 

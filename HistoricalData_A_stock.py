import akshare as ak
import pandas as pd
import time

import pandas as pd
import requests
import json

startDate = '20251101'
endDate = '20260302'
closing_date = "2026-03-02"
import akshare as ak
import time
import random
import pandas as pd
from typing import List, Optional

class AShareDataFetcher:
    def __init__(self):
        self.setup_session()
        
    def setup_session(self):
        """配置带有重试机制的会话"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 配置重试
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        # 创建会话
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 应用到akshare
        ak.session = self.session
    
    def safe_fetch_data(self, fetch_func, max_retries=3, delay=2, **kwargs):
        """安全获取数据，带重试和延迟"""
        for attempt in range(max_retries):
            try:
                # 随机延迟，避免过于规律的请求
                time.sleep(delay + random.uniform(0, 1))
                
                # 调用获取函数
                result = fetch_func(**kwargs)
                
                # 检查结果是否为空
                if result is not None and (isinstance(result, pd.DataFrame) and not result.empty):
                    return result
                else:
                    print(f"第{attempt+1}次尝试返回空数据，重试中...")
                    
            except Exception as e:
                print(f"第{attempt+1}次尝试失败: {str(e)[:100]}")
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)  # 指数退避
                    print(f"等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"所有{max_retries}次尝试均失败")
                    raise
        
        return None
    
    def get_stock_history(self, symbol: str, start_date: str, end_date: str, period: str = "daily"):
        """获取单只股票历史数据"""
        return self.safe_fetch_data(
            ak.stock_zh_a_hist,
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
    
    def get_multiple_stocks(self, symbols: List[str], start_date: str, end_date: str):
        """批量获取多只股票数据"""
        all_data = []
        
        for i, symbol in enumerate(symbols):
            print(f"正在获取 {symbol} 的数据 ({i+1}/{len(symbols)})")
            
            try:
                df = self.get_stock_history(symbol, start_date, end_date)
                if df is not None and not df.empty:
                    all_data.append(df) 
                    print(f"成功获取 {len(df)} 条记录")
                else:
                    print(f"获取失败或数据为空")
            except Exception as e:
                print(f"获取 {symbol} 时出错: {e}")
            
            # 每3只股票后增加较长延迟
            if (i + 1) % 3 == 0:
                long_delay = random.uniform(3, 5)
                print(f"批量获取暂停{long_delay:.1f}秒...")
                time.sleep(long_delay)
        
        return all_data

# 使用示例
if __name__ == "__main__":
    # 初始化获取器
    fetcher = AShareDataFetcher()
    
    stock_list_df = pd.read_csv("hs300_list_new.csv",dtype={"成分券代码": str})
    # 获取单只股票
    # df_single = fetcher.get_stock_history("600519", "20240101", "20240630")
    # print(f"单只股票数据形状: {df_single.shape if df_single is not None else '无数据'}")
    
    # 批量获取
    stock_list = stock_list_df["成分券代码"].dropna().unique().tolist()
    all_dfs = fetcher.get_multiple_stocks(stock_list, startDate, endDate)
    
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # 生成文件名
        filename = f"300_{startDate}_{endDate}.csv"
        
        # 保存
        combined_df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 数据已成功保存!")
        print(f"   文件名: {filename}")
        print(f"   包含股票: {len(all_dfs)} 只")
        print(f"   总数据行: {len(combined_df)} 行")
        
        # 显示前几只股票
        unique_stocks = combined_df['股票代码'].unique()[:5]
        print(f"   示例股票: {', '.join(unique_stocks)}")
    else:
        print("没有获取到有效数据")

# 直接取
# stock_list = ak.index_stock_cons_csindex(symbol="000300")  
# hs300_df = get_hs300_list()
 
# 保存成csv


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
    selected_stocks = all_stock_dfs[(all_stock_dfs["stock_code"]!=600519)&(all_stock_dfs["日期"]==closing_date)&(all_stock_dfs["MA5"]>=all_stock_dfs["MA20"])&(all_stock_dfs["MA20"]>=all_stock_dfs["MA60"])] 
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
    # stock_list = pd.read_csv("hs300_list_new.csv",dtype={"成分券代码": str})
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

#################### full run
main()
#################### Only print plot 
# final_df = pd.read_csv('hs300_monthly_ma_akshare.csv')
# filter_stocks_and_plot(final_df)
####################
# df = ak.stock_zh_a_hist("000001", period="monthly", start_date="20250101", end_date="20250426", adjust="qfq")
# print(df)
 


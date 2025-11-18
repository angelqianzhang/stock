import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class ChineseStockAnalyzer:
    def __init__(self):
        pass
        
    def get_stock_data(self, stock_code, start_date, end_date):
        """
        Fetch stock data for a given code and date range using akshare
        stock_code format: sh600000 or sz000001
        """
        try:
            # Convert tushare format to akshare format
            if '.SH' in stock_code:
                # ak_code = f"sh{stock_code.split('.')[0]}"
                ak_code = f"{stock_code.split('.')[0]}"
            else:
                # ak_code = f"sz{stock_code.split('.')[0]}"
                ak_code = f"{stock_code.split('.')[0]}"
                
            df = ak.stock_zh_a_hist(symbol=ak_code, 
                                  start_date=start_date, 
                                  end_date=end_date,
                                  adjust="qfq")  # qfq means forward adjustment
            
            # Rename columns to match our visualization code
            df = df.rename(columns={
                '日期': 'trade_date',
                '收盘': 'close',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'vol',
                '成交额': 'amount'
            })
            
            return df.sort_values('trade_date')
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """
        Calculate common technical indicators
        """
        # Calculate MA5, MA20, MA60
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change()
        
        # Calculate volatility (20-day rolling std of returns)
        df['volatility'] = df['daily_return'].rolling(window=20).std()
        
        return df 
import matplotlib.pyplot as plt
import seaborn as sns

class StockVisualizer:
    @staticmethod
    def plot_price_trend(df, title="Stock Price Trend"):
        """
        Plot stock price trend with moving averages
        """
        plt.figure(figsize=(15, 8))
        plt.plot(df['trade_date'], df['close'], label='Close Price')
        plt.plot(df['trade_date'], df['MA5'], label='MA5')
        plt.plot(df['trade_date'], df['MA20'], label='MA20')
        plt.plot(df['trade_date'], df['MA60'], label='MA60')
        
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_volume_analysis(df, title="Volume Analysis"):
        """
        Plot trading volume analysis
        """
        plt.figure(figsize=(15, 6))
        plt.bar(df['trade_date'], df['vol'], color='blue', alpha=0.5)
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_returns_distribution(df, title="Returns Distribution"):
        """
        Plot distribution of daily returns
        """
        plt.figure(figsize=(10, 6))
        sns.histplot(df['daily_return'].dropna(), bins=50, kde=True)
        plt.title(title)
        plt.xlabel('Daily Returns')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.tight_layout()
        plt.show() 
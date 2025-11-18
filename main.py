from stock_analyzer import ChineseStockAnalyzer
from visualization import StockVisualizer
from datetime import datetime, timedelta

def main():
    # Initialize analyzer (no token needed)
    analyzer = ChineseStockAnalyzer()
    
    # Set parameters
    stock_code = '000001.SZ'  # Ping An Bank as example
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    # Fetch and analyze data
    df = analyzer.get_stock_data(stock_code, start_date, end_date)
    if df is not None:
        df = analyzer.calculate_technical_indicators(df)
        
        # Create visualizations
        visualizer = StockVisualizer()
        visualizer.plot_price_trend(df, f"Stock Price Trend - {stock_code}")
        visualizer.plot_volume_analysis(df, f"Volume Analysis - {stock_code}")
        visualizer.plot_returns_distribution(df, f"Returns Distribution - {stock_code}")
    
if __name__ == "__main__":
    main() 
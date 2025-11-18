import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class StockAnalyzer:
    def __init__(self):
        """Initialize StockAnalyzer with default parameters"""
        self.proxy = "http://127.0.0.1:33210"

    def get_financial_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetch and analyze financial data for a given stock ticker.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Dictionary containing financial metrics or None if data fetch fails
        """
        try:
            stock = yf.Ticker(ticker) #, proxy=self.proxy)
            
            info = stock.info
            # print(info)
            incom_stmt = stock.income_stmt
            cashflow = stock.cashflow
            earnings = incom_stmt.get("NetIncome", np.nan)
            # earnings = stock.earnings

            # Extract necessary metrics
            roic = info.get('returnOnInvestment', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            gross_margin = info.get('grossMargins', np.nan)
            revenue_growth = self._calculate_revenue_growth(earnings)
            free_cash_flow = self._calculate_free_cash_flow(cashflow)
            debt_to_equity = info.get('debtToEquity', np.nan)
            earnings_stability = self._calculate_earnings_stability(earnings)
            print(roic, roe, gross_margin)

            return {
                'Ticker': ticker,
                'ROIC': roic,
                'ROE': roe,
                'Gross Margin': gross_margin,
                'Revenue Growth': revenue_growth,
                'Free Cash Flow': free_cash_flow,
                'Debt to Equity': debt_to_equity,
                'Earnings Stability': earnings_stability
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def _calculate_revenue_growth(self, earnings: pd.DataFrame) -> float:
        """Calculate 5-year revenue growth rate"""
        try:
            if len(earnings) >= 5:
                revenue_t0 = earnings['Revenue'].iloc[0]
                revenue_t4 = earnings['Revenue'].iloc[4]
                return (revenue_t4 - revenue_t0) / revenue_t0
            return np.nan
        except Exception:
            return np.nan

    def _calculate_free_cash_flow(self, cashflow: pd.DataFrame) -> float:
        """Calculate free cash flow from operating activities and capital expenditures"""
        try:
            cfo = cashflow.loc['Total Cash From Operating Activities'][0]
            capex = cashflow.loc['Capital Expenditures'][0] if 'Capital Expenditures' in cashflow.index else 0
            return cfo + capex  # Capex is usually negative
        except Exception:
            return np.nan

    def _calculate_earnings_stability(self, earnings: pd.DataFrame) -> float:
        """Calculate earnings stability using standard deviation of earnings growth"""
        try:
            if len(earnings) >= 5:
                earnings_growth = earnings['Earnings'].pct_change().dropna()
                return earnings_growth.std() if len(earnings_growth) > 1 else np.nan
            return np.nan
        except Exception:
            return np.nan

    def compute_moat_score(self, metrics: Dict) -> float:
        """
        Compute economic moat score based on various financial metrics
        
        Args:
            metrics (Dict): Dictionary containing financial metrics
            
        Returns:
            float: Moat score between 0 and 1
        """
        scoring_functions = {
            'ROIC': self._score_roic,
            'ROE': self._score_roe,
            'Gross Margin': self._score_gross_margin,
            'Revenue Growth': self._score_revenue_growth,
            'Free Cash Flow': self._score_free_cash_flow,
            'Debt to Equity': self._score_debt_to_equity,
            'Earnings Stability': self._score_earnings_stability
        }

        scores = [scoring_functions[metric](metrics[metric]) 
                 for metric in scoring_functions.keys()]
        return np.mean(scores)

    def filter_stocks(self, tickers: List[str], criteria: Dict) -> pd.DataFrame:
        """
        Filter stocks based on Buffett's criteria
        
        Args:
            tickers (List[str]): List of stock tickers to analyze
            criteria (Dict): Dictionary containing filtering criteria
            
        Returns:
            pd.DataFrame: Filtered DataFrame of stocks meeting criteria
        """
        financial_data = []
        for ticker in tickers:
            data = self.get_financial_data(ticker)
            if data:
                financial_data.append(data)

        df = pd.DataFrame(financial_data)
        
        # Apply Buffett's criteria
        filtered_df = df[
            (df['Debt to Equity'] < criteria.get('max_debt_equity', 0.5)) &
            (df['ROE'] > criteria.get('min_roe', 0.15)) &
            (df['Revenue Growth'] > criteria.get('min_revenue_growth', 0.05)) &
            (df['Free Cash Flow'] > 0)
        ]

        return filtered_df

    # Scoring functions
    def _score_roic(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value >= 15 else 0.7 if value >= 10 else 0.4 if value >= 5 else 0

    def _score_roe(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value >= 20 else 0.7 if value >= 15 else 0.4 if value >= 10 else 0

    def _score_gross_margin(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value >= 50 else 0.7 if value >= 40 else 0.4 if value >= 30 else 0

    def _score_revenue_growth(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value >= 0.15 else 0.7 if value >= 0.10 else 0.4 if value >= 0.05 else 0

    def _score_free_cash_flow(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value > 0 else 0

    def _score_debt_to_equity(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value < 0.5 else 0.7 if value < 1 else 0.4 if value < 2 else 0

    def _score_earnings_stability(self, value: float) -> float:
        if pd.isna(value): return 0
        return 1 if value < 0.05 else 0.7 if value < 0.10 else 0.4 if value < 0.15 else 0

def main():
    """Main function to demonstrate usage"""
    analyzer = StockAnalyzer()
    
    # Example usage
    sp500_tickers = ['AAPL', 'MSFT', 'GOOGL']  # Add more tickers as needed
    criteria = {
        'max_debt_equity': 0.5,
        'min_roe': 0.15,
        'min_revenue_growth': 0.05
    }
    
    filtered_stocks = analyzer.filter_stocks(sp500_tickers, criteria)
    print("Filtered Stocks:")
    print(filtered_stocks)

if __name__ == "__main__":
    main()
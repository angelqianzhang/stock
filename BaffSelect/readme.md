fix the error in selectStock.py: 
def get_financial_data(ticker):    
    try:        
        stock = yf.Ticker(ticker, proxy="http://127.0.0.1:33210")        
        qinfo = stock.info        # financials = stock.financials        
         # balance_sheet = stock.balance_sheet        
        cashflow = stock.cashflow        
        earnings = stock.earnings
        # Extract necessary metrics        
        roic = info.get('returnOnInvestment', np.nan)        
        roe = info.get('returnOnEquity', np.nan)        
        gross_margin = info.get('grossMargins', np.nan)        
        revenue_growth = calculate_revenue_growth(earnings)        
        free_cash_flow = calculate_free_cash_flow(cashflow)        
        debt_to_equity = info.get('debtToEquity', np.nan)        
        earnings_stability = calculate_earnings_stability(earnings)
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

# Calculate Revenue Growth over the last 5 years
def calculate_revenue_growth(earnings):
    try:        
        if len(earnings) >= 5:            
            revenue_t0 = earnings['Revenue'].iloc[0]            
            revenue_t4 = earnings['Revenue'].iloc[4]            
            growth = (revenue_t4 - revenue_t0) / revenue_t0            
            return growth        
        else:            
            return np.nan    
    except:        
        return np.nan


# Calculate Free Cash Flow (Simplified as Cash from Operations - Capital Expenditures)
def calculate_free_cash_flow(cashflow):    
    try:        
        cfo = cashflow.loc['Total Cash From Operating Activities'][0]        
        capex = cashflow.loc['Capital Expenditures'][0] if 'Capital Expenditures' in cashflow.index else 0        
        fcf = cfo + capex  # Capex is usually negative        
        return fcf    
    except:        
        return np.nan

# Calculate Earnings Stability (Standard Deviation of Earnings Growth)
def calculate_earnings_stability(earnings):    
    try:        
        if len(earnings) >= 5:            
            earnings_growth = earnings['Earnings'].pct_change().dropna()            
            if len(earnings_growth) > 1:                
                std_dev = earnings_growth.std()                
                return std_dev            
            else:                
                return np.nan        
        else:            
            return np.nan    
    except:        
        return np.nan

# Define scoring functions for each metric
def score_roic(roic):    
    if pd.isna(roic):        
        return 0    
    elif roic >= 15:        
        return 1    
    elif roic >= 10:        
        return 0.7    
    elif roic >= 5:        
        return 0.4    
    else:        
        return 0

def score_roe(roe):    
    if pd.isna(roe):        
        return 0    
    elif roe >= 20:        
        return 1    
    elif roe >= 15:        
        return 0.7    
    elif roe >= 10:        
        return 0.4    
    else:        
        return 0

def score_gross_margin(gm):    
    if pd.isna(gm):        
        return 0    
    elif gm >= 50:        
        return 1    
    elif gm >= 40:        
        return 0.7    
    elif gm >= 30:        
        return 0.4    
    else:        
        return 0

def score_revenue_growth(rg):    
    if pd.isna(rg):        
        return 0    
    elif rg >= 0.15:        
        return 1    
    elif rg >= 0.10:        
        return 0.7    
    elif rg >= 0.05:        
        return 0.4    
    else:        
        return 0

def score_free_cash_flow(fcf):    
    if pd.isna(fcf):        
        return 0    
    elif fcf > 0:        
        return 1    
    else:        
        return 0

def score_debt_to_equity(de):    
    if pd.isna(de):        
        return 0    
    elif de < 0.5:        
        return 1    
    elif de < 1:        
        return 0.7    
    elif de < 2:        
        return 0.4    
    else:        
        return 0

def score_earnings_stability(es):    
    if pd.isna(es):        
        return 0    
    elif es < 0.05:        
        return 1    
    elif es < 0.10:        
        return 0.7    
    elif es < 0.15:        
        return 0.4    
    else:        
        return 0

def compute_moat_score(row):    
    scores = [        
        score_roic(row['ROIC']),        
        score_roe(row['ROE']),        
        score_gross_margin(row['Gross Margin']),        
        score_revenue_growth(row['Revenue Growth']),        
        score_free_cash_flow(row['Free Cash Flow']),        
        score_debt_to_equity(row['Debt to Equity']),        
        score_earnings_stability(row['Earnings Stability'])    ]   
         # Assign equal weights or customize as needed    
    moat_score = np.sum(scores) / len(scores)  # Average score 
           
    return moat_score

def get_interest_coverage(ticker):    
    """    Fetches the Interest Coverage Ratio for a given stock ticker.
    Parameters:    ticker (str): The stock ticker symbol (e.g., 'AAPL').
    Returns:    float or None: The Interest Coverage Ratio, or None if data is unavailable.    """    
    try:        
        stock = yf.Ticker(ticker)        
        income_statement = stock.financials
        # Ensure the necessary data is present        
        if 'Operating Income' in income_statement.index and 'Interest Expense' in income_statement.index:            
            operating_income = income_statement.loc['Operating Income'][0]            
            interest_expense = income_statement.loc['Interest Expense'][0]
            # Handle cases where Interest Expense is zero to avoid division by zero            
            if interest_expense != 0:                
                interest_coverage = operating_income / abs(interest_expense)               
                return round(interest_coverage, 2)            
            else:                
                print(f"Interest Expense is zero for {ticker}. Cannot compute Interest Coverage Ratio.")                return None        else:            print(f"Necessary financial data not available for {ticker}.")            return None
    except Exception as e:        
        print(f"Error fetching data for {ticker}: {e}")        
        return None

def get_financials(ticker):    
    try:        
        stock = yf.Ticker(ticker)        
        balance = stock.balance_sheet        
        cashflow = stock.cashflow        
        income = stock.financials        
        info = stock.info
        # Extract necessary metrics        
        debt_equity = info.get('debtToEquity', np.nan)        
        current_ratio = info.get('currentRatio', np.nan)        
        price_book = info.get('priceToBook', np.nan)        
        roe = info.get('returnOnEquity', np.nan) * 100  
        # Convert to percentage        
        roa = info.get('returnOnAssets', np.nan) * 100  
        # Convert to percentage        
        interest_coverage = get_interest_coverage(ticker)        
        dividend_growth = info.get('dividendRate', np.nan)  
        # Simplified        
        eps_growth = info.get('earningsQuarterlyGrowth', np.nan)
        # Book value and EPS growth could be more complex to calculate        
        # Here we'll use simplified placeholders        
        book_value_growth = info.get('bookValue', np.nan)  
        # Placeholder        
        eps = info.get('earningsPerShare', np.nan)  # Latest EPS
        # Economic moat is not directly available; using 'moat' information if available        
        moat = get_moat_stocks(ticker)
        return {            
            'Ticker': ticker,            
            'Debt/Equity': debt_equity,            
            'Current Ratio': current_ratio,            
            'Price/Book': price_book,            
            'ROE (%)': roe,            
            'ROA (%)': roa,            
            'Interest Coverage': interest_coverage,            
            'Moat': moat,            
            'EPS Growth': eps_growth,            
            # Additional fields can be added as needed        
            }    
    except Exception as e:        
        print(f"Error fetching data for {ticker}: {e}")        
        return None

# Fetch financial data for all tickers
financial_data = []
for ticker in sp500_tickers[:10]:  
    # For demonstration, we're limiting to the first 10 tickers    
    data = get_financials(ticker)    
    if data:        
        financial_data.append(data)
# Convert to DataFrame
df = pd.DataFrame(financial_data)
# Apply Buffett's criteria
filtered_df = df[    
    (df['Debt/Equity'] < 0.5) &    
    (df['Current Ratio'] > 1.5) & 
    (df['Current Ratio'] < 2.5) &    
    (df['Price/Book'] < 1.5) &    
    (df['ROE (%)'] > 8) &    
    (df['ROA (%)'] > 6) &    
    (df['Interest Coverage'] > 5) &    
    (df['Moat'] > 0) &    
    (df['EPS Growth'] > 0.08)  # Assuming 8% EPS growth    
    ]

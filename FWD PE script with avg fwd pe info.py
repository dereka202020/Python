import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def get_yahoo_forward_pe(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('forwardPE', None)
    except Exception as e:
        print(f"Yahoo Finance error for {ticker}: {str(e)}")
        return None

def get_google_finance_forward_pe(ticker):
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:NASDAQ"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google Finance structure as of April 2025
        pe_ratio = soup.find('div', {'class': 'P6K39c'}, text='P/E ratio').find_next_sibling('div').text
        return float(pe_ratio.split(' ')[0])
    except Exception as e:
        print(f"Google Finance error for {ticker}: {str(e)}")
        return None

def get_marketwatch_forward_pe(ticker):
    try:
        url = f"https://www.marketwatch.com/investing/stock/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # MarketWatch structure as of April 2025
        forward_pe = soup.find('li', {'class': 'kv__item'}, text='Forward P/E').find_next('span').text
        return float(forward_pe)
    except Exception as e:
        print(f"MarketWatch error for {ticker}: {str(e)}")
        return None

def get_moomoo_forward_pe(ticker):
    try:
        url = f"https://www.moomoo.com/market/stock/{ticker}-US"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Moomoo structure as of April 2025
        pe_section = soup.find('div', text='Valuation').find_next('div')
        forward_pe = pe_section.find('div', text='Forward P/E').find_next('div').text
        return float(forward_pe)
    except Exception as e:
        print(f"Moomoo error for {ticker}: {str(e)}")
        return None

def get_average_forward_pe(ticker):
    sources = [
        ('Yahoo', get_yahoo_forward_pe),
        ('Google', get_google_finance_forward_pe),
        ('MarketWatch', get_marketwatch_forward_pe),
        ('Moomoo', get_moomoo_forward_pe)
    ]
    
    values = []
    for source_name, source_func in sources:
        try:
            value = source_func(ticker)
            if value is not None:
                values.append(value)
                print(f"Got {source_name} forward PE for {ticker}: {value}")
            time.sleep(1)  # Be polite between requests
        except Exception as e:
            print(f"Error getting {source_name} data for {ticker}: {str(e)}")
    
    return round(sum(values)/len(values), 2) if values else None

def get_pe_ratios(tickers):
    data = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            avg_forward_pe = get_average_forward_pe(ticker)
            
            data.append({
                'Ticker': ticker,
                'Company Name': info.get('shortName', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Price': info.get('currentPrice', 'N/A'),
                'Current PE': info.get('trailingPE', 'N/A'),
                'Yahoo Forward PE': info.get('forwardPE', 'N/A'),
                'Average Forward PE': avg_forward_pe,
                'Date Recorded': pd.Timestamp.today().strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            print(f"General error processing {ticker}: {str(e)}")
            data.append({
                'Ticker': ticker,
                'Company Name': 'N/A',
                'Sector': 'N/A',
                'Industry': 'N/A',
                'Price': 'N/A',
                'Current PE': 'N/A',
                'Yahoo Forward PE': 'N/A',
                'Average Forward PE': 'N/A',
                'Date Recorded': pd.Timestamp.today().strftime('%Y-%m-%d')
            })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    stocks = input("Enter stock tickers (comma-separated, max 150): ").upper().replace(' ', '').split(',')[:150]
    
    df = get_pe_ratios(stocks)
    
    print("\nComprehensive P/E Analysis:")
    print(df.to_string(index=False))
    
    df.to_csv('comprehensive_pe_analysis.csv', index=False)
    print("\nResults saved to comprehensive_pe_analysis.csv")

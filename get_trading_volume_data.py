"""
Description: This script gets last year's trading volume data for a given stock ticker
"""
import os
import time
import json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# Get trading volume data for a given stock ticker and date range
def get_trading_volume_data(symbol: str, start: str, end: str):
    """
    Get trading volume data for a given stock ticker and date range
    """
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}?adjusted=true&sort=asc&apiKey={os.getenv('POLYGON_API_KEY')}"
    response = requests.get(url, timeout=50)
    json_body = response.json()
    # save json response to file
    with open(os.path.join('trading-volume-data', f'{symbol}.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_body))


if __name__ == '__main__':
    stocks = pd.read_csv('stocks.csv')
    for index, row in stocks.iterrows():
        ticker = row['ticker']
        START_DATE = '2024-01-01'
        END_DATE = '2024-12-31'
        get_trading_volume_data(ticker, START_DATE, END_DATE)
        print(f"Trading volume data for {ticker} saved to {ticker}.json")
        time.sleep(2)  # sleep for 2 seconds to avoid rate limiting
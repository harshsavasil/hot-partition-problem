import os
import json
import pandas as pd
import numpy as np

# {
#     "v": 1441581.0,
#     "vw": 138.9896,
#     "o": 138.19,
#     "c": 138.75,
#     "h": 140.59,
#     "l": 137.91,
#     "t": 1704171600000,
#     "n": 30485
# }

def get_p95_volume_data(symbol: str):
    """
    Get the 95th percentile of trading volume data for a given stock ticker
    """
    with open(os.path.join('trading-volume-data', f'{symbol}.json'), 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        entries = json_data.get('resultsCount', 0)
        if entries == 0:
            return 0
        trading_volume_data = [item['v'] for item in json_data.get('results', [])]
        p95 = np.percentile(trading_volume_data, 95)
        return p95


if __name__ == '__main__':
    stocks = pd.read_csv('stocks.csv')
    final_data = []
    for index, row in stocks.iterrows():
        ticker = row['ticker']
        p95_volume = get_p95_volume_data(ticker)
        final_data.append({ "symbol": row['ticker'], "volume": p95_volume })
    with open('trading-volumes.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(final_data))
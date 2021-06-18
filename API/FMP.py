import json
import pandas as pd
from urllib.request import urlopen


class FMP:
    def __init__(self, ticker, timeframe):
        self._ticker = ticker
        self.fmp_api_key = 'demo'
        self.ticker = ticker
        self.timeframe = timeframe
        self.get_data()

    def __repr__(self):
        return f"FMP(ticker = {self.ticker}, timeframe = {self.timeframe})"

    def get_data(self):
        if self.timeframe == 'daily':
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{self.ticker}?apikey={self.fmp_api_key}"
            data = self.parse_data(url)['historical'][0]
            return pd.json_normalize(data)

        else:
            url = f"https://financialmodelingprep.com/api/v3/historical-chart/{self.timeframe}/{self.ticker}?apikey={self.fmp_api_key}"
            return self.parse_data(url)

    def parse_data(self, url):
        response = urlopen(url)
        data = response.read().decode("utf-8")
        data = json.loads(data)
        df = pd.json_normalize(data)
        df.sort_values(by=['date'], ascending=True, inplace=True, ignore_index=True)
        return df


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from API.FMP import FMP
import plotly.graph_objects as go

# plt.style.use("seaborn")


# Final Version


class FinancialInstrument():
    """ Class for analyzing Financial Instruments like stocks.

    Attributes
    ==========
    ticker: str
        ticker symbol with which to work with
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval

    Methods
    =======
    get_data:
        retrieves daily price data (from yahoo finance) and prepares the data
    log_returns:
        calculates log returns
    plot_prices:
        creates a price chart
    plot_returns:
        plots log returns either as time series ("ts") or histogram ("hist")
    set_ticker:
        sets a new ticker
    mean_return:
        calculates mean return
    std_returns:
        calculates the standard deviation of returns (risk)
    annualized_perf:
        calculates annulized return and risk
    """
    
    def __init__(self, ticker, timeframe, start, end):
        self._ticker = ticker
        self.timeframe = timeframe
        self.start = start
        self.end = end
        self.get_data()
        self.log_returns()
        self.cumulative_returns()
    
    def __repr__(self): 
        return f"FinancialInstrument(ticker = {self._ticker}, start = {self.start}, end = {self.end})"
    
    def get_data(self):
        # ''' retrieves (from yahoo finance) and prepares the data
        # '''
        # raw = yf.download(self._ticker, self.start, self.end).Close.to_frame()
        # raw.rename(columns = {"Close":"price"}, inplace = True)
        # self.data = raw

        """retrieves (from Financial Modelling Prep) and prepares the data
        """
        data = FMP(self._ticker, self.timeframe).get_data()[['date', 'close']]
        data['date'] = data[['date']]
        data['price'] = data[['close']]
        # data[self._ticker] = data[['close']]
        self.data = data.dropna()
        
    def log_returns(self):
        """calculates log returns
        """
        self.data["log_returns"] = np.log(self.data.price/self.data.price.shift(1))

    def cumulative_returns(self):
        self.data["cumulative_returns"] = self.data.log_returns.cumsum().apply(np.exp)

    def plot_prices(self):
        """ creates a price chart
        """
        fig = go.Figure([
            go.Scatter(
                x=list(self.data['date']),
                y=list(self.data.price)
            )])

        fig.update_layout(
            title=f"{self._ticker}",
            xaxis_title="Time",
            yaxis_title="Price (Close)",
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="RebeccaPurple"
            )
        )

        fig.show()

    def plot_cumulative_returns(self):
        self.data.cumulative_returns.plot(figsize=(12, 8))
        plt.title("Cumulative Returns Chart: {}".format(self._ticker), fontsize=15)

    def plot_log_returns(self, kind="ts"):
        """ plots log returns either as time series ("ts") or histogram ("hist")
        """
        if kind == "ts":
            self.data.log_returns.plot(figsize=(12, 8))
            plt.title("Returns: {}".format(self._ticker), fontsize=15)
        elif kind == "hist":
            self.data.log_returns.hist(figsize=(12, 8), bins=int(np.sqrt(len(self.data))))
            plt.title("Frequency of Returns: {}".format(self._ticker), fontsize=15)
    
    def set_ticker(self, ticker=None):
        """sets a new ticker
        """
        if ticker is not None:
            self._ticker = ticker
            self.get_data()
            self.log_returns()

    def summary(self):
        print(f"mean return: {self.mean_return()}")
        print(f"std return: {self.std_returns()}")
        self.annualized_performance()
            
    def mean_return(self, freq=None):
        """calculates mean return
        """
        if freq is None:
            return self.data.log_returns.mean()
        else:
            resampled_price = self.data.price.resample(freq).last()
            resampled_returns = np.log(resampled_price / resampled_price.shift(1))
            return resampled_returns.mean()
    
    def std_returns(self, freq=None):
        """calculates the standard deviation of returns (risk)
        """
        if freq is None:
            return self.data.log_returns.std()
        else:
            resampled_price = self.data.price.resample(freq).last()
            resampled_returns = np.log(resampled_price / resampled_price.shift(1))
            return resampled_returns.std()
        
    def annualized_performance(self):
        """calculates annulized return and risk
        """
        mean_return = round(self.data.log_returns.mean() * 252, 3)
        risk = round(self.data.log_returns.std() * np.sqrt(252), 3)
        print("Annualized Return: {} | Annualized Risk: {}".format(mean_return, risk))

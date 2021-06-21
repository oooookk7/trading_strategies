import pandas as pd
import numpy as np
from itertools import product
import plotly.graph_objects as go


class EMAVectorized:
    """ Class for the vectorized backtesting of EMA-based trading strategies.
    """

    def __init__(self, data, ticker, EMA_S, EMA_L, start, end):
        """
        Parameters
        ----------
        price: str
            ticker price (instrument) to be backtested
        EMA_S: int
            moving window in bars (e.g. days) for shorter EMA
        EMA_L: int
            moving window in bars (e.g. days) for longer EMA
        start: str
            start date for data import
        end: str
            end date for data import
        """
        self.ticker = ticker
        self.data = data
        self.EMA_S = EMA_S
        self.EMA_L = EMA_L
        self.start = start
        self.end = end
        self.results = None
        self.get_data()
        self.prepare_data()

    def __repr__(self):
        return "EMABacktester(price = {}, EMA_S = {}, EMA_L = {}, start = {}, end = {})".format(self.data.price, self.EMA_S,
                                                                                                self.EMA_L, self.start,
                                                                                                self.end)

    def get_data(self):
        # raw.rename(columns={self.ticker: "price"}, inplace=True)
        raw = self.data
        raw['log_returns'] = np.log(raw.price / raw.price.shift(1))
        raw['date'] = self.data['date']

        self.data = raw

    def prepare_data(self):
        """ data for strategy backtesting (strategy-specific)."""
        data = self.data.copy()
        data["EMA_S"] = self.data.price.ewm(span=self.EMA_S).mean()
        data["EMA_L"] = self.data.price.ewm(span=self.EMA_L).mean()

    def set_parameters(self, EMA_S: int = None, EMA_L: int = None) -> None:
        """ Updates EMA parameters and the prepared dataset.
        """
        if EMA_S is not None:
            self.EMA_S = EMA_S
            self.data["EMA_S"] = self.data.price.ewm(span=self.EMA_S).mean()
        if EMA_L is not None:
            self.EMA_L = EMA_L
            self.data["EMA_L"] = self.data.price.ewm(span=self.EMA_L).mean()

    def test_strategy(self):
        """ Backtests the EMA-based trading strategy.
        """
        data = self.data.copy().dropna()
        data["position"] = np.where(data["EMA_S"] > data["EMA_L"], 1, -1)
        data["strategy"] = data["position"].shift(1) * data["log_returns"]
        data.dropna(inplace=True)
        data["cumulative returns"] = data["log_returns"].cumsum().apply(np.exp)
        data["cumulative strategy"] = data["strategy"].cumsum().apply(np.exp)
        self.results = data

        # absolute performance of the strategy
        perf = data["cumulative strategy"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - data["cumulative returns"].iloc[-1]

        return round(perf, 6), round(outperf, 6)

    def plot_results(self):
        """ Plots the performance of the trading strategy and compares to "buy and hold".
        """
        if self.results is None:
            print("Run test_strategy() first.")
        else:
            title = "{} | EMA_S = {} | EMA_L = {}".format(self.ticker, self.EMA_S, self.EMA_L)
            # self.results[["cumulative returns", "cumulative strategy"]].plot(title=title, figsize=(12, 8))
            fig = go.Figure([
                go.Scatter(
                    x=list(self.data['date']),
                    y=list(self.results["cumulative returns"]),
                    name='cumulative returns'
                )])

            fig.add_trace(
                go.Scatter(
                    x=list(self.data['date']),
                    y=list(self.results["cumulative strategy"]),
                    name='cumulative strategy'
                )
            )

            fig.update_layout(
                title=f"{title}",
                xaxis_title="Time",
                yaxis_title="Price (Close)",
                font=dict(
                    family="Courier New, monospace",
                    size=14,
                    color="RebeccaPurple"
                )
            )

            fig.show()

    def optimize_parameters(self, EMA_S_range, EMA_L_range):
        """ Finds the optimal strategy (global maximum) given the EMA parameter ranges.

        Parameters
        ----------
        EMA_S_range, EMA_L_range: tuple
            tuples of the form (start, end, step size)
        """

        combinations = list(product(range(*EMA_S_range), range(*EMA_L_range)))

        # test all combinations
        results = []
        for comb in combinations:
            self.set_parameters(comb[0], comb[1])
            results.append(self.test_strategy()[0])

        best_perf = np.max(results)  # best performance
        opt = combinations[np.argmax(results)]  # optimal parameters

        # run/set the optimal strategy
        self.set_parameters(opt[0], opt[1])
        self.test_strategy()

        # create a df with many results
        many_results = pd.DataFrame(data=combinations, columns=["EMA_S", "EMA_L"])
        many_results["performance"] = results
        self.results_overview = many_results

        return opt, best_perf

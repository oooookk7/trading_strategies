import pandas as pd
import numpy as np


class IterativeBase:

    def __init__(self, data, ticker, start, end, amount, use_spread=True):
        self.data = data
        self.ticker = ticker
        self.start = start
        self.end = end
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trades = 0
        self.position = 0
        self.use_spread = use_spread
        self.get_data()

    def get_data(self):
        # raw = pd.read_csv("./detailed.csv", parse_dates=["time"], index_col="time").dropna()
        raw = self.data.copy()
        raw = raw.loc[self.start:self.end]
        raw["returns"] = np.log(raw.price / raw.price.shift(1))
        self.data = raw
        # raw = self.data['price'].to_frame().dropna()
        # raw["log_returns"] = np.log(raw / raw.shift(1))
        # # raw['date'] = self.data['date']
        # self.data = raw

    def plot_data(self, cols=None):
        if cols is None:
            cols = "price"
        self.data[cols].plot(figsize=(12, 8), title=self.ticker)

    def get_values(self, bar):
        date = str(self.data.index[bar].date())
        price = round(self.data.price.iloc[bar], 5)
        spread = round(self.data.spread.iloc[bar], 5)
        return date, price, spread

    def print_current_balance(self, bar):
        date, price, spread = self.get_values(bar)
        print("{} | Current Balance: {}".format(date, round(self.current_balance, 2)))

    def buy_instrument(self, bar, units=None, amount=None):
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price += spread / 2  # ask price
        if amount is not None:  # use units if units are passed, otherwise calculate units
            units = int(amount / price)
        self.current_balance -= units * price  # reduce cash balance by "purchase price"
        self.units += units
        self.trades += 1
        print("{} |  Buying {} for {}".format(date, units, round(price, 5)))

    def sell_instrument(self, bar, units=None, amount=None):
        date, price, spread = self.get_values(bar)
        if self.use_spread:
            price -= spread / 2  # bid price
        if amount is not None:  # use units if units are passed, otherwise calculate units
            units = int(amount / price)
        self.current_balance += units * price  # increases cash balance by "purchase price"
        self.units -= units
        self.trades += 1
        print("{} |  Selling {} for {}".format(date, units, round(price, 5)))

    def print_current_position_value(self, bar):
        date, price, spread = self.get_values(bar)
        cpv = self.units * price
        print("{} |  Current Position Value = {}".format(date, round(cpv, 2)))

    def print_current_nav(self, bar):
        date, price, spread = self.get_values(bar)
        nav = self.current_balance + self.units * price
        print("{} |  Net Asset Value = {}".format(date, round(nav, 2)))

    def close_pos(self, bar):
        date, price, spread = self.get_values(bar)
        print(75 * "-")
        print("{} | +++ CLOSING FINAL POSITION +++".format(date))
        self.current_balance += self.units * price  # closing final position (works with short and long!)
        self.current_balance -= (abs(self.units) * spread / 2 * self.use_spread)  # substract half-spread costs
        print("{} | closing position of {} for {}".format(date, self.units, price))
        self.units = 0  # setting position to neutral
        self.trades += 1
        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        self.print_current_balance(bar)
        print("{} | net performance (%) = {}".format(date, round(perf, 2)))
        print("{} | number of trades executed = {}".format(date, self.trades))
        print(75 * "-")

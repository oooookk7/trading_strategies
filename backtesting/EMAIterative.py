from .IterativeBase import *


class EMAIterative(IterativeBase):

    # helper method
    def go_long(self, bar, units=None, amount=None):
        if self.position == -1:
            self.buy_instrument(bar, units=-self.units)  # if short position, go neutral first
        if units:
            self.buy_instrument(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(bar, amount=amount)  # go long

    # helper method
    def go_short(self, bar, units=None, amount=None):
        if self.position == 1:
            self.sell_instrument(bar, units=self.units)  # if long position, go neutral first
        if units:
            self.sell_instrument(bar, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(bar, amount=amount)  # go short

    def test_sma_strategy(self, SMA_S, SMA_L):

        # nice printout
        stm = "Testing SMA strategy | {} | SMA_S = {} & SMA_L = {}".format(self.ticker, SMA_S, SMA_L)
        print("-" * 75)
        print(stm)
        print("-" * 75)

        # reset
        self.position = 0  # initial neutral position
        self.trades = 0  # no trades yet
        self.current_balance = self.initial_balance  # reset initial capital
        self.get_data()  # reset dataset

        # prepare data
        self.data["SMA_S"] = self.data["price"].rolling(SMA_S).mean()
        self.data["SMA_L"] = self.data["price"].rolling(SMA_L).mean()
        self.data.dropna(inplace=True)

        # sma crossover strategy
        for bar in range(len(self.data) - 1):  # all bars (except the last bar)
            if self.data["SMA_S"].iloc[bar] > self.data["SMA_L"].iloc[bar]:  # signal to go long
                if self.position in [0, -1]:
                    self.go_long(bar, amount="all")  # go long with full amount
                    self.position = 1  # long position
            elif self.data["SMA_S"].iloc[bar] < self.data["SMA_L"].iloc[bar]:  # signal to go short
                if self.position in [0, 1]:
                    self.go_short(bar, amount="all")  # go short with full amount
                    self.position = -1  # short position
        self.close_pos(bar + 1)  # close position at the last bar

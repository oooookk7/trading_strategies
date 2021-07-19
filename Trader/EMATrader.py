from .BaseTrader import *


class EMATrader(BaseTrader):

    def __init__(self, instrument, bar_length, EMA_S, EMA_L, units):
        super(EMATrader, self).__init__(
            instrument,
            bar_length,
            units
        )

        self.EMA_S = EMA_S
        self.EMA_L = EMA_L

    def define_strategy(self):  # "strategy-specific"
        df = self.raw_data.copy()

        # ******************** define your strategy here ************************
        df["EMA_S"] = df[self.instrument].ewm(span=self.EMA_S).mean()
        df["EMA_L"] = df[self.instrument].emw(span=self.EMA_L).mean()
        df["position"] = np.where(df["EMA_S"] > df["EMA_L"], 1, -1)
        # ***********************************************************************

        self.data = df.copy()

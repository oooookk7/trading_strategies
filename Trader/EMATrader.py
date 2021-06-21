from .BaseTrader import *


class EMATrader(BaseTrader):

    def __init__(self, instrument, bar_length, SMA_S, SMA_L, units):
        super(EMATrader, self).__init__(
            instrument,
            bar_length,
            units
        )

        self.SMA_S = SMA_S
        self.SMA_L = SMA_L

    def define_strategy(self):  # "strategy-specific"
        df = self.raw_data.copy()

        # ******************** define your strategy here ************************
        df["SMA_S"] = df[self.instrument].rolling(self.SMA_S).mean()
        df["SMA_L"] = df[self.instrument].rolling(self.SMA_L).mean()
        df["position"] = np.where(df["SMA_S"] > df["SMA_L"], 1, -1)
        # ***********************************************************************

        self.data = df.copy()

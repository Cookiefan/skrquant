import backtrader as bt
from indicators import WaveIndicator
import pandas as pds
from strategy.SkrStrategy import SkrStrategy
from utils import HS300Data, code300


class WaveStrategy(SkrStrategy):
    paras = (
        ('theta', 0.05),
    )
    def __init__(self):
        self.t = 0
        self.hs300 = self.datas[0]
        self.stocks = self.datas[1:]
        self.hs300_wave = WaveIndicator(self.hs300, theta = 0.03)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True))
    for ticker in code300:
        df = pds.read_csv(f"DATA/HS300/{ticker}.csv",
                          parse_dates=True,
                          index_col=0)
        if len(df) > 100:
            cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))

    cerebro.addstrategy(WaveStrategy)
    results = cerebro.run()
    cerebro.plot(iplot=False)
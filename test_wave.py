import backtrader as bt
from indicators.WaveIndicator import WaveIndicator
import pandas as pds
from strategy.SkrStrategy import SkrStrategy
from utils import HS300Data, code300


class WaveStrategy(SkrStrategy):
    def __init__(self):
        self.t = 0
        self.hs300 = self.datas[0]
        self.hs300_wave = WaveIndicator(self.hs300, theta=0.05)

    def prenext(self):
        self.next()

    def next(self):
        if self.hs300_wave.l.status == 1:
            self.buy()
        else:
            self.close()
        self.t += 1



if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True))

    cerebro.addstrategy(WaveStrategy)
    cerebro.broker.setcash(100000.0)
    results = cerebro.run()
    cerebro.plot(style='bar',iplot=False)

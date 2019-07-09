import pandas as pds
import backtrader as bt
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy


class BollingStrategy(SkrStrategy):
    params = dict(
        period=20,
        devfactor=2
    )

    def __init__(self):
        self.t = 0
        self.hs300 = self.datas[0]
        self.boll = bt.ind.BollingerBands(self.hs300)

    def prenext(self):
        self.next()

    def next(self):
        if self.t % 1 == 0:
            if self.hs300.low[0] < self.boll.l.bot[0] and self.hs300.high[0] > self.boll.l.bot[0]:
                if not self.getposition():
                    self.buy()
            if self.hs300.low[0] < self.boll.l.top[0] and self.hs300.high[0] > self.boll.l.top[0]:
                if self.getposition():
                    self.close()
        self.t += 1

    def stop(self):
        self.log(f'{self.p.period}->{self.broker.getvalue()}')


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True))
    cerebro.addstrategy(BollingStrategy)
    # cerebro.optstrategy(BollingStrategy, period = range(5, 56, 5))
    cerebro.broker.setcash(100000.0)
    results = cerebro.run()
    cerebro.plot(style='bar')

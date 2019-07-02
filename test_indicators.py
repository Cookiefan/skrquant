import backtrader as bt
from indicators.WaveIndicator import WaveIndicator
import pandas as pds
from strategy.SkrStrategy import SkrStrategy
from utils import HS300Data, code300


class WaveStrategy(SkrStrategy):
    params = (
        ('ranker', 100),
    )

    def __init__(self):
        self.t = 0
        self.hs300 = self.datas[0]
        self.stocks = self.datas[1:]
        self.hs300_wave = WaveIndicator(self.hs300, theta=0.05)
        self.inds = {}
        for s in self.stocks:
            self.inds[s] = {}
            self.inds[s]["wave"] = WaveIndicator(s, theta=0.05)
            self.inds[s]["atr20"] = bt.indicators.ATR(s, period=20)

    def prenext(self):
        self.next()

    def next(self):
        if self.t % 5 == 0:
            self.rebalance_portfolio()
        if self.t % 10 == 0:
            self.rebalance_positions()
        self.t += 1

    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda s: len(s) > 100, self.stocks))
        self.rankings.sort(key=lambda s: self.inds[s]["wave"].hlr)
        num_stocks = len(self.rankings)
        for i, s in enumerate(self.rankings[int(num_stocks * self.p.ranker):]):
            if self.getposition(s).size:
                self.close(s)
        if self.hs300_wave.status == -1:
            return
        for i, s in enumerate(self.rankings[:int(num_stocks * self.p.ranker)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(s).size:
                size = value * 0.001 / self.inds[s]["atr20"]
                self.buy(s, size=size)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)
        if self.hs300_wave.status == -1:
            return
        for i, s in enumerate(self.rankings[:int(num_stocks * self.p.ranker)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[s]["atr20"]
            self.order_target_size(s, size)

    def stop(self):
        self.log('Ending Value %.2f' %
                 (self.broker.getvalue()))



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
    cerebro.broker.setcash(100000.0)
    results = cerebro.run()
    cerebro.plot(style='bar', iplot=False)

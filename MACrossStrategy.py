import pandas as pds
import backtrader as bt
from utils import HS300Data
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy
from datamaker import code300,code_cement
from indicators.MomentumIndicator import Momentum


class CrossLineStrategy(SkrStrategy):
    params = dict(
        tuning=False,
        ranker=0.1,
        global_period=100,
        short_period=14,
        long_period=80,
        atr_period=20
    )

    def __init__(self):
        self.t = 0
        self.inds = {}
        self.hs300 = self.datas[0]
        self.stocks = self.datas[1:]
        self.hs300_ma = self.hs300 - bt.indicators.SimpleMovingAverage(self.hs300, period = 100)
        for s in self.stocks:
            self.inds[s] = {}
            self.inds[s]["short_ma"] = bt.indicators.SimpleMovingAverage(s.close, period=self.p.short_period)
            self.inds[s]["long_ma"] = bt.indicators.SimpleMovingAverage(s.close, period=self.p.long_period)
            self.inds[s]["cross"] = (self.inds[s]["short_ma"] - self.inds[s]["long_ma"])/(self.inds[s]["short_ma"]+self.inds[s]["long_ma"])
            self.inds[s]["atr20"] = bt.indicators.ATR(s, period=self.p.atr_period)

    def start(self):
        if self.p.tuning:
            self.tim = tqdm(total=608,desc = 'opt(%f):'%(self.p.ranker))


    def next(self):
        if self.t % 5 == 0:
            self.rebalance_portfolio()
        if self.t % 10 == 0:
            self.rebalance_positions()
        self.t += 1
        if self.p.tuning:
            self.tim.update(1)

    def stop(self):
        if self.p.tuning:
            self.tim.close()
            self.log('({rk}) -> Ending Value {va}'
                     .format(rk=self.p.ranker,
                             va=self.broker.getvalue()))

    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda s: len(s) > 100, self.stocks))
        self.rankings.sort(key=lambda s: self.inds[s]["cross"])
        num_stocks = len(self.rankings)
        num_pick = int(num_stocks * self.p.ranker)
        for i, s in enumerate(self.rankings[num_pick:]):
            if self.getposition(s).size:
                self.close(s)

        if self.hs300_ma < 0:
            return
        for i, s in enumerate(self.rankings[:num_pick]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(s).size:
                size = value * 0.001 / self.inds[s]["atr20"]
                self.buy(s, size=size)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)
        num_pick = int(num_stocks * self.p.ranker)
        if self.hs300_ma < 0:
            return
        for i, s in enumerate(self.rankings[:num_pick]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[s]["atr20"]
            self.order_target_size(s, size)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True, name = 'HS300'))
    for ticker in tqdm(code300):
        df = pds.read_csv(f"DATA/HS300/{ticker}.csv",
                          parse_dates=True,
                          index_col=0)
        if len(df) > 100:
            cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False, name = ticker))

    cerebro.addstrategy(CrossLineStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    # cerebro.optstrategy(CrossLineStrategy,
    #                     tuning=True,
    #                     order_print=False,
    #                     ranker = [0.1,0.2,0.3,0.4,0.5])
    results = cerebro.run()
    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    cerebro.plot(iplot=False)

import pandas as pds
import backtrader as bt
from utils import HS300Data
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy
from datamaker import code300, code_cement
from indicators.MomentumIndicator import Momentum
from datetime import date


class CrossLineStrategy(SkrStrategy):
    params = dict(
        ranker=0.3,
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
        self.hs300_ma = self.hs300.close - bt.ind.SMA(self.hs300.close, period=self.p.global_period)
        for s in self.stocks:
            self.inds[s] = {}
            self.inds[s]["short_ma"] = bt.ind.SMA(s.close, period=self.p.short_period)
            self.inds[s]["long_ma"] = bt.ind.SMA(s.close, period=self.p.long_period)
            self.inds[s]["cross"] = (self.inds[s]["short_ma"] - self.inds[s]["long_ma"]) / (
                        self.inds[s]["short_ma"] + self.inds[s]["long_ma"])
            self.inds[s]["atr20"] = bt.ind.ATR(s, period=self.p.atr_period)

    def next(self):
        if self.p.start!=None and self.data0.datetime.date(0) < self.p.start:
            return
        if self.p.start!=None and self.data0.datetime.date(0) > self.p.end:
            return

        if self.t % 5 == 0:
            self.rebalance_portfolio()
        # if self.t % 10 == 0:
        #     self.rebalance_positions()
        self.t += 1

    def rebalance_portfolio(self):
        self.rankings = self.stocks[:]
        self.rankings.sort(key=lambda s: self.inds[s]["cross"][0])
        # self.log([s._name for s in self.rankings])

        for s in self.rankings:
            if self.getposition(s).size and self.inds[s]["cross"][0] < 0:
                self.close(s)
        if self.hs300_ma[0] < 0:
            return

        cash = self.broker.get_cash()
        value = self.broker.get_value()
        for s in self.rankings:
            size = value * 0.01 / self.inds[s]["atr20"][0]
            size = size//100 * 100
            if self.inds[s]["cross"][0] < 0 or self.getposition(s).size > 0:
                continue
            if size * s.close[0] > cash:
                continue
            print(s._name, size * s.close[0], cash)
            cash -= size * s.close[0]
            self.buy(s, size=size)

    def rebalance_positions(self):
        if self.hs300_ma[0] < 0:
            return
        for s in self.rankings:
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            size = value * 0.01 / self.inds[s]["atr20"][0]
            size = size//100 * 100
            if self.inds[s]["cross"][0] < 0 or size * s.close[0] > cash or self.getposition(s).size > 0:
                continue
            self.order_target_size(s, size)


if __name__ == '__main__':
    start = date(2017, 1, 3)
    end = date(2019, 6, 30)
    cerebro = bt.Cerebro(stdstats=False)
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True, name='HS300'))
    # code_cement = ['600425','600801','000935','600668']
    for ticker in code_cement:
        df = pds.read_csv(f"DATA/Cement/{ticker}.csv", parse_dates=True, index_col=0)
        cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False, name=ticker))
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.0008)
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addstrategy(CrossLineStrategy, start=start, end=end)
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
    cerebro.plot(style='bar', iplot=False, start=start, end=end)

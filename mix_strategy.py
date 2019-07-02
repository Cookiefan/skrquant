import datetime
import tushare
import pandas as pds
import backtrader as bt
from utils import HS300Data, code300
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy






class CrossLineStrategy(SkrStrategy):
    params = (
        ('message_order', True),
        ('ranker', 0.2),
        ('global_period', 100),
        ('short_period', 5),
        ('long_period', 60),
        ('atr_period', 20),
    )

    def __init__(self):
        self.t = 0
        self.inds = {}
        self.hs300 = self.datas[0]
        self.stocks = self.datas[1:]
        self.hs300_ma = bt.indicators.SimpleMovingAverage(self.hs300.close,
                                                          period=self.p.global_period)
        for s in self.stocks:
            self.inds[s] = {}
            self.inds[s]["short_ma"] = bt.indicators.SimpleMovingAverage(s.close, period=self.p.short_period)
            self.inds[s]["long_ma"] = bt.indicators.SimpleMovingAverage(s.close, period=self.p.long_period)
            self.inds[s]["cross"] = self.inds[s]["short_ma"] - self.inds[s]["long_ma"]
            self.inds[s]["atr20"] = bt.indicators.ATR(s, period=self.p.atr_period)

    def prenext(self):
        self.next()

    def next(self):
        if self.t % 5 == 0:
            self.rebalance_portfolio()
        if self.t % 10 == 0:
            self.rebalance_positions()
        self.t += 1

    def stop(self):
        self.log('(MA Period (%d, %d)) Ending Value %.2f' %
                 (self.p.short_period, self.p.long_period, self.broker.getvalue()))

    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda s: len(s) > 100, self.stocks))
        self.rankings.sort(key=lambda s: self.inds[s]["cross"])
        num_stocks = len(self.rankings)
        for i, s in enumerate(self.rankings[int(num_stocks * self.p.ranker):]):
            if self.getposition(s).size:
                self.close(s)

        if self.hs300.close < self.hs300_ma:
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
        if self.hs300.close < self.hs300_ma:
            return
        for i, s in enumerate(self.rankings[:int(num_stocks * self.p.ranker)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[s]["atr20"]
            self.order_target_size(s, size)


class OrderObserver(bt.observer.Observer):
    lines = ('created', 'expired',)

    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

    plotlines = dict(
        created=dict(marker='*', markersize=8.0, color='lime', fillstyle='full'),
        expired=dict(marker='s', markersize=8.0, color='red', fillstyle='full')
    )

    def next(self):
        for order in self._owner._orderspending:
            if order.data is not self.data:
                continue

            if not order.isbuy():
                continue

            # Only interested in "buy" orders, because the sell orders
            # in the strategy are Market orders and will be immediately
            # executed

            if order.status in [bt.Order.Accepted, bt.Order.Submitted]:
                self.lines.created[0] = order.created.price

            elif order.status in [bt.Order.Expired]:
                self.lines.expired[0] = order.created.price


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True))
    for ticker in tqdm(code300):
        df = pds.read_csv(f"DATA/HS300/{ticker}.csv",
                          parse_dates=True,
                          index_col=0)
        if len(df) > 100:
            cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))

    cerebro.addstrategy(CrossLineStrategy)
    # cerebro.optstrategy(CrossLineStrategy, message_order = False, short_period=range(3, 10, 1), long_period = range(10, 100, 10))
    cerebro.broker.setcash(100000.0)
    cerebro.addobserver(OrderObserver)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    cerebro.plot(iplot=False)
    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")

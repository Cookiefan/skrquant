import pandas as pds
import backtrader as bt
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy
from datamaker import code300, code_cement,code_electronics


class TurtleStrategy(SkrStrategy):
    params = dict(
        long_period=10,
        short_period=5,
    )

    def __init__(self):
        self.t = 0
        self.bigplate = self.datas[0]
        self.bpma = self.bigplate - bt.indicators.SimpleMovingAverage(self.bigplate, period=100)
        self.stocks = self.datas
        self.atr = {}
        self.high20 = {}
        self.low10 = {}
        self.level = {}
        self.stop_price = {}
        for s in self.stocks:
            self.atr[s] = bt.ind.AverageTrueRange(s)
            self.high20[s] = bt.ind.MovingAverageSimple(s.high, period=self.p.long_period)
            self.low10[s] = bt.ind.MovingAverageSimple(s.low, period=self.p.short_period)
            self.level[s] = 0
            self.stop_price[s] = 0

    def next(self):
        self.t += 1
        for s in self.stocks:
            if s.low < self.stop_price[s] or self.bpma < 0:
                self.level[s] = 0
                self.stop_price[s] = 0
            elif s.high > self.high20[s]:
                self.level[s] += 1
                self.level[s] = min(self.level[s], 5)
                self.stop_price[s] = s.close - 2. * self.atr[s]
            elif s.low < self.low10[s]:
                self.level[s] -= 1
                self.level[s] = max(self.level[s], 0)
                self.stop_price[s] = s.close - 2. * self.atr[s]
        self.check_position()

    def stop(self):
        self.log(f'({self.p.long_period, self.p.short_period}) -> Ending Value {self.broker.get_value()}')


    def check_position(self):
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        for s in self.stocks:
            pos = self.level[s] * value * 0.01 / self.atr[s]
            # print(s._name,pos)
            self.order_target_value(s, target=pos)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=False))
    cerebro.addstrategy(TurtleStrategy)
    for ticker in tqdm(code_cement):
        df = pds.read_csv(f"DATA/Cement/{ticker}.csv",
                          parse_dates=True,
                          index_col=0)
        if len(df) > 100:
            cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False, name=ticker))

    # cerebro.optstrategy(TurtleStrategy, long_period=range(10, 51, 10), short_period=range(5, 26, 5), order_print=False)
    cerebro.broker.setcash(1000000.0)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    cerebro.plot(style='bar', iplot=False)

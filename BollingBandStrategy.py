import pandas as pds
import backtrader as bt
from tqdm import tqdm
from strategy.SkrStrategy import SkrStrategy
from datamaker import code300, code_cement


class BollingStrategy(SkrStrategy):
    params = dict()

    def __init__(self):
        self.t = 0
        self.hs300 = self.datas[0]
        self.stocks = self.datas[1:]
        self.hs300_boll = bt.ind.BollingerBands(self.hs300)
        self.boll = {}
        self.atr = {}
        for s in self.stocks:
            self.boll[s] = bt.ind.BollingerBands(s, period=20)
            self.atr[s] = bt.ind.AverageTrueRange(s)

    def next(self):
        score = {}
        car = []
        for s in self.stocks:
            b = self.boll[s].l
            if s.close[0] > b.top[0]:
                car.append(s)
                score[s] = (s.close[0] - b.top[0]) / s.close[0]
        car.sort(key=lambda x: score[x], reverse=True)
        for s in self.stocks:
            if s not in car:
                self.close(s)
        for s in car[:1]:
            self.order_target_percent(s, target=0.99 / len(car))
        self.t += 1


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # cerebro.broker.set_coc(True)
    hs = pds.read_csv("DATA/hs300.csv",
                      parse_dates=True,
                      index_col=0)
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True))
    cerebro.addstrategy(BollingStrategy)
    for ticker in tqdm(code_cement):
        df = pds.read_csv(f"DATA/Cement/{ticker}.csv",
                          parse_dates=True,
                          index_col=0)
        if len(df) > 100:
            cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False, name=ticker))

    # cerebro.optstrategy(BollingStrategy, period = range(5, 56, 5))
    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
    print(f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}")
    print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    cerebro.plot(style='bar', iplot=False)

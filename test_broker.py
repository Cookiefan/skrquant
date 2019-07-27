import pandas as pds
import backtrader as bt
from datetime import datetime

class testStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Rejected]:
            self.log('Order Canceled/Rejected')
        elif order.status == order.Margin:
            self.log('Order Margin')
        self.order = None

    def next(self):
        self.buy(size=5)
        self.buy(size=3)
        self.buy(size=3)
        self.buy(size=1)

        # try order [1000, 5000, 3000, 3000] will get different result
        # self.buy(size=1)
        # self.buy(size=5)
        # self.buy(size=3)
        # self.buy(size=3)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    hs = pds.DataFrame([[1000,1000,1000,1000],[1000,1000,1000,1000]], columns=['open','close','high','close'])
    hs.index = pds.Series([datetime(2000,1,1),datetime(2000,1,2)], name='date')
    print(hs)
    print('----------------------------------------------------------')
    cerebro.adddata(bt.feeds.PandasData(dataname=hs, plot=True, name='HS300'))
    cerebro.broker.setcash(10000.0)
    cerebro.addstrategy(testStrategy)
    results = cerebro.run()

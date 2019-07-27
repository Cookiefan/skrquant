import backtrader as bt
from datetime import date


class SkrStrategy(bt.Strategy):
    params = dict(
        order_print=True,
        trading_limit=True,
        start=None,
        end=None,
    )

    def log(self, txt, dt=None):
        # The logging function
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):

        if order.status == order.Submitted:
            if self.data0.datetime.date(0) != order.data.datetime.date(0):
                self.broker.cancel(order)
                if self.p.order_print:
                    self.log(f'<{order.data._name}> Suspended!')
            elif order.isbuy() and order.data.high[0] / order.data.low[0] > 1.0950:
                self.broker.cancel(order)
                if self.p.order_print:
                    self.log(f'<{order.data._name}> Buy Limit!')
            elif order.issell() and order.data.low[0] / order.data.high[0] < 0.910:
                self.broker.cancel(order)
                if self.p.order_print:
                    self.log(f'<{order.data._name}> Sell Limit!')

        elif order.status == order.Completed:
            if order.isbuy():
                if self.p.order_print:
                    self.log(
                        f'<{order.data._name}> BUY EXECUTED, Price: %.2f, Size: %.2f, Comm %.2f' %
                        (order.executed.price,
                         order.executed.size,
                         order.executed.comm))
            else:
                if self.p.order_print:
                    self.log(f'<{order.data._name}> SELL EXECUTED, Price: %.2f, Size: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.p.order_print:
                if order.status == order.Canceled:
                    self.log(f'<{order.data._name}> Order Canceled')
                elif order.status == order.Margin:
                    self.log(f'<{order.data._name}> Order Margin')
                else:
                    self.log(f'<{order.data._name}> Order Rejected')

        self.order = None


    def prenext(self):
        # Important! Call next() even data is not available

        self.next()

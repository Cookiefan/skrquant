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
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if self.p.trading_limit and order.status == order.Submitted:
            if order.isbuy():
                if order.data.high[0] / order.data.low[0] > 1.0950:
                    self.broker.cancel(order)
                    if self.p.order_print:
                        if not self.p.order_print:
                            return
                        self.log(f'<{order.data._name}> BUYING LIMIT!')
            else:
                if order.data.low[0] / order.data.high[0] < 0.910:
                    self.broker.cancel(order)
                    if self.p.order_print:
                        if not self.p.order_print:
                            return
                        self.log(f'<{order.data._name}> SELLING LIMIT!')

        if order.status == order.Completed:
            if order.isbuy():
                if not self.p.order_print:
                    return
                self.log(
                    f'<{order.data._name}> BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:
                if not self.p.order_print:
                    return
                self.log(f'<{order.data._name}> SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if not self.p.order_print:
                return
            self.log(f'<{order.data._name}> Order Canceled/Margin/Rejected')
        order = None
        
    def prenext(self):
        # Important! Call next() even data is not available

        self.next()
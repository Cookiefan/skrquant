import backtrader as bt


class SkrStrategy(bt.Strategy):
    params = (
        ('order_print', True),
        ('trading_limit', True),
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
                        self.log('BUYING LIMIT!')
            else:
                if order.data.low[0] / order.data.high[0] < 0.910:
                    self.broker.cancel(order)
                    if self.p.order_print:
                        if not self.p.order_print:
                            return
                        self.log('SELLING LIMIT!')

        if order.status == order.Completed:
            if order.isbuy():
                if not self.p.order_print:
                    return
                self.log(
                    'BUY %s EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:
                if not self.p.order_print:
                    return
                self.log('SELL %s EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.data._name,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if not self.p.order_print:
                return
            self.log('Order Canceled/Margin/Rejected')
        order = None
        
    def prenext(self):
        # Important! Call next() even data is not available
        self.next()
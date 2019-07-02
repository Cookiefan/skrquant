import backtrader as bt


class WaveIndicator(bt.Indicator):
    plotinfo = (
        ('subplot', False),
    )
    lines = ('low', 'high', 'hlr', 'status')
    plotlines = dict(
        low=dict(color='black'),
        high=dict(color='blue')
    )
    params = (
        ('theta', 0.05),
        ('delta', 0),
    )

    def __init__(self):
        self.t = 0
        self.wave_high = 0
        self.wave_low = 1

    def next(self):
        if self.t == 0:
            self.lines.low[0] = 100
            self.lines.high[0] = 0
        else:
            self.lines.low[0] = self.lines.low[-1]
            self.lines.high[0] = self.lines.high[-1]

        if self.t == 0 or self.status[-1] == 1:
            if self.data.high[0] > self.wave_high:
                self.wave_high = self.data.high[0]
            elif self.wave_high - self.data.low[0] > self.wave_high * self.p.theta + self.p.delta:
                self.status[0] = -1
                self.wave_low = self.data.low[0]
            self.lines.high[0] = self.wave_high
        else:
            if self.data.low[0] < self.wave_low:
                self.wave_low = self.data.low[0]
            elif self.data.high[0] - self.wave_low > self.wave_low * self.p.theta + self.p.delta:
                self.status[0] = 1
                self.wave_high = self.data.high[0]
            self.lines.low[0] = self.wave_low
        self.hlr[0] = self.high[0] / self.low[0]
        self.t += 1

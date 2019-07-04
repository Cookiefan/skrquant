import backtrader as bt


class WaveIndicator(bt.Indicator):
    plotinfo = (
        ('subplot', True),
    )
    lines = ('low', 'high','status')
    plotlines = dict(
        low=dict(color='black'),
        high=dict(color='blue'),
        hlr = dict(color = 'red')
    )
    params = (
        ('theta', 0.05),
        ('delta', 0),
    )

    def __init__(self):
        self.t = 0
        self.wave_high = 0
        self.wave_low = 0
        self.status = 1

    def next(self):
        if self.status == 1:
            if self.data.high[0] >= self.wave_high:
                self.wave_high = self.data.high[0]
            elif self.wave_high - self.data.low[0] > self.wave_high * self.p.theta + self.p.delta:
                self.status = 0
                self.wave_low = self.data.low[0]
        else:
            if self.data.low[0] <= self.wave_low:
                self.wave_low = self.data.low[0]
            elif self.data.high[0] - self.wave_low > self.wave_low * self.p.theta + self.p.delta:
                self.status = 1
                self.wave_high = self.data.high[0]

        self.lines.status[0] = self.status
        self.lines.low[0] = self.wave_low
        self.lines.high[0] = self.wave_high
        self.t += 1

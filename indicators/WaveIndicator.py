import backtrader as bt


class WaveIndicator(bt.Indicator):
    lines = ('wave',)
    params = (
        ('theta',0.05),
        ('delta', 0),
    )
    def __init__(self):
        self.status = 1
        self.wave_high = 0
        self.wave_low = 0

    def next(self):
        if self.status == 1:
            if self.data.high > self.wave_high:
                self.wave_high = self.data.high
            elif self.wave_high - self.data.low > self.wave_high * self.p.theta + self.p.delta:
                self.status = -1
                self.wave_low = self.data.low
            self.lines.wave = self.wave_high
        else:
            if self.data.low < self.wave_low:
                self.wave_low = self.data.low
            elif self.data.high - self.wave_low > self.wave_low * self.p.theta + self.p.delta:
                self.status = 1
                self.wave_high = self.data.high
            self.lines.wave = self.wave_low
import numpy as npy
import backtrader as bt
from scipy.stats import linregress

class BollingerBandModified(bt.Indicator):
    lines = ('M','U')
    params = (('period', 20),('alpha', 0.15),('f', 2.5))

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
       self.l.M = self.p.alpha * self.data.close[0]
from datetime import datetime
import backtrader as bt

class HS300Data(bt.feeds.GenericCSVData):
  params = (
    ('fromdate', datetime(2017, 1, 1),),
    ('todate', datetime(2018, 12, 31)),
    ('nullvalue', 0.0),
    ('dtformat', ('%Y-%m-%d')),
    ('datetime', 0),
    ('high', 1),
    ('low', 2),
    ('open', 3),
    ('close', 4),
    ('volume', 5),
    ('openinterest', -1)
)

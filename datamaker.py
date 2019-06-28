import tushare as ts
import pandas as pds
from tqdm import tqdm


now = ts.get_hist_data('hs300')[['open','close','high','low','volume']].sort_index()
now.to_csv('./DATA/HS300/%s.csv'%'hs300')

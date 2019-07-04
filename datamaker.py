import tushare as ts
import pandas as pds
from tqdm import tqdm
from utils import code_cement

# now = ts.get_hist_data('hs300')[['open','close','high','low','volume']].sort_index()
# now.to_csv('./DATA/HS300/%s.csv'%'hs300')

for code in tqdm(code_cement):
    try:
        now = ts.get_hist_data(code)[['open','close','high','low','volume']].sort_index()
        now.to_csv('./DATA/Cement/%s.csv'%code)
    except:
        print(code)
        continue


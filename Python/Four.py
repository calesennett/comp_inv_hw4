import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
import copy
import math
import datetime as dt
import numpy as np
import pandas as pd
from itertools import *
import matplotlib.pyplot as plt

def main():
    s_date = dt.datetime(2008, 1, 1)
    e_date = dt.datetime(2009, 12, 31)
    print "Reading data..."
    data, symbols = setup(s_date, e_date)
    print "Finding events..."
    events = create_matrix(data, symbols)
    print "Making graph..."
    ep.eventprofiler(events, data, i_lookback=20, i_lookforward=20, s_filename="SP500 2012.pdf")

def create_matrix(data, syms):
    prices = data['actual_close']
    events = copy.deepcopy(prices)
    events = events * np.NAN

    timestamps = prices.index

    for sym in syms:
        for i in range(1, len(timestamps)):
            p_today = prices[sym].ix[timestamps[i]]
            p_yesterday = prices[sym].ix[timestamps[i-1]]

            # specified event
            if p_yesterday >= 10.0 and p_today < 10.0:
                events[sym].ix[timestamps[i]] = 1

    return events

def setup(s_date, e_date):
    time_of_day = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(s_date, e_date, time_of_day)
    data, symbols = read_data(timestamps)
    return data, symbols

def read_data(timestamps):
    data_obj = da.DataAccess('Yahoo')
    symbols = data_obj.get_symbols_from_list("sp5002012")
    symbols.append('SPY')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    all_data = data_obj.get_data(timestamps, symbols, keys)

    # remove NaN from price data
    all_data = dict(zip(keys, all_data))
    for s_key in keys:
        all_data[s_key] = all_data[s_key].fillna(method='ffill')
        all_data[s_key] = all_data[s_key].fillna(method='bfill')
        all_data[s_key] = all_data[s_key].fillna(1.0)
    return all_data, symbols

if __name__ == "__main__":
    main()

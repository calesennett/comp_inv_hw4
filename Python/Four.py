import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
import copy
import math
import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd
from itertools import *
import matplotlib.pyplot as plt
import csv

def main():
    s_date = dt.datetime(2008, 1, 1)
    e_date = dt.datetime(2010, 1, 1)
    print "Reading data..."
    data, symbols = setup(s_date, e_date)
    print "Finding events..."
    events = create_matrix(data, symbols)

def create_matrix(data, syms):
    prices = data['actual_close']
    events = copy.deepcopy(prices)
    events = events * np.NAN

    timestamps = prices.index

    trades = []
    count = 0

    for i in range(1, len(timestamps)):
        for sym in syms:
            p_today = prices[sym].ix[timestamps[i]]
            p_yesterday = prices[sym].ix[timestamps[i-1]]

            # specified event
            if p_yesterday >= 5.0 and p_today < 5.0:
                trades.append({ "Year": int(str(timestamps[i])[:10].split('-')[0]),
                                "Month": int(str(timestamps[i])[:10].split('-')[1]),
                                "Day": int(str(timestamps[i])[:10].split('-')[2]),
                                "Sym": sym, "Type": "Buy", "Shares": 100})
                if (i >= len(timestamps) - 5):
                    trades.append({ "Year": int(str(timestamps[len(timestamps)-1])[:10].split('-')[0]),
                                    "Month": int(str(timestamps[len(timestamps)-1])[:10].split('-')[1]),
                                    "Day": int(str(timestamps[len(timestamps)-1])[:10].split('-')[2]),
                                    "Sym": sym, "Type": "Sell", "Shares": 100})
                else:
                    trades.append({ "Year": int(str(timestamps[i+5])[:10].split('-')[0]),
                                    "Month": int(str(timestamps[i+5])[:10].split('-')[1]),
                                    "Day": int(str(timestamps[i+5])[:10].split('-')[2]),
                                    "Sym": sym, "Type": "Sell", "Shares": 100})
    output_trades(trades)
    return events

def output_trades(trades):
    header = ["Year", "Month", "Day", "Sym", "Type", "Shares"]
    trades_file = open('trades.csv', 'wb')
    csv_writer = csv.DictWriter(trades_file, delimiter=',', fieldnames=header)
    csv_writer.writerow(dict((fn,fn) for fn in header))
    for row in trades:
         csv_writer.writerow(row)

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

import time
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from copy import copy
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sb

#Define time interval to download data
period1 = int(time.mktime(datetime.datetime(2019,8,1,23,59).timetuple()))
period2 = int(time.mktime(datetime.datetime.now().timetuple()))
interval = '1d' #1wk - 1m - 1d

#As NYSE & NASDAQ has different labour days, we need to download the tickers in 2 different structures to then merge them
tickersus = ['GGAL', 'BBAR', 'BMA', 'CEPU','CRESY','EDN','SUPV','IRS','LOMA','PAM','TEO','TX','TGS','YPF']
tickersars = ['GGAL.BA', 'BMA.BA', 'CEPU.BA','CRES.BA','EDN.BA','SUPV.BA','IRSA.BA','LOMA.BA','PAMP.BA','TECO2.BA','TGSU2.BA','YPFD.BA']

def historicaldata(tickers, period1, period2, interval):
    data = {}
    data = pd.DataFrame(data)
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{tickers[0]}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    df0 = pd.read_csv(query_string)
    date = pd.DataFrame(df0['Date'])
    data = pd.concat([data, date], axis=1)
        

    for i in tickers:
        
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{i}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
        df = pd.read_csv(query_string)
        df = df.drop(['Date','Open', 'Adj Close'], axis = 1)
        df = df.add_suffix(' ' + i)
        data = pd.concat([data, df], axis=1)
        
    stockdata = data.copy()
    
    return stockdata

stockdataus = historicaldata(tickersus, period1, period2, interval)

stockdataars = historicaldata(tickersars, period1, period2, interval)

dfmerged = pd.merge(stockdataars, stockdataus, on='Date', how='outer')
dfmerged['Date'] = pd.to_datetime(dfmerged['Date'], format='%Y-%m-%d')

dfmerged = dfmerged.dropna()

dfmerged['ccl_GGAL'] = (dfmerged['Close GGAL.BA'] / dfmerged['Close GGAL']) * 10
dfmerged['ccl_BMA'] = (dfmerged['Close BMA.BA'] / dfmerged['Close BMA']) * 10
dfmerged['ccl_CEPU'] = (dfmerged['Close CEPU.BA'] / dfmerged['Close CEPU']) * 10
dfmerged['ccl_CRES'] = (dfmerged['Close CRES.BA'] / dfmerged['Close CRESY']) * 10
dfmerged['ccl_IRSA'] = (dfmerged['Close IRSA.BA'] / dfmerged['Close IRS']) * 10
dfmerged['ccl_SUPV'] = (dfmerged['Close SUPV.BA'] / dfmerged['Close SUPV']) * 5
dfmerged['ccl_EDN'] = (dfmerged['Close EDN.BA'] / dfmerged['Close EDN']) * 20
dfmerged['ccl_TECO2'] = (dfmerged['Close TECO2.BA'] / dfmerged['Close TEO']) * 5
dfmerged['ccl_LOMA'] = (dfmerged['Close LOMA.BA'] / dfmerged['Close LOMA']) * 5
dfmerged['ccl_TGSU2'] = (dfmerged['Close TGSU2.BA'] / dfmerged['Close TGS']) * 5
dfmerged['ccl_YPFD'] = (dfmerged['Close YPFD.BA'] / dfmerged['Close YPF'])
dfmerged.tail()

dfccl = dfmerged.filter(['Date','ccl_GGAL','ccl_BMA','ccl_CEPU','ccl_CRES','ccl_IRSA','ccl_SUPV','ccl_EDN','ccl_TECO2','ccl_LOMA','ccl_TGSU2','ccl_YPFD'], axis=1)

pricears = dfmerged.filter(['Date','Close GGAL.BA','Close BMA.BA','Close CEPU.BA','Close CRES.BA','Close EDN.BA','Close SUPV.BA',
                           'Close IRSA.BA','Close LOMA.BA','Close PAMP.BA','Close TECO2.BA','Close TGSU2.BA','Close YPFD.BA'], axis=1)


def normalize(df):
  x = df.copy()
  for i in x.columns[1:]:
    x[i] = x[i]/x[i][0]
  return x

pricearsnorm = normalize(pricears)

priceus = dfmerged.filter(['Date','Close GGAL','Close BBAR','Close BMA','Close CEPU','Close CRESY','Close EDN','Close SUPV',
                           'Close IRS','Close LOMA','Close PAM','Close TEO','Close TX','Close TGS','Close YPF'], axis=1)

priceusnorm = normalize(priceus)

dfcclnorm = normalize(dfccl)

priceus.columns = priceus.columns.str.replace('Close ', '')
priceusnorm.columns = priceusnorm.columns.str.replace('Close ', '')
pricears.columns = pricears.columns.str.replace('Close ', '')
pricearsnorm.columns = pricearsnorm.columns.str.replace('Close ', '')
dfccl.columns = dfccl.columns.str.replace('Close ', '')
dfcclnorm.columns = dfcclnorm.columns.str.replace('Close ', '')
dfmerged.columns = dfmerged.columns.str.replace('Close ', '')

def compute_daily_returns(df):
    
    daily_returns = df.iloc[: , 1:].copy() 
    daily_returns = daily_returns.pct_change()
    daily_returns = daily_returns.fillna(value=0)
    daily_returns['Date'] = df['Date']
    first_column = daily_returns.pop('Date')
    daily_returns.insert(0, 'Date', first_column)
  
    return daily_returns

returnars = compute_daily_returns(pricears)
returnus = compute_daily_returns(priceus)


returnarscorr = returnars[1:].corr()
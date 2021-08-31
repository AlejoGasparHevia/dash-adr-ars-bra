import time
import datetime
import plotly.express as px
import pandas as pd
import pandas_datareader.data as web
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from copy import copy
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

period1 = int(time.mktime(datetime.datetime(2018,12,31,23,59).timetuple()))
period2 = int(time.mktime(datetime.datetime.now().timetuple()))
interval = '1wk' #1wk - 1m - 1d

def historicaldata2(tickers, period1, period2, interval):
    data = {}
    data = pd.DataFrame(data)
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{tickers[0]}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    df0 = pd.read_csv(query_string)
    date = pd.DataFrame(df0['Date'])
    data = pd.concat([data, date], axis=1)
        

    for i in tickers:
        
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{i}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
        df = pd.read_csv(query_string)
        df = df.drop(['Date','Open', 'High', 'Low', 'Adj Close'], axis = 1)
        df = df.add_suffix(' ' + i)
        data = pd.concat([data, df], axis=1)
        
    stockdata = data.copy()
    
    return stockdata

tickersbra = ['ITUB', 'BBD', 'VALE', 'PBR','ABEV', 'GGB', 'SID', 'BRFS', 'CIG', 'ERJ','UGP', 'GOL', 'SUZ', 'SBS']
tickersars = ['GGAL', 'BBAR', 'BMA', 'CEPU','CRESY','EDN','SUPV','IRS','LOMA','PAM','TEO','TX','TGS','YPF']

databra = historicaldata2(tickersbra, period1, period2, interval)
databra.dropna(inplace=True)
dataars = historicaldata2(tickersars, period1, period2, interval)
dataars.dropna(inplace=True)

arsprice = dataars[['Date','Close GGAL', 'Close BBAR', 'Close BMA', 'Close CEPU','Close CRESY','Close EDN','Close SUPV','Close IRS','Close LOMA','Close PAM','Close TEO','Close TX','Close TGS','Close YPF']]
arsvol = dataars[['Date','Volume GGAL', 'Volume BBAR', 'Volume BMA', 'Volume CEPU','Volume CRESY','Volume EDN','Volume SUPV','Volume IRS','Volume LOMA','Volume PAM','Volume TEO','Volume TX','Volume TGS','Volume YPF']]
braprice = databra[['Date', 'Close ITUB', 'Close BBD', 'Close VALE', 'Close PBR','Close ABEV', 'Close GGB', 'Close SID', 'Close BRFS', 'Close CIG', 'Close ERJ','Close UGP', 'Close GOL', 'Close SUZ', 'Close SBS']]
bravol = databra[['Date', 'Volume ITUB', 'Volume BBD', 'Volume VALE', 'Volume PBR','Volume ABEV', 'Volume GGB', 'Volume SID', 'Volume BRFS', 'Volume CIG', 'Volume ERJ','Volume UGP', 'Volume GOL', 'Volume SUZ', 'Volume SBS']]

arsprice = arsprice.rename(columns = lambda x: x.replace('Close ', '').strip())
braprice = braprice.rename(columns = lambda x: x.replace('Close ', '').strip())
arsvol = arsvol.rename(columns = lambda x: x.replace('Volume ', '').strip())
bravol = bravol.rename(columns = lambda x: x.replace('Volume ', '').strip())

def varvst0(df):
    x = df.copy()
    for i in x.columns[1:]:
        x[i] = (x[i]/x[i][0] - 1) * 100
    return x

varars = varvst0(arsprice)
varbra = varvst0(braprice)

vs_ars = varars.melt('Date', var_name='ticker')
vs_ars['country'] = 'ARG'

vs_bra = varbra.melt('Date', var_name='ticker')
vs_bra['country'] = 'BRA'


vs = pd.concat([vs_bra, vs_ars], axis=0, sort=True, ignore_index=True)

def culrelvol(df):
    x = df.copy()
    y = x.iloc[:,1:]
    y = y[1:].cumsum()
    
    for i in y.columns:
        x[i] = (x[i]/df.sum(axis=1)) * 100
    return x


relativevolumebra = culrelvol(bravol)
relativevolumears = culrelvol(arsvol)

rv_ars = relativevolumears.melt('Date', var_name='ticker')
rv_ars['country'] = 'ARG'


rv_bra = relativevolumebra.melt('Date', var_name='ticker')
rv_bra['country'] = 'BRA'

rv = pd.concat([rv_bra, rv_ars], axis=0, sort=True, ignore_index=True)

merged = rv.merge(vs.drop(columns=['country']).rename(columns={'value':'variacion'}), on=['Date', 'ticker'], how='left')
merged = merged.rename(columns={'value':'local_%_volume'})
merged = merged.rename(columns={'variacion':'cumulative_return'})

cumsdbra = braprice.copy()

cumsdbra['dv ITUB'] = cumsdbra['ITUB'].expanding(2).std()
cumsdbra['dv BBD'] = cumsdbra['BBD'].expanding(2).std()
cumsdbra['dv VALE'] = cumsdbra['VALE'].expanding(2).std()
cumsdbra['dv PBR'] = cumsdbra['PBR'].expanding(2).std()
cumsdbra['dv ABEV'] = cumsdbra['ABEV'].expanding(2).std()
cumsdbra['dv GGB'] = cumsdbra['GGB'].expanding(2).std()
cumsdbra['dv SID'] = cumsdbra['SID'].expanding(2).std()
cumsdbra['dv BRFS'] = cumsdbra['BRFS'].expanding(2).std()
cumsdbra['dv CIG'] = cumsdbra['CIG'].expanding(2).std()
cumsdbra['dv ERJ'] = cumsdbra['ERJ'].expanding(2).std()
cumsdbra['dv UGP'] = cumsdbra['UGP'].expanding(2).std()
cumsdbra['dv GOL'] = cumsdbra['GOL'].expanding(2).std()
cumsdbra['dv SUZ'] = cumsdbra['SUZ'].expanding(2).std()
cumsdbra['dv SBS'] = cumsdbra['SBS'].expanding(2).std()

cumsdbra.drop(cumsdbra.columns[1:15], axis=1, inplace=True)
cumsdbra.columns = cumsdbra.columns.str.replace('dv ', '')
cumsdbra = cumsdbra.fillna(0)


cumsdars = arsprice.copy()

cumsdars['dv GGAL'] = cumsdars['GGAL'].expanding(2).std()
cumsdars['dv BBAR'] = cumsdars['BBAR'].expanding(2).std()
cumsdars['dv BMA'] = cumsdars['BMA'].expanding(2).std()
cumsdars['dv CEPU'] = cumsdars['CEPU'].expanding(2).std()
cumsdars['dv CRESY'] = cumsdars['CRESY'].expanding(2).std()
cumsdars['dv EDN'] = cumsdars['EDN'].expanding(2).std()
cumsdars['dv SUPV'] = cumsdars['SUPV'].expanding(2).std()
cumsdars['dv IRS'] = cumsdars['IRS'].expanding(2).std()
cumsdars['dv LOMA'] = cumsdars['LOMA'].expanding(2).std()
cumsdars['dv PAM'] = cumsdars['PAM'].expanding(2).std()
cumsdars['dv TEO'] = cumsdars['TEO'].expanding(2).std()
cumsdars['dv TX'] = cumsdars['TX'].expanding(2).std()
cumsdars['dv TGS'] = cumsdars['TGS'].expanding(2).std()
cumsdars['dv YPF'] = cumsdars['YPF'].expanding(2).std()

cumsdars.drop(cumsdars.columns[1:15], axis=1, inplace=True)
cumsdars.columns = cumsdars.columns.str.replace('dv ', '')
cumsdars = cumsdars.fillna(0)

arsmelt = cumsdars.melt('Date', var_name='ticker')
arsmelt['country'] = 'ARG'

bramelt = cumsdbra.melt('Date', var_name='ticker')
bramelt['country'] = 'BRA'


dv = pd.concat([bramelt, arsmelt], axis=0, sort=True, ignore_index=True)


dfanimation = merged.merge(dv.drop(columns=['country']).rename(columns={'value':'cumulative_deviation'}), on=['Date', 'ticker'], how='left')

dfanimation.Date = pd.to_datetime(dfanimation.Date, format='%Y-%m-%d')
dfanimation['Date2'] = dfanimation['Date'].astype(np.int64)

# generando fechared que nos permitira tener la animacion mas corta con data distribuida para 30 valores del intervalo
dftest = dfanimation.copy()
datint = dftest.Date2.drop_duplicates().sort_values()

maxdate = len(datint)-1

index = [0, maxdate *0.03, maxdate*0.06, maxdate *0.09, maxdate*0.12, maxdate*0.15,maxdate*0.18, maxdate*0.21,maxdate*0.24,maxdate*0.27,maxdate*0.3,maxdate*0.33,
         maxdate*0.36,maxdate*0.39,maxdate*0.42,maxdate*0.45,maxdate*0.48,maxdate*0.51,maxdate*0.54,maxdate*0.57,maxdate*0.6,maxdate*0.63,maxdate*0.66, maxdate*0.69,
         maxdate*0.72,maxdate*0.75,maxdate*0.78,maxdate*0.81,maxdate*0.84,maxdate*0.87,maxdate*0.9,maxdate*0.93,maxdate*0.96,maxdate]
index = [int(x) for x in index]


fechared = []

for index in index:
    fechared.append(datint[index])


datagraph = dfanimation.copy()
datagraph = datagraph[datagraph['Date2'].isin(fechared)]

dvmax = datagraph.cumulative_deviation.quantile(0.98)
rangodv = [0, dvmax]
crmax = datagraph.cumulative_return.quantile(0.98)*1.1
crmin = datagraph.cumulative_return.quantile(0.02)*1.1
rangocr = [crmin, crmax]



animarsbra = px.scatter(datagraph, x="cumulative_deviation", y="cumulative_return", animation_frame="Date2", animation_group="ticker", 
            size="local_%_volume", color="country", size_max=60,hover_name='ticker', range_x=rangodv, range_y=rangocr, 
            labels = 'ticker',opacity=0.65)
animarsbra.update_layout(legend_bgcolor="lightblue", legend_bordercolor="blue", legend_borderwidth=1,paper_bgcolor="lightblue",plot_bgcolor="white")


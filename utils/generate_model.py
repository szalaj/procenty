import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal



def generateFromWiborFile(kapital, okresy, start_date, marza, dzien_zamrozenia, transze=None):

    df = pd.read_csv('static\plopln3m_d.csv', usecols=[0,1], index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')

    miesiace = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]


    zmr_iloc_idx = df.index.get_indexer([dzien_zamrozenia], method='nearest')
    wibor_zamr_value = df.iloc[zmr_iloc_idx].iloc[0][0]
   

    grosze =  decimal.Decimal('.01')
    
    opr_arr = []
    for i in range(0, int(okresy/3)+1):

       wibor_day =  start_date + relativedelta(months=3*i)
       if wibor_day > dzien_zamrozenia:
        wibor_value = wibor_zamr_value
       else:
        iloc_idx = df.index.get_indexer([wibor_day], method='nearest')
        wibor_value = df.iloc[iloc_idx].iloc[0][0]



       opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze))})

    transze_out = []
    if transze:
        for tr in transze:
            transze_out.append({"dzien":tr['dzien'].strftime('%Y-%m-%d'), "kapital": tr['wartosc']})

    data = {"K": kapital,
            "transze": transze_out,
            "p": df.iloc[df.index.get_indexer([start_date], method='nearest')].iloc[0][0],
            "start": miesiace[0],
            "daty_splaty": miesiace[1:],
            "oprocentowanie": opr_arr,
            "dzien_zamrozenia": dzien_zamrozenia.strftime('%Y-%m-%d')}

    return data


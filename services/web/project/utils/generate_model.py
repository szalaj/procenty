import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal



class Wibor:

    def __init__(self, rodzajWiboru: str):

        file_name=''
        if rodzajWiboru=='3M':
            file_name = 'plopln3m_d.csv'
            self._okres = 3
        elif rodzajWiboru=='6M':
            file_name = 'plopln6m_d.csv'
            self._okres = 6

        self.df = pd.read_csv('project/static/{}'.format(file_name), usecols=[0,1], index_col=0)
        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')

    def getWibor(self, data: str):
        zmr_iloc_idx = self.df.index.get_indexer([data], method='nearest')
        wibor_zamr_value = self.df.iloc[zmr_iloc_idx].iloc[0][0]
        return wibor_zamr_value
    
    @property
    def okres(self):
        return self._okres





def generateFromWiborFile(kapital, okresy, start_date, marza, dzien_zamrozenia, rodzajWiboru, transze, tylko_marza=False):


    wibor = Wibor(rodzajWiboru)

    miesiace = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]

    wibor_zamr_value = wibor.getWibor(dzien_zamrozenia)
   
    grosze =  decimal.Decimal('.01')

    opr_arr = []
    if not tylko_marza:
        for i in range(0, int(okresy/wibor.okres)+1):
                wibor_day =  start_date + relativedelta(months=3*i)
                if wibor_day < dzien_zamrozenia:
                    wibor_value = wibor.getWibor(wibor_day)
                    opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze))})

        opr_arr.append({"dzien":dzien_zamrozenia.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_zamr_value).quantize(grosze))})

    transze_out = []
    if transze:
        for tr in transze:
            transze_out.append({"dzien":tr['dzien'].strftime('%Y-%m-%d'), "kapital": tr['wartosc']})


    if tylko_marza:
        p_start = float(decimal.Decimal(marza).quantize(grosze))
    else:
        p_start = float(decimal.Decimal(wibor.getWibor(start_date)+marza).quantize(grosze))

    data = {"K": kapital,
            "transze": transze_out,
            "p": p_start,
            "start": miesiace[0],
            "daty_splaty": miesiace[1:],
            "oprocentowanie": opr_arr,
            "dzien_zamrozenia": dzien_zamrozenia.strftime('%Y-%m-%d'),
            "wibor_zamrozony": wibor_zamr_value }

    return data


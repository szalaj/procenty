import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal
from dataclasses import dataclass
from scipy.interpolate import interp1d
import numpy as np
from obliczeniakredytowe.models import User, Dom, Zapytanie,  Kredyt
from obliczeniakredytowe.models import Wibor as WiborModel
from obliczeniakredytowe import db
from sqlalchemy import text as sql_text

@dataclass
class WiborInter:
    """interpolowanie wibour dla wartosci, ktorych jeszce nie znamy."""

    wibor_typ: str
    data_start: dt.datetime
    okresy: int
    liczba_wakacji: int
    points: list

    def __post_init__(self):
        if self.wibor_typ=='3M':
            self._okres = 3
            wib_rodzaj = 'wibor3m'
        elif self.wibor_typ=='6M':
            self._okres = 6
            wib_rodzaj = 'wibor6m'

        # self.df = pd.read_csv('obliczeniakredytowe/static/{}'.format(file_name), usecols=[0,1], index_col=0)
        # self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')    

        self.df = pd.read_sql(sql_text(f"SELECT data, wartosc FROM wibor WHERE rodzaj='{wib_rodzaj}'"), con=db.engine.connect(), index_col='data')

        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')

        self.df.sort_index(inplace=True)

 

        self.df = self.df[self.df.index >= self.data_start-relativedelta(days=5)] 

        self.data_koniec = self.data_start + relativedelta(months=(self.okresy+self.liczba_wakacji))



        self.max_wibor_real = self.df.index.max()



        if self.data_koniec > self.max_wibor_real:

            if self.points:
                self.points = [(dt.datetime.strptime(p[0], '%d/%m/%Y'), p[1]) for p in self.points if dt.datetime.strptime(p[0], '%d/%m/%Y') > self.df.index.max()]
    
            self.points.append((self.df.index.max(), self.df.loc[self.df.index.max(), 'wartosc']))



            #interpolation
            dates, values = zip(*self.points)

            # Convert dates to numerical values representing time or elapsed time
            timestamps = np.array([(date - self.max_wibor_real).total_seconds() for date in dates])

            # Create an interpolation function using scipy.interpolate.interp1d
            self.interpolation_function = interp1d(timestamps, values)

            # Convert the new date to a numerical value
            end_timestamp = (self.data_koniec - self.max_wibor_real).total_seconds()

            # Use the interpolation function to estimate the value at the new date
            wibor_value_koniec= self.interpolation_function(end_timestamp).item()

            self.points = [p for p in self.points if p[0] < self.data_koniec]

            self.points.append((self.data_koniec, wibor_value_koniec))

    
            new_df = pd.DataFrame(self.points, columns=['data', 'wartosc'])
            #new_df['Date'] = pd.to_datetime(new_df['Date'])
            new_df.set_index('data', inplace=True)

            # Concatenate the original DataFrame and the new DataFrame
            dff = pd.concat([self.df, new_df])

        else:
            dff = self.df[self.df.index <= self.data_koniec]

        dff = dff.sort_index()
        self.json_data = [{'date': dt.datetime.strftime(index, '%Y-%m-%d'), 'value': value} for index, value in dff['wartosc'].items()]


    def getWibor(self, data) -> float:
        if data > self.max_wibor_real:
            # Generate a new date for interpolation
            
            # Convert the new date to a numerical value
            new_timestamp = (data - self.max_wibor_real).total_seconds()

            # Use the interpolation function to estimate the value at the new date
            wibor_value = self.interpolation_function(new_timestamp)
            
              
            
            
        else:
            wibor_value = self._getWiborLastAvailable(data)
        
        
        return wibor_value

        

    def _getWiborLastAvailable(self, data: str) -> float:
        try:
            wibor_value = self.df.loc[data.strftime('%Y-%m-%d')][0]
        except:
            try:
                wibor_value = self.df[self.df.index < data.strftime('%Y-%m-%d')].iloc[-1][0]
            except:
                raise Exception('wibor not available')
                wibor_value = None
        return wibor_value
    
    @property
    def okres(self):
        return self._okres


class Wibor:

    def __init__(self, rodzajWiboru: str):

        file_name=''
        if rodzajWiboru=='3M':
            self._okres = 3
            wib_rodzaj = 'wibor3m'
        elif rodzajWiboru=='6M':
            self._okres = 6
            wib_rodzaj = 'wibor6m'

        self.df = pd.read_sql(sql_text(f"SELECT data, wartosc FROM wibor WHERE rodzaj='{wib_rodzaj}'"), con=db.engine.connect(), index_col='data')

        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')

        self.df.sort_index(inplace=True)



    def getWibor(self, data: str) -> float:
        return self._getWiborLastAvailable(data)

    def getNearestWibor(self, data: str):
        zmr_iloc_idx = self.df.index.get_indexer([data], method='nearest')
        wibor_zamr_value = self.df.iloc[zmr_iloc_idx].iloc[0][0]
        return wibor_zamr_value
    
    def getWiborExact(self, data: str):
        try:
            wibor_zamr_value = self.df.loc[data.strftime('%Y-%m-%d')][0]
        except:
            wibor_zamr_value = None
        return wibor_zamr_value
    
    def _getWiborLastAvailable(self, data: str) -> float:
        try:
            wibor_value = self.df.loc[data.strftime('%Y-%m-%d')][0]
        except:
            try:
                wibor_value = self.df[self.df.index < data.strftime('%Y-%m-%d')].iloc[-1][0]
            except:
                raise Exception('wibor not available')
                wibor_value = None
        return wibor_value

    
    @property
    def okres(self):
        return self._okres



def generateFromWiborFileInter(wibor, kapital, okresy, start_date, marza, transze, nadplaty, tylko_marza=False):


    #daty_splaty = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]
    daty_splaty = []
    wakacje= ['2022-08', '2022-09','2022-10','2022-11', '2023-02','2023-05','2023-08','2023-11']

    grosze =  decimal.Decimal('.01')

    # 1. dane zwyklego oprocentowania
    # 2. dane o splatach rat
    # 3. generator

    opr_arr = []
    opr_wib = []
    if not tylko_marza:
        for i in range(0, int(okresy/wibor.okres)+1):
                wibor_day =  start_date + relativedelta(months=3*i)
                wibor_value = wibor.getWibor(wibor_day)
                opr_wib.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze))})
                opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze)), "rodzaj": "wibor", 'typ': ""})


    n=1
    N=0
    wakacje_in_progress=False
    while N!=okresy:
        dzien_splaty =  start_date + relativedelta(months=n)
        # check if dzien_splaty is not same month and day as wakacje
        if not (dzien_splaty.strftime('%Y-%m') in wakacje):
            N+=1
            daty_splaty.append(dzien_splaty.strftime('%Y-%m-%d'))
            if wakacje_in_progress:
                wakacje_in_progress=False
                #opr_wib.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty)).quantize(grosze))})
                opr_arr.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty)).quantize(grosze)), "rodzaj": "splata", 'typ': ""})
        else:
            wakacje_in_progress=True
            #opr_wib.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(0).quantize(grosze))})
            opr_arr.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty)).quantize(grosze)), "rodzaj": "splata", 'typ': "W"})
        n+=1

        
    # sort opr_arr by dzien
    opr_arr = sorted(opr_arr, key = lambda i: i['dzien'])

    # data frame from opr_wib
    df = pd.DataFrame(opr_wib)
    df['dzien'] = pd.to_datetime(df['dzien'])

    # df sorted by dzien
    df = df.sort_values(by=['dzien'])

    print(df)

    # oprocentowanie z uwzglednieniem wakacji kredytowych
    opr_wakacje = []
    wakacje = False
    for r in opr_arr:
        if r['rodzaj']=='splata' and r['typ']=='W':
            opr_wakacje.append({"dzien":r['dzien'], "proc": float(decimal.Decimal(0).quantize(grosze))})
            wakacje = True
        else:
            if wakacje:
                if r['rodzaj']=='splata' and r['typ']=="":
                    wibor_value = df[df['dzien']<r['dzien']]['proc'].iloc[-1]
                    
                    opr_wakacje.append({"dzien":r['dzien'], "proc": wibor_value})
                    wakacje = False

            else:
                opr_wakacje.append({"dzien":r['dzien'], "proc": r['proc']})


    print(opr_wakacje)

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
            "nadplaty": nadplaty,
            "p": p_start,
            "marza": marza,
            "start": start_date.strftime('%Y-%m-%d'),
            "daty_splaty": daty_splaty,
            "oprocentowanie": opr_wakacje}

    return data


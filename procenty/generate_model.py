import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import BDay
import decimal
from dataclasses import dataclass
from scipy.interpolate import interp1d
import numpy as np


from sqlalchemy import text as sql_text

@dataclass
class WiborInter:
    """interpolowanie wibour dla wartosci, ktorych jeszce nie znamy."""
    db: object
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

        self.df = pd.read_sql(sql_text(f"SELECT data, wartosc FROM wibor WHERE rodzaj='{wib_rodzaj}'"), con=self.db.engine.connect(), index_col='data')

        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')

        self.df['real'] = 'Y'

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
            new_df['real'] = 'N'
            #new_df['Date'] = pd.to_datetime(new_df['Date'])
            new_df.set_index('data', inplace=True)

            # Concatenate the original DataFrame and the new DataFrame
            dff = pd.concat([self.df, new_df])

        else:
            dff = self.df[self.df.index <= self.data_koniec]

        dff = dff.sort_index()



        self.json_data = [{'date': dt.datetime.strftime(index, '%Y-%m-%d'), 'value': value['wartosc'], 'real': value['real']} for index, value in dff.iterrows()]


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
   
        return wibor_value
    
    def isWiborReal(self, data):
        if data >= self.max_wibor_real:
            return 'N'
        return 'Y'    
        
        return wibor_value
    @property
    def okres(self):
        return self._okres
    



class Wibor:

    def __init__(self, rodzajWiboru: str, db):

        file_name=''
        if rodzajWiboru=='3M':
            self._okres = 3
            wib_rodzaj = 'wibor3m'
        if rodzajWiboru=='1M':
            self._okres = 1
            wib_rodzaj = 'wibor1m'
        elif rodzajWiboru=='6M':
            self._okres = 6
            wib_rodzaj = 'wibor6m'
        elif rodzajWiboru=='stopa_ref':
            self._okres = 1
            wib_rodzaj = 'stopa_ref'
   

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
                
        return wibor_value

    
    @property
    def okres(self):
        return self._okres
    

    @property
    def max_wibor_date(self):
        return self.df.index.max()

def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))

def next_business_day(date):
    i = 0
    while not is_business_day(date):
        date = date + dt.timedelta(days=1)
        if i > 100:
            raise Exception('next_business_day not found')
    return date


def generateFromWiborFileInter(wibor, kapital, okresy, start_date, marza, transze, nadplaty, wakacje, dni_zmiany_splaty,
                               ubezpieczenie_pomostowe_do, ubezpieczenie_pomostowe_stopa, wibor_value_start, tylko_marza=False):



    #daty_splaty = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]
    daty_splaty = []
    #wakacje= ['2022-08', '2022-09','2022-10','2022-11', '2023-02','2023-05','2023-08','2023-11']

    # nasze_daty_splaty = [(dt.datetime.strptime('2021-11-18', '%Y-%m-%d') + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(6)] + \
    # [(dt.datetime.strptime('2022-05-04', '%Y-%m-%d') + relativedelta(months=i)).strftime('%Y-%m-%d')  for i in range(3)] + \
    # [(dt.datetime.strptime('2022-08-29', '%Y-%m-%d') + relativedelta(months=i)).strftime('%Y-%m-%d')  for i in range(360)] 

    # print(f"nasze daty splaty {nasze_daty_splaty}")

    grosze =  decimal.Decimal('.01')

    # 1. dane zwyklego oprocentowania
    # 2. dane o splatach rat
    # 3. generator
    pomost_done = False
    old_wibor_value =0
    old_wibor_day_business_day = start_date
    wibor_value = 0
    wibor_day_business_day = start_date
    opr_arr = []
    opr_wib = []
    if not tylko_marza:
        for i in range(0, int(okresy/wibor.okres)+1):
                wibor_day =  start_date + relativedelta(months=3*i)

                old_wibor_day_business_day = wibor_day_business_day
                wibor_day_business_day = wibor_day - BDay(2)
            

                old_wibor_value = wibor_value

                # check if wibor_value_start is not None

                wibor_value = wibor.getWibor(wibor_day_business_day)

                if wibor_value_start is not None and i == 0:
                    wibor_value = wibor_value_start


                if ubezpieczenie_pomostowe_do and not pomost_done:
                    if wibor_day < dt.datetime.strptime(ubezpieczenie_pomostowe_do,'%Y-%m-%d'):
                        wibor_value += ubezpieczenie_pomostowe_stopa
                    else:
                        opr_wib.append({"dzien":ubezpieczenie_pomostowe_do, "proc": float(decimal.Decimal(marza+old_wibor_value).quantize(grosze)), "real": wibor.isWiborReal(old_wibor_day_business_day)})
                        opr_arr.append({"dzien":ubezpieczenie_pomostowe_do, "proc": float(decimal.Decimal(marza+old_wibor_value).quantize(grosze)), "real": wibor.isWiborReal(old_wibor_day_business_day), "rodzaj": "wibor", 'typ': ""})
                        pomost_done = True

                #print(f"day: {wibor_day}, value: {wibor_value}")
                opr_wib.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze)), "real": wibor.isWiborReal(wibor_day_business_day)})
                opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze)), "real": wibor.isWiborReal(wibor_day_business_day), "rodzaj": "wibor", 'typ': ""})


    n=1
    N=0
    wakacje_in_progress=False
    miesiac_start_date = start_date.strftime('%Y-%m')
    aktualny_dzien_splaty = start_date
    aktualny_dzien_splaty_dzien = dt.datetime.strftime(start_date, '%d')
    for s in dni_zmiany_splaty:
        if miesiac_start_date==s[0:7] and dt.datetime.strptime(s, '%Y-%m-%d')>start_date:
            aktualny_dzien_splaty = dt.datetime.strptime(s, '%Y-%m-%d')
            aktualny_dzien_splaty_dzien = dt.datetime.strftime(aktualny_dzien_splaty, '%d')
            break

    while N!=okresy:
        # potrzebny nam miesiac
        dzien_splaty =  aktualny_dzien_splaty + relativedelta(months=1)
 
        # month of dzien_splaty
        miesiac = dt.datetime.strftime(dzien_splaty, '%m')
        # rok of dzien_splaty
        rok = dt.datetime.strftime(dzien_splaty, '%Y')

        # sprobujmy utworzyc nowa date splaty
        try:
            str_dzien = f"{rok}-{miesiac}-{aktualny_dzien_splaty_dzien}"
            #print(f"str dzien: {str_dzien}")
            dzien_splaty = dt.datetime.strptime(str_dzien, '%Y-%m-%d')
        except:
            # zostajemy przy aktualnej dacie splaty
            pass

        miesiac_dnia_splaty = dzien_splaty.strftime('%Y-%m')
        for s in dni_zmiany_splaty:
            if miesiac_dnia_splaty==s[0:7]:
                dzien_splaty = dt.datetime.strptime(s, '%Y-%m-%d')
                aktualny_dzien_splaty_dzien = dt.datetime.strftime(dzien_splaty, '%d')
                break
        
      
        dzien_splaty_business_day = dzien_splaty
        # check if dzien_splaty is business day
        if not is_business_day(dzien_splaty_business_day):
            dzien_splaty_business_day = next_business_day(dzien_splaty_business_day)


        ########################################
        ## WAKACJE KREYDTOWE
        ########################################

        #dzien_splaty = dt.datetime.strptime(nasze_daty_splaty[n], '%Y-%m-%d')
        # check if dzien_splaty is not same month and day as wakacje
        if not (dzien_splaty.strftime('%Y-%m') in wakacje):
            N+=1


            daty_splaty.append(dzien_splaty_business_day.strftime('%Y-%m-%d'))
            if wakacje_in_progress:
                wakacje_in_progress=False
                #opr_wib.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty)).quantize(grosze))})
                opr_arr.append({"dzien":dzien_splaty_business_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty_business_day)).quantize(grosze)), "real": wibor.isWiborReal(dzien_splaty_business_day),"rodzaj": "splata", 'typ': ""})
        else:
            wakacje_in_progress=True
            #opr_wib.append({"dzien":dzien_splaty.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(0).quantize(grosze))})
            opr_arr.append({"dzien":dzien_splaty_business_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor.getWibor(dzien_splaty_business_day)).quantize(grosze)), "real": wibor.isWiborReal(dzien_splaty_business_day), "rodzaj": "splata", 'typ': "W"})
        aktualny_dzien_splaty = dzien_splaty
        n+=1

        
    # sort opr_arr by dzien
    opr_arr = sorted(opr_arr, key = lambda i: i['dzien'])

    # data frame from opr_wib
    df = pd.DataFrame(opr_wib)
    df['dzien'] = pd.to_datetime(df['dzien'])

    # df sorted by dzien
    df = df.sort_values(by=['dzien'])

    #print(df)

    # oprocentowanie z uwzglednieniem wakacji kredytowych
    opr_wakacje = []
    wakacje = False
    for r in opr_arr:
        if r['rodzaj']=='splata' and r['typ']=='W':
            opr_wakacje.append({"dzien":r['dzien'], "proc": float(decimal.Decimal(0).quantize(grosze)), "real": r['real']})
            wakacje = True
        else:
            if wakacje:
                if r['rodzaj']=='splata' and r['typ']=="":
                    wibor_value = df[df['dzien']<r['dzien']]['proc'].iloc[-1]
                    
                    opr_wakacje.append({"dzien":r['dzien'], "proc": wibor_value, "real": r['real']})
                    wakacje = False

            else:
                opr_wakacje.append({"dzien":r['dzien'], "proc": r['proc'], "real": r['real']})


    #print(opr_wakacje)

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


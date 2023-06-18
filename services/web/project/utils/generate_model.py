import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal
from dataclasses import dataclass

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
            file_name = 'plopln3m_d.csv'
            self._okres = 3
        elif self.wibor_typ=='6M':
            file_name = 'plopln6m_d.csv'
            self._okres = 6

        self.df = pd.read_csv('project/static/{}'.format(file_name), usecols=[0,1], index_col=0)
        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')

        self.df = self.df[self.df.index >= self.data_start-relativedelta(days=5)] 

        self.data_koniec = self.data_start + relativedelta(months=(self.okresy+self.liczba_wakacji))

        print(f"index min: {self.df.index.min()} , index max: {self.df.index.max()}, data koniec: {self.data_koniec}")

        if self.points:
            self.points = [(dt.datetime.strptime(p[0], '%d/%m/%Y'), p[1]) for p in self.points if dt.datetime.strptime(p[0], '%d/%m/%Y') > self.df.index.max()]
   
        self.points.append((self.df.index.max(), self.df.loc[self.df.index.max(), 'Otwarcie']))

        new_df = pd.DataFrame(self.points, columns=['Data', 'Otwarcie'])
        #new_df['Date'] = pd.to_datetime(new_df['Date'])
        new_df.set_index('Data', inplace=True)

        # Concatenate the original DataFrame and the new DataFrame
        dff = pd.concat([self.df, new_df])
        dff = dff.sort_index()
        self.json_data = [{'date': dt.datetime.strftime(index, '%d-%m-%Y'), 'value': value} for index, value in dff['Otwarcie'].items()]


    


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

        # print(self.df.loc['2021-01-05'][0])
        # print(self.df.index.get_indexer('2021-01-05'))



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
    
    def getWiborLastAvailable(self, data: str) -> float:
        try:
            wibor_zamr_value = self.df.loc[data.strftime('%Y-%m-%d')][0]
        except:
            try:
                wibor_zamr_value = self.df[self.df.index < data.strftime('%Y-%m-%d')].iloc[-1][0]
            except:
                raise Exception('wibor not available')
                wibor_zamr_value = None
        return wibor_zamr_value

    
    @property
    def okres(self):
        return self._okres





def generateFromWiborFile(kapital, okresy, start_date, marza, dzien_zamrozenia, rodzajWiboru, transze, wibor_start, tylko_marza=False):


    wibor = Wibor(rodzajWiboru)

    miesiace = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]

    wibor_zamr_value = wibor.getWiborLastAvailable(dzien_zamrozenia)
   
    grosze =  decimal.Decimal('.01')

    opr_arr = []
    if not tylko_marza:
        for i in range(0, int(okresy/wibor.okres)+1):
                wibor_day =  start_date + relativedelta(months=3*i)
                if wibor_day < dzien_zamrozenia:
                    if not wibor_start:
                        wibor_value = wibor.getWiborLastAvailable(wibor_day)
                    else:
                        wibor_value = wibor_start
                    opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_value).quantize(grosze))})
        if not wibor_start:
            opr_arr.append({"dzien":dzien_zamrozenia.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_zamr_value).quantize(grosze))})
        else:
            opr_arr.append({"dzien":dzien_zamrozenia.strftime('%Y-%m-%d'), "proc": float(decimal.Decimal(marza+wibor_start).quantize(grosze))})

    transze_out = []
    if transze:
        for tr in transze:
            transze_out.append({"dzien":tr['dzien'].strftime('%Y-%m-%d'), "kapital": tr['wartosc']})


    if tylko_marza:
        p_start = float(decimal.Decimal(marza).quantize(grosze))
    else:
        p_start = float(decimal.Decimal(wibor.getWiborLastAvailable(start_date)+marza).quantize(grosze))

    data = {"K": kapital,
            "transze": transze_out,
            "p": p_start,
            "marza": marza,
            "start": miesiace[0],
            "daty_splaty": miesiace[1:],
            "oprocentowanie": opr_arr,
            "dzien_zamrozenia": dzien_zamrozenia.strftime('%Y-%m-%d'),
            "wibor_zamrozony": wibor_zamr_value }

    return data


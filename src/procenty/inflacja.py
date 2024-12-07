import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal
from dataclasses import dataclass
from scipy.interpolate import interp1d
import numpy as np
from typing import List, Tuple
from procenty.stopy import Krzywa
import copy

@dataclass
class Inflacja:
    krzywa: Krzywa
    miesiac_ref: dt.datetime

    def __post_init__(self):

        self.inflacja_miesiace = self.krzywa.podzial_miesiac()

        self.inflator = self._oblicz_inflator()

    def _oblicz_inflator(self):
        min_miesiac = min(self.inflacja_miesiace, key=lambda x: x[0])[0]
        max_miesiac = max(self.inflacja_miesiace, key=lambda x: x[0])[0]

        #print(f"min_miesiac: {min_miesiac}, max_miesiac: {max_miesiac}, ref: {self.miesiac_ref}")

        if self.miesiac_ref < min_miesiac or self.miesiac_ref > max_miesiac:
            raise ValueError(f"Miesac ref spoza przedzialu danych. min_miesiac: {min_miesiac}, max_miesiac: {max_miesiac}, ref: {self.miesiac_ref}")
        
        # miesiace przed miesiacem referencyjnym

        miesiac_i = self.miesiac_ref - relativedelta(months=1)


   
        inflator = 1
        inflatory = []

        inflatory.append((self.miesiac_ref, 1))

        i = 0
        while miesiac_i >= min_miesiac:
            i+=1

            mi = miesiac_i.strftime('%Y-%m')
            
            for m in self.inflacja_miesiace:
                m0 = m[0].strftime('%Y-%m')
                #print(f"m0: {m0}, mi: {mi}")
                
                if mi == m0:
                    inflator = inflator*m[1]
                    inflatory.append((copy.copy(miesiac_i), copy.copy(inflator)))
                    break
                    
                
            miesiac_i = miesiac_i - relativedelta(months=1)
            #raise Exception(f"Brak danych dla miesiaca: {miesiac_i}")

        # miesiace po miesiacu referencyjnym
        miesiac_i = self.miesiac_ref + relativedelta(months=1)
        inflator = 1
        
        i = 0
        while miesiac_i <= max_miesiac:
            i+=1
            mi = miesiac_i.strftime('%Y-%m')
            for m in self.inflacja_miesiace:
                m0 = m[0].strftime('%Y-%m')
                if mi == m0:
                    inflator = inflator*(1.0/m[1])
                    inflatory.append((copy.copy(miesiac_i), copy.copy(inflator)))
                    break
                    
                
            miesiac_i = miesiac_i + relativedelta(months=1)
            #raise Exception(f"Brak danych dla miesiaca: {miesiac_i}")

        inflatory = sorted(inflatory, key=lambda x: x[0])

        return inflatory
    
    def urealnij(self, data, wartosc) -> float:
            
        miesiac = data.strftime('%Y-%m')

        for i in self.inflator:
            if i[0].strftime('%Y-%m') == miesiac:
                #print(wartosc, i[1])
                return float(wartosc)*float(i[1])
            
        raise ValueError(f"Brak danych dla miesiaca: {miesiac}")


@dataclass
class InflacjaMiesiac:

    data_start: dt.datetime
    okresy: int
    liczba_wakacji: int
    dane: list
    prognoza: list

    def __post_init__(self):

        self.data_koniec = self.data_start + relativedelta(months=(self.okresy+self.liczba_wakacji))

        if self.dane:
            self.df = pd.DataFrame(self.dane)

            #self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')
            self.df.set_index('miesiac', inplace=True)
            self.df["wartosc"] = pd.to_numeric(self.df["wartosc"])
            self.df.index = pd.to_datetime(self.df.index, format='%Y-%m')
       


            self.max_inflacja_real = self.df.index.max()

            if self.data_koniec > self.max_inflacja_real:

                if self.prognoza:
                    self.prognoza = [(dt.datetime.strptime(p[0], '%d/%m/%Y'), p[1]) for p in self.prognoza if dt.datetime.strptime(p[0], '%d/%m/%Y') > self.df.index.max()]
        
                self.prognoza.append((self.df.index.max(), self.df.loc[self.df.index.max(), 'wartosc']))

                #interpolation
                dates, values = zip(*self.prognoza)

                # Convert dates to numerical values representing time or elapsed time
                timestamps = np.array([(date - self.max_inflacja_real).total_seconds() for date in dates])

                # Create an interpolation function using scipy.interpolate.interp1d
                self.interpolation_function = interp1d(timestamps, values)

                # Convert the new date to a numerical value
                end_timestamp = (self.data_koniec - self.max_inflacja_real).total_seconds()

                # Use the interpolation function to estimate the value at the new date
                inflacja_value_koniec= self.interpolation_function(end_timestamp).item()

                self.prognoza = [p for p in self.prognoza if p[0] < self.data_koniec and p[0]> self.df.index.max()]

                self.prognoza.append((self.data_koniec, inflacja_value_koniec))

                new_df = pd.DataFrame(self.prognoza, columns=['miesiac', 'wartosc'])
                #new_df['Date'] = pd.to_datetime(new_df['Date'])
                new_df.set_index('miesiac', inplace=True)
        
                # Concatenate the original DataFrame and the new DataFrame
                self.dff = pd.concat([self.df, new_df])
            else:
                self.dff = self.df[self.df.index <= self.data_koniec]


        else:

            if self.prognoza:
                self.prognoza = [(dt.datetime.strptime(p[0], '%d/%m/%Y'), p[1]) for p in self.prognoza]

            #interpolation
            dates, values = zip(*self.prognoza)

            min_date = min(dates)

            # print(f"min_date: {min_date}, data start: {self.data_start}, data koniec: {self.data_koniec}")

            # Convert dates to numerical values representing time or elapsed time
            timestamps = np.array([(date-min_date).total_seconds() for date in dates])

            # Create an interpolation function using scipy.interpolate.interp1d
            self.interpolation_function = interp1d(timestamps, values)

            # Convert the new date to a numerical value
            start_timestamp = (self.data_start-min_date).total_seconds()

            inflacja_value_start= self.interpolation_function(start_timestamp).item()

            # Convert the new date to a numerical value
            end_timestamp = (self.data_koniec - min_date).total_seconds()

            # Use the interpolation function to estimate the value at the new date
            inflacja_value_koniec= self.interpolation_function(end_timestamp).item()

            self.prognoza.append((self.data_start, inflacja_value_start))
            self.prognoza.append((self.data_koniec, inflacja_value_koniec))

            self.prognoza = [p for p in self.prognoza if p[0] >= self.data_start and p[0]<=self.data_koniec]

            self.dff = pd.DataFrame(self.prognoza, columns=['miesiac', 'wartosc'])
            #new_df['Date'] = pd.to_datetime(new_df['Date'])
            self.dff.set_index('miesiac', inplace=True)


        self.dff = self.dff.sort_index()

      

        self.json_data = [{'date': dt.datetime.strftime(index, '%Y-%m-%d'), 'value': round(value,2)} for index, value in self.dff['wartosc'].items()]

    def _getInflacja(self, dzien):
        if self.dane:
            if dzien > self.max_inflacja_real:
                # Generate a new date for interpolation
                
                # Convert the new date to a numerical value
                new_timestamp = (dzien - self.max_inflacja_real).total_seconds()

                # Use the interpolation function to estimate the value at the new date
                inflacja_value = float(self.interpolation_function(new_timestamp))
                
            else:
                inflacja_value = self._getInflacjaReal(dzien)
            
        else:
            # Convert the new date to a numerical value
            new_timestamp = (dzien - self.data_start).total_seconds()

            # Use the interpolation function to estimate the value at the new date
            inflacja_value = float(self.interpolation_function(new_timestamp))
            
        return inflacja_value

    def _getInflacjaReal(self,dzien):
        inflacja_value = self.dff.loc[(self.dff.index.year == dzien.year) & (self.dff.index.month == dzien.month),'wartosc']
        return inflacja_value[0]

    def urealnij(self, dates_values_list) -> list:

        start_date = self.data_start

        end_date = max([dv['dzien'] for dv in dates_values_list])

        inflator = {f"{dt.datetime.strftime(start_date, '%Y-%m')}":1}
        current_date = start_date

        rolling_mult = 1
        while current_date < end_date:
            current_date = current_date + relativedelta(months=1)
            wartosc = self._getInflacja(current_date)/100.0
            rolling_mult = rolling_mult*wartosc
            inflator[f"{dt.datetime.strftime(current_date, '%Y-%m')}"]= rolling_mult



        new_values= []
        for dv in dates_values_list:
            miesiac = dt.datetime.strftime(dv['dzien'], '%Y-%m')
            wsk_infl = inflator[miesiac]
            new_values.append({'miesiac': miesiac, 'wartosc': float(dv['wartosc'])/wsk_infl})
        
        return new_values
    

@dataclass
class Nieruchomosc:

    data_start: dt.datetime
    okresy: int
    liczba_wakacji: int
    points: list
    dzien_ostatniej_raty: dt.datetime

    def __post_init__(self):

        self.points = [(p['dzien'], p['wartosc']) for p in self.points]

        dates, values = zip(*self.points)

        timestamps = np.array([(date - dates[0]).total_seconds() for date in dates])

        # Create an interpolation function using scipy.interpolate.interp1d
        self.interpolation_function = interp1d(timestamps, values)

        #self.data_koniec = self.data_start + relativedelta(months=(self.okresy+self.liczba_wakacji))
        data_koniec=self.dzien_ostatniej_raty

        start_date = self.data_start

        end_date = max([dv[0] for dv in self.points])
        current_date = dates[0]

        wartosci = []


        while current_date<data_koniec:
            
            new_timestamp = (current_date - dates[0]).total_seconds()
           
            wartosc_value = float(self.interpolation_function(new_timestamp))
            wartosci.append({'dzien': current_date, 'wartosc': wartosc_value})

            current_date = current_date + relativedelta(months=1)

        new_timestamp = (data_koniec - dates[0]).total_seconds()
           
        wartosc_value = float(self.interpolation_function(new_timestamp))
        wartosci.append({'dzien': data_koniec, 'wartosc': wartosc_value})

       
        # wartosci.append({'miesiac': dt.datetime.strftime(self.data_koniec, '%Y-%m'), 'wartosc': wartosc_value_koniec})
        self.json_data = wartosci
    
    def get_points(self):
        return [{'dzien': dt.datetime.strftime(w['dzien'], '%Y-%m'), 'wartosc': w['wartosc']} for w in self.json_data]
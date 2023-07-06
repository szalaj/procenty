

import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import decimal
from dataclasses import dataclass
from scipy.interpolate import interp1d
import numpy as np

@dataclass
class InflacjaMiesiac:

    data_start: dt.datetime
    okresy: int
    liczba_wakacji: int
    dane: list
    prognoza: list

    def __post_init__(self):
        self.df = pd.DataFrame(self.dane)
        #self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')
        self.df.set_index('miesiac', inplace=True)
        self.df["wartosc"] = pd.to_numeric(self.df["wartosc"])
        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m')
        print(self.df)

        self.data_koniec = self.data_start + relativedelta(months=(self.okresy+self.liczba_wakacji))

        self.max_inflacja_real = self.df.index.max()


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

        self.prognoza = [p for p in self.prognoza if p[0] < self.data_koniec]

        self.prognoza.append((self.data_koniec, inflacja_value_koniec))

 
        new_df = pd.DataFrame(self.prognoza, columns=['miesiac', 'wartosc'])
        #new_df['Date'] = pd.to_datetime(new_df['Date'])
        new_df.set_index('miesiac', inplace=True)

        # Concatenate the original DataFrame and the new DataFrame
        dff = pd.concat([self.df, new_df])
        dff = dff.sort_index()
        self.json_data = [{'date': dt.datetime.strftime(index, '%d-%m-%Y'), 'value': round(value,2)} for index, value in dff['wartosc'].items()]



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
    dane: list
    prognoza: list

    def __post_init__(self):
        self.df = pd.DataFrame(self.dane)
        #self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d')
        self.df.set_index('miesiac', inplace=True)
        self.df.index = pd.to_datetime(self.df.index, format='%Y-%m')
        print(self.df)
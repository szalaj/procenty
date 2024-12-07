'''
1. krzywa typu splajn posiada punkt startowy, końcowy, oraz punkty pośrednie
2. do każdego punktu przypisany jest timestamp oraz wartość
3. krzywą można interpolować
'''

from typing import List, Tuple
from datetime import datetime
from dataclasses import dataclass
import numpy as np
from scipy.interpolate import CubicSpline, interp1d
from dateutil.relativedelta import relativedelta


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

@dataclass
class Krzywa:

    punkty: List[Tuple[datetime, float]]

    def __post_init__(self):
        
        self.punkty.sort(key=lambda x: x[0])

        self.start = self.punkty[0][0]
        self.end = self.punkty[-1][0]

        self.timestamps = np.array([dt.timestamp() for dt, _ in self.punkty])
        self.values = np.array([val for _, val in self.punkty])

        spline = CubicSpline(self.timestamps, self.values)

        # Generate points for smooth plot
        self.timestamps_smooth = np.linspace(self.timestamps.min(), self.timestamps.max(), 500)
        self.values_smooth = spline(self.timestamps_smooth)
        
        self.interpolation_function = interp1d(self.timestamps_smooth, self.values_smooth)

 
    def __repr__(self):
        return f'Krzywa({self.start}, {self.end}, {self.punkty})'
    
    def __mul__(self, inflator):
        from procenty.inflacja import Inflacja
        if isinstance(inflator, Inflacja):
            
            wynik = []
            punkty_miesiac = self.podzial_miesiac()

            for punkt in punkty_miesiac:
                wartosc_inflator = inflator.urealnij(punkt[0], punkt[1])
                wynik.append((punkt[0], wartosc_inflator))
                
            return wynik
        return NotImplemented
    
    @property
    def splajn(self):
        return list(zip(self.timestamps_smooth, self.values_smooth))
    
    @property
    def punkty_zip(self):
        return list(zip(self.timestamps, self.values))
    
    def podzial(self, okres_dni:int) -> list:
        '''
        Dzieli krzywą na okresy o długości okres_dni
        '''

        dajs = [self.start + relativedelta(days=(i+1)*okres_dni) for i in range(int((self.end - self.start).days/okres_dni))]
        opr = [(d,self.interpolation_function(d.timestamp()).item()) for d in dajs]

        return opr
    
    def podzial_miesiac(self) -> list:
        '''
        Na razie dzieli na miesace biorac konkretny dzień.
        Trzeba zrobić uśrednienie z całego miesiąca.
        '''
        dajs = [self.start]
        dajs.extend([self.start + relativedelta(months=(i+1)) for i in range(diff_month(self.end, self.start))])
        opr = [(d,self.interpolation_function(d.timestamp()).item()) for d in dajs]

        return opr
    

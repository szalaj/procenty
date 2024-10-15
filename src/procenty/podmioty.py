import numpy as np
import pandas as pd
from dataclasses import dataclass
import networkx as nx




@dataclass
class Menadzer:
    start: str
    czas: int = 0
    def __post_init__(self):
        # check if start is a valid date
        try:
            self._start = pd.to_datetime(self.start)
        except:
            raise ValueError('Niepoprawna data')
        
        self._max_period_przeplyw = None
        
        self.g = nx.MultiDiGraph()

    def dodaj_przeplyw(self, podmiot1, podmiot2, typ, czas, kwota):
        try:
            czas = pd.to_datetime(czas)
        except:
            raise ValueError('Niepoprawna data')
        
        if self._max_period_przeplyw is None:
            self._max_period_przeplyw = czas
        else:
            if czas > self._max_period_przeplyw:
                self._max_period_przeplyw = czas
                
        self.g.add_edge(podmiot1, podmiot2, typ=typ, kwota=kwota, kiedy=czas)
    
    def __repr__(self):
        return f'Menadzer: {self.start}'
    
    @property
    def rokmiesiac(self):
        return self._start.to_period('M')
     
    @property
    def max_period_przeplyw(self):
        return self._max_period_przeplyw

    def sim(self, n=None):
        max_n = self.max_period_przeplyw
        
        start_n = self._start.to_period('M')
        while start_n < max_n.to_period('M'):

            for podmiot1, podmiot2, data in self.g.edges(data=True):
                if data['typ'] == 'przeplyw':
                    if data['kiedy'].to_period('M') == start_n:
                        podmiot2.konto.ma += float(data['kwota'])
                        podmiot1.konto.ma -= float(data['kwota'])


            start_n = start_n + 1




@dataclass
class Konto:
    winien: float
    ma: float
    
    @property
    def saldo(self):
        return self.ma - self.winien
    
    def __repr__(self):
        return f'Konto: {self.saldo}, winien: {self.winien}, ma: {self.ma}'


'''Stan posiadania Podmiotu może się zmieniać co miesiąc.
Podmiot ma konto, które jest zawsze z nim związane.

'''
@dataclass
class Podmiot:
    start: str
    nazwa: str
    mng: object
    def __post_init__(self):
        # check if start is a valid date
        try:
            self._start = pd.to_datetime(self.start)
        except:
            raise ValueError('Niepoprawna data')
        
        if self._start.to_period('M') != self.mng.rokmiesiac:
            raise ValueError('Data niezgodna z menadżerem.')       
        
        self.konto = Konto(0, 0)
    def __hash__(self):
        return hash(self.nazwa)
    def __repr__(self):
        return f'Podmiot: {self.nazwa}'





@dataclass
class BankCentralny:
    stopa_ref: float
    weksle: list

@dataclass
class Weksel:
    stopa: float
    wartosc: float
    okres: int
    okres_start: int

@dataclass
class Bank:
    stopa_pozyczki: float
    stopa_lokaty: float

@dataclass
class Firma():
    """Klasa do symulacji firmy.
    
    Argumenty:
    kapital -- kapitał początkowy firmy
    przychod -- przychód firmy
    koszty -- koszty firmy
    okres -- okres symulacji w latach
    """
    kapital: float
    przychod: float
    koszty: float
    okres: int

    def symulacja(self):
        """Symuluje firmę.
        
        Zwraca DataFrame z kapitałem firmy w kolejnych latach.
        """
        kapital = self.kapital
        przychod = self.przychod
        koszty = self.koszty
        okres = self.okres

        kapitaly = []
        for i in range(okres):
            kapital = kapital + przychod - koszty
            kapitaly.append(kapital)

        return pd.DataFrame({'Kapitał': kapitaly})
    

class Gospodarstwa():
    """Klasa do symulacji gospodarstw domowych.
    
    Argumenty:
    kapital -- kapitał początkowy gospodarstwa
    przychod -- przychód gospodarstwa
    koszty -- koszty gospodarstwa
    okres -- okres symulacji w latach
    """
    def __init__(self, kapital, przychod, koszty, okres):
        self.kapital = kapital
        self.przychod = przychod
        self.koszty = koszty
        self.okres = okres

    def symulacja(self):
        """Symuluje gospodarstwo domowe.
        
        Zwraca DataFrame z kapitałem gospodarstwa w kolejnych latach.
        """
        kapital = self.kapital
        przychod = self.przychod
        koszty = self.koszty
        okres = self.okres

        kapitaly = []
        for i in range(okres):
            kapital = kapital + przychod - koszty
            kapitaly.append(kapital)

        return pd.DataFrame({'Kapitał': kapitaly})


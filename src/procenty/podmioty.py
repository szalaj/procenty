import numpy as np
import pandas as pd
from dataclasses import dataclass


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


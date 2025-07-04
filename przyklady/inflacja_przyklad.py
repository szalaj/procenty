from procenty.kredyt import Kredyt, KredytPorownanie, KredytSuwak, Zdarzenie, Rodzaj
from procenty.utils import create_kredyt
from procenty.stopy import Krzywa
from procenty.inflacja import Inflacja
from decimal import Decimal
from datetime import datetime


if __name__ == "__main__":

    punkty = [(datetime(2021, 10, 13), 1.01), 
                (datetime(2040, 6, 13), 1.01)]
    
    kr = Krzywa(punkty)
    
    inflacja = Inflacja(kr, datetime(2021, 10, 13))

    print(inflacja.inflator)
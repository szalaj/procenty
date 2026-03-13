from datetime import datetime
from decimal import Decimal

from procenty.inflacja import Inflacja
from procenty.kredyt import Kredyt, KredytPorownanie, KredytSuwak, Rodzaj, Zdarzenie
from procenty.stopy import Krzywa
from procenty.utils import create_kredyt

if __name__ == "__main__":

    punkty = [(datetime(2021, 10, 13), 1.01), (datetime(2040, 6, 13), 1.01)]

    kr = Krzywa(punkty)

    inflacja = Inflacja(kr, datetime(2021, 10, 13))

    print(inflacja.inflator)

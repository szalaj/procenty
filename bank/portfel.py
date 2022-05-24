

import datetime
from dateutil.relativedelta import relativedelta


class Portfel:
    '''
    Miejsce do przechowywania róznych
    produktów finansowych
    '''
    def __init__(self):

        self.produkty = []


    def dodajProdukt(self, produkt):

        self.produkty.append(produkt)


    def getSumaSald(self, miesiac):
        suma = 0
        for prod in self.produkty:

            suma += prod.getSaldoMiesiac(miesiac)

        return suma


class Inflator:

    def __init__(self, inflacja_dane, miesiac_baza):

        self.inflacja = inflacja_dane
        self.miesiac_baza = miesiac_baza

    def oblicz(self, kwota, miesiac_obliczany):

        dbaza = datetime.datetime.strptime(self.miesiac_baza, "%d/%m/%Y")
        #doblicz = datetime.datetime.strptime(miesiac_obliczany, "%d/%m/%Y")
        doblicz = miesiac_obliczany

        # obliczenie wartosci inflacji z ciagu
        # pomiedzy miesiącem bazowy a obliczanym

        liczba_miesiecy = (doblicz.year - dbaza.year) * 12 + doblicz.month - dbaza.month

        inflator = 1

        for i in range(1, liczba_miesiecy+1):

            data_next = dbaza + relativedelta(months=i)

            inflator *= 1 + self.inflacja[data_next.strftime('%m/%Y')]



        return kwota/inflator

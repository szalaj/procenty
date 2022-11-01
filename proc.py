
from xmlrpc.client import Boolean
import yaml
import sys
import getopt
import datetime as dt
from dataclasses import dataclass
from enum import auto, Enum
import decimal
from decimal import Decimal
import logging


logging.basicConfig(filename='loginfo.log', encoding='utf-8', level=logging.DEBUG)

class Rodzaj(Enum):
    SPLATA = auto()
    OPROCENTOWANIE = auto()
    NADPLATA = auto()

@dataclass
class Zdarzenie:
    data:dt.datetime
    rodzaj:Rodzaj
    wartosc:object
    def __lt__(self, other):
        return self.data < other.data

class Kredyt:
    def __init__(self,K:Decimal, N:int, p:Decimal, start:dt.datetime):

        self.K = K
        self.N = N
        self.p = p
        self.start = start
        self.dzien_odsetki = start
        self.zdarzenia = []
    
        self.odsetki_naliczone = 0
        self.I = 0

        self.wynik = []

    def __repr__(self) -> str:
        return "kredyt : {}".format(self.K)

    def wyswietl(self, dzien_raty):

        grosze =  decimal.Decimal('.01')

        return "dzien: {}, K: {} zł, odsetki: {} zł, rata: {} zł".format(dzien_raty, 
                                                              self.K.quantize(grosze),  
                                                              self.odsetki_naliczone.quantize(grosze), 
                                                              self.I.quantize(grosze))

    def zapisz_stan(self, dzien_raty):

        grosze =  decimal.Decimal('.01')

        data = {
            'dzien': str(dzien_raty),
            'K': str(self.K.quantize(grosze)),  
            'odsetki': str(self.odsetki_naliczone.quantize(grosze)), 
            'rata':str(self.I.quantize(grosze))
        }

        self.wynik.append(data)

        

        
        return 1

            

    def oblicz_rate(self) -> Decimal:  
        k = 12

        do_splaty = self.K + self.odsetki_naliczone

        L = (do_splaty * self.p)
        M = k*(1-pow(k/(k+self.p),self.N) )
        I =L/M
        return I
        

    def zmien_oprocentowanie(self, dzien_zmiany:dt.datetime, nowe_p:Decimal) -> Boolean:

        # nalicz odsetki do dnia zmiany raty
        o_dni = (dzien_zmiany - self.dzien_odsetki).days

        opr = Decimal((o_dni/365))*self.p

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K

        self.p = Decimal(nowe_p/100.0)

        self.dzien_odsetki = dzien_zmiany

    def zrob_nadplate(self, dzien_nadplaty:dt.datetime, kwota:Decimal) -> Boolean:

        o_dni = (dzien_nadplaty - self.dzien_odsetki).days

        opr = Decimal((o_dni/365))*self.p

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K

        self.K = self.K - kwota

        self.dzien_odsetki = dzien_nadplaty



    def splata_raty(self, dzien_raty:dt.datetime) -> Boolean:

        o_dni = (dzien_raty - self.dzien_odsetki).days

        opr = Decimal((o_dni/365))*self.p

        self.odsetki_naliczone = self.odsetki_naliczone + opr*self.K

        self.I = self.oblicz_rate()


        if self.odsetki_naliczone > self.I:
            self.I = self.odsetki_naliczone

        self.zapisz_stan(dzien_raty)

        print(self.wyswietl(dzien_raty))
    
        self.K = self.K - (self.I-self.odsetki_naliczone)
        self.odsetki_naliczone = 0

        self.dzien_odsetki = dzien_raty
        self.N -= 1

    def symuluj(self):

        for zdarzenie in sorted(self.zdarzenia):
            if zdarzenie.rodzaj == Rodzaj.OPROCENTOWANIE:
                self.zmien_oprocentowanie(zdarzenie.data, zdarzenie.wartosc)
            elif zdarzenie.rodzaj == Rodzaj.SPLATA:
                self.splata_raty(zdarzenie.data)
            elif zdarzenie.rodzaj == Rodzaj.NADPLATA:
                self.zrob_nadplate(zdarzenie.data, zdarzenie.wartosc)

    def zapisz_do_pliku(self, nazwa_pliku):

        zapis = {"raty": self.wynik, "kapital_na_koniec": str(self.K.quantize(decimal.Decimal('0.01')))}

        yaml.dump(zapis, open(nazwa_pliku, 'w'), default_flow_style=False)

            
            

if __name__== "__main__":

    logging.info("{} start aplikacji".format(dt.datetime.now()))

    try:

        opts, arg = getopt.getopt(sys.argv[1:], 'm:',  ["model="])
        
        for opt, arg in opts:
            if opt in ("-m", "--model"):
                plik_model = str(arg)
                
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

    stream = open("./models/{}.yml".format(plik_model), 'r')
    dane = yaml.safe_load(stream)


    k = 12
    p = Decimal(dane['p']/100.0)
    K = Decimal(dane['K'])
    dni = dane['daty_splaty']
    N = len(dni)

    kr = Kredyt(K, N, p, dt.datetime.strptime(dane['start'], '%Y-%m-%d'))

    for dzien_splaty in dane['daty_splaty']:
        kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(dzien_splaty, '%Y-%m-%d'), Rodzaj.SPLATA, 0))

    if 'oprocentowanie' in dane:
        for zmiana_opr in dane['oprocentowanie']:
            kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(zmiana_opr['dzien'], '%Y-%m-%d'), Rodzaj.OPROCENTOWANIE, zmiana_opr['proc']))

    if 'nadplaty' in dane:
        for nadplata in dane['nadplaty']:
            kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(nadplata['dzien'], '%Y-%m-%d'), Rodzaj.NADPLATA, nadplata['kwota']))


    kr.symuluj()


    print("kapital na koniec : {}".format(kr.K.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))

    kr.zapisz_do_pliku('wynik_mod2.yml')

    logging.info("{} koniec aplikacji".format(dt.datetime.now()))
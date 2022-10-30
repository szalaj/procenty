from xmlrpc.client import Boolean
import yaml
import sys
import getopt
import datetime as dt
from dataclasses import dataclass
from enum import auto, Enum
import decimal
from decimal import Decimal



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

    def __repr__(self) -> str:
        return " K: {}\n N: {} \n p: {} \n start_dzien: {}".format(self.K, self.N, self.p, self.start)

    def rata(self) -> Decimal:  
        k = 12
        L = (self.K * self.p)
        M = k*(1-pow(k/(k+self.p),self.N) )
        I =L/M
        return I

    def splata_raty(self, dzien_raty:dt.datetime) -> Boolean:

        I = kr.rata()
            
        o_dni = (dzien_raty - self.dzien_odsetki).days

        opr = Decimal((o_dni/365))*self.p

        odsetki = self.odsetki_naliczone +  opr*self.K

        self.K = self.K - (I-odsetki)
        self.dzien_odsetki = dzien_raty

        self.N -= 1




if __name__== "__main__":

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

    print(dane['oprocentowanie'])

    k = 12
    p = Decimal(dane['p']/100.0)
    K = Decimal(dane['K'])
    dni = dane['daty_splaty']
    N = len(dni)

    kr = Kredyt(K, N, p, dt.datetime.strptime(dane['start'], '%Y-%m-%d'))

    for dzien_splaty in dane['daty_splaty']:
        kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(dzien_splaty, '%Y-%m-%d'), Rodzaj.SPLATA, 0))

    for zmiana_opr in dane['oprocentowanie']:
        kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(zmiana_opr['dzien'], '%Y-%m-%d'), Rodzaj.OPROCENTOWANIE, zmiana_opr['proc']))

    

    dzien_o = kr.start
    for zdarzenie in sorted(kr.zdarzenia):

        if zdarzenie.rodzaj == Rodzaj.OPROCENTOWANIE:
            print(zdarzenie.rodzaj)
        elif zdarzenie.rodzaj == Rodzaj.SPLATA:
            kr.splata_raty(zdarzenie.data)
            

    #print('I : {}'.format(I.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))

    print("kapital na koniec : {}".format(kr.K.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))
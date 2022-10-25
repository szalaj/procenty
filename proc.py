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
        self.zdarzenia = []
        print(type(K))

    def __repr__(self) -> str:
        return " K: {}\n N: {} \n p: {} \n start_dzien: {}".format(self.K, self.N, self.p, self.start)

    def rata(self) -> Decimal:  
        k = 12
        L = (self.K * self.p)
        M = k*(1-pow(k/(k+self.p),self.N) )
        I =L/M
        return I


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

    I = kr.rata()

    dzien_o = kr.start
    for zdarzenie in sorted(kr.zdarzenia):
        dzien_k = zdarzenie.data
        o_dni = (dzien_k - dzien_o).days
        opr = Decimal((o_dni/365))*kr.p
        odsetki = opr*kr.K
        kr.K = kr.K - (I-odsetki)
        dzien_o = dzien_k

    print('I : {}'.format(I.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))

    print("kapital na koniec : {}".format(kr.K.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))
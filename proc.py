import yaml
import sys
import getopt
import datetime as dt
from dataclasses import dataclass
from enum import auto, Enum
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

    def __repr__(self) -> str:
        
        return " K: {}\n N: {} \n p: {} \n start_dzien: {}".format(self.K, self.N, self.p, self.start)

if __name__== "__main__":

    stream = open("./models/mod1.yml", 'r')
    dane = yaml.safe_load(stream)
    for key, value in dane.items():
        print (key + " : " + str(value))

    k = 12
    p = dane['p']/100.0
    S = dane['K']
    N = dane['N']
    dni = dane['daty_splaty']

    kr = Kredyt('aa', 23, 3, '2022-01-01')
    print(kr)

    L = (S*p)
    M = k*(1-pow(k/(k+p), N))
    I = L/M

    dzien_o = dt.datetime.strptime(dane['start'], '%Y-%m-%d')
    Kap = float(S)
    for dzien in dni:
        dzien_k = dt.datetime.strptime(dzien, '%Y-%m-%d')
        
        o_dni = (dzien_k - dzien_o).days

        opr = (o_dni/365)*p

        odsetki = opr*Kap

        Kap = Kap - (I-odsetki)

        dzien_o = dzien_k

    print(Kap)



    print('I : {}'.format(I))
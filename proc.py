import yaml
import sys
import getopt
import datetime as dt

class Kredyt:
    def __init__(self,K):
        self.K = K
        self.zdarzenia = []

class Zdarzenie:
    def __init__(self, data, desc):
        self.data = data
        self.desc = desc
    def __lt__(self, other):
        return self.data < other.data

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

    kr = Kredyt(S)

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
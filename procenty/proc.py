import yaml
import sys
import logging
import getopt
import datetime as dt
from dataclasses import dataclass
from enum import auto, Enum
import decimal
from decimal import Decimal, ROUND_HALF_UP
from procenty.miary import Odleglosc

class Rodzaj(Enum):
    SPLATA = 3
    OPROCENTOWANIE = 4
    NADPLATA = 2
    SPLATA_CALKOWITA = 6
    TRANSZA = 1
    WAKACJE = 5

@dataclass
class Zdarzenie:
    data:dt.datetime
    rodzaj:Rodzaj
    wartosc:object
    def __lt__(self, other):

        return str(self.data) + str(self.rodzaj.value) < str(other.data) + str(other.rodzaj.value)

class Kredyt:
    def __init__(self,K:Decimal, N:int, p:Decimal, marza:Decimal, start:dt.datetime, rodzajRat:str):
        grosze =  decimal.Decimal('.01')

        self.K = K.quantize(grosze, ROUND_HALF_UP)
        self.N = N
        self.p = p
        self.marza = marza
        self.start = start
        self.rodzajRat = rodzajRat

        self.dzien_odsetki = start
        self.zdarzenia = []
    
        self.odsetki_naliczone = 0
        self.odsetki_naliczone_marza = 0
        self.I = 0
        
        self.licznik_rat = 0

        self.wynik = []
        self.wynik_nadplaty = []


    def __repr__(self) -> str:
        return "kredyt : {}".format(self.K)

    def wyswietl(self, dzien_raty):

        grosze =  decimal.Decimal('.01')

        return "dzien: {}, K: {} zł, odsetki: {} zł, rata: {} zł".format(dzien_raty, 
                                                              self.K.quantize(grosze, ROUND_HALF_UP),  
                                                              self.odsetki_naliczone.quantize(grosze, ROUND_HALF_UP), 
                                                              self.I.quantize(grosze, ROUND_HALF_UP))

    def zapisz_stan(self, dzien_raty):


        grosze =  decimal.Decimal('.01')

        data = {
            'dzien': dzien_raty.strftime('%Y-%m-%d'),
            'K': str(self.K.quantize(grosze, ROUND_HALF_UP)),  
            'odsetki': str(self.odsetki_naliczone.quantize(grosze, ROUND_HALF_UP)), 
            'odsetki_marza': str(self.odsetki_naliczone_marza.quantize(grosze, ROUND_HALF_UP)), 
            'odsetki_wibor': str(self.odsetki_naliczone.quantize(grosze, ROUND_HALF_UP)-self.odsetki_naliczone_marza.quantize(grosze, ROUND_HALF_UP)), 
            'kapital': str(self.I.quantize(grosze, ROUND_HALF_UP)-self.odsetki_naliczone.quantize(grosze, ROUND_HALF_UP)), 
            'rata':str(self.I.quantize(grosze, ROUND_HALF_UP)),
            'nr_raty': self.licznik_rat,
            'K_po': str((self.K-(self.I-self.odsetki_naliczone)).quantize(grosze, ROUND_HALF_UP))
        }

        self.wynik.append(data)


        return 1

            

    def oblicz_rate(self) -> Decimal:  

        if self.rodzajRat=='rowne':
            k = 12
            do_splaty = self.K
            if self.p>0:
                L = (do_splaty * self.p)
                M = k*(1-pow(k/(k+self.p),self.N) )
                I =L/M
            else: 
                I = do_splaty/self.N
        elif self.rodzajRat=='malejace':
            I = (self.K/self.N)*(1+(self.p/12)*self.N)
        else:
            raise Exception('nie ma takich rat')


        return I
        

    def zmien_oprocentowanie(self, dzien_zmiany:dt.datetime, nowe_p:Decimal):


        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_zmiany.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K
        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza +  opr_marza*self.K

        self.p = Decimal(nowe_p/100.0)

        self.dzien_odsetki = dzien_zmiany


    def zrob_nadplate(self, dzien_nadplaty:dt.datetime, kwota:Decimal):

        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_nadplaty.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K

        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza +  opr_marza*self.K

        if kwota > self.K:
            kwota = self.K
            self.K = Decimal(0)
        else:
            self.K = self.K - kwota

        self.dzien_odsetki = dzien_nadplaty
        grosze =  decimal.Decimal('.01')
        self.wynik_nadplaty.append({'dzien': str(dzien_nadplaty.strftime('%Y-%m-%d')),
                                    'kwota': str(kwota.quantize(grosze, ROUND_HALF_UP)),
                                    })


    def zrob_transze(self, dzien_transzy:dt.datetime, kwota:Decimal):

        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_transzy.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K
        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza +  opr_marza*self.K

        self.K = self.K + kwota

        self.dzien_odsetki = dzien_transzy

    def zrob_splate_calkowita(self, dzien_splaty:dt.datetime):
        grosze =  decimal.Decimal('.01')

        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_splaty.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        self.odsetki_naliczone = (self.odsetki_naliczone + opr*self.K).quantize(grosze, ROUND_HALF_UP)

        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza +  opr_marza*self.K


        self.I = self.K - self.odsetki_naliczone
  
        self.licznik_rat += 1
        self.zapisz_stan(dzien_splaty)

        self.K = Decimal(0).quantize(grosze, ROUND_HALF_UP)

        self.dzien_odsetki = dzien_splaty



    def splata_raty(self, dzien_raty:dt.datetime):

        grosze =  decimal.Decimal('.01')

        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_raty.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        if self.K > 0:
            self.I = self.oblicz_rate().quantize(grosze, ROUND_HALF_UP)
        else:
            self.I = Decimal(0).quantize(grosze, ROUND_HALF_UP)

        self.odsetki_naliczone = (self.odsetki_naliczone + opr*self.K).quantize(grosze, ROUND_HALF_UP)
        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza + opr_marza*self.K

        
        if self.odsetki_naliczone > self.I:
            self.I = self.odsetki_naliczone

        #ostatnia rata
        if self.N == 1:
            roznica_na_koniec = self.K - (self.I-self.odsetki_naliczone)
            self.I += roznica_na_koniec

        self.licznik_rat += 1
        self.zapisz_stan(dzien_raty)

    
        self.K = self.K - (self.I-self.odsetki_naliczone)


        self.odsetki_naliczone = 0
        self.odsetki_naliczone_marza = 0

        self.dzien_odsetki = dzien_raty
        self.N -= 1

    def symuluj(self):

        for zdarzenie in sorted(self.zdarzenia):
            #print(zdarzenie)
            if zdarzenie.rodzaj == Rodzaj.OPROCENTOWANIE:
                self.zmien_oprocentowanie(zdarzenie.data, zdarzenie.wartosc)
            elif zdarzenie.rodzaj == Rodzaj.SPLATA:
                self.splata_raty(zdarzenie.data)
            elif zdarzenie.rodzaj == Rodzaj.SPLATA_CALKOWITA:
                self.zrob_splate_calkowita(zdarzenie.data)
            elif zdarzenie.rodzaj == Rodzaj.NADPLATA:
                self.zrob_nadplate(zdarzenie.data, zdarzenie.wartosc)
            elif zdarzenie.rodzaj == Rodzaj.TRANSZA:
                self.zrob_transze(zdarzenie.data, zdarzenie.wartosc)
            
            if self.K == Decimal(0):
                break

        return {"raty": self.wynik, "nadplaty": self.wynik_nadplaty, "kapital_na_koniec": str(self.K.quantize(decimal.Decimal('0.01')))}

    def zapisz_do_pliku(self, nazwa_pliku):

        zapis = {"raty": self.wynik, "kapital_na_koniec": str(self.K.quantize(decimal.Decimal('0.01')))}

        yaml.dump(zapis, open(nazwa_pliku, 'w'), default_flow_style=False)

            

def create_kredyt(dane_kredytu, rodzajRat):

    dane = dane_kredytu

    p = Decimal(dane['p']/100.0)
    marza = Decimal(dane['marza']/100.0)
    K = Decimal(dane['K'])
    dni = dane['daty_splaty']
    N = len(dni)
    start_kredytu = dt.datetime.strptime(dane['start'], '%Y-%m-%d')

    kr = Kredyt(K, N, p, marza, start_kredytu, rodzajRat)

    for dzien_splaty in dane['daty_splaty']:
        kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(dzien_splaty, '%Y-%m-%d'), Rodzaj.SPLATA, 0))

    if 'oprocentowanie' in dane:
        for zmiana_opr in dane['oprocentowanie']:
            kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(zmiana_opr['dzien'], '%Y-%m-%d'), Rodzaj.OPROCENTOWANIE, zmiana_opr['proc']))

    if 'nadplaty' in dane:
        for nadplata in dane['nadplaty']:
            if nadplata['calkowita'] == True:
                kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(nadplata['dzien'], '%Y-%m-%d'), Rodzaj.SPLATA_CALKOWITA, Decimal(nadplata['kwota'])))
            else:
                kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(nadplata['dzien'], '%Y-%m-%d'), Rodzaj.NADPLATA, Decimal(nadplata['kwota'])))
            
    if 'transze' in dane:
        for transza in dane['transze']:
            kr.zdarzenia.append(Zdarzenie(dt.datetime.strptime(transza['dzien'], '%Y-%m-%d'), Rodzaj.TRANSZA, Decimal(transza['kapital'])))


    return kr.symuluj()




if __name__== "__main__":

    logging.basicConfig(filename='logs/loginfo.log', encoding='utf-8', level=logging.DEBUG)
    logging.info("{} start aplikacji".format(dt.datetime.now()))

    try:

        opts, arg = getopt.getopt(sys.argv[1:], 'm:',  ["model="])
        
        for opt, arg in opts:
            if opt in ("-m", "--model"):
                plik_model = str(arg)
                
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

    kr = create_kredyt(plik_model)

    kr.symuluj()


    #print("kapital na koniec : {}".format(kr.K.quantize(Decimal('.01'), decimal.ROUND_HALF_UP)))

    kr.zapisz_do_pliku('./results/last_result.yml')

    logging.info("{} koniec aplikacji".format(dt.datetime.now()))

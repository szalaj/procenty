from loguru import logger
from typing import Any
import datetime as dt
from dataclasses import dataclass
from enum import auto, Enum
import decimal
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from procenty.miary import Odleglosc
import procenty.inwestycja as inv
import copy

from dateutil.relativedelta import relativedelta

grosze =  decimal.Decimal('.01')

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

@dataclass
class Kredyt:
    """Klasa do obsługi kredytów."""
    K:Decimal
    N:int
    p:Decimal
    marza:Decimal
    start:dt.datetime
    rodzajRat:str
    splaty_normalne:bool=True
    operacje:Optional[list[Zdarzenie]] = None


    def __post_init__(self):
        self.Kstart = self.K
        self.Nstart = self.N

        self.K = self.K.quantize(grosze, ROUND_HALF_UP)
        self.dzien_odsetki: dt.datetime = self.start
        self.zdarzenia: list[Zdarzenie] = []
        if self.operacje:
            self.zdarzenia.extend(self.operacje)
    
        self.odsetki_naliczone = 0
        self.odsetki_naliczone_marza = 0
        self.I = 0
        
        self.licznik_rat = 0

        self.transze = []

        self.wynik = []
        self.wynik_nadplaty = []

        if self.splaty_normalne:
            dni_splaty = [self.start + relativedelta(months=i+1) for i in range(self.N)]
            for dzien_splaty in dni_splaty:
                self.zdarzenia.append(Zdarzenie(dzien_splaty, Rodzaj.SPLATA, 0))

        N_zdarzenie=[z for z in self.zdarzenia if z.rodzaj == Rodzaj.SPLATA]
        if len(N_zdarzenie) != self.N:
            logger.warning(f"Kredyt: {self.K}, splaty normalne {self.splaty_normalne}.Nie zgadza się liczba zdarzeń {len(N_zdarzenie)} z N {self.N}")
            raise Exception('Nie zgadza się liczba zdarzeń SPLATA RATY z argumentem N')

            
        self.kredyt_wynik = self._symuluj()


    def __repr__(self) -> str:
        return "kredyt : {}".format(self.K)

    def wyswietl(self, dzien_raty):

        grosze =  decimal.Decimal('.01')
        return "dzien: {}, K: {} zł, odsetki: {} zł, rata: {} zł".format(dzien_raty, 
                                                              self.K.quantize(grosze, ROUND_HALF_UP),  
                                                              self.odsetki_naliczone.quantize(grosze, ROUND_HALF_UP), 
                                                              self.I.quantize(grosze, ROUND_HALF_UP))

    def zapisz_stan(self, dzien_raty):


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

        self.transze.append({'dzien': dzien_transzy, 'kwota': kwota})

    def zrob_splate_calkowita(self, dzien_splaty:dt.datetime):

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
        

    def _symuluj(self):
        

        for zdarzenie in sorted(self.zdarzenia):


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

    @property
    def raty(self) -> list:
        return self.kredyt_wynik['raty']
    
    @property
    def xirr(self)->float:
        cashflows = [(dt.datetime.strptime(x['dzien'], '%Y-%m-%d'), float(x['rata'])) for x in self.kredyt_wynik['raty']]
        cashflows = cashflows + [(dt.datetime.strptime(x['dzien'], '%Y-%m-%d'), float(x['kwota'])) for x in self.kredyt_wynik['nadplaty']]
        cashflows = cashflows + [(self.start, float(-self.Kstart))]
        cashflows = cashflows + [(x['dzien'], float(-x['kwota'])) for x in self.transze]

        return inv.xirr(cashflows)

    @property
    def podsumowanie(self) -> str:
        raty = [float(x['rata']) for x in self.kredyt_wynik['raty']]
        ile = len(raty)
        suma = sum(raty)
        return f"K: {self.Kstart}, suma rat: {suma}, liczba rat: {ile}, xirr: {self.xirr}"
            
@dataclass
class KredytPorownanie():
    """Klasa do obsługi kredytów."""
    kredyt:Kredyt
    p:Decimal
    def __post_init__(self):

        self.kredyt = copy.deepcopy(self.kredyt)

        self.kredyt_suwak = Kredyt(self.kredyt.Kstart, 
                                   self.kredyt.Nstart, 
                                   self.p,
                                   self.kredyt.marza, 
                                   self.kredyt.start, 
                                   self.kredyt.rodzajRat, 
                                   self.kredyt.splaty_normalne, 
                                   self.kredyt.operacje)
        

    
    @property
    def xirr(self) -> float:
        return self.kredyt_suwak.xirr

    @property
    def raty(self) -> list:
        return self.kredyt_suwak.raty

def create_kredyt(dane:list[dict[str, Any]], rodzajRat:str):


    p = Decimal(dane['p']/100.0)
    marza = Decimal(dane['marza']/100.0)
    K = Decimal(dane['K'])
    dni = dane['daty_splaty']
    N = len(dni)
    start_kredytu = dt.datetime.strptime(dane['start'], '%Y-%m-%d')

    zdarzenia = []

    for dzien_splaty in dane['daty_splaty']:
        zdarzenia.append(Zdarzenie(dt.datetime.strptime(dzien_splaty, '%Y-%m-%d'), Rodzaj.SPLATA, 0))

    if 'oprocentowanie' in dane:
        for zmiana_opr in dane['oprocentowanie']:
            zdarzenia.append(Zdarzenie(dt.datetime.strptime(zmiana_opr['dzien'], '%Y-%m-%d'), Rodzaj.OPROCENTOWANIE, zmiana_opr['proc']))

    if 'nadplaty' in dane:
        for nadplata in dane['nadplaty']:
            if nadplata['calkowita'] == True:
                zdarzenia.append(Zdarzenie(dt.datetime.strptime(nadplata['dzien'], '%Y-%m-%d'), Rodzaj.SPLATA_CALKOWITA, Decimal(nadplata['kwota'])))
            else:
                zdarzenia.append(Zdarzenie(dt.datetime.strptime(nadplata['dzien'], '%Y-%m-%d'), Rodzaj.NADPLATA, Decimal(nadplata['kwota'])))
            
    if 'transze' in dane:
        for transza in dane['transze']:
            zdarzenia.append(Zdarzenie(dt.datetime.strptime(transza['dzien'], '%Y-%m-%d'), Rodzaj.TRANSZA, Decimal(transza['kapital'])))


    kr = Kredyt(K, N, p, marza, start_kredytu, rodzajRat, False, zdarzenia)



    return kr




if __name__== "__main__":
    pass
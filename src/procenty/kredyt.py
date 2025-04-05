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
from procenty.inflacja import Inflacja
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
    r:Decimal
    marza:Decimal
    start:dt.datetime
    rodzajRat:str
    splaty_normalne:bool=True
    operacje:Optional[list[Zdarzenie]] = None


    def __post_init__(self):
        self.Kstart = self.K
        self.Nstart = self.N

        self.p = self.r + self.marza

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

        self.wszystkie_koszty= []
        self.wszystkie_koszty_kwota = 0

        if self.splaty_normalne:
            dni_splaty = [self.start + relativedelta(months=i+1) for i in range(self.N)]
            for dzien_splaty in dni_splaty:
                self.zdarzenia.append(Zdarzenie(dzien_splaty, Rodzaj.SPLATA, 0))

        N_zdarzenie=[z for z in self.zdarzenia if z.rodzaj == Rodzaj.SPLATA]
        if len(N_zdarzenie) != self.N:
            logger.warning(f"Kredyt: {self.K}, splaty normalne {self.splaty_normalne}.Nie zgadza się liczba zdarzeń {len(N_zdarzenie)} z N {self.N}")
            raise Exception('Nie zgadza się liczba zdarzeń SPLATA RATY z argumentem N')

            
        self.kredyt_wynik = self._symuluj()

        if self.rodzajRat=='malejace_met2':
            print("przeliczam---------------------------")
            odsetki = [float(x['odsetki']) for x in self.kredyt_wynik['raty']]
            odsetki_marza = [float(x['odsetki_marza']) for x in self.kredyt_wynik['raty']]
            odsetki_wibor = [float(x['odsetki_wibor']) for x in self.kredyt_wynik['raty']]

            nowe_odsetki = self.__przelicz_odsetki_mal2(odsetki)
            nowe_odsetki_marza = self.__przelicz_odsetki_mal2(odsetki_marza)
            nowe_odsetki_wibor = self.__przelicz_odsetki_mal2(odsetki_wibor)

            for i in range(len(self.kredyt_wynik['raty'])):
                self.kredyt_wynik['raty'][i]['odsetki'] = str(Decimal(nowe_odsetki[i]).quantize(grosze, ROUND_HALF_UP))
                self.kredyt_wynik['raty'][i]['odsetki_marza'] = nowe_odsetki_marza[i]
                self.kredyt_wynik['raty'][i]['odsetki_wibor'] = nowe_odsetki_wibor[i]
                
                nowa_rata= Decimal(nowe_odsetki[i]  + float(self.kredyt_wynik['raty'][i]['kapital']))
                self.kredyt_wynik['raty'][i]['rata'] = str(nowa_rata.quantize(grosze, ROUND_HALF_UP))


    def __repr__(self) -> str:
        return "kredyt : {}".format(self.K)
    
    def _dodaj_koszt(self, dzien_koszt:dt.datetime, kwota:Decimal):
        dotychczasowe_koszty = self.wszystkie_koszty_kwota
        self.wszystkie_koszty_kwota = dotychczasowe_koszty + kwota
        self.wszystkie_koszty.append({'dzien': dzien_koszt.strftime('%Y-%m-%d'), 'kwota': float(copy.copy(self.wszystkie_koszty_kwota))})

    def __przelicz_odsetki_mal2(self, ciag_platnosci:list[float]) -> list[float]:
    

        N = len(ciag_platnosci)
        sum_O = sum(ciag_platnosci)


        o_N = ciag_platnosci[-1]

        # Wyznaczanie współczynnika A
        # A = (2 * sum_O - N * o_N) / (N * (N + 1))

        a1 = N*((1+N)/2)-N*N
        A= (sum_O - N*o_N)/a1


        # Wyznaczanie współczynnika B
        B = o_N - A * N

        # Tworzenie nowego ciągu odsetek
        nowy_ciag = [A * i + B for i in range(1, N + 1)]
        

        return nowy_ciag
      

    def pokaz_koszty(self):
        return self.wszystkie_koszty
    
    def pokaz_koszty_real(self, inflator:Inflacja):
        wynik = []
        for koszt in self.wszystkie_koszty:
            wynik.append({'dzien':koszt['dzien'], 'kwota': inflator.urealnij(dt.datetime.strptime(koszt['dzien'], '%Y-%m-%d'), koszt['kwota'])})
        return wynik

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
        elif self.rodzajRat=='malejace_met2':
            I = (self.K/self.N)*(1+(self.p/12)*(self.N+1)/2) #workaround
        else:
            raise Exception('nie ma takich rat')


        return I
        

    def zmien_oprocentowanie(self, dzien_zmiany:dt.datetime, nowe_r:Decimal):


        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_zmiany.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        opr_marza = o_d.mnoznik*self.marza

        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K
        self.odsetki_naliczone_marza = self.odsetki_naliczone_marza +  opr_marza*self.K

        self.p = Decimal((nowe_r/100.0))+self.marza

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
        
        self._dodaj_koszt(dzien_nadplaty, kwota)


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

        kwota = self.K - self.odsetki_naliczone

        self.I = kwota
  
        self.licznik_rat += 1
        self.zapisz_stan(dzien_splaty)

        self.K = Decimal(0).quantize(grosze, ROUND_HALF_UP)
        self.dzien_odsetki = dzien_splaty
        self._dodaj_koszt(dzien_splaty, kwota)


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

        #work around
        if self.rodzajRat=='malejace_met2':
            self.I = (self.Kstart/self.Nstart + self.odsetki_naliczone).quantize(grosze, ROUND_HALF_UP)
            if self.K <=0:
                self.I = Decimal(0).quantize(grosze, ROUND_HALF_UP)

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

        self._dodaj_koszt(dzien_raty, self.I)
        

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
    def nadplaty(self) -> list:
        return self.kredyt_wynik['nadplaty']  
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
        nadplaty = [float(x['kwota']) for x in self.kredyt_wynik['nadplaty']]
        suma_nadplat = sum(nadplaty)
        odsetki = [float(x['odsetki']) for x in self.kredyt_wynik['raty']]
        suma_odsetek = sum(odsetki)

        dane = {'raty': self.kredyt_wynik['raty'],
                'info': {
                    'suma_rat': str(Decimal(suma).quantize(grosze, ROUND_HALF_UP)),
                    'suma_nadplat': str(Decimal(suma_nadplat).quantize(grosze, ROUND_HALF_UP)),
                    'suma_odsetek': str(Decimal(suma_odsetek).quantize(grosze, ROUND_HALF_UP)),
                    'liczba_rat': ile,
                    'xirr': str(self.xirr),
                    'K': str(self.Kstart.quantize(grosze, ROUND_HALF_UP))}
                }
        


        return dane
            
@dataclass
class KredytPorownanie():
    """Klasa do obsługi kredytów."""
    kredyt:Kredyt
    r:Decimal
    def __post_init__(self):

        self.kredyt = copy.deepcopy(self.kredyt)

        self.kredyt_porownanie = Kredyt(self.kredyt.Kstart, 
                                   self.kredyt.Nstart, 
                                   self.r,
                                   self.kredyt.marza, 
                                   self.kredyt.start, 
                                   self.kredyt.rodzajRat, 
                                   self.kredyt.splaty_normalne, 
                                   self.kredyt.operacje)
        
    @property
    def xirr(self) -> float:
        return self.kredyt_porownanie.xirr

    @property
    def raty(self) -> list:
        return self.kredyt_porownanie.raty
    
    @property
    def podsumowanie(self) -> dict:
        return self.kredyt_porownanie.podsumowanie

@dataclass
class KredytSuwak:
    K:Decimal
    N:int
    p:Decimal
    marza: Decimal
    start:dt.datetime
    operacje:Optional[list[Zdarzenie]] = None


    def __post_init__(self):
        self.dzien_odsetki: dt.datetime = self.start
        self.I = 0
        self.odsetki_naliczone = 0

    def zmien_oprocentowanie(self, dzien_zmiany:dt.datetime, nowe_r:Decimal):


        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_zmiany.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p


        self.odsetki_naliczone = self.odsetki_naliczone +  opr*self.K

        self.p = Decimal((nowe_r*0.01))+self.marza

        self.dzien_odsetki = dzien_zmiany


    def splata_raty(self, dzien_raty:dt.datetime):


        o_d = Odleglosc(self.dzien_odsetki.strftime('%Y-%m-%d'), dzien_raty.strftime('%Y-%m-%d'), 'a')

        opr = o_d.mnoznik*self.p

        if self.K > 0:
            self.I = self.oblicz_rate().quantize(grosze, ROUND_HALF_UP)
        else:
            self.I = Decimal(0).quantize(grosze, ROUND_HALF_UP)

        self.odsetki_naliczone = (self.odsetki_naliczone + opr*self.K).quantize(grosze, ROUND_HALF_UP)
    
        if self.odsetki_naliczone > self.I:
            self.I = self.odsetki_naliczone

        #ostatnia rata
        if self.N == 1:
            roznica_na_koniec = self.K - (self.I-self.odsetki_naliczone)
            self.I += roznica_na_koniec

    
        self.K = self.K - (self.I-self.odsetki_naliczone)


        self.odsetki_naliczone = 0
  

        self.dzien_odsetki = dzien_raty
        self.N -= 1


    def next(self, data:dt.datetime, rata_porownawcza:Decimal):

        # sprawdz czy pomiędzy ostatnią spłatą a datą jest zmiana oprocentowania
        # jeśli tak to zmień oprocentowanie

        if self.N > 0 and self.K > 0:

            if self.operacje:
                for zdarzenie in self.operacje:
                    if zdarzenie.data > self.dzien_odsetki and zdarzenie.data <= data:
                        if zdarzenie.rodzaj == Rodzaj.OPROCENTOWANIE:
                            self.zmien_oprocentowanie(zdarzenie.data, zdarzenie.wartosc)

            self.splata_raty(data)

            nadplata = 0
            if self.I < rata_porownawcza:
                nadplata = rata_porownawcza - self.I
                self.K = self.K - nadplata

        return self.K
          
    def oblicz_rate(self) -> Decimal:  


        k = 12
        do_splaty = self.K
        liczba_rat = self.N 
        if self.p>0:
            L = (do_splaty * self.p)
            M = k*(1-pow(k/(k+self.p),liczba_rat) )
            I =L/M
        else: 
            I = do_splaty/liczba_rat


        return I




def create_kredyt(dane:list[dict[str, Any]], rodzajRat:str):

    # print(dane)


    r = Decimal(dane['r']/100.0)
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


    kr = Kredyt(K, N, r, marza, start_kredytu, rodzajRat, False, zdarzenia)



    return kr




if __name__== "__main__":
    pass
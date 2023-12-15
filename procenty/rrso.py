
from dataclasses import dataclass
import datetime as dt
from dateutil.relativedelta import relativedelta

@dataclass
class RRSO:
    wyplata: float
    raty: list
    rrso_0: float


    def right_side(self, rrso):

        R = 0
        for i,r in enumerate(self.raty):
            R += float(r['rata'])/((1+rrso)**((i+1)/12))
        return R
    

    
    def oblicz_rrso(self):
        rrso = self.rrso_0
        l_granica = 0
        r_granica = 10

        
        rs = self.right_side(rrso)

        i = 0

        while abs(self.wyplata-rs)>0.0001:
            
            if self.wyplata>rs:
                r_granica = rrso
            else:
                l_granica = rrso

            rrso = (l_granica+r_granica)/2

            
            rs = self.right_side(rrso)
            i+=1
            if i > 1000:
                raise Exception('Za dużo iteracji')

        print(f'iteracje: {i}')
        return rrso
    


def rata_rowna(kwota, okresy, i):
    rata = kwota * (i/12) / (1 - (1 + i/12)**(-okresy))
    return rata

def oblicz_rate(K,k,N,p): 



    L = (K * p)
    M = k*(1-pow(k/(k+p),N) )
    I =L/M

    return I

def sprawdz_rate(K,k,N,p,R):
    K = K
    for i in range(N):
        K -= R-K*(p/k)
    return K

def liczba_dni_w_roku(rok):
    if rok % 4 == 0:
        dni_rok = 366
    else:
        dni_rok = 365
    
    return dni_rok

def mpkk(K, N, data_start):
    # 28.12.2020 - 04.01.2021
    # 29,30,31,1,2,3,4
    # 3 + 4 = 7


    data_koniec = data_start + relativedelta(months=N)

    # get year out of data_start
    rok_start = data_start.year
    rok_koniec = data_koniec.year

    if rok_start == rok_koniec:
        dni_rok = liczba_dni_w_roku(rok_start)
        dni = (data_koniec - data_start).days
        print(f"ile dni {dni}")
        mpkk = K * 0.1 + K * dni/dni_rok * 0.1
    else:
        wspolczynnik = 0
        for rok in range(rok_start, rok_koniec+1):
            # sprawdz czy rok startowy jest przestepny
            if rok == rok_start:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (dt.datetime(rok,12,31) - data_start).days
                wspolczynnik = dni/dni_rok
            elif rok == rok_koniec:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (data_koniec - dt.datetime(rok-1,12,31)).days
                wspolczynnik += dni/dni_rok
            else:
                wspolczynnik += 1

        mpkk = K * 0.1 + K * wspolczynnik * 0.1

    return mpkk
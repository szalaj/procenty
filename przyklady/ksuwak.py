import procenty.suwak as sw 
import procenty.kredyt as pr
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta




if __name__ == "__main__":

    K = Decimal(400000)
    N = 420
    p1 = Decimal(0.076)
    p2 = Decimal(0.066)
    marza = Decimal(0.04)
    start = datetime(2021, 10, 1)
    rodzaj = 'rowne'

    datetimes = [datetime(2021, 11, 1) + relativedelta(months=i) for i in range(420)]

    # Kap = sw.Zloty(K)
    # Kap2 = sw.Zloty(2*K)

    # print(Kap2 > 0)
    print('Kredyt')
    k = pr.Kredyt(K, N, p1, marza, start, rodzaj)

    k2 = sw.KredytSuwak(k,p2)

    for dzien_splaty in datetimes:
        k.zdarzenia.append(pr.Zdarzenie(dzien_splaty, sw.Rodzaj.SPLATA, 0))
    
    k2.zdarzenia.extend(k.kopiuj_zdarzenia_splaty())

    wynik = k.symuluj()


    wynik2 = k2.symuluj(wynik['raty'])

    if wynik == wynik2:
        print("Wyniki są takie same")


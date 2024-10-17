import procenty.suwak as sw 
import procenty.proc as pr
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta




if __name__ == "__main__":

    K = Decimal(400000)
    N = 420
    p = Decimal(0.076)
    marza = Decimal(0.04)
    start = datetime(2021, 10, 1)
    rodzaj = 'rowne'

    datetimes = [datetime(2021, 11, 1) + relativedelta(months=i) for i in range(420)]

    k = sw.Kredyt(K, N, p, marza, start, rodzaj)
    k2 = pr.Kredyt(K, N, p, marza, start, rodzaj)

    for dzien_splaty in datetimes:
        k.zdarzenia.append(sw.Zdarzenie(dzien_splaty, sw.Rodzaj.SPLATA, 0))
        k2.zdarzenia.append(pr.Zdarzenie(dzien_splaty, pr.Rodzaj.SPLATA, 0))

    wynik = k.symuluj()
    wynik2 = k2.symuluj()

    if wynik == wynik2:
        print("Wyniki są takie same")


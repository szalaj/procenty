from datetime import datetime
from decimal import Decimal

import numpy as np
from dateutil.relativedelta import relativedelta
from scipy.optimize import fsolve

from procenty.kredyt import Kredyt, Rodzaj, Zdarzenie
from procenty.stopy import Krzywa

k = 1.8
beta = 1000
M = 1
Pc = 2
alfa = 0.5
omega = 4
A = 10


def rownaniestanu(vars):
    Y, r = vars
    eq1 = r - (k / beta) * Y + (1 / beta) * (M / Pc)
    eq2 = r + (1 / (alfa * omega)) * Y - A / omega
    return [eq1, eq2]


def oblicz():
    Y_eq, r_eq = fsolve(rownaniestanu, [3, 5])
    return Y_eq, r_eq


def sym1():

    start_p = datetime.strptime("2021-10-13", "%Y-%m-%d")
    lista_r = []
    for i in range(1, 500):
        Pc = i / 2.0
        kol = start_p + relativedelta(months=(i))
        Y, r = oblicz()
        lista_r.append((kol, r))

    kr = Krzywa(lista_r)

    # print(kr)

    K = Decimal(400000)
    N = 300
    p1 = Decimal(0.02)
    p2 = p1 * 2
    marza = Decimal(0.1)
    start = datetime(2021, 10, 13)
    rodzaj = "rowne"

    oprocentowania = [
        Zdarzenie(d[0], Rodzaj.OPROCENTOWANIE, d[1]) for d in kr.podzial(30)
    ]
    zdarzenia = []
    zdarzenia.extend(oprocentowania)

    k4 = Kredyt(K, N, p1, marza, start, rodzaj, True, zdarzenia)
    print(k4.podsumowanie)
    return k4.podsumowanie


if __name__ == "__main__":
    sym1()
    # Y, r = oblicz()
    # print(f"Y_eq: {Y}, r_eq: {r}")
    # print(f"Równanie stanu: {rownaniestanu([Y, r])}")

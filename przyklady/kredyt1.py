from datetime import datetime
from decimal import Decimal

from procenty.kredyt import Kredyt, KredytPorownanie, KredytSuwak, Rodzaj, Zdarzenie
from procenty.utils.create_kredyt import create_kredyt, create_kredyt_normalny

if __name__ == "__main__":

    K = Decimal(400000)
    N = 420
    p1 = Decimal(0.076)
    p2 = Decimal(0.026)
    marza = Decimal(0.04)
    start = datetime(2021, 10, 13)
    rodzaj = "rowne"

    print("--------------------------Kredyty-----------------------")

    zdarzenia = [
        Zdarzenie(
            datetime.strptime("2021-12-12", "%Y-%m-%d"), Rodzaj.NADPLATA, Decimal(40000)
        ),
        Zdarzenie(
            datetime.strptime("2024-12-12", "%Y-%m-%d"),
            Rodzaj.OPROCENTOWANIE,
            float(0.2),
        ),
        # Zdarzenie(datetime.strptime('2025-12-12', '%Y-%m-%d'), Rodzaj.SPLATA_CALKOWITA, float(0.2))
    ]

    k1 = Kredyt(K, N, p1, marza, start, rodzaj, True, zdarzenia)
    k2 = KredytPorownanie(k1, p2)

    dane: dict = {
        "daty_splaty": ["2021-11-13", "2021-12-13", "2022-01-13"],
        "K": 3000,
        "N": 3,
        "r": 12,
        "marza": 4,
        "start": "2021-10-13",
    }

    k3 = create_kredyt(dane, "rowne")

    dane_normalny: dict = {
        "K": 3000,
        "N": 3,
        "r": 12,
        "marza": 4,
        "start": "2021-10-13",
    }

    k3n = create_kredyt_normalny(dane_normalny, "rowne")

    k1s = KredytSuwak(K, N, p1, marza, start, zdarzenia)

    for i, zd in enumerate(k1.podsumowanie["raty"]):

        # print(zd)
        data_raty = datetime.strptime(zd["dzien"], "%Y-%m-%d")
        kwota_raty = Decimal(zd["rata"])
        kl = k1s.next(data_raty, kwota_raty)
        # print(f"{i}: Kolejna kwota: {kl}")

    # for i,zd in enumerate(k1.zdarzenia):
    #     if zd.rodzaj == Rodzaj.SPLATA:
    #         # print(zd.data)
    #         # print(type(zd.data))
    #         kl = k1s.next(zd.data,4000)
    #         if kl>0:
    #             print(f"{i}: Kolejna kwota: {kl}")

    print(f"XIRR1: {k1.xirr}, XIRR2: {k2.xirr}, XIRR3: {k3.xirr}")
    print(k3n.podsumowanie)

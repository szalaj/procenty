import datetime as dt
from decimal import Decimal
from typing import Any

from ..kredyt import Kredyt, Rodzaj, Zdarzenie


def create_kredyt(dane: list[dict[str, Any]], rodzajRat: str):

    r = Decimal(dane["r"] / 100.0)
    marza = Decimal(dane["marza"] / 100.0)
    K = Decimal(dane["K"])
    dni = dane["daty_splaty"]
    N = len(dni)
    start_kredytu = dt.datetime.strptime(dane["start"], "%Y-%m-%d")

    zdarzenia = []

    for dzien_splaty in dane["daty_splaty"]:
        zdarzenia.append(
            Zdarzenie(dt.datetime.strptime(dzien_splaty, "%Y-%m-%d"), Rodzaj.SPLATA, 0)
        )

    if "oprocentowanie" in dane:
        for zmiana_opr in dane["oprocentowanie"]:
            zdarzenia.append(
                Zdarzenie(
                    dt.datetime.strptime(zmiana_opr["dzien"], "%Y-%m-%d"),
                    Rodzaj.OPROCENTOWANIE,
                    zmiana_opr["proc"],
                )
            )

    if "nadplaty" in dane:
        for nadplata in dane["nadplaty"]:
            if nadplata["calkowita"] == True:
                zdarzenia.append(
                    Zdarzenie(
                        dt.datetime.strptime(nadplata["dzien"], "%Y-%m-%d"),
                        Rodzaj.SPLATA_CALKOWITA,
                        Decimal(nadplata["kwota"]),
                    )
                )
            else:
                zdarzenia.append(
                    Zdarzenie(
                        dt.datetime.strptime(nadplata["dzien"], "%Y-%m-%d"),
                        Rodzaj.NADPLATA,
                        Decimal(nadplata["kwota"]),
                    )
                )

    if "transze" in dane:
        for transza in dane["transze"]:
            zdarzenia.append(
                Zdarzenie(
                    dt.datetime.strptime(transza["dzien"], "%Y-%m-%d"),
                    Rodzaj.TRANSZA,
                    Decimal(transza["kapital"]),
                )
            )

    kr = Kredyt(K, N, r, marza, start_kredytu, rodzajRat, False, zdarzenia)

    return kr

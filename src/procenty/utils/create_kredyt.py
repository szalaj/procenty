import datetime as dt
from decimal import Decimal
from typing import Any

from ..kredyt import Kredyt, Rodzaj, Zdarzenie


def create_kredyt(dane: dict[str, Any], rodzajRat: str) -> "Kredyt":
    """Buduje Kredyt z harmonogramem i zdarzeniami ze slownika `dane`.

    Konwencja: `r` i `marza` w PROCENTACH (np. 7.6); kwoty w zlotowkach.
    Konwersja %->ulamek dzieje sie tutaj, na granicy; klasa Kredyt operuje
    juz na ulamku (r=0.076).
    """
    # Decimal(str(...)) zamiast Decimal(float) eliminuje szum reprezentacji floata.
    r = Decimal(str(dane["r"])) / Decimal(100)
    marza = Decimal(str(dane["marza"])) / Decimal(100)
    K = Decimal(str(dane["K"]))
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
            if nadplata["calkowita"] is True:
                zdarzenia.append(
                    Zdarzenie(
                        dt.datetime.strptime(nadplata["dzien"], "%Y-%m-%d"),
                        Rodzaj.SPLATA_CALKOWITA,
                        Decimal(str(nadplata["kwota"])),
                    )
                )
            else:
                zdarzenia.append(
                    Zdarzenie(
                        dt.datetime.strptime(nadplata["dzien"], "%Y-%m-%d"),
                        Rodzaj.NADPLATA,
                        Decimal(str(nadplata["kwota"])),
                    )
                )

    if "transze" in dane:
        for transza in dane["transze"]:
            zdarzenia.append(
                Zdarzenie(
                    dt.datetime.strptime(transza["dzien"], "%Y-%m-%d"),
                    Rodzaj.TRANSZA,
                    Decimal(str(transza["kapital"])),
                )
            )

    kr = Kredyt(K, N, r, marza, start_kredytu, rodzajRat, False, zdarzenia)

    return kr


def create_kredyt_normalny(dane: dict[str, Any], rodzajRat: str) -> "Kredyt":

    # Wejscie r/marza jest w PROCENTACH (np. 7.6); klasa Kredyt oczekuje ulamka
    # (0.076). Decimal(str(...)) zamiast Decimal(float) eliminuje szum floata.
    r = Decimal(str(dane["r"])) / Decimal(100)
    marza = Decimal(str(dane["marza"])) / Decimal(100)
    K = Decimal(str(dane["K"]))
    N = dane["N"]
    start_kredytu = dt.datetime.strptime(dane["start"], "%Y-%m-%d")

    kr = Kredyt(K, N, r, marza, start_kredytu, rodzajRat, True, [])

    return kr

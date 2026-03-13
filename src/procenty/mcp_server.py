"""Serwer MCP dla biblioteki procenty - obliczenia finansowe."""

import datetime as dt
from decimal import Decimal
from typing import Optional

from mcp.server.fastmcp import FastMCP

from procenty.inwestycja import Lokata, mpkk, npv, xirr, xnpv
from procenty.kredyt import Kredyt, Rodzaj, Zdarzenie
from procenty.miary import LiczbaDni

mcp_server = FastMCP(
    "procenty",
    instructions="Obliczenia finansowe: kredyty hipoteczne, lokaty, XIRR, RRSO, MPKK",
)


@mcp_server.tool()
def oblicz_kredyt(
    kwota: float,
    liczba_rat: int,
    stopa_bazowa: float,
    marza: float,
    data_start: str,
    rodzaj_rat: str = "rowne",
    pokaz_raty: bool = False,
) -> dict:
    """Symulacja kredytu hipotecznego.

    Args:
        kwota: Kwota kredytu w PLN (np. 400000)
        liczba_rat: Liczba rat (np. 360 = 30 lat)
        stopa_bazowa: Bazowa stopa procentowa (np. 0.076)
        marza: Marża banku (np. 0.04)
        data_start: Data uruchomienia kredytu w formacie YYYY-MM-DD
        rodzaj_rat: Rodzaj rat - "rowne", "malejace" lub "malejace_met2"
        pokaz_raty: Czy zwrócić pełny harmonogram rat (domyślnie False - tylko podsumowanie)
    """
    kredyt = Kredyt(
        K=Decimal(str(kwota)),
        N=liczba_rat,
        r=Decimal(str(stopa_bazowa)),
        marza=Decimal(str(marza)),
        start=dt.datetime.strptime(data_start, "%Y-%m-%d"),
        rodzajRat=rodzaj_rat,
    )

    podsumowanie = kredyt.podsumowanie

    if pokaz_raty:
        return podsumowanie
    else:
        return podsumowanie["info"]


@mcp_server.tool()
def oblicz_lokate(
    kwota: float,
    oprocentowanie: float,
    czas_miesiace: int,
    kapitalizacja: int = 12,
) -> dict:
    """Oblicza przyszłą wartość lokaty bankowej.

    Args:
        kwota: Kwota lokaty w PLN
        oprocentowanie: Oprocentowanie roczne (np. 0.045 = 4.5%)
        czas_miesiace: Czas lokaty w miesiącach
        kapitalizacja: Liczba kapitalizacji w roku (1=roczna, 4=kwartalna, 12=miesięczna)
    """
    lokata = Lokata(
        kwota=kwota,
        oprocentowanie=oprocentowanie,
        czas=czas_miesiace,
        kapitalizacja=kapitalizacja,
    )
    return {
        "przyszla_wartosc": round(lokata.przyszla_wartosc(), 2),
        "zysk": round(lokata.oblicz_zysk(), 2),
        "kwota": kwota,
        "oprocentowanie": oprocentowanie,
        "czas_miesiace": czas_miesiace,
    }


@mcp_server.tool()
def oblicz_xirr(przeplywy: list[dict]) -> dict:
    """Oblicza XIRR (wewnętrzną stopę zwrotu) dla nieregularnych przepływów pieniężnych.

    Args:
        przeplywy: Lista przepływów, każdy to dict z polami:
            - data: Data w formacie YYYY-MM-DD
            - kwota: Kwota (ujemna = inwestycja, dodatnia = zwrot)
    """
    cashflows = [
        (dt.datetime.strptime(p["data"], "%Y-%m-%d"), float(p["kwota"]))
        for p in przeplywy
    ]
    wynik = float(xirr(cashflows))
    return {"xirr": round(wynik, 6), "xirr_procent": round(wynik * 100, 4)}


@mcp_server.tool()
def oblicz_xnpv(stopa: float, przeplywy: list[dict]) -> dict:
    """Oblicza XNPV (wartość bieżącą netto) dla nieregularnych przepływów pieniężnych.

    Args:
        stopa: Stopa dyskontowa (np. 0.05 = 5%)
        przeplywy: Lista przepływów, każdy to dict z polami:
            - data: Data w formacie YYYY-MM-DD
            - kwota: Kwota (ujemna = inwestycja, dodatnia = zwrot)
    """
    cashflows = [
        (dt.datetime.strptime(p["data"], "%Y-%m-%d"), float(p["kwota"]))
        for p in przeplywy
    ]
    wynik = float(xnpv(stopa, cashflows))
    return {"xnpv": round(wynik, 2), "stopa": stopa}


@mcp_server.tool()
def oblicz_npv(stopa: float, przeplywy: list[float]) -> dict:
    """Oblicza NPV (wartość bieżącą netto) dla regularnych przepływów pieniężnych.

    Args:
        stopa: Stopa dyskontowa (np. 0.05 = 5%)
        przeplywy: Lista kwot (pierwsza to zazwyczaj ujemna inwestycja, kolejne to zwroty)
    """
    wynik = npv(stopa, przeplywy)
    return {"npv": round(wynik, 2), "stopa": stopa}


@mcp_server.tool()
def oblicz_mpkk(kwota: float, okres_miesiace: int, data_start: str) -> dict:
    """Oblicza MPKK - Maksymalny Pozaodsetkowy Koszt Kredytu.

    Args:
        kwota: Kwota kredytu w PLN
        okres_miesiace: Okres kredytu w miesiącach
        data_start: Data rozpoczęcia kredytu w formacie YYYY-MM-DD
    """
    wynik = mpkk(
        K=kwota,
        N=okres_miesiace,
        data_start=dt.datetime.strptime(data_start, "%Y-%m-%d"),
    )
    return {"mpkk": round(wynik, 2), "kwota": kwota, "okres_miesiace": okres_miesiace}


@mcp_server.tool()
def oblicz_dni_odsetkowe(data_start: str, data_koniec: str) -> dict:
    """Oblicza liczbę dni odsetkowych i mnożnik odsetkowy między dwoma datami.

    Uwzględnia lata przestępne zgodnie z regułą kalendarza gregoriańskiego.

    Args:
        data_start: Data początkowa w formacie YYYY-MM-DD
        data_koniec: Data końcowa w formacie YYYY-MM-DD
    """
    ld = LiczbaDni(start=data_start, koniec=data_koniec)
    return {
        "dni_odsetkowe": ld.dni_odsetkowe,
        "mnoznik": round(float(ld.mnoznik), 8),
    }


if __name__ == "__main__":
    mcp_server.run()

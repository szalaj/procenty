"""Moduł do obliczeń inwestycyjnych: lokaty, XIRR, XNPV, IRR, RRSO, MPKK."""

import datetime as dt
from dataclasses import dataclass
from typing import Any

from dateutil.relativedelta import relativedelta
from scipy import optimize

from procenty.utils import liczba_dni_w_roku


@dataclass
class Lokata:
    """Klasa do obsługi lokat bankowych.

    Argumenty:
        kwota: kwota lokaty
        oprocentowanie: oprocentowanie lokaty (np. 0.05 dla 5%)
        czas: czas lokaty w miesiącach
        kapitalizacja: liczba kapitalizacji w roku (np. 1 - roczna, 12 - miesięczna)
    """

    kwota: float
    oprocentowanie: float
    czas: int
    kapitalizacja: int

    def __post_init__(self) -> None:
        if self.kwota < 0:
            raise ValueError("Kwota lokaty nie może być ujemna")
        if self.czas <= 0:
            raise ValueError("Czas lokaty musi być dodatni")
        if self.kapitalizacja <= 0:
            raise ValueError("Kapitalizacja musi być dodatnia")

        liczba_okresow = self.czas / (12 / self.kapitalizacja)
        stopa_okresowa = self.oprocentowanie / self.kapitalizacja
        self._przyszla_wartosc = self.kwota * (1 + stopa_okresowa) ** liczba_okresow

    def oblicz_zysk(self) -> float:
        """Zwraca zysk z lokaty (przyszła wartość - kwota początkowa)."""
        return self._przyszla_wartosc - self.kwota

    def przyszla_wartosc(self) -> float:
        """Zwraca przyszłą wartość lokaty."""
        return self._przyszla_wartosc


def npv(rate: float, cash_flows: list[float]) -> float:
    """Oblicza wartość bieżącą netto (NPV) dla regularnych przepływów pieniężnych."""
    return sum([cf / (1 + rate) ** i for i, cf in enumerate(cash_flows)])


def irr(cash_flows: list[float]) -> float:
    """Oblicza wewnętrzną stopę zwrotu (IRR) dla regularnych przepływów pieniężnych."""
    if not cash_flows:
        raise ValueError("Lista przepływów pieniężnych nie może być pusta")
    return optimize.brentq(lambda r: npv(r, cash_flows), -0.99, 10.0)


@dataclass
class Inwestycja:
    """Prosta inwestycja z oprocentowaniem."""

    kwota: float
    czas_start: int
    czas_trwania: int

    def zysk(
        self, oprocentowanie: float, czas_oprocentowania: int, aktualny_czas: int
    ) -> float:
        """Oblicza zysk z inwestycji w danym momencie."""
        if aktualny_czas <= self.czas_start + self.czas_trwania:
            return self.kwota * (oprocentowanie / 100) * (czas_oprocentowania / 12)
        else:
            return 0.0


def secant_method(tol: float, f: Any, x0: float) -> float:
    """
    Rozwiązuje f(x)=0 metodą siecznych.

    Argumenty:
        tol: tolerancja jako procent wyniku końcowego
        f: funkcja jednej zmiennej
        x0: wartość początkowa x
    """
    x1 = x0 * 1.1
    while abs(x1 - x0) / abs(x1) > tol:
        x0, x1 = x1, x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    return x1


def xnpv(rate: float, cashflows: list[tuple[dt.datetime, float]]) -> float:
    """
    Oblicza wartość bieżącą netto (NPV) dla nieregularnych przepływów pieniężnych.

    Argumenty:
        rate: stopa dyskontowa
        cashflows: lista krotek (data, kwota). Ujemne kwoty = inwestycje, dodatnie = zwroty.

    Zwraca:
        Wartość NPV.
    """
    chron_order = sorted(cashflows, key=lambda x: x[0])
    t0 = chron_order[0][0]

    return sum([cf / (1 + rate) ** ((t - t0).days / 365.0) for (t, cf) in chron_order])


def xirr(cashflows: list[tuple[dt.datetime, float]], guess: float = 0.1) -> float:
    """
    Oblicza wewnętrzną stopę zwrotu (IRR) dla nieregularnych przepływów pieniężnych.

    Argumenty:
        cashflows: lista krotek (data, kwota)
        guess: wartość początkowa do optymalizacji (domyślnie 0.1)

    Zwraca:
        Wewnętrzna stopa zwrotu (IRR).
    """
    return optimize.newton(lambda r: xnpv(r, cashflows), guess)


@dataclass
class RRSO:
    """Oblicza Rzeczywistą Roczną Stopę Oprocentowania."""

    wyplata: float
    raty: list[dict[str, Any]]
    rrso_0: float

    def right_side(self, rrso: float) -> float:
        """Oblicza prawą stronę równania RRSO."""
        R = 0.0
        for i, r in enumerate(self.raty):
            R += float(r["rata"]) / ((1 + rrso) ** ((i + 1) / 12))
        return R

    def oblicz_rrso(self) -> float:
        """Oblicza RRSO metodą bisekcji."""
        rrso = self.rrso_0
        l_granica = 0.0
        r_granica = 10.0

        rs = self.right_side(rrso)

        i = 0

        while abs(self.wyplata - rs) > 0.0001:
            if self.wyplata > rs:
                r_granica = rrso
            else:
                l_granica = rrso

            rrso = (l_granica + r_granica) / 2

            rs = self.right_side(rrso)

            i += 1
            if i > 1000:
                raise RuntimeError(
                    "RRSO: brak zbieżności po 1000 iteracjach"
                )

        return rrso


def mpkk(K: float, N: int, data_start: dt.datetime) -> float:
    """Oblicza Maksymalny Pozaodsetkowy Koszt Kredytu.

    Argumenty:
        K: kwota kredytu
        N: okres kredytu w miesiącach
        data_start: data rozpoczęcia kredytu
    """
    if K <= 0:
        raise ValueError("Kwota kredytu musi być dodatnia")
    if N <= 0:
        raise ValueError("Okres kredytu musi być dodatni")

    data_koniec = data_start + relativedelta(months=N)

    rok_start = data_start.year
    rok_koniec = data_koniec.year

    if rok_start == rok_koniec:
        dni_rok = liczba_dni_w_roku(rok_start)
        dni = (data_koniec - data_start).days
        result = K * 0.1 + K * dni / dni_rok * 0.1
    else:
        wspolczynnik = 0.0
        for rok in range(rok_start, rok_koniec + 1):
            if rok == rok_start:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (dt.datetime(rok, 12, 31) - data_start).days
                wspolczynnik = dni / dni_rok
            elif rok == rok_koniec:
                dni_rok = liczba_dni_w_roku(rok)
                dni = (data_koniec - dt.datetime(rok - 1, 12, 31)).days
                wspolczynnik += dni / dni_rok
            else:
                wspolczynnik += 1

        result = K * 0.1 + K * wspolczynnik * 0.1

    return result

"""Testy modułu inwestycja."""

import datetime as dt
from decimal import Decimal

import pytest

from procenty.inwestycja import RRSO, Inwestycja, Lokata, irr, mpkk, npv, xirr, xnpv


class TestLokata:
    """Testy klasy Lokata."""

    def test_lokata_roczna(self):
        """Lokata 10000 PLN, 5%, 12 miesięcy, kapitalizacja roczna."""
        l = Lokata(kwota=10000, oprocentowanie=0.05, czas=12, kapitalizacja=1)
        assert abs(l.przyszla_wartosc() - 10500.0) < 0.01

    def test_lokata_miesieczna(self):
        """Lokata z kapitalizacją miesięczną daje więcej niż roczna."""
        l_roczna = Lokata(kwota=10000, oprocentowanie=0.05, czas=12, kapitalizacja=1)
        l_miesieczna = Lokata(
            kwota=10000, oprocentowanie=0.05, czas=12, kapitalizacja=12
        )
        assert l_miesieczna.przyszla_wartosc() > l_roczna.przyszla_wartosc()

    def test_lokata_zysk_dodatni(self):
        l = Lokata(kwota=10000, oprocentowanie=0.05, czas=12, kapitalizacja=1)
        assert l.oblicz_zysk() > 0

    def test_lokata_zero_oprocentowanie(self):
        l = Lokata(kwota=10000, oprocentowanie=0.0, czas=12, kapitalizacja=1)
        assert l.przyszla_wartosc() == 10000.0
        assert l.oblicz_zysk() == 0.0

    def test_lokata_krotki_okres(self):
        """Lokata 3 miesiące."""
        l = Lokata(kwota=10000, oprocentowanie=0.04, czas=3, kapitalizacja=4)
        assert l.przyszla_wartosc() > 10000
        assert l.przyszla_wartosc() < 10500  # Mniej niż przy pełnym roku


class TestInwestycja:
    """Testy klasy Inwestycja."""

    def test_zysk_w_okresie(self):
        inv = Inwestycja(kwota=10000, czas_start=0, czas_trwania=12)
        zysk = inv.zysk(oprocentowanie=5.0, czas_oprocentowania=12, aktualny_czas=6)
        assert zysk > 0

    def test_zysk_po_okresie(self):
        inv = Inwestycja(kwota=10000, czas_start=0, czas_trwania=12)
        zysk = inv.zysk(oprocentowanie=5.0, czas_oprocentowania=12, aktualny_czas=15)
        assert zysk == 0.0


class TestXIRR:
    """Testy funkcji XIRR i XNPV."""

    def test_xirr_prosty(self):
        """Prosty przypadek: inwestycja -1000 i zwrot +1100 po roku."""
        cashflows = [
            (dt.datetime(2021, 1, 1), -1000),
            (dt.datetime(2022, 1, 1), 1100),
        ]
        result = xirr(cashflows)
        assert abs(result - 0.10) < 0.01  # ~10%

    def test_xnpv_zerowa_stopa(self):
        """Przy stopie 0, NPV = suma przepływów."""
        cashflows = [
            (dt.datetime(2021, 1, 1), -1000),
            (dt.datetime(2022, 1, 1), 1100),
        ]
        result = xnpv(0, cashflows)
        assert abs(result - 100) < 0.01

    def test_xnpv_dodatnia_stopa(self):
        """Przy dodatniej stopie dyskontowej, NPV < suma."""
        cashflows = [
            (dt.datetime(2021, 1, 1), -1000),
            (dt.datetime(2022, 1, 1), 1100),
        ]
        npv_zero = xnpv(0, cashflows)
        npv_positive = xnpv(0.1, cashflows)
        assert npv_positive < npv_zero


class TestNPV:
    """Testy funkcji NPV."""

    def test_npv_zerowa_stopa(self):
        result = npv(0, [-1000, 500, 600])
        assert abs(result - 100) < 0.01

    def test_npv_ujemna(self):
        """Przy wysokiej stopie, NPV inwestycji z małym zwrotem jest ujemna."""
        result = npv(1.0, [-1000, 500, 200])
        assert result < 0


class TestRRSO:
    """Testy klasy RRSO."""

    def test_rrso_prosty(self):
        """RRSO dla prostego kredytu."""
        raty = [{"rata": "100"} for _ in range(12)]
        rrso = RRSO(wyplata=1100, raty=raty, rrso_0=0.1)
        wynik = rrso.oblicz_rrso()
        assert wynik > 0
        assert wynik < 1  # Rozsądny zakres

    def test_rrso_za_duzo_iteracji(self):
        """RRSO rzuca wyjątek przy zbyt wielu iteracjach."""
        raty = [{"rata": "1"} for _ in range(12)]
        rrso = RRSO(wyplata=1000000, raty=raty, rrso_0=0.1)
        with pytest.raises(RuntimeError, match="brak zbieżności"):
            rrso.oblicz_rrso()


class TestMPKK:
    """Testy funkcji MPKK."""

    def test_mpkk_ten_sam_rok(self):
        """MPKK gdy start i koniec w tym samym roku."""
        result = mpkk(10000, 6, dt.datetime(2021, 1, 1))
        assert result > 0

    def test_mpkk_rozne_lata(self):
        """MPKK gdy start i koniec w różnych latach."""
        result = mpkk(10000, 18, dt.datetime(2021, 6, 1))
        assert result > 0

    def test_mpkk_dlugi_okres(self):
        """MPKK dla dłuższego okresu powinien być większy."""
        mpkk_krotki = mpkk(10000, 6, dt.datetime(2021, 1, 1))
        mpkk_dlugi = mpkk(10000, 24, dt.datetime(2021, 1, 1))
        assert mpkk_dlugi > mpkk_krotki

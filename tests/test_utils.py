"""Testy modułu utils — liczba_dni_w_roku, diff_month, create_kredyt."""

import datetime as dt
from decimal import Decimal

import pytest

from procenty.miary import LiczbaDni, Zloty
from procenty.utils.inne import diff_month, liczba_dni_w_roku

# --- Testy liczba_dni_w_roku ---


class TestLiczbaDniWRoku:
    def test_rok_normalny(self):
        assert liczba_dni_w_roku(2023) == 365

    def test_rok_przestepny(self):
        assert liczba_dni_w_roku(2024) == 366

    def test_rok_podzielny_100_nie_przestepny(self):
        """Rok 2100 NIE jest przestępny (podzielny przez 100 ale nie przez 400)."""
        assert liczba_dni_w_roku(2100) == 365

    def test_rok_podzielny_400_przestepny(self):
        """Rok 2000 JEST przestępny (podzielny przez 400)."""
        assert liczba_dni_w_roku(2000) == 366

    def test_rok_1900_nie_przestepny(self):
        assert liczba_dni_w_roku(1900) == 365

    def test_rok_2400_przestepny(self):
        assert liczba_dni_w_roku(2400) == 366


# --- Testy diff_month ---


class TestDiffMonth:
    def test_ten_sam_miesiac(self):
        d1 = dt.datetime(2021, 5, 15)
        d2 = dt.datetime(2021, 5, 1)
        assert diff_month(d1, d2) == 0

    def test_roznica_6_miesiecy(self):
        d1 = dt.datetime(2021, 12, 1)
        d2 = dt.datetime(2021, 6, 1)
        assert diff_month(d1, d2) == 6

    def test_roznica_miedzy_latami(self):
        d1 = dt.datetime(2023, 3, 1)
        d2 = dt.datetime(2021, 1, 1)
        assert diff_month(d1, d2) == 26

    def test_ujemna_roznica(self):
        d1 = dt.datetime(2021, 1, 1)
        d2 = dt.datetime(2021, 6, 1)
        assert diff_month(d1, d2) == -5


# --- Testy LiczbaDni (rozszerzone) ---


class TestLiczbaDniRozszerzone:
    def test_jeden_dzien(self):
        ld = LiczbaDni("2024-01-01", "2024-01-02")
        assert ld.dni_odsetkowe == 1

    def test_rok_przestepny(self):
        """Cały rok 2024 (przestępny) = 366 dni."""
        ld = LiczbaDni("2024-01-01", "2025-01-01")
        assert ld.dni_odsetkowe == 366

    def test_rok_normalny(self):
        """Cały rok 2023 (normalny) = 365 dni."""
        ld = LiczbaDni("2023-01-01", "2024-01-01")
        assert ld.dni_odsetkowe == 365

    def test_mnoznik_caly_rok_normalny(self):
        ld = LiczbaDni("2023-01-01", "2024-01-01")
        assert abs(float(ld.mnoznik) - 1.0) < 0.001

    def test_mnoznik_caly_rok_przestepny(self):
        ld = LiczbaDni("2024-01-01", "2025-01-01")
        assert abs(float(ld.mnoznik) - 1.0) < 0.001

    def test_mnoznik_pol_roku(self):
        """Pół roku ≈ 0.5."""
        ld = LiczbaDni("2023-01-01", "2023-07-01")
        assert abs(float(ld.mnoznik) - 181 / 365) < 0.01

    def test_kilka_lat(self):
        ld = LiczbaDni("2020-01-01", "2023-01-01")
        assert ld.dni_odsetkowe == 1096  # 366 + 365 + 365

    def test_start_po_koncu_rzuca_blad(self):
        with pytest.raises(Exception, match="start > Dzien koniec"):
            LiczbaDni("2024-01-02", "2024-01-01")

    def test_ten_sam_dzien(self):
        ld = LiczbaDni("2024-01-01", "2024-01-01")
        assert ld.dni_odsetkowe == 0
        assert float(ld.mnoznik) == 0.0


# --- Testy Zloty ---


class TestZloty:
    def test_dodawanie(self):
        assert Zloty(100) + Zloty(50) == Zloty(150)

    def test_odejmowanie(self):
        assert Zloty(100) - Zloty(30) == Zloty(70)

    def test_mnozenie(self):
        assert Zloty(100) * 2 == Zloty(200)

    def test_dzielenie(self):
        assert Zloty(100) / 4 == Zloty(25)

    def test_porownania(self):
        assert Zloty(100) > Zloty(50)
        assert Zloty(50) < Zloty(100)
        assert Zloty(100) >= Zloty(100)
        assert Zloty(100) <= Zloty(100)
        assert Zloty(100) != Zloty(50)

    def test_str(self):
        assert "zł" in str(Zloty(100))

    def test_repr(self):
        assert "zł" in repr(Zloty(100))


# --- Testy create_kredyt ---


class TestCreateKredyt:
    def test_create_kredyt_normalny(self):
        from procenty.utils.create_kredyt import create_kredyt_normalny

        dane = {
            "K": 100000,
            "N": 120,
            "r": 5.0,
            "marza": 2.0,
            "start": "2021-01-01",
        }
        k = create_kredyt_normalny(dane, "rowne")
        assert len(k.raty) == 120

    def test_create_kredyt_z_oprocentowaniem(self):
        from procenty.utils.create_kredyt import create_kredyt

        dane = {
            "K": 100000,
            "r": 5.0,
            "marza": 2.0,
            "start": "2021-01-01",
            "daty_splaty": [
                (
                    dt.datetime(2021, 1, 1)
                    + __import__(
                        "dateutil.relativedelta", fromlist=["relativedelta"]
                    ).relativedelta(months=i + 1)
                ).strftime("%Y-%m-%d")
                for i in range(120)
            ],
            "oprocentowanie": [
                {"dzien": "2022-01-01", "proc": 8.0},
            ],
        }
        k = create_kredyt(dane, "rowne")
        assert len(k.raty) == 120

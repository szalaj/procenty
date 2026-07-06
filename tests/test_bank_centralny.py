"""Testy modułu bank_centralny — emisja, inflacja (MV=PY), reguła Taylora."""

from datetime import datetime

import pytest

from procenty.bank_centralny import BankCentralny
from procenty.konto import Konto

# --- Konstrukcja i walidacja ---


def test_walidacja_parametrow():
    with pytest.raises(ValueError):
        BankCentralny(podaz_pieniadza=-1.0)
    with pytest.raises(ValueError):
        BankCentralny(predkosc_obiegu=0.0)
    with pytest.raises(ValueError):
        BankCentralny(stopa_min=0.5, stopa_max=0.1)


# --- Emisja pieniądza ---


def test_emisja_i_absorpcja_zmienia_podaz():
    bank = BankCentralny(podaz_pieniadza=100.0)
    assert bank.emituj(50.0) == pytest.approx(150.0)
    assert bank.emituj(-30.0) == pytest.approx(120.0)
    assert bank.podaz_pieniadza == pytest.approx(120.0)


def test_absorpcja_ponad_podaz_wyjatek():
    bank = BankCentralny(podaz_pieniadza=100.0)
    with pytest.raises(ValueError):
        bank.emituj(-150.0)


def test_emisja_na_konto_dopisuje_zapis():
    bank = BankCentralny(podaz_pieniadza=0.0)
    konto = Konto("skarb", "PLN")
    teraz = datetime(2024, 1, 1)
    bank.emituj(1000.0, konto=konto, t_symulacji=1, tr_rzeczywisty=teraz)
    assert konto.saldo(1) == pytest.approx(1000.0)
    # absorpcja schodzi z konta (strona Winien)
    bank.emituj(-400.0, konto=konto, t_symulacji=2, tr_rzeczywisty=teraz)
    assert konto.saldo(2) == pytest.approx(600.0)
    assert bank.podaz_pieniadza == pytest.approx(600.0)


def test_emisja_na_konto_bez_czasu_wyjatek():
    bank = BankCentralny()
    konto = Konto("skarb", "PLN")
    with pytest.raises(ValueError):
        bank.emituj(100.0, konto=konto)


# --- Poziom cen i inflacja (ilościowa teoria pieniądza) ---


def test_poziom_cen_rownanie_wymiany():
    bank = BankCentralny(podaz_pieniadza=1000.0, predkosc_obiegu=2.0)
    # P = M * V / Y = 1000 * 2 / 500
    assert bank.poziom_cen(500.0) == pytest.approx(4.0)
    with pytest.raises(ValueError):
        bank.poziom_cen(0.0)


def test_zmierz_inflacje_pierwszy_pomiar_zeruje():
    bank = BankCentralny(podaz_pieniadza=1000.0)
    assert bank.zmierz_inflacje(500.0) == 0.0


def test_dodruk_pieniadza_daje_inflacje_przy_stalej_produkcji():
    bank = BankCentralny(podaz_pieniadza=1000.0)
    bank.zmierz_inflacje(500.0)  # zakotwiczenie
    bank.emituj(100.0)  # +10% podaży
    assert bank.zmierz_inflacje(500.0) == pytest.approx(0.10)


def test_wzrost_produkcji_bez_dodruku_daje_deflacje():
    bank = BankCentralny(podaz_pieniadza=1000.0)
    bank.zmierz_inflacje(500.0)
    # produkcja rośnie o 25% bez zmiany podaży -> ceny spadają
    assert bank.zmierz_inflacje(625.0) == pytest.approx(500.0 / 625.0 - 1.0)


def test_inflacja_ze_stop():
    # sam dodruk 10%, produkcja stała
    assert BankCentralny.inflacja_ze_stop(0.10, 0.0) == pytest.approx(0.10)
    # dodruk 10% i wzrost produkcji 10% znoszą się prawie do zera
    assert BankCentralny.inflacja_ze_stop(0.10, 0.10) == pytest.approx(0.0, abs=1e-9)
    with pytest.raises(ValueError):
        BankCentralny.inflacja_ze_stop(0.0, -1.0)


# --- Reguła Taylora ---


def test_regula_taylora_przy_celu():
    bank = BankCentralny(stopa_neutralna=0.02, cel_inflacji=0.02)
    # inflacja równa celowi, brak luki -> r = r* + π = 0.02 + 0.02
    assert bank.regula_taylora(0.02, 0.0) == pytest.approx(0.04)


def test_regula_taylora_reaguje_mocniej_niz_11_na_inflacje():
    bank = BankCentralny(stopa_neutralna=0.02, cel_inflacji=0.02, wsp_inflacji=0.5)
    # inflacja 0.06 (cel 0.02): r = 0.02 + 0.06 + 0.5*(0.06-0.02) = 0.10
    assert bank.regula_taylora(0.06, 0.0) == pytest.approx(0.10)


def test_ustal_stope_przycina_do_granic():
    bank = BankCentralny(stopa_min=0.0, stopa_max=0.15)
    assert bank.ustal_stope(1.0) == pytest.approx(0.15)  # ogromna inflacja -> sufit
    assert bank.stopa == pytest.approx(0.15)
    assert bank.ustal_stope(-1.0) == pytest.approx(0.0)  # deflacja -> podłoga
    assert bank.stopa == pytest.approx(0.0)


def test_stopa_realna_fishera():
    bank = BankCentralny(stopa=0.05)
    assert bank.stopa_realna(0.03) == pytest.approx(0.02)

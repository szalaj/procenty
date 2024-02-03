import pytest
import yaml
import procenty.rrso
import procenty.miary
import procenty.proc
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP

def test_rr_wieksza_zero():
    """Check if column names in header are uppercase"""
    r = procenty.rrso.rata_rowna(10,1,1)
    assert r > 0


def test_mnoznik_odsetkowy():
    # w tym tescie nie ma lat przestepnych
    dzien_start = '2021-05-10'
    dzien_koniec = '2022-01-12' 
    print(f"--d start {dzien_start}, d koniec {dzien_koniec}")

    o_d = procenty.miary.Odleglosc(dzien_start, dzien_koniec, 'a')
    mnoznik_nowy = o_d.mnoznik

    # nalicz odsetki do dnia zmiany raty
    o_dni = (dt.datetime.strptime(dzien_koniec, '%Y-%m-%d') - dt.datetime.strptime(dzien_start, '%Y-%m-%d')).days
    mnoznik_klasyczny = Decimal(o_dni/365)

    assert abs(mnoznik_nowy - mnoznik_klasyczny) < 10**-6

    # w tym tescie nie ma lat przestepnych, ten sam rok
    dzien_start = '2021-05-10'
    dzien_koniec = '2021-10-12' 
    print(f"--d start {dzien_start}, d koniec {dzien_koniec}")

    o_d = procenty.miary.Odleglosc(dzien_start, dzien_koniec, 'a')
    mnoznik_nowy = o_d.mnoznik

    # nalicz odsetki do dnia zmiany raty
    o_dni = (dt.datetime.strptime(dzien_koniec, '%Y-%m-%d') - dt.datetime.strptime(dzien_start, '%Y-%m-%d')).days
    mnoznik_klasyczny = Decimal(o_dni/365)

    assert abs(mnoznik_nowy - mnoznik_klasyczny) < 10**-6

    # w tym tescie sa lata przestepne
    dzien_start = '2011-05-10'
    dzien_koniec = '2024-01-12' 

    # liczba lat przestepnych pomiedzy datami
    n = 4

    print(f"--d start {dzien_start}, d koniec {dzien_koniec}")

    o_d = procenty.miary.Odleglosc(dzien_start, dzien_koniec, 'a')
    mnoznik_nowy = Decimal(o_d.mnoznik)

    # nalicz odsetki do dnia zmiany raty
    o_dni = (dt.datetime.strptime(dzien_koniec, '%Y-%m-%d') - dt.datetime.strptime(dzien_start, '%Y-%m-%d')).days
    mnoznik_klasyczny = Decimal(o_dni/365)

    assert mnoznik_nowy < mnoznik_klasyczny
    assert abs(mnoznik_nowy - mnoznik_klasyczny) < n*2.74*10**-3 # max roznica (366/365)

def test_rrso_wieksze_zero():
    k = procenty.proc.Kredyt(Decimal(1000), 12, Decimal(0.01), Decimal(0.01), dt.datetime(2020, 12, 11), 'rowne')
    wynik = k.symuluj()

    assert wynik
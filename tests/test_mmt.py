"""Testy modułu mmt: wydatek tworzy pieniądz, podatek umarza, inflacja z
presji fiskalnej, salda sektorowe."""

from datetime import datetime

import pytest

from procenty.konto import Konto
from procenty.mmt import PanstwoMMT

# --- Konstrukcja i walidacja ---


def test_walidacja_parametrow():
    with pytest.raises(ValueError):
        PanstwoMMT(podaz_pieniadza=-1.0)
    with pytest.raises(ValueError):
        PanstwoMMT(poziom_cen=0.0)
    with pytest.raises(ValueError):
        PanstwoMMT(moc_fiskalna=0.0)
    with pytest.raises(ValueError):
        PanstwoMMT(wrazliwosc_inflacji=-0.1)


# --- Wydatek tworzy pieniądz, podatek umarza ---


def test_wydatek_emituje_a_podatek_umarza():
    p = PanstwoMMT(podaz_pieniadza=100.0)
    assert p.wydaj(50.0) == pytest.approx(150.0)
    assert p.opodatkuj(30.0) == pytest.approx(120.0)
    assert p.podaz_pieniadza == pytest.approx(120.0)
    assert p.emisja_okresu == pytest.approx(20.0)
    assert p.deficyt_skumulowany == pytest.approx(20.0)


def test_wydatek_nie_wymaga_pokrycia():
    # MMT: emitent własnej waluty nie ma ograniczenia kasowego.
    p = PanstwoMMT(podaz_pieniadza=0.0)
    assert p.wydaj(1_000_000.0) == pytest.approx(1_000_000.0)


def test_podatek_ponad_obieg_wyjatek():
    p = PanstwoMMT(podaz_pieniadza=100.0)
    with pytest.raises(ValueError):
        p.opodatkuj(150.0)


def test_ujemne_kwoty_wyjatek():
    p = PanstwoMMT(podaz_pieniadza=100.0)
    with pytest.raises(ValueError):
        p.wydaj(-1.0)
    with pytest.raises(ValueError):
        p.opodatkuj(-1.0)


def test_zapisy_na_konto_sektora_niepanstwowego():
    p = PanstwoMMT()
    konto = Konto("gospodarka", "PLN")
    t0 = datetime(2026, 1, 1)
    p.wydaj(100.0, konto=konto, t_symulacji=1, tr_rzeczywisty=t0)
    p.opodatkuj(40.0, konto=konto, t_symulacji=2, tr_rzeczywisty=t0)
    assert konto.saldo(2, tr_obecny=datetime.now()) == pytest.approx(60.0)


def test_zapis_wymaga_t_symulacji():
    p = PanstwoMMT()
    with pytest.raises(ValueError):
        p.wydaj(10.0, konto=Konto("gospodarka", "PLN"))


# --- Inflacja z presji fiskalnej ---


def test_deficyt_w_ramach_przestrzeni_bez_inflacji():
    # Sedno MMT: wolne moce wchłaniają popyt, deficyt do granicy mocy nie
    # podnosi cen.
    p = PanstwoMMT(moc_fiskalna=0.15, wrazliwosc_inflacji=0.3)
    p.wydaj(150.0)  # dokładnie przestrzeń fiskalna przy Y*=1000, P=1
    assert p.zamknij_okres(potencjal_realny=1000.0) == pytest.approx(0.0)
    assert p.poziom_cen == pytest.approx(1.0)


def test_deficyt_ponad_przestrzen_podnosi_ceny():
    # Punkt liczony też w silniku gry (tests/test_dymny_gry.js, punkt 6):
    # emisja 200, Y*=1000, P=1, moc 0,15, wrażliwość 0,3 → presja 4/3,
    # inflacja 10%, poziom cen 1,1.
    p = PanstwoMMT(moc_fiskalna=0.15, wrazliwosc_inflacji=0.3)
    p.wydaj(200.0)
    inflacja = p.zamknij_okres(potencjal_realny=1000.0)
    assert inflacja == pytest.approx(0.1)
    assert p.poziom_cen == pytest.approx(1.1)
    assert p.ostatnia_inflacja == pytest.approx(0.1)
    assert p.emisja_okresu == pytest.approx(0.0)  # licznik wyzerowany


def test_ceny_lepkie_w_dol():
    # Nadwyżka podatkowa (ujemna emisja netto) nie obniża poziomu cen.
    p = PanstwoMMT(podaz_pieniadza=500.0)
    p.opodatkuj(200.0)
    assert p.zamknij_okres(potencjal_realny=1000.0) == pytest.approx(0.0)
    assert p.poziom_cen == pytest.approx(1.0)


def test_szok_podazowy_podnosi_presje():
    # Ta sama emisja przy niższym potencjale (utrata mocy) daje wyższą
    # inflację: kanał podażowy jest endogeniczny.
    infl_pokoj = PanstwoMMT.inflacja_z_presji(200.0, 1000.0, 1.0, 0.15, 0.3)
    infl_wojna = PanstwoMMT.inflacja_z_presji(200.0, 500.0, 1.0, 0.15, 0.3)
    assert infl_wojna > infl_pokoj


def test_inflacja_z_presji_walidacja():
    with pytest.raises(ValueError):
        PanstwoMMT.inflacja_z_presji(100.0, 0.0, 1.0, 0.15, 0.3)
    with pytest.raises(ValueError):
        PanstwoMMT.inflacja_z_presji(100.0, 1000.0, 0.0, 0.15, 0.3)


def test_stopa_jest_zwyklym_atrybutem_polityki():
    # MMT: stopa to decyzja polityczna, nie funkcja reakcji; domyślnie zero.
    p = PanstwoMMT()
    assert p.stopa == pytest.approx(0.0)
    p.stopa = 0.01  # zmiana polityki nie przechodzi przez żadną regułę
    assert p.stopa == pytest.approx(0.01)


# --- Salda sektorowe ---


def test_saldo_sektorowe_rowna_sie_deficytowi():
    # Niezmiennik MMT: deficyt państwa = nadwyżka finansowa sektora
    # niepaństwowego, co do grosza, po dowolnej sekwencji operacji.
    p = PanstwoMMT(podaz_pieniadza=300.0)
    p.wydaj(120.0)
    p.opodatkuj(50.0)
    p.zamknij_okres(potencjal_realny=1000.0)
    p.wydaj(80.0)
    p.opodatkuj(90.0)
    assert p.saldo_sektorowe() == pytest.approx(p.deficyt_skumulowany)
    assert p.deficyt_skumulowany == pytest.approx(60.0)

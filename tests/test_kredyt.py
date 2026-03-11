"""Testy modułu kredyt."""

import datetime as dt
from decimal import Decimal

import pytest

from procenty.kredyt import Kredyt, KredytPorownanie, KredytSuwak, Rodzaj, Zdarzenie


# --- Fixtures ---


@pytest.fixture
def kredyt_rowne():
    """Kredyt 100k PLN, 120 rat równych, r=5%, marża=2%."""
    return Kredyt(
        K=Decimal(100000),
        N=120,
        r=Decimal("0.05"),
        marza=Decimal("0.02"),
        start=dt.datetime(2021, 1, 1),
        rodzajRat="rowne",
    )


@pytest.fixture
def kredyt_malejace():
    """Kredyt 100k PLN, 120 rat malejących, r=5%, marża=2%."""
    return Kredyt(
        K=Decimal(100000),
        N=120,
        r=Decimal("0.05"),
        marza=Decimal("0.02"),
        start=dt.datetime(2021, 1, 1),
        rodzajRat="malejace",
    )


@pytest.fixture
def kredyt_malejace_met2():
    """Kredyt 100k PLN, 120 rat malejących met2, r=5%, marża=2%."""
    return Kredyt(
        K=Decimal(100000),
        N=120,
        r=Decimal("0.05"),
        marza=Decimal("0.02"),
        start=dt.datetime(2021, 1, 1),
        rodzajRat="malejace_met2",
    )


# --- Testy podstawowe ---


class TestKredytPodstawowy:
    """Testy podstawowej funkcjonalności kredytu."""

    def test_liczba_rat_rowne(self, kredyt_rowne):
        assert len(kredyt_rowne.raty) == 120

    def test_liczba_rat_malejace(self, kredyt_malejace):
        assert len(kredyt_malejace.raty) == 120

    def test_liczba_rat_malejace_met2(self, kredyt_malejace_met2):
        assert len(kredyt_malejace_met2.raty) == 120

    def test_kapital_na_koniec_zerowy(self, kredyt_rowne):
        """Po spłacie wszystkich rat kapitał powinien wynosić 0."""
        assert kredyt_rowne.kredyt_wynik["kapital_na_koniec"] == "0.00"

    def test_kapital_na_koniec_malejace(self, kredyt_malejace):
        assert kredyt_malejace.kredyt_wynik["kapital_na_koniec"] == "0.00"

    def test_suma_rat_wieksza_niz_kapital(self, kredyt_rowne):
        """Suma rat musi być większa niż kapitał (odsetki)."""
        suma = sum(float(r["rata"]) for r in kredyt_rowne.raty)
        assert suma > 100000

    def test_odsetki_dodatnie(self, kredyt_rowne):
        """Każda rata powinna mieć dodatnie odsetki (poza ewentualnie pierwszą)."""
        for rata in kredyt_rowne.raty[1:]:
            assert float(rata["odsetki"]) > 0

    def test_rata_rowna_stala(self, kredyt_rowne):
        """Raty równe powinny być w przybliżeniu stałe."""
        raty = [float(r["rata"]) for r in kredyt_rowne.raty]
        # Poza ostatnią ratą (wyrównawczą), różnice powinny być małe
        for i in range(1, len(raty) - 1):
            assert abs(raty[i] - raty[0]) < 1.0  # mniej niż 1 PLN różnicy

    def test_raty_malejace_maleja(self, kredyt_malejace):
        """Raty malejące powinny maleć (lub być równe)."""
        raty = [float(r["rata"]) for r in kredyt_malejace.raty]
        for i in range(1, len(raty)):
            assert raty[i] <= raty[i - 1] + 1.0  # tolerancja 1 PLN

    def test_xirr_dodatni(self, kredyt_rowne):
        """XIRR powinien być dodatni."""
        assert kredyt_rowne.xirr > 0

    def test_podsumowanie_zawiera_pola(self, kredyt_rowne):
        """Podsumowanie powinno zawierać wymagane pola."""
        pods = kredyt_rowne.podsumowanie
        assert "raty" in pods
        assert "info" in pods
        info = pods["info"]
        assert "suma_rat" in info
        assert "suma_odsetek" in info
        assert "liczba_rat" in info
        assert "xirr" in info
        assert "K" in info

    def test_repr(self, kredyt_rowne):
        assert "kredyt" in repr(kredyt_rowne)


# --- Testy walidacji ---


class TestKredytWalidacja:
    """Testy walidacji danych wejściowych kredytu."""

    def test_rok_przed_1900_rzuca_blad(self):
        with pytest.raises(ValueError, match="1900"):
            Kredyt(
                K=Decimal(10000),
                N=12,
                r=Decimal("0.05"),
                marza=Decimal("0.02"),
                start=dt.datetime(1, 1, 1),
                rodzajRat="rowne",
            )

    def test_rata_w_dniu_startu_rzuca_blad(self):
        """Rata w dniu startu kredytu powinna rzucić błąd."""
        zdarzenia = [Zdarzenie(dt.datetime(2021, 1, 1), Rodzaj.SPLATA, 0)]
        with pytest.raises(ValueError, match="rata"):
            Kredyt(
                K=Decimal(10000),
                N=1,
                r=Decimal("0.05"),
                marza=Decimal("0.02"),
                start=dt.datetime(2021, 1, 1),
                rodzajRat="rowne",
                splaty_normalne=False,
                operacje=zdarzenia,
            )

    def test_bledny_rodzaj_rat(self):
        with pytest.raises(Exception, match="nie ma takich"):
            Kredyt(
                K=Decimal(10000),
                N=12,
                r=Decimal("0.05"),
                marza=Decimal("0.02"),
                start=dt.datetime(2021, 1, 1),
                rodzajRat="nieistniejacy",
            )

    def test_niezgodna_liczba_zdarzen(self):
        """Liczba zdarzeń SPLATA musi zgadzać się z N."""
        zdarzenia = [
            Zdarzenie(dt.datetime(2021, 2, 1), Rodzaj.SPLATA, 0),
            Zdarzenie(dt.datetime(2021, 3, 1), Rodzaj.SPLATA, 0),
        ]
        with pytest.raises(Exception, match="Nie zgadza się"):
            Kredyt(
                K=Decimal(10000),
                N=5,
                r=Decimal("0.05"),
                marza=Decimal("0.02"),
                start=dt.datetime(2021, 1, 1),
                rodzajRat="rowne",
                splaty_normalne=False,
                operacje=zdarzenia,
            )


# --- Testy nadpłat ---


class TestKredytNadplaty:
    """Testy kredytu z nadpłatami."""

    def test_nadplata_zmniejsza_kapital(self):
        """Nadpłata powinna zmniejszyć kapitał do spłaty."""
        zdarzenia = [
            Zdarzenie(dt.datetime(2021, 6, 1), Rodzaj.NADPLATA, Decimal(10000))
        ]
        k = Kredyt(
            K=Decimal(100000),
            N=120,
            r=Decimal("0.05"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
            rodzajRat="rowne",
            operacje=zdarzenia,
        )
        assert len(k.nadplaty) == 1
        assert float(k.nadplaty[0]["kwota"]) == 10000.0

    def test_nadplata_zmniejsza_sume_odsetek(self, kredyt_rowne):
        """Kredyt z nadpłatą powinien mieć mniejszą sumę odsetek."""
        zdarzenia = [
            Zdarzenie(dt.datetime(2021, 6, 1), Rodzaj.NADPLATA, Decimal(20000))
        ]
        k_z_nadplata = Kredyt(
            K=Decimal(100000),
            N=120,
            r=Decimal("0.05"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
            rodzajRat="rowne",
            operacje=zdarzenia,
        )

        odsetki_bez = sum(float(r["odsetki"]) for r in kredyt_rowne.raty)
        odsetki_z = sum(float(r["odsetki"]) for r in k_z_nadplata.raty)
        assert odsetki_z < odsetki_bez


# --- Testy zmian oprocentowania ---


class TestKredytZmianaOprocentowania:
    """Testy kredytu ze zmianami oprocentowania."""

    def test_zmiana_oprocentowania(self):
        """Zmiana oprocentowania w trakcie kredytu."""
        zdarzenia = [
            Zdarzenie(dt.datetime(2022, 1, 1), Rodzaj.OPROCENTOWANIE, 8.0),
        ]
        k = Kredyt(
            K=Decimal(100000),
            N=120,
            r=Decimal("0.05"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
            rodzajRat="rowne",
            operacje=zdarzenia,
        )
        assert len(k.raty) == 120
        assert k.kredyt_wynik["kapital_na_koniec"] == "0.00"


# --- Testy transz ---


class TestKredytTransze:
    """Testy kredytu z transzami."""

    def test_transza_zwieksza_kapital(self):
        zdarzenia = [
            Zdarzenie(dt.datetime(2021, 3, 1), Rodzaj.TRANSZA, Decimal(50000)),
        ]
        k = Kredyt(
            K=Decimal(50000),
            N=120,
            r=Decimal("0.05"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
            rodzajRat="rowne",
            operacje=zdarzenia,
        )
        assert len(k.raty) == 120
        # Suma rat powinna być większa niż 100k (50k + 50k transza)
        suma = sum(float(r["rata"]) for r in k.raty)
        assert suma > 100000


# --- Testy KredytPorownanie ---


class TestKredytPorownanie:
    """Testy porównywania kredytów."""

    def test_porownanie_inne_oprocentowanie(self, kredyt_rowne):
        kp = KredytPorownanie(kredyt_rowne, Decimal("0.03"))
        assert len(kp.raty) == 120
        assert kp.podsumowanie is not None

    def test_porownanie_xirr(self, kredyt_rowne):
        kp = KredytPorownanie(kredyt_rowne, Decimal("0.03"))
        assert kp.xirr > 0


# --- Testy KredytSuwak ---


class TestKredytSuwak:
    """Testy iteracyjnej symulacji kredytu."""

    def test_suwak_podstawowy(self):
        ks = KredytSuwak(
            K=Decimal(100000),
            N=120,
            p=Decimal("0.07"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
        )
        # Symulujemy kilka rat
        from dateutil.relativedelta import relativedelta

        data = dt.datetime(2021, 2, 1)
        for i in range(12):
            data = dt.datetime(2021, 1, 1) + relativedelta(months=i + 1)
            k = ks.next(data, Decimal(1500))

        # Po 12 ratach kapitał powinien być mniejszy niż 100k
        assert k < 100000

    def test_suwak_z_oprocentowaniem(self):
        operacje = [
            Zdarzenie(dt.datetime(2021, 7, 1), Rodzaj.OPROCENTOWANIE, 8.0),
        ]
        ks = KredytSuwak(
            K=Decimal(100000),
            N=120,
            p=Decimal("0.07"),
            marza=Decimal("0.02"),
            start=dt.datetime(2021, 1, 1),
            operacje=operacje,
        )
        from dateutil.relativedelta import relativedelta

        data = dt.datetime(2021, 1, 1)
        for i in range(24):
            data = dt.datetime(2021, 1, 1) + relativedelta(months=i + 1)
            k = ks.next(data, Decimal(1500))

        assert k < 100000


# --- Testy zerowego oprocentowania ---


class TestKredytZeroweOprocentowanie:
    """Testy kredytu z zerowym oprocentowaniem."""

    def test_zero_oprocentowanie_rowne(self):
        """Kredyt z zerowym oprocentowaniem — raty = K/N."""
        k = Kredyt(
            K=Decimal(12000),
            N=12,
            r=Decimal("0"),
            marza=Decimal("0"),
            start=dt.datetime(2021, 1, 1),
            rodzajRat="rowne",
        )
        for rata in k.raty:
            assert abs(float(rata["rata"]) - 1000.0) < 1.0
        assert k.kredyt_wynik["kapital_na_koniec"] == "0.00"


# --- Testy zdarzenia sortowanie ---


class TestZdarzenie:
    """Testy klasy Zdarzenie."""

    def test_sortowanie_chronologiczne(self):
        z1 = Zdarzenie(dt.datetime(2021, 1, 1), Rodzaj.SPLATA, 0)
        z2 = Zdarzenie(dt.datetime(2021, 2, 1), Rodzaj.SPLATA, 0)
        assert z1 < z2

    def test_sortowanie_priorytet(self):
        """Zdarzenia w tym samym dniu sortowane według priorytetu."""
        z_transza = Zdarzenie(dt.datetime(2021, 1, 1), Rodzaj.TRANSZA, 100)  # value=1
        z_nadplata = Zdarzenie(dt.datetime(2021, 1, 1), Rodzaj.NADPLATA, 100)  # value=2
        z_splata = Zdarzenie(dt.datetime(2021, 1, 1), Rodzaj.SPLATA, 0)  # value=3
        zdarzenia = sorted([z_splata, z_transza, z_nadplata])
        assert zdarzenia[0].rodzaj == Rodzaj.TRANSZA
        assert zdarzenia[1].rodzaj == Rodzaj.NADPLATA
        assert zdarzenia[2].rodzaj == Rodzaj.SPLATA

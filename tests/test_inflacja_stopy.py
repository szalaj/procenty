"""Testy modułów inflacja i stopy."""

import datetime as dt

import pytest

from procenty.inflacja import Inflacja
from procenty.stopy import Krzywa

# --- Fixtures ---


@pytest.fixture
def krzywa_stala():
    """Krzywa stała 1.0 od 2021 do 2025."""
    punkty = [
        (dt.datetime(2021, 1, 1), 1.0),
        (dt.datetime(2022, 1, 1), 1.0),
        (dt.datetime(2023, 1, 1), 1.0),
        (dt.datetime(2024, 1, 1), 1.0),
        (dt.datetime(2025, 1, 1), 1.0),
    ]
    return Krzywa(punkty=punkty)


@pytest.fixture
def krzywa_rosnaca():
    """Krzywa rosnąca od 0.5 do 2.0."""
    punkty = [
        (dt.datetime(2021, 1, 1), 0.5),
        (dt.datetime(2022, 1, 1), 1.0),
        (dt.datetime(2023, 1, 1), 1.5),
        (dt.datetime(2024, 1, 1), 2.0),
    ]
    return Krzywa(punkty=punkty)


@pytest.fixture
def inflacja_stala(krzywa_stala):
    """Inflacja stała = 1.0 (brak inflacji)."""
    return Inflacja(krzywa=krzywa_stala, miesiac_ref=dt.datetime(2023, 1, 1))


# --- Testy Krzywa ---


class TestKrzywa:
    def test_start_i_end(self, krzywa_stala):
        assert krzywa_stala.start == dt.datetime(2021, 1, 1)
        assert krzywa_stala.end == dt.datetime(2025, 1, 1)

    def test_repr(self, krzywa_stala):
        r = repr(krzywa_stala)
        assert "Krzywa" in r

    def test_podzial_dni(self, krzywa_stala):
        """Podział na okresy 30-dniowe."""
        wynik = krzywa_stala.podzial(30)
        assert len(wynik) > 0
        # Wszystkie wartości powinny być bliskie 1.0
        for _, val in wynik:
            assert abs(val - 1.0) < 0.1

    def test_podzial_miesiac(self, krzywa_stala):
        wynik = krzywa_stala.podzial_miesiac()
        assert len(wynik) > 0
        # Sprawdź czy jest w przybliżeniu 48 miesięcy (2021-2025)
        assert 40 <= len(wynik) <= 50

    def test_krzywa_rosnaca_wartosci(self, krzywa_rosnaca):
        """Wartości na krzywej rosnącej powinny rosnąć."""
        wynik = krzywa_rosnaca.podzial_miesiac()
        wartosci = [v for _, v in wynik]
        # Ogólny trend powinien być rosnący
        assert wartosci[-1] > wartosci[0]

    def test_splajn(self, krzywa_stala):
        splajn = krzywa_stala.splajn
        assert len(splajn) == 500

    def test_punkty_zip(self, krzywa_stala):
        pz = krzywa_stala.punkty_zip
        assert len(pz) == 5

    def test_mnozenie_przez_inflacje(self, krzywa_rosnaca, inflacja_stala):
        """Mnożenie krzywej przez inflator."""
        wynik = krzywa_rosnaca * inflacja_stala
        assert isinstance(wynik, list)
        assert len(wynik) > 0


# --- Testy Inflacja ---


class TestInflacja:
    def test_inflacja_stala_inflator(self, inflacja_stala):
        """Stała inflacja 1.0 — inflator powinien być ~1.0."""
        for data, wartosc in inflacja_stala.inflator:
            assert abs(wartosc - 1.0) < 0.05

    def test_urealnij_stala_inflacja(self, inflacja_stala):
        """Urealnienie przy stałej inflacji nie powinno zmieniać wartości."""
        wynik = inflacja_stala.urealnij(dt.datetime(2023, 6, 1), 1000.0)
        assert abs(wynik - 1000.0) < 50  # Mała tolerancja

    def test_urealnij_poza_zakresem_rzuca_blad(self, inflacja_stala):
        with pytest.raises(ValueError, match="Brak danych"):
            inflacja_stala.urealnij(dt.datetime(2030, 1, 1), 1000.0)

    def test_miesiac_ref_poza_zakresem(self, krzywa_stala):
        with pytest.raises(ValueError, match="spoza przedzialu"):
            Inflacja(krzywa=krzywa_stala, miesiac_ref=dt.datetime(2030, 1, 1))

    def test_inflacja_rosnaca(self):
        """Inflacja > 1 powinna zmniejszać wartość w przyszłości."""
        punkty = [
            (dt.datetime(2021, 1, 1), 1.02),
            (dt.datetime(2022, 1, 1), 1.02),
            (dt.datetime(2023, 1, 1), 1.02),
            (dt.datetime(2024, 1, 1), 1.02),
        ]
        krzywa = Krzywa(punkty=punkty)
        infl = Inflacja(krzywa=krzywa, miesiac_ref=dt.datetime(2022, 1, 1))
        # Wartość w przyszłości powinna być mniejsza w ujęciu realnym
        przyszla = infl.urealnij(dt.datetime(2023, 6, 1), 1000.0)
        obecna = infl.urealnij(dt.datetime(2022, 1, 1), 1000.0)
        assert przyszla < obecna

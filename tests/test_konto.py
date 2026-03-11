"""Testy modułu konto — Zapis, Konto, Agent, SiecAgentow."""

from datetime import datetime

import pytest

from procenty.konto import Agent, Konto, SiecAgentow, Zapis


# --- Fixtures ---


@pytest.fixture
def teraz():
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def konto_pln(teraz):
    k = Konto("gotowka", "PLN")
    k.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=10000.0, opis="Kapitał")
    )
    return k


@pytest.fixture
def agent_jan(teraz):
    jan = Agent("Jan")
    k_pln = Konto("PLN", "PLN")
    k_pln.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=15000.0, opis="Start")
    )
    k_wegiel = Konto("wegiel", "tony")
    k_wegiel.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=10.0, opis="Zapas")
    )
    jan.dodaj_konto(k_pln)
    jan.dodaj_konto(k_wegiel)
    return jan


@pytest.fixture
def agent_anna(teraz):
    anna = Agent("Anna")
    k_pln = Konto("PLN", "PLN")
    k_pln.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=5000.0, opis="Start")
    )
    k_wegiel = Konto("wegiel", "tony")
    k_wegiel.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=20.0, opis="Zapas")
    )
    anna.dodaj_konto(k_pln)
    anna.dodaj_konto(k_wegiel)
    return anna


# --- Testy Zapis ---


class TestZapis:
    def test_zapis_ma(self, teraz):
        z = Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=100.0, opis="Test")
        assert z.ma == 100.0
        assert z.winien == 0.0

    def test_zapis_winien(self, teraz):
        z = Zapis(t_symulacji=1, tr_rzeczywisty=teraz, winien=50.0, opis="Test")
        assert z.winien == 50.0
        assert z.ma == 0.0

    def test_zapis_obie_strony_rzuca_blad(self, teraz):
        with pytest.raises(ValueError, match="jednocześnie"):
            Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=100.0, winien=50.0)

    def test_zapis_zero_rzuca_blad(self, teraz):
        with pytest.raises(ValueError, match="wypełnioną"):
            Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=0.0, winien=0.0)

    def test_zapis_ujemny_czas_rzuca_blad(self, teraz):
        with pytest.raises(ValueError, match="dodatnią"):
            Zapis(t_symulacji=0, tr_rzeczywisty=teraz, ma=100.0)

    def test_klucz_zlozony(self, teraz):
        z = Zapis(t_symulacji=5, tr_rzeczywisty=teraz, ma=100.0)
        assert z.klucz_zlozony == (5, teraz)

    def test_sortowanie(self, teraz):
        z1 = Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=100.0)
        z2 = Zapis(t_symulacji=2, tr_rzeczywisty=teraz, ma=200.0)
        assert z1 < z2


# --- Testy Konto ---


class TestKonto:
    def test_saldo_proste(self, konto_pln):
        assert konto_pln.saldo(5) == 10000.0

    def test_saldo_po_winien(self, konto_pln, teraz):
        konto_pln.dodaj_zapis(
            Zapis(t_symulacji=3, tr_rzeczywisty=teraz, winien=3000.0, opis="Wypłata")
        )
        assert konto_pln.saldo(5) == 7000.0

    def test_rachunek_biezacy(self, konto_pln):
        ma, winien = konto_pln.rachunek_biezacy(5)
        assert ma == 10000.0
        assert winien == 0.0

    def test_saldo_ujemny_okres_rzuca_blad(self, konto_pln):
        with pytest.raises(ValueError, match="dodatnią"):
            konto_pln.saldo(0)

    def test_zapisy_w_okresie(self, konto_pln, teraz):
        konto_pln.dodaj_zapis(
            Zapis(t_symulacji=3, tr_rzeczywisty=teraz, winien=1000.0, opis="A")
        )
        konto_pln.dodaj_zapis(
            Zapis(t_symulacji=5, tr_rzeczywisty=teraz, ma=500.0, opis="B")
        )
        zapisy = konto_pln.zapisy_w_okresie(2, 4)
        assert len(zapisy) == 1

    def test_historia_sald(self, konto_pln, teraz):
        konto_pln.dodaj_zapis(
            Zapis(t_symulacji=3, tr_rzeczywisty=teraz, winien=2000.0, opis="A")
        )
        historia = konto_pln.historia_sald([2, 4])
        assert historia[2] == 10000.0
        assert historia[4] == 8000.0

    def test_transakcja_miedzy_kontami(self, teraz):
        k1 = Konto("A", "PLN")
        k2 = Konto("B", "PLN")
        k1.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=5000.0))
        Konto.transakcja(k1, k2, 1000.0, 5, teraz, "Przelew")
        # k1 gets Ma (credit), k2 gets Winien (debit)
        assert k1.saldo(10) == 6000.0  # 5000 + 1000 Ma
        assert k2.saldo(10) == -1000.0  # 0 - 1000 Winien... actually:
        # transakcja dodaje Ma do konto_ma i Winien do konto_winien
        # więc k1 (konto_ma) dostaje +1000 Ma, k2 (konto_winien) dostaje 1000 Winien

    def test_transakcja_rozne_jednostki_rzuca_blad(self, teraz):
        k1 = Konto("A", "PLN")
        k2 = Konto("B", "USD")
        with pytest.raises(ValueError, match="jednostkach"):
            Konto.transakcja(k1, k2, 100.0, 1, teraz)

    def test_transakcja_rozne_nazwy_ok(self, teraz):
        """Po naprawie: transakcja między kontami o różnych nazwach powinna działać."""
        k1 = Konto("Bank A", "PLN")
        k2 = Konto("Bank B", "PLN")
        k1.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=5000.0))
        # Nie powinno rzucić wyjątku
        Konto.transakcja(k1, k2, 1000.0, 5, teraz)

    def test_str(self, konto_pln):
        s = str(konto_pln)
        assert "gotowka" in s
        assert "PLN" in s

    def test_cache_invalidacja(self, konto_pln, teraz):
        """Cache powinien być zinwalidowany po dodaniu zapisu."""
        saldo_przed = konto_pln.saldo(5)
        konto_pln.dodaj_zapis(
            Zapis(t_symulacji=2, tr_rzeczywisty=teraz, winien=1000.0, opis="Test")
        )
        saldo_po = konto_pln.saldo(5)
        assert saldo_po == saldo_przed - 1000.0


# --- Testy Agent ---


class TestAgent:
    def test_dodaj_konto(self, teraz):
        agent = Agent("Test")
        k = Konto("PLN", "PLN")
        agent.dodaj_konto(k)
        assert "PLN" in agent.lista_nazw_kont()

    def test_dodaj_duplikat_konta_rzuca_blad(self, teraz):
        agent = Agent("Test")
        agent.dodaj_konto(Konto("PLN", "PLN"))
        with pytest.raises(ValueError, match="już posiada"):
            agent.dodaj_konto(Konto("PLN", "PLN"))

    def test_pobierz_nieistniejace_konto_rzuca_blad(self):
        agent = Agent("Test")
        with pytest.raises(ValueError, match="nie posiada"):
            agent.pobierz_konto("brak")

    def test_saldo_konta(self, agent_jan):
        assert agent_jan.saldo_konta("PLN", 5) == 15000.0

    def test_wszystkie_salda(self, agent_jan):
        salda = agent_jan.wszystkie_salda(5)
        assert "Jan" in salda
        assert salda["Jan"]["PLN"] == 15000.0
        assert salda["Jan"]["wegiel"] == 10.0

    def test_wymiana_wewnetrzna(self, agent_jan, teraz):
        """Agent wymienia PLN na węgiel wewnętrznie."""
        agent_jan.wymiana(
            nazwa_konta_oddawanego="PLN",
            ilosc_oddawana=1000.0,
            nazwa_konta_otrzymywanego="wegiel",
            ilosc_otrzymywana=2.0,
            t_symulacji=5,
            tr_rzeczywisty=teraz,
        )
        assert agent_jan.saldo_konta("PLN", 10) == 14000.0
        assert agent_jan.saldo_konta("wegiel", 10) == 12.0

    def test_wymiana_brak_srodkow(self, agent_jan, teraz):
        with pytest.raises(ValueError, match="Niewystarczające"):
            agent_jan.wymiana(
                nazwa_konta_oddawanego="PLN",
                ilosc_oddawana=100000.0,
                nazwa_konta_otrzymywanego="wegiel",
                ilosc_otrzymywana=1.0,
                t_symulacji=5,
                tr_rzeczywisty=teraz,
            )

    def test_transfer_miedzy_agentami(self, agent_jan, agent_anna, teraz):
        agent_jan.transfer(
            nazwa_konta_oddawanego="PLN",
            ilosc=1000.0,
            agent_otrzymujacy=agent_anna,
            nazwa_konta_otrzymywanego="PLN",
            t_symulacji=5,
            tr_rzeczywisty=teraz,
        )
        assert agent_jan.saldo_konta("PLN", 10) == 14000.0
        assert agent_anna.saldo_konta("PLN", 10) == 6000.0

    def test_transfer_rozne_jednostki_rzuca_blad(self, agent_jan, teraz):
        anna = Agent("Anna2")
        anna.dodaj_konto(Konto("gotowka", "USD"))
        with pytest.raises(ValueError, match="jednostki"):
            agent_jan.transfer(
                nazwa_konta_oddawanego="PLN",
                ilosc=100.0,
                agent_otrzymujacy=anna,
                nazwa_konta_otrzymywanego="gotowka",
                t_symulacji=5,
                tr_rzeczywisty=teraz,
            )

    def test_wymiana_miedzy_agentami(self, agent_jan, agent_anna, teraz):
        """Jan oddaje 2000 PLN za 5 ton węgla od Anny."""
        Agent.wymiana_miedzy_agentami(
            agent_oddajacy=agent_jan,
            nazwa_produktu_oddawanego="PLN",
            ilosc_oddawana=2000.0,
            agent_otrzymujacy=agent_anna,
            nazwa_produktu_otrzymywanego="wegiel",
            ilosc_otrzymywana=5.0,
            t_symulacji=10,
            tr_rzeczywisty=teraz,
        )
        assert agent_jan.saldo_konta("PLN", 15) == 13000.0
        assert agent_jan.saldo_konta("wegiel", 15) == 15.0
        assert agent_anna.saldo_konta("PLN", 15) == 7000.0
        assert agent_anna.saldo_konta("wegiel", 15) == 15.0

    def test_str(self, agent_jan):
        s = str(agent_jan)
        assert "Jan" in s


# --- Testy SiecAgentow ---


class TestSiecAgentow:
    def test_dodaj_i_pobierz(self, agent_jan, agent_anna):
        siec = SiecAgentow("TestEkonomia")
        siec.dodaj_agenta(agent_jan)
        siec.dodaj_agenta(agent_anna)
        assert len(siec.lista_agentow()) == 2
        assert siec.pobierz_agenta("Jan") is agent_jan

    def test_duplikat_agenta_rzuca_blad(self, agent_jan):
        siec = SiecAgentow()
        siec.dodaj_agenta(agent_jan)
        with pytest.raises(ValueError, match="już istnieje"):
            siec.dodaj_agenta(agent_jan)

    def test_nieistniejacy_agent_rzuca_blad(self):
        siec = SiecAgentow()
        with pytest.raises(ValueError, match="nie istnieje"):
            siec.pobierz_agenta("brak")

    def test_wszystkie_salda(self, agent_jan, agent_anna):
        siec = SiecAgentow()
        siec.dodaj_agenta(agent_jan)
        siec.dodaj_agenta(agent_anna)
        salda = siec.wszystkie_salda(5)
        assert "Jan" in salda
        assert "Anna" in salda
        assert salda["Jan"]["PLN"] == 15000.0
        assert salda["Anna"]["PLN"] == 5000.0

    def test_wymiana_po_nazwie(self, agent_jan, agent_anna, teraz):
        siec = SiecAgentow()
        siec.dodaj_agenta(agent_jan)
        siec.dodaj_agenta(agent_anna)
        siec.wymiana(
            nazwa_agenta_oddajacego="Jan",
            nazwa_produktu_oddawanego="PLN",
            ilosc_oddawana=1000.0,
            nazwa_agenta_otrzymujacego="Anna",
            nazwa_produktu_otrzymywanego="wegiel",
            ilosc_otrzymywana=3.0,
            t_symulacji=10,
            tr_rzeczywisty=teraz,
        )
        assert agent_jan.saldo_konta("PLN", 15) == 14000.0
        assert agent_anna.saldo_konta("wegiel", 15) == 17.0

    def test_transfer_po_nazwie(self, agent_jan, agent_anna, teraz):
        siec = SiecAgentow()
        siec.dodaj_agenta(agent_jan)
        siec.dodaj_agenta(agent_anna)
        siec.transfer(
            nazwa_agenta_oddajacego="Jan",
            nazwa_konta_oddawanego="PLN",
            ilosc=500.0,
            nazwa_agenta_otrzymujacego="Anna",
            nazwa_konta_otrzymywanego="PLN",
            t_symulacji=10,
            tr_rzeczywisty=teraz,
        )
        assert agent_jan.saldo_konta("PLN", 15) == 14500.0
        assert agent_anna.saldo_konta("PLN", 15) == 5500.0

    def test_str(self):
        siec = SiecAgentow("Moja Siec")
        assert "Moja Siec" in str(siec)

from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import bisect


@dataclass
class Zapis:
    """Pojedynczy zapis księgowy"""

    t_symulacji: int  # czas symulacji (liczba całkowita dodatnia)
    tr_rzeczywisty: datetime  # czas rzeczywisty wpisu
    ma: float = 0.0  # strona Ma (przychody)
    winien: float = 0.0  # strona Winien (rozchody)
    opis: str = ""

    def __post_init__(self):
        """Walidacja - tylko jedna strona może być niezerowa i czas symulacji musi być dodatni"""
        if self.t_symulacji <= 0:
            raise ValueError("Czas symulacji musi być liczbą całkowitą dodatnią")
        if self.ma != 0 and self.winien != 0:
            raise ValueError("Zapis nie może mieć jednocześnie Ma i Winien")
        if self.ma == 0 and self.winien == 0:
            raise ValueError("Zapis musi mieć wypełnioną stronę Ma lub Winien")

    @property
    def klucz_zlozony(self) -> Tuple[int, datetime]:
        """Klucz złożony z czasu symulacji i czasu rzeczywistego"""
        return (self.t_symulacji, self.tr_rzeczywisty)

    def __lt__(self, other):
        """Porównanie dla sortowania według klucza złożonego"""
        return self.klucz_zlozony < other.klucz_zlozony


class Konto:
    """
    Konto składające się z zapisów i rachunku bieżącego.

    Zapisy zawierają wszystkie transakcje z kluczem złożonym (t_symulacji, tr_rzeczywisty).
    Rachunek bieżący oblicza saldo na konkretną chwilę czasową.
    Może przechowywać różne rodzaje rzeczy wyrażanych liczbowo (pieniądze, cegły, armaty, itp.)
    """

    def __init__(self, nazwa: str, jednostka: str = "PLN"):
        self.nazwa = nazwa
        self.jednostka = jednostka  # jednostka miary (np. PLN, kg, szt, t)
        self._zapisy: List[
            Zapis
        ] = []  # Lista zapisów sortowana według klucza złożonego
        self._ostatnie_obliczenie_t: Optional[int] = None
        self._cache_saldo: Dict[int, Tuple[float, float]] = {}  # cache sald

    def dodaj_zapis(self, zapis: Zapis) -> None:
        """
        Dodaje zapis do konta, zachowując sortowanie według klucza złożonego.
        """
        # Znajdź właściwą pozycję dla nowego zapisu
        pozycja = bisect.bisect_left(self._zapisy, zapis)
        self._zapisy.insert(pozycja, zapis)

        # Usuń cache dla dat >= t_symulacji nowego zapisu
        self._invalidate_cache_od(zapis.t_symulacji)

    def _invalidate_cache_od(self, t_od: int) -> None:
        """Usuwa cache dla okresów >= t_od"""
        klucze_do_usuniecia = [t for t in self._cache_saldo.keys() if t >= t_od]
        for klucz in klucze_do_usuniecia:
            del self._cache_saldo[klucz]

    def rachunek_biezacy(
        self, t_i: int, tr_obecny: Optional[datetime] = None
    ) -> Tuple[float, float]:
        """
        Oblicza rachunek bieżący (Ma, Winien) na okres t_i.

        Args:
            t_i: Okres symulacji dla którego obliczamy saldo (liczba całkowita dodatnia)
            tr_obecny: Czas rzeczywisty obliczenia (domyślnie datetime.now())

        Returns:
            Tuple[float, float]: (suma_ma, suma_winien)
        """
        if t_i <= 0:
            raise ValueError("Okres symulacji musi być liczbą całkowitą dodatnią")

        if tr_obecny is None:
            tr_obecny = datetime.now()

        # Sprawdź cache
        if t_i in self._cache_saldo:
            return self._cache_saldo[t_i]

        suma_ma = 0.0
        suma_winien = 0.0

        for zapis in self._zapisy:
            # Uwzględnij zapis jeśli:
            # 1. Okres symulacji <= t_i
            # 2. Jeśli okres symulacji == t_i, to czas rzeczywisty <= tr_obecny
            if zapis.t_symulacji < t_i or (
                zapis.t_symulacji == t_i and zapis.tr_rzeczywisty <= tr_obecny
            ):
                suma_ma += zapis.ma
                suma_winien += zapis.winien

            # Przerwij jeśli przekroczyliśmy okres symulacji
            elif zapis.t_symulacji > t_i:
                break

        # Zapisz w cache
        self._cache_saldo[t_i] = (suma_ma, suma_winien)
        return suma_ma, suma_winien

    def saldo(self, t_i: int, tr_obecny: Optional[datetime] = None) -> float:
        """
        Oblicza saldo (Ma - Winien) na okres t_i.

        Returns:
            float: Saldo (dodatnie = nadwyżka, ujemne = deficyt)
        """
        ma, winien = self.rachunek_biezacy(t_i, tr_obecny)
        return ma - winien

    def zapisy_w_okresie(self, t_od: int, t_do: int) -> List[Zapis]:
        """Zwraca zapisy z okresu [t_od, t_do]"""
        wynik = []
        for zapis in self._zapisy:
            if t_od <= zapis.t_symulacji <= t_do:
                wynik.append(zapis)
            elif zapis.t_symulacji > t_do:
                break
        return wynik

    def przyszle_zapisy(self, t_od: int) -> List[Zapis]:
        """Zwraca zapisy zaplanowane na przyszłość (t_symulacji > t_od)"""
        wynik = []
        for zapis in self._zapisy:
            if zapis.t_symulacji > t_od:
                wynik.append(zapis)
        return wynik

    def historia_sald(self, okresy: List[int]) -> Dict[int, float]:
        """Oblicza salda dla listy okresów"""
        wynik = {}
        for okres in sorted(okresy):
            wynik[okres] = self.saldo(okres)
        return wynik

    def __str__(self) -> str:
        return f"Konto({self.nazwa}, {self.jednostka}): {len(self._zapisy)} zapisów"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def transakcja(
        cls,
        konto_ma: "Konto",
        konto_winien: "Konto",
        kwota: float,
        t_symulacji: int,
        tr_rzeczywisty: datetime,
        opis: str = "",
    ) -> Tuple["Konto", "Konto"]:
        """
        Wykonuje transakcję pomiędzy dwoma kontami.
        Dodaje zapis Ma do konta_ma i zapis Winien do konto_winien.
        Zwraca oba konta po zmianach.

        Konta muszą mieć tę samą jednostkę.
        """
        if konto_ma.jednostka != konto_winien.jednostka:
            raise ValueError(
                f"Transakcja między kontami o różnych jednostkach: {konto_ma.jednostka} vs {konto_winien.jednostka}"
            )

        zapis_ma = Zapis(
            t_symulacji=t_symulacji, tr_rzeczywisty=tr_rzeczywisty, ma=kwota, opis=opis
        )
        zapis_winien = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            winien=kwota,
            opis=opis,
        )
        konto_ma.dodaj_zapis(zapis_ma)
        konto_winien.dodaj_zapis(zapis_winien)
        return konto_ma, konto_winien


class Agent:
    """
    Agent posiadający wiele kont różnych typów.

    Może wykonywać wymiany między kontami z różnymi jednostkami,
    automatycznie tworząc odpowiednie zapisy księgowe.
    """

    def __init__(self, nazwa: str):
        self.nazwa = nazwa
        self._konta: Dict[str, Konto] = {}  # słownik kont według nazw (nie jednostek)

    def dodaj_konto(self, konto: Konto) -> None:
        """Dodaje konto do agenta"""
        if konto.nazwa in self._konta:
            raise ValueError(f"Agent już posiada konto o nazwie '{konto.nazwa}'")
        self._konta[konto.nazwa] = konto

    def pobierz_konto(self, nazwa: str) -> Konto:
        """Pobiera konto dla danej nazwy"""
        if nazwa not in self._konta:
            raise ValueError(f"Agent nie posiada konta o nazwie '{nazwa}'")
        return self._konta[nazwa]

    def lista_nazw_kont(self) -> List[str]:
        """Zwraca listę wszystkich nazw kont, które posiada agent"""
        return list(self._konta.keys())

    def lista_jednostek(self) -> List[str]:
        """Zwraca listę wszystkich jednostek, które posiada agent"""
        return [konto.jednostka for konto in self._konta.values()]

    def saldo_konta(
        self, nazwa: str, t_i: int, tr_obecny: Optional[datetime] = None
    ) -> float:
        """Zwraca saldo konta dla danej nazwy"""
        return self.pobierz_konto(nazwa).saldo(t_i, tr_obecny)

    def wszystkie_salda(
        self, t_i: int, tr_obecny: Optional[datetime] = None
    ) -> Dict[str, Dict[str, float]]:
        """Zwraca salda wszystkich kont agenta (klucz: nazwa agenta -> nazwa konta -> saldo)"""
        return {
            self.nazwa: {
                nazwa: konto.saldo(t_i, tr_obecny)
                for nazwa, konto in self._konta.items()
            }
        }

    def wymiana(
        self,
        nazwa_konta_oddawanego: str,
        ilosc_oddawana: float,
        nazwa_konta_otrzymywanego: str,
        ilosc_otrzymywana: float,
        t_symulacji: int,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> None:
        """
        Wykonuje wymianę między dwoma kontami agenta.

        Args:
            nazwa_konta_oddawanego: Nazwa konta, z którego oddajemy
            ilosc_oddawana: Ilość produktu, który oddajemy (dodatnia)
            nazwa_konta_otrzymywanego: Nazwa konta, na które otrzymujemy
            ilosc_otrzymywana: Ilość produktu, który otrzymujemy (dodatnia)
            t_symulacji: Okres symulacji
            tr_rzeczywisty: Czas rzeczywisty (domyślnie datetime.now())
            opis: Opis wymiany
        """
        if tr_rzeczywisty is None:
            tr_rzeczywisty = datetime.now()

        if ilosc_oddawana <= 0 or ilosc_otrzymywana <= 0:
            raise ValueError("Ilości w wymianie muszą być dodatnie")

        # Pobierz konta
        konto_oddawane = self.pobierz_konto(nazwa_konta_oddawanego)
        konto_otrzymywane = self.pobierz_konto(nazwa_konta_otrzymywanego)

        # Sprawdź czy mamy wystarczająco środków do oddania
        saldo_oddawane = konto_oddawane.saldo(t_symulacji, tr_rzeczywisty)
        if saldo_oddawane < ilosc_oddawana:
            raise ValueError(
                f"Niewystarczające środki w koncie '{nazwa_konta_oddawanego}': "
                f"saldo={saldo_oddawane}, potrzeba={ilosc_oddawana}"
            )

        # Przygotuj opis jeśli nie podano
        if not opis:
            opis = f"Wymiana {ilosc_oddawana} {konto_oddawane.jednostka} na {ilosc_otrzymywana} {konto_otrzymywane.jednostka}"

        # Utwórz zapisy księgowe
        # Oddajemy z konta (strona Winien)
        zapis_oddawany = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            winien=ilosc_oddawana,
            opis=opis,
        )

        # Otrzymujemy na konto (strona Ma)
        zapis_otrzymywany = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            ma=ilosc_otrzymywana,
            opis=opis,
        )

        # Dodaj zapisy do odpowiednich kont
        konto_oddawane.dodaj_zapis(zapis_oddawany)
        konto_otrzymywane.dodaj_zapis(zapis_otrzymywany)

    def transfer(
        self,
        nazwa_konta_oddawanego: str,
        ilosc: float,
        agent_otrzymujacy: "Agent",
        nazwa_konta_otrzymywanego: str,
        t_symulacji: int,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> None:
        """
        Wykonuje transfer (jednostronne przekazanie) produktu do innego agenta.
        Agent oddający traci produkt, agent otrzymujący go zyskuje.

        Args:
            nazwa_konta_oddawanego: Nazwa konta u tego agenta, z którego oddajemy
            ilosc: Ilość produktu do przekazania (dodatnia)
            agent_otrzymujacy: Agent, który otrzymuje produkt
            nazwa_konta_otrzymywanego: Nazwa konta u agenta otrzymującego
            t_symulacji: Okres symulacji
            tr_rzeczywisty: Czas rzeczywisty (domyślnie datetime.now())
            opis: Opis transferu
        """
        if tr_rzeczywisty is None:
            tr_rzeczywisty = datetime.now()

        if ilosc <= 0:
            raise ValueError("Ilość w transferze musi być dodatnia")

        # Pobierz konta
        konto_oddawane = self.pobierz_konto(nazwa_konta_oddawanego)
        konto_otrzymywane = agent_otrzymujacy.pobierz_konto(nazwa_konta_otrzymywanego)

        # Sprawdź zgodność jednostek
        if konto_oddawane.jednostka != konto_otrzymywane.jednostka:
            raise ValueError(
                f"Konta mają różne jednostki: {konto_oddawane.jednostka} vs {konto_otrzymywane.jednostka}"
            )

        # Sprawdź czy mamy wystarczająco środków do oddania
        saldo_oddawane = konto_oddawane.saldo(t_symulacji, tr_rzeczywisty)
        if saldo_oddawane < ilosc:
            raise ValueError(
                f"Niewystarczające środki w koncie '{nazwa_konta_oddawanego}': "
                f"saldo={saldo_oddawane}, potrzeba={ilosc}"
            )

        # Przygotuj opis jeśli nie podano
        if not opis:
            opis = f"Transfer {ilosc} {konto_oddawane.jednostka} od {self.nazwa} do {agent_otrzymujacy.nazwa}"

        # Utwórz zapisy księgowe
        # Oddajemy z konta (strona Winien)
        zapis_oddawany = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            winien=ilosc,
            opis=f"{opis} - oddanie",
        )

        # Otrzymujemy na konto (strona Ma)
        zapis_otrzymywany = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            ma=ilosc,
            opis=f"{opis} - otrzymanie",
        )

        # Dodaj zapisy do odpowiednich kont
        konto_oddawane.dodaj_zapis(zapis_oddawany)
        konto_otrzymywane.dodaj_zapis(zapis_otrzymywany)

    def __str__(self) -> str:
        nazwy_kont = ", ".join(
            [f"{nazwa}({konto.jednostka})" for nazwa, konto in self._konta.items()]
        )
        return f"Agent({self.nazwa}): konta [{nazwy_kont}]"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def wymiana_miedzy_agentami(
        cls,
        agent_oddajacy: "Agent",
        nazwa_produktu_oddawanego: str,
        ilosc_oddawana: float,
        agent_otrzymujacy: "Agent",
        nazwa_produktu_otrzymywanego: str,
        ilosc_otrzymywana: float,
        t_symulacji: int,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> Tuple["Agent", "Agent"]:
        """
        Wykonuje pełną wymianę między dwoma różnymi agentami.

        Agent oddający oddaje swój produkt i otrzymuje produkt od agenta otrzymującego.
        Agent otrzymujący otrzymuje produkt od agenta oddającego i oddaje swój produkt.

        Args:
            agent_oddajacy: Agent, który oddaje swój produkt
            nazwa_produktu_oddawanego: Nazwa produktu (konta), który oddaje agent_oddajacy
            ilosc_oddawana: Ilość produktu, który oddaje agent_oddajacy (dodatnia)
            agent_otrzymujacy: Agent, który otrzymuje produkt od agent_oddajacy
            nazwa_produktu_otrzymywanego: Nazwa produktu (konta), który oddaje agent_otrzymujacy
            ilosc_otrzymywana: Ilość produktu, który otrzymuje agent_oddajacy (dodatnia)
            t_symulacji: Okres symulacji
            tr_rzeczywisty: Czas rzeczywisty (domyślnie datetime.now())
            opis: Opis wymiany

        Returns:
            Tuple[Agent, Agent]: (agent_oddajacy, agent_otrzymujacy) po wykonaniu wymiany
        """
        if tr_rzeczywisty is None:
            tr_rzeczywisty = datetime.now()

        if ilosc_oddawana <= 0 or ilosc_otrzymywana <= 0:
            raise ValueError("Ilości w wymianie muszą być dodatnie")

        # Pobierz konta produktów które są oddawane
        konto_produktu_oddawanego_u_oddajacego = agent_oddajacy.pobierz_konto(
            nazwa_produktu_oddawanego
        )
        konto_produktu_otrzymywanego_u_otrzymujacego = agent_otrzymujacy.pobierz_konto(
            nazwa_produktu_otrzymywanego
        )

        # Pobierz konta produktów które są otrzymywane (muszą istnieć u drugiej strony)
        konto_produktu_oddawanego_u_otrzymujacego = agent_otrzymujacy.pobierz_konto(
            nazwa_produktu_oddawanego
        )
        konto_produktu_otrzymywanego_u_oddajacego = agent_oddajacy.pobierz_konto(
            nazwa_produktu_otrzymywanego
        )

        # Sprawdź czy konta mają zgodne jednostki
        if (
            konto_produktu_oddawanego_u_oddajacego.jednostka
            != konto_produktu_oddawanego_u_otrzymujacego.jednostka
        ):
            raise ValueError(
                f"Konta produktu '{nazwa_produktu_oddawanego}' mają różne jednostki: "
                f"{konto_produktu_oddawanego_u_oddajacego.jednostka} vs {konto_produktu_oddawanego_u_otrzymujacego.jednostka}"
            )

        if (
            konto_produktu_otrzymywanego_u_oddajacego.jednostka
            != konto_produktu_otrzymywanego_u_otrzymujacego.jednostka
        ):
            raise ValueError(
                f"Konta produktu '{nazwa_produktu_otrzymywanego}' mają różne jednostki: "
                f"{konto_produktu_otrzymywanego_u_oddajacego.jednostka} vs {konto_produktu_otrzymywanego_u_otrzymujacego.jednostka}"
            )

        # Sprawdź czy agenci mają wystarczająco środków
        saldo_produktu_oddawanego = konto_produktu_oddawanego_u_oddajacego.saldo(
            t_symulacji, tr_rzeczywisty
        )
        if saldo_produktu_oddawanego < ilosc_oddawana:
            raise ValueError(
                f"Agent {agent_oddajacy.nazwa} ma niewystarczające środki w produkcie '{nazwa_produktu_oddawanego}': "
                f"saldo={saldo_produktu_oddawanego}, potrzeba={ilosc_oddawana}"
            )

        saldo_produktu_otrzymywanego = (
            konto_produktu_otrzymywanego_u_otrzymujacego.saldo(
                t_symulacji, tr_rzeczywisty
            )
        )
        if saldo_produktu_otrzymywanego < ilosc_otrzymywana:
            raise ValueError(
                f"Agent {agent_otrzymujacy.nazwa} ma niewystarczające środki w produkcie '{nazwa_produktu_otrzymywanego}': "
                f"saldo={saldo_produktu_otrzymywanego}, potrzeba={ilosc_otrzymywana}"
            )

        # Przygotuj opis jeśli nie podano
        if not opis:
            opis = f"Wymiana: {agent_oddajacy.nazwa} oddaje {ilosc_oddawana} {konto_produktu_oddawanego_u_oddajacego.jednostka} za {ilosc_otrzymywana} {konto_produktu_otrzymywanego_u_otrzymujacego.jednostka} od {agent_otrzymujacy.nazwa}"

        # Utwórz 4 zapisy księgowe:

        # 1. Agent oddający oddaje swój produkt (Winien)
        zapis_oddajacy_oddaje = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            winien=ilosc_oddawana,
            opis=f"{opis} - oddanie {nazwa_produktu_oddawanego}",
        )

        # 2. Agent otrzymujący otrzymuje produkt od oddającego (Ma)
        zapis_otrzymujacy_otrzymuje_oddawany = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            ma=ilosc_oddawana,
            opis=f"{opis} - otrzymanie {nazwa_produktu_oddawanego}",
        )

        # 3. Agent otrzymujący oddaje swój produkt (Winien)
        zapis_otrzymujacy_oddaje = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            winien=ilosc_otrzymywana,
            opis=f"{opis} - oddanie {nazwa_produktu_otrzymywanego}",
        )

        # 4. Agent oddający otrzymuje produkt od otrzymującego (Ma)
        zapis_oddajacy_otrzymuje = Zapis(
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            ma=ilosc_otrzymywana,
            opis=f"{opis} - otrzymanie {nazwa_produktu_otrzymywanego}",
        )

        # Dodaj zapisy do odpowiednich kont
        konto_produktu_oddawanego_u_oddajacego.dodaj_zapis(zapis_oddajacy_oddaje)
        konto_produktu_oddawanego_u_otrzymujacego.dodaj_zapis(
            zapis_otrzymujacy_otrzymuje_oddawany
        )
        konto_produktu_otrzymywanego_u_otrzymujacego.dodaj_zapis(
            zapis_otrzymujacy_oddaje
        )
        konto_produktu_otrzymywanego_u_oddajacego.dodaj_zapis(zapis_oddajacy_otrzymuje)

        return agent_oddajacy, agent_otrzymujacy


class SiecAgentow:
    """
    Sieć agentów umożliwiająca zarządzanie wieloma agentami
    i śledzenie globalnego stanu gospodarki.
    """

    def __init__(self, nazwa: str = "Gospodarka"):
        self.nazwa = nazwa
        self._agenci: Dict[str, Agent] = {}

    def dodaj_agenta(self, agent: Agent) -> None:
        """Dodaje agenta do sieci."""
        if agent.nazwa in self._agenci:
            raise ValueError(f"Agent o nazwie '{agent.nazwa}' już istnieje w sieci")
        self._agenci[agent.nazwa] = agent

    def pobierz_agenta(self, nazwa: str) -> Agent:
        """Pobiera agenta po nazwie."""
        if nazwa not in self._agenci:
            raise ValueError(f"Agent '{nazwa}' nie istnieje w sieci")
        return self._agenci[nazwa]

    def lista_agentow(self) -> List[str]:
        """Zwraca listę nazw agentów w sieci."""
        return list(self._agenci.keys())

    def wszystkie_salda(
        self, t_i: int, tr_obecny: Optional[datetime] = None
    ) -> Dict[str, Dict[str, float]]:
        """Zwraca salda wszystkich kont wszystkich agentów."""
        wynik: Dict[str, Dict[str, float]] = {}
        for nazwa, agent in self._agenci.items():
            wynik[nazwa] = {
                nazwa_konta: agent.saldo_konta(nazwa_konta, t_i, tr_obecny)
                for nazwa_konta in agent.lista_nazw_kont()
            }
        return wynik

    def wymiana(
        self,
        nazwa_agenta_oddajacego: str,
        nazwa_produktu_oddawanego: str,
        ilosc_oddawana: float,
        nazwa_agenta_otrzymujacego: str,
        nazwa_produktu_otrzymywanego: str,
        ilosc_otrzymywana: float,
        t_symulacji: int,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> Tuple[Agent, Agent]:
        """Wykonuje wymianę między dwoma agentami w sieci po ich nazwach."""
        agent_oddajacy = self.pobierz_agenta(nazwa_agenta_oddajacego)
        agent_otrzymujacy = self.pobierz_agenta(nazwa_agenta_otrzymujacego)
        return Agent.wymiana_miedzy_agentami(
            agent_oddajacy=agent_oddajacy,
            nazwa_produktu_oddawanego=nazwa_produktu_oddawanego,
            ilosc_oddawana=ilosc_oddawana,
            agent_otrzymujacy=agent_otrzymujacy,
            nazwa_produktu_otrzymywanego=nazwa_produktu_otrzymywanego,
            ilosc_otrzymywana=ilosc_otrzymywana,
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            opis=opis,
        )

    def transfer(
        self,
        nazwa_agenta_oddajacego: str,
        nazwa_konta_oddawanego: str,
        ilosc: float,
        nazwa_agenta_otrzymujacego: str,
        nazwa_konta_otrzymywanego: str,
        t_symulacji: int,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> None:
        """Wykonuje transfer między agentami w sieci po ich nazwach."""
        agent_oddajacy = self.pobierz_agenta(nazwa_agenta_oddajacego)
        agent_otrzymujacy = self.pobierz_agenta(nazwa_agenta_otrzymujacego)
        agent_oddajacy.transfer(
            nazwa_konta_oddawanego=nazwa_konta_oddawanego,
            ilosc=ilosc,
            agent_otrzymujacy=agent_otrzymujacy,
            nazwa_konta_otrzymywanego=nazwa_konta_otrzymywanego,
            t_symulacji=t_symulacji,
            tr_rzeczywisty=tr_rzeczywisty,
            opis=opis,
        )

    def __str__(self) -> str:
        return f"SiecAgentow({self.nazwa}): {len(self._agenci)} agentów"

    def __repr__(self) -> str:
        return self.__str__()

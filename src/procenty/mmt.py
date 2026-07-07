"""
Państwo MMT: model monetarny zgodny z Modern Monetary Theory dla symulacji
krokowych. Alternatywa dla monetarystycznego `procenty.bank_centralny`
(MV=PY, reguła Taylora), który pozostaje w pakiecie bez zmian.

Zasady modelu (MMT):

1. Pieniądz czartalistyczny: wydatek państwa TWORZY pieniądz (emisja),
   podatek go UMARZA. Podatki nie finansują wydatków; ściągają siłę nabywczą
   z obiegu. Emitent własnej waluty nie ma ograniczenia kasowego.
2. Inflacja z presji na realne moce, nie z podaży pieniądza: emisja netto
   okresu (wydatki minus podatki) do wysokości przestrzeni fiskalnej
   (ułamek nominalnego potencjału) nie podnosi cen; ponad nią poziom cen
   rośnie proporcjonalnie do przekroczenia. Ceny są lepkie w dół.
3. Stopa procentowa jest decyzją polityczną (zwykły atrybut), nie funkcją
   reakcji na inflację.
4. Salda sektorowe: skumulowany deficyt państwa co do grosza równa się
   przyrostowi pieniądza sektora niepaństwowego (niezmiennik do testów).

Obiekt jest krokowy (kolejne okresy symulacji) i domenowo neutralny. Może
działać samodzielnie albo wpinać emisję i podatek w księgowość
`procenty.konto.Konto`. Wartości jako float, spójnie z `Konto`/`Zapis`
(warstwa symulacyjna); rozliczenia co do grosza są domeną modułu `kredyt`.
"""

from datetime import datetime
from typing import Optional

from procenty.konto import Konto, Zapis


class PanstwoMMT:
    """Państwo emitujące własną walutę: wydatek tworzy pieniądz, podatek
    umarza, inflacja bierze się z presji fiskalnej na realne moce.

    Typowy krok symulacji:
        panstwo.wydaj(zakupy, konto=konto_gospodarki, t_symulacji=t)
        panstwo.opodatkuj(danina, konto=konto_gospodarki, t_symulacji=t)
        inflacja = panstwo.zamknij_okres(potencjal_realny=y_potencjalne)
    """

    def __init__(
        self,
        podaz_pieniadza: float = 0.0,
        poziom_cen: float = 1.0,
        stopa: float = 0.0,
        moc_fiskalna: float = 0.15,
        wrazliwosc_inflacji: float = 0.3,
    ) -> None:
        """
        Args:
            podaz_pieniadza: początkowy pieniądz w obiegu sektora
                niepaństwowego (>= 0).
            poziom_cen: początkowy poziom cen P (> 0).
            stopa: stopa referencyjna jako decyzja polityczna (MMT: naturalna
                stopa to zero); zwykły atrybut, bez reguły reakcji.
            moc_fiskalna: ułamek nominalnego potencjału stanowiący przestrzeń
                fiskalną okresu (> 0); emisja netto do tej granicy nie
                podnosi cen.
            wrazliwosc_inflacji: inflacja za każde 100% przekroczenia
                przestrzeni fiskalnej (>= 0).
        """
        if podaz_pieniadza < 0:
            raise ValueError("Podaż pieniądza nie może być ujemna")
        if poziom_cen <= 0:
            raise ValueError("Poziom cen musi być dodatni")
        if moc_fiskalna <= 0:
            raise ValueError("Moc fiskalna musi być dodatnia")
        if wrazliwosc_inflacji < 0:
            raise ValueError("Wrażliwość inflacji nie może być ujemna")

        self.podaz_pieniadza: float = float(podaz_pieniadza)
        self.poziom_cen: float = float(poziom_cen)
        self.stopa: float = float(stopa)
        self.moc_fiskalna: float = float(moc_fiskalna)
        self.wrazliwosc_inflacji: float = float(wrazliwosc_inflacji)

        # Emisja netto bieżącego okresu (wydatki minus podatki): mierzy
        # presję fiskalną; zeruje ją zamknij_okres().
        self.emisja_okresu: float = 0.0
        # Skumulowany deficyt (dług własnowalutowy). Informacyjny: emitent
        # nie bankrutuje we własnej walucie; hamulcem jest inflacja.
        self.deficyt_skumulowany: float = 0.0
        self._podaz_poczatkowa: float = float(podaz_pieniadza)
        self.ostatnia_inflacja: float = 0.0

    def __repr__(self) -> str:
        return (
            f"PanstwoMMT(podaz={self.podaz_pieniadza:.2f}, "
            f"P={self.poziom_cen:.4f}, deficyt={self.deficyt_skumulowany:.2f})"
        )

    # -- Wydatki i podatki (wydatek tworzy pieniądz, podatek umarza) ----------

    def _zapisz(
        self,
        konto: Optional[Konto],
        kwota: float,
        strona_ma: bool,
        t_symulacji: Optional[int],
        tr_rzeczywisty: Optional[datetime],
        opis: str,
    ) -> None:
        if konto is None or kwota == 0:
            return
        if t_symulacji is None:
            raise ValueError("Zapis na konto wymaga t_symulacji")
        if tr_rzeczywisty is None:
            tr_rzeczywisty = datetime.now()
        if strona_ma:
            konto.dodaj_zapis(Zapis(t_symulacji, tr_rzeczywisty, ma=kwota, opis=opis))
        else:
            konto.dodaj_zapis(
                Zapis(t_symulacji, tr_rzeczywisty, winien=kwota, opis=opis)
            )

    def wydaj(
        self,
        kwota: float,
        konto: Optional[Konto] = None,
        t_symulacji: Optional[int] = None,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> float:
        """Wydatek państwa: emituje pieniądz do obiegu (kwota >= 0).

        Nie wymaga pokrycia; emitent własnej waluty zawsze może zapłacić,
        kosztem jest presja inflacyjna, nie brak środków. Jeśli podano
        `konto`, dopisuje zapis Ma (pieniądz trafia do sektora
        niepaństwowego). Zwraca nową podaż pieniądza.
        """
        if kwota < 0:
            raise ValueError("Wydatek nie może być ujemny (podatek: opodatkuj)")
        self._zapisz(
            konto,
            kwota,
            True,
            t_symulacji,
            tr_rzeczywisty,
            opis or "Wydatek państwa (emisja)",
        )
        self.podaz_pieniadza += float(kwota)
        self.emisja_okresu += float(kwota)
        self.deficyt_skumulowany += float(kwota)
        return self.podaz_pieniadza

    def opodatkuj(
        self,
        kwota: float,
        konto: Optional[Konto] = None,
        t_symulacji: Optional[int] = None,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> float:
        """Podatek: umarza pieniądz z obiegu (kwota >= 0, nie więcej niż
        krąży).

        Podatek nie finansuje wydatków (nie zasila żadnego skarbu); ściąga
        siłę nabywczą i obniża presję fiskalną okresu. Jeśli podano `konto`,
        dopisuje zapis Winien (pieniądz schodzi z sektora niepaństwowego).
        Zwraca nową podaż pieniądza.
        """
        if kwota < 0:
            raise ValueError("Podatek nie może być ujemny")
        if kwota > self.podaz_pieniadza:
            raise ValueError(
                "Podatek przekracza pieniądz w obiegu "
                f"(kwota={kwota}, podaż={self.podaz_pieniadza})"
            )
        self._zapisz(
            konto,
            kwota,
            False,
            t_symulacji,
            tr_rzeczywisty,
            opis or "Podatek (umorzenie pieniądza)",
        )
        self.podaz_pieniadza -= float(kwota)
        self.emisja_okresu -= float(kwota)
        self.deficyt_skumulowany -= float(kwota)
        return self.podaz_pieniadza

    # -- Inflacja z presji fiskalnej -------------------------------------------

    @staticmethod
    def inflacja_z_presji(
        emisja_netto: float,
        potencjal_realny: float,
        poziom_cen: float,
        moc_fiskalna: float,
        wrazliwosc_inflacji: float,
    ) -> float:
        """Inflacja okresu z presji fiskalnej (bezstanowa, lustro silnika gry):

        presja = max(0, emisja_netto) / (moc_fiskalna * Y* * P),
        inflacja = wrazliwosc * max(0, presja - 1).

        Do granicy przestrzeni fiskalnej emisja jest bezinflacyjna (wolne
        moce wchłaniają popyt); ceny są lepkie w dół (inflacja >= 0). Kanał
        podażowy jest endogeniczny: spadek potencjału Y* podnosi presję przy
        tej samej emisji.
        """
        if potencjal_realny <= 0:
            raise ValueError("Potencjał realny musi być dodatni")
        if poziom_cen <= 0:
            raise ValueError("Poziom cen musi być dodatni")
        przestrzen = moc_fiskalna * potencjal_realny * poziom_cen
        presja = max(0.0, emisja_netto) / przestrzen
        return wrazliwosc_inflacji * max(0.0, presja - 1.0)

    def zamknij_okres(self, potencjal_realny: float) -> float:
        """Zamyka okres: mierzy inflację z emisji netto okresu wobec
        potencjału realnego, aktualizuje poziom cen (multiplikatywnie)
        i zeruje licznik emisji. Zwraca inflację okresu.
        """
        inflacja = self.inflacja_z_presji(
            self.emisja_okresu,
            potencjal_realny,
            self.poziom_cen,
            self.moc_fiskalna,
            self.wrazliwosc_inflacji,
        )
        self.poziom_cen *= 1.0 + inflacja
        self.ostatnia_inflacja = inflacja
        self.emisja_okresu = 0.0
        return inflacja

    # -- Salda sektorowe --------------------------------------------------------

    def saldo_sektorowe(self) -> float:
        """Nadwyżka finansowa sektora niepaństwowego od startu symulacji
        (przyrost pieniądza w obiegu). Z konstrukcji równa skumulowanemu
        deficytowi państwa; rozjazd oznacza błąd księgowania.
        """
        return self.podaz_pieniadza - self._podaz_poczatkowa

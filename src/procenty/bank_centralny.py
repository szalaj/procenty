"""
Bank centralny: ogólny, domenowo neutralny model polityki pieniężnej dla
symulacji krokowych.

Model opiera się na dwóch klasycznych zależnościach makroekonomicznych, więc
nadaje się do dowolnej symulacji (nie tylko gospodarczej gry), w której coś
pełni rolę pieniądza:

1. Ilościowa teoria pieniądza (równanie wymiany): M * V = P * Y, gdzie M to
   podaż pieniądza, V prędkość obiegu, P poziom cen, Y realna produkcja. Z tego
   poziom cen P = M * V / Y, a inflacja to względna zmiana P między okresami.
2. Reguła Taylora: bank ustala nominalną stopę referencyjną w reakcji na
   odchylenie inflacji od celu oraz na lukę produktową.

To jest model MONETARYSTYCZNY (ilościowa teoria pieniądza plus reguła
Taylora). Alternatywny model zgodny z MMT (wydatek tworzy pieniądz, podatek
umarza, inflacja z presji fiskalnej na realne moce, stopa jako decyzja
polityczna) jest w module `procenty.mmt` (`PanstwoMMT`).

Obiekt jest krokowy (operuje na kolejnych okresach symulacji, nie na
kalendarzu, w odróżnieniu od `procenty.inflacja.Inflacja`). Może działać
samodzielnie (czysta makroekonomia) albo wpinać emisję pieniądza w księgowość
`procenty.konto.Konto` (dopisywanie zapisów na wskazane konto).

Wartości trzymamy jako float, spójnie z `Konto`/`Zapis` (warstwa symulacyjna).
Precyzyjne rozliczenia pieniężne co do grosza (Decimal) są domeną modułu
`kredyt`, nie makroekonomii.
"""

from datetime import datetime
from typing import Optional

from procenty.konto import Konto, Zapis


class BankCentralny:
    """Bank centralny: emisja pieniądza, stopa referencyjna, inflacja i reguła
    polityki pieniężnej.

    Typowy krok symulacji:
        bank.emituj(nowy_pieniadz, konto=konto_skarbu, t_symulacji=t)
        inflacja = bank.zmierz_inflacje(produkcja_realna=Y)
        stopa = bank.ustal_stope(inflacja, luka_produktowa=luka)
    """

    def __init__(
        self,
        podaz_pieniadza: float = 0.0,
        stopa: float = 0.02,
        cel_inflacji: float = 0.02,
        stopa_neutralna: float = 0.02,
        predkosc_obiegu: float = 1.0,
        wsp_inflacji: float = 0.5,
        wsp_luki: float = 0.5,
        stopa_min: float = 0.0,
        stopa_max: float = 1.0,
    ) -> None:
        """
        Args:
            podaz_pieniadza: początkowa podaż pieniądza M (>= 0).
            stopa: początkowa nominalna stopa referencyjna na okres.
            cel_inflacji: cel inflacyjny π* (dla reguły Taylora).
            stopa_neutralna: neutralna stopa realna r* (dla reguły Taylora).
            predkosc_obiegu: prędkość obiegu pieniądza V w równaniu wymiany (> 0).
            wsp_inflacji: waga odchylenia inflacji od celu w regule Taylora (>= 0).
            wsp_luki: waga luki produktowej w regule Taylora (>= 0).
            stopa_min: dolne ograniczenie ustalanej stopy.
            stopa_max: górne ograniczenie ustalanej stopy.
        """
        if podaz_pieniadza < 0:
            raise ValueError("Podaż pieniądza nie może być ujemna")
        if predkosc_obiegu <= 0:
            raise ValueError("Prędkość obiegu musi być dodatnia")
        if stopa_min > stopa_max:
            raise ValueError("stopa_min nie może przekraczać stopa_max")

        self.podaz_pieniadza: float = float(podaz_pieniadza)
        self.stopa: float = float(stopa)
        self.cel_inflacji: float = float(cel_inflacji)
        self.stopa_neutralna: float = float(stopa_neutralna)
        self.predkosc_obiegu: float = float(predkosc_obiegu)
        self.wsp_inflacji: float = float(wsp_inflacji)
        self.wsp_luki: float = float(wsp_luki)
        self.stopa_min: float = float(stopa_min)
        self.stopa_max: float = float(stopa_max)

        # Poziom cen z poprzedniego pomiaru (do liczenia inflacji jako zmiany P).
        self._poprzedni_poziom_cen: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"BankCentralny(podaz={self.podaz_pieniadza:.2f}, "
            f"stopa={self.stopa:.4f}, cel_inflacji={self.cel_inflacji:.4f})"
        )

    # -- Emisja pieniądza -----------------------------------------------------

    def emituj(
        self,
        kwota: float,
        konto: Optional[Konto] = None,
        t_symulacji: Optional[int] = None,
        tr_rzeczywisty: Optional[datetime] = None,
        opis: str = "",
    ) -> float:
        """Emituje (kwota > 0) albo absorbuje (kwota < 0) pieniądz.

        Zmienia podaż pieniądza M. Jeśli podano `konto`, dopisuje zapis
        księgowy: emisja to strona Ma (pieniądz trafia na konto), absorpcja to
        strona Winien (pieniądz schodzi z konta). Zapis wymaga `t_symulacji`.

        Zwraca nową podaż pieniądza.
        """
        if kwota < 0 and -kwota > self.podaz_pieniadza:
            raise ValueError(
                "Absorpcja przekracza podaż pieniądza "
                f"(kwota={kwota}, podaż={self.podaz_pieniadza})"
            )

        if konto is not None and kwota != 0:
            if t_symulacji is None:
                raise ValueError("Zapis na konto wymaga t_symulacji")
            if tr_rzeczywisty is None:
                tr_rzeczywisty = datetime.now()
            opis = opis or ("Emisja pieniądza" if kwota > 0 else "Absorpcja pieniądza")
            if kwota > 0:
                konto.dodaj_zapis(
                    Zapis(t_symulacji, tr_rzeczywisty, ma=kwota, opis=opis)
                )
            else:
                konto.dodaj_zapis(
                    Zapis(t_symulacji, tr_rzeczywisty, winien=-kwota, opis=opis)
                )

        self.podaz_pieniadza = self.podaz_pieniadza + float(kwota)
        return self.podaz_pieniadza

    # -- Ceny i inflacja (ilościowa teoria pieniądza) -------------------------

    def poziom_cen(self, produkcja_realna: float) -> float:
        """Poziom cen z równania wymiany: P = M * V / Y.

        Args:
            produkcja_realna: realna produkcja Y (> 0).
        """
        if produkcja_realna <= 0:
            raise ValueError("Produkcja realna musi być dodatnia")
        return self.podaz_pieniadza * self.predkosc_obiegu / produkcja_realna

    def zmierz_inflacje(self, produkcja_realna: float) -> float:
        """Mierzy inflację jako względną zmianę poziomu cen od poprzedniego
        pomiaru i zapamiętuje bieżący poziom jako odniesienie dla następnego.

        UWAGA: metoda jest stanowa (przesuwa punkt odniesienia). Pierwszy pomiar
        zakotwicza poziom bazowy i zwraca 0.0. W jednym kroku symulacji wołaj ją
        raz. Do bezstanowego odczytu poziomu cen użyj `poziom_cen`.
        """
        poziom = self.poziom_cen(produkcja_realna)
        if self._poprzedni_poziom_cen is None:
            self._poprzedni_poziom_cen = poziom
            return 0.0
        inflacja = poziom / self._poprzedni_poziom_cen - 1.0
        self._poprzedni_poziom_cen = poziom
        return inflacja

    @staticmethod
    def inflacja_ze_stop(
        wzrost_podazy: float,
        wzrost_produkcji: float,
        wzrost_predkosci: float = 0.0,
    ) -> float:
        """Inflacja z równania wymiany w postaci stóp wzrostu:
        (1+π) = (1+gM)(1+gV) / (1+gY), więc π = powyższe minus 1.

        Bezstanowa funkcja pomocnicza, gdy znasz same stopy wzrostu podaży (gM),
        produkcji (gY) i ewentualnie prędkości obiegu (gV).
        """
        if wzrost_produkcji <= -1.0:
            raise ValueError("Wzrost produkcji nie może wynosić -100% ani mniej")
        return (1.0 + wzrost_podazy) * (1.0 + wzrost_predkosci) / (
            1.0 + wzrost_produkcji
        ) - 1.0

    # -- Polityka stóp (reguła Taylora) ---------------------------------------

    def regula_taylora(self, inflacja: float, luka_produktowa: float = 0.0) -> float:
        """Nominalna stopa wg reguły Taylora (bez przycięcia do granic):
        r = r* + π + a·(π − π*) + b·luka,
        gdzie r* to stopa neutralna, π inflacja, π* cel, a/b wagi.
        """
        return (
            self.stopa_neutralna
            + inflacja
            + self.wsp_inflacji * (inflacja - self.cel_inflacji)
            + self.wsp_luki * luka_produktowa
        )

    def ustal_stope(self, inflacja: float, luka_produktowa: float = 0.0) -> float:
        """Ustawia stopę referencyjną wg reguły Taylora, przyciętą do
        [stopa_min, stopa_max], i zwraca ją.
        """
        stopa = self.regula_taylora(inflacja, luka_produktowa)
        self.stopa = max(self.stopa_min, min(self.stopa_max, stopa))
        return self.stopa

    def stopa_realna(self, inflacja: float) -> float:
        """Stopa realna z równania Fishera (przybliżenie): r_real = r_nom − π."""
        return self.stopa - inflacja

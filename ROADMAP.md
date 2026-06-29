# Roadmap i ocena projektu

Dokument wewnętrzny: ocena stanu i kierunki rozwoju. Część użytkowa jest w [README](README.md).

## Co działa dobrze

- **Rdzeń kredytowy jest solidny.** Event-driven symulacja z obsługą transz, nadpłat, wakacji i zmian stóp to realistyczny model. Naliczanie odsetek na bazie rzeczywistej liczby dni (act/act) odpowiada praktyce bankowej.
- **XIRR/RRSO**: poprawna implementacja, wyniki zgodne (test potwierdza |RRSO - XIRR| < 0.0001).
- **Cubic spline na krzywej stóp**: sensowne podejście do interpolacji, lepsze niż liniowe dla scenariuszy makro.
- **Model IS-LM w gospodarka.py**: łączenie makroekonomii z symulacją kredytową (stopa równowagi prowadzi do oprocentowania kredytu).

## Naprawione bugi (historia)

- `konto.py:269` literówka: naprawione.
- `generate_model.py`: moduł zależny od bazy danych usunięty z biblioteki.
- `inne.py` `liczba_dni_w_roku()`: naprawione (pełna reguła gregoriańska).
- `inwestycja.py` martwy kod: naprawione.
- `zrob_splate_calkowita` błąd znaku odsetek: naprawione w 0.2.1.
- `xirr` bez zbieżności wywracał podsumowanie: zabezpieczone w 0.2.1.
- `malejace_met2` N=1 dzielenie przez zero: naprawione w 0.2.1.
- Higiena precyzji `Decimal(str(...))` w create_kredyt: 0.2.2.

## Propozycje zmian architektonicznych

1. **Kontrakt `podsumowanie`/`raty`**: liczby zwracane jako stringi. Docelowo czyste typy liczbowe, ale to zmiana łamiąca konsumenta (kredytoweobliczenia.pl pinuje 0.1.3), więc wymaga skoordynowanego wydania major.
2. **Rozwinąć `konto.py`** (system Zapis/Konto/Agent) jako bazę do symulacji agent-based (ABM): funkcja `produkcja()`, mechanizm cenowy `rynek()`, połączenie z kredytem.
3. **Wyrzucić martwy kod**: `zasoby.py` (puste klasy), zakomentowane fragmenty.
4. **Zależności przykładów**: `networkx` używany w `przyklady/`, nie w bibliotece (świadomie poza zależnościami pakietu).

## Perspektywa makroekonomiczna

**Kierunek A: Kalkulator finansów osobistych.** Dojrzały rdzeń kredytowy + lokaty + inflacja dają narzędzie do porównywania scenariuszy (np. „nadpłacać kredyt czy inwestować?"). Brakuje: podatku Belki, obligacji skarbowych, portfela mieszanego.

**Kierunek B: Symulator makro (ABM).** `gospodarka.py` (IS-LM) + `konto.py` (agenci) + `zasoby.py` (grafy) szkicują framework do agent-based modeling. Brakuje: mechanizmu cenowego, funkcji produkcji, cyklu koniunkturalnego.

Rekomendacja: najpierw kierunek A (obligacje, podatki), `konto.py` rozwijać równolegle jako eksperyment.

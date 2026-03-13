# Procenty

Biblioteka Python do symulacji finansowych: kredyty hipoteczne, lokaty, inflacja, stopy procentowe.

## Instalacja

```bash
pip install procenty
# lub w trybie deweloperskim:
poetry install
```

## Moduły

| Moduł | Opis |
|-------|------|
| `kredyt` | Symulacja kredytów hipotecznych (raty równe/malejące, nadpłaty, wakacje, transze, zmienne stopy) |
| `inwestycja` | Lokaty, XIRR, XNPV, IRR, RRSO, MPKK |
| `inflacja` | Urealnianie wartości pieniądza w czasie, interpolacja CPI |
| `stopy` | Krzywa stóp procentowych (cubic spline) |
| `miary` | Dni odsetkowe z uwzględnieniem lat przestępnych, klasa Zloty |
| `konto` | System księgowy z podwójnym zapisem, agenci, wymiana zasobów |

## Szybki start

```python
from procenty.kredyt import Kredyt
from decimal import Decimal
from datetime import datetime

# Kredyt 400k PLN, 35 lat, raty równe
k = Kredyt(
    K=Decimal(400000), N=420,
    r=Decimal(0.076), marza=Decimal(0.04),
    start=datetime(2021, 10, 13), rodzajRat='rowne'
)
print(f"XIRR: {k.xirr:.4f}")
print(f"Suma odsetek: {k.podsumowanie['info']['suma_odsetek']} PLN")
```

## Ocena projektu i propozycje zmian

### Co działa dobrze

- **Rdzeń kredytowy jest solidny.** Event-driven symulacja z obsługą transz, nadpłat, wakacji i zmian stóp to realistyczny model. Naliczanie odsetek na bazie rzeczywistej liczby dni (act/act) odpowiada praktyce bankowej.
- **XIRR/RRSO** - poprawna implementacja z użyciem metody Newtona, wyniki zgodne (test potwierdza |RRSO - XIRR| < 0.0001).
- **Cubic spline na krzywej stóp** - sensowne podejście do interpolacji, lepsze niż liniowe dla scenariuszy makro.
- **Model IS-LM w gospodarka.py** - ciekawy pomysł łączenia makroekonomii z symulacją kredytową (stopa równowagi -> oprocentowanie kredytu).

### Co wymaga naprawy (bugi)

1. ~~**`konto.py:269`** - literówka~~ - naprawione
2. ~~**`generate_model.py`** - usunięty~~ - moduł zależny od bazy danych usunięty z biblioteki
3. ~~**`inne.py:2`** - `liczba_dni_w_roku()`~~ - naprawione (pełna reguła gregoriańska)
4. ~~**`inwestycja.py:178-179`** - martwy kod~~ - naprawione

### Propozycje zmian architektonicznych

1. **Dopisać testy** - priorytetowe:
   - Kredyt z nadpłatami i zmianami stóp
   - Lokata - przyszła wartość
   - Inflacja - urealnianie
   - Konto - transakcje i salda

4. **Rozwinąć moduł konto.py** - to najciekawszy kierunek rozwoju. System Zapis/Konto/Agent może stać się bazą do symulacji makroekonomicznych agent-based (ABM). Konkretne następne kroki:
   - Naprawić literówkę
   - Dodać `produkcja()` - Agent produkuje dobra w każdym okresie
   - Dodać `rynek()` - mechanizm ustalania cen przy wymianie
   - Połączyć z kredytem: agent zaciąga kredyt, spłaca ratami ze swoich kont

5. **Wyrzucić martwy kod** - zasoby.py (puste klasy), zakomentowane testy w test_1.py, zakomentowane printy.

6. **Zadeklarować brakujące zależności** - networkx jest używany w przykładach ale nie w pyproject.toml.

### Perspektywa makroekonomiczna

Projekt ma potencjał do ewolucji w dwóch kierunkach:

**Kierunek A: Kalkulator finansów osobistych** - dojrzały rdzeń kredytowy + lokaty + inflacja dają kompletne narzędzie do porównywania scenariuszy (np. "nadpłacać kredyt czy inwestować?"). Brakuje: uwzględnienia podatku Belki, obligacji skarbowych, portfela mieszanego.

**Kierunek B: Symulator makro (ABM)** - `gospodarka.py` (IS-LM) + `konto.py` (agenci) + `zasoby.py` (grafy) szkicują framework do agent-based modeling. To ambitniejszy cel, ale `konto.py` jest dobrym fundamentem. Brakuje: mechanizmu cenowego (aukcja/targowanie), funkcji produkcji, cyklu koniunkturalnego.

Rekomendacja: skupić się najpierw na kierunku A (naprawić bugi, dopisać testy, dodać obligacje/podatki), a konto.py rozwijać równolegle jako eksperyment.

## Przykłady

Katalog `przyklady/` zawiera skrypty demonstracyjne:
- `kredyt1.py` - kredyty z nadpłatami i porównania
- `inflacja_przyklad.py` - urealnianie wartości
- `gospodarka.py` - model IS-LM + kredyt
- `zasoby.py` - grafy zasobów (prototyp)

## Zastrzeżenie

**Użytkowanie na własną odpowiedzialność.** Ta biblioteka jest narzędziem edukacyjnym i symulacyjnym. Wyniki obliczeń mogą zawierać błędy i nie powinny stanowić podstawy do podejmowania decyzji finansowych. Autor nie ponosi odpowiedzialności za jakiekolwiek straty wynikające z użycia tego oprogramowania. Przed podjęciem decyzji finansowych skonsultuj się z wykwalifikowanym doradcą.

## Licencja

MIT - patrz [LICENSE](LICENSE).

## Autor

szalaj (mszalajski@gmail.com)

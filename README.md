# Procenty

Biblioteka Python do obliczeń finansowych z naciskiem na kredyty i lokaty.

## Przegląd

Procenty to kompleksowy zestaw narzędzi do obliczeń finansowych, obejmujący:

- Symulacje kredytów z różnymi metodami spłaty
- Obliczenia zwrotu z inwestycji
- Modelowanie i interpolację stóp procentowych
- Obliczenia uwzględniające inflację
- Obliczanie wskaźników finansowych (XIRR, RRSO)

## Instalacja

```bash
# Instalacja z repozytorium w trybie deweloperskim
pip install -e .

# Lub instalacja z PyPI
pip install procenty
```

## Funkcje

### Obliczenia kredytowe (`kredyt.py`)

- Różne rodzaje kredytów (raty równe, raty malejące)
- Obsługa złożonych zdarzeń kredytowych:
  - Zmiany stóp procentowych
  - Wcześniejsze spłaty (częściowe lub całkowite)
  - Wakacje kredytowe
  - Transze kredytowe
- Obliczanie kluczowych wskaźników finansowych:
  - XIRR (wewnętrzna stopa zwrotu)
  - Całkowity koszt kredytu
  - Wartości skorygowane o inflację

```python
from procenty.kredyt import Kredyt, Zdarzenie, Rodzaj
from decimal import Decimal
from datetime import datetime

# Prosty kredyt: 400 000 PLN, 35 lat, oprocentowanie 7,6%, marża 4%
kredyt = Kredyt(
    K=Decimal(400000),            # kwota kredytu
    N=420,                        # liczba rat (35 lat * 12 miesięcy)
    r=Decimal(0.076),             # bazowa stopa procentowa
    marza=Decimal(0.04),          # marża
    start=datetime(2021, 10, 13), # data rozpoczęcia
    rodzajRat='rowne'             # raty równe
)

# Analiza szczegółów kredytu
print(f"Całkowita liczba rat: {len(kredyt.raty)}")
print(f"XIRR: {kredyt.xirr:.4f}")
podsumowanie = kredyt.podsumowanie
print(f"Suma spłat: {podsumowanie['info']['suma_rat']} PLN")
print(f"Suma odsetek: {podsumowanie['info']['suma_odsetek']} PLN")
```

### Obliczenia inwestycyjne (`inwestycja.py`)

- Symulacje lokat terminowych
- Różne częstotliwości kapitalizacji
- Obliczenia XIRR i IRR
- Obliczenia RRSO (Rzeczywistej Rocznej Stopy Oprocentowania)

```python
from procenty.inwestycja import Lokata, xirr

# Lokata: 10 000 PLN, 4,5% oprocentowania, 12 miesięcy, kapitalizacja miesięczna
lokata = Lokata(
    kwota=10000,           # kwota lokaty
    oprocentowanie=0.045,  # stopa procentowa (4,5%)
    czas=12,               # czas trwania w miesiącach
    kapitalizacja=12       # kapitalizacja miesięczna
)

# Obliczenie wartości końcowej i zysku
print(f"Wartość końcowa: {lokata.przyszla_wartosc():.2f} PLN")
print(f"Zysk: {lokata.oblicz_zysk():.2f} PLN")
```

### Modelowanie stóp procentowych (`stopy.py`)

- Interpolacja krzywej stóp procentowych
- Obsługa i prognozowanie stóp WIBOR
- Obliczenia oparte na okresach

### Korekty inflacyjne (`inflacja.py`)

- Modelowanie stopy inflacji
- Obliczenia wartości skorygowanych o inflację
- Obliczenia wartości realnej w czasie

### Miary finansowe (`miary.py`)

- Obliczenia liczby dni dla naliczania odsetek
- Obsługa waluty z klasą `Zloty`
- Różne narzędzia do pomiarów finansowych

## Narzędzia

- Obliczenia dat finansowych
- Interpolacja stóp procentowych
- Formatowanie i obliczenia walutowe
- Korekty dni roboczych

## Przykłady

Zobacz katalog `przyklady/` dla przykładowych skryptów demonstrujących różne funkcje.

## Licencja

Projekt jest udostępniany na licencji MIT. Pełna treść licencji znajduje się w pliku [LICENSE](LICENSE).

## Autor

szalaj (mszalajski@gmail.com)
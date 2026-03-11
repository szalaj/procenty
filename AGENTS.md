# AGENTS.md - Opis projektu `procenty` dla agentów AI

## Cel projektu

Biblioteka Python do symulacji finansowych i makroekonomicznych. Rdzeń stanowi symulator kredytów hipotecznych ze zmiennym oprocentowaniem (WIBOR), ale projekt ewoluuje w kierunku ogólniejszego frameworku do modelowania przepływów ekonomicznych między agentami.

## Architektura

```
src/procenty/
├── kredyt.py          # RDZEŃ - symulator kredytów (Kredyt, KredytPorownanie, KredytSuwak)
├── inwestycja.py      # Lokata, XIRR/XNPV, RRSO, IRR, Inwestycja, MPKK
├── inflacja.py        # Inflacja (urealnianie wartości), InflacjaMiesiac (interpolacja CPI)
├── stopy.py           # Krzywa stóp procentowych (cubic spline interpolation)
├── miary.py           # LiczbaDni (dni odsetkowe z latami przestępnymi), Zloty
├── konto.py           # System księgowy: Zapis, Konto, Agent, SiecAgentow
├── utils/
│   ├── inne.py        # liczba_dni_w_roku, diff_month
│   ├── create_kredyt.py   # Fabryki kredytów z dict/JSON
│   └── generate_model.py  # WiborInter, Wibor (opcjonalnie wymaga SQLAlchemy), generator modelu
przyklady/
├── kredyt1.py         # Przykład użycia kredytów
├── inflacja_przyklad.py   # Przykład inflacji
├── gospodarka.py      # Model IS-LM (równowaga Y, r) -> symulacja kredytu
└── zasoby.py          # Grafy zasobów (NetworkX), strefy gospodarcze
```

## Kluczowe koncepcje domenowe

### Kredyt (kredyt.py)
- Symulacja oparta na zdarzeniach (`Zdarzenie` + `Rodzaj`): SPLATA, OPROCENTOWANIE, NADPLATA, TRANSZA, SPLATA_CALKOWITA, WAKACJE
- Zdarzenia sortowane chronologicznie z priorytetem typu (enum value)
- Odsetki naliczane na bazie rzeczywistej liczby dni (LiczbaDni z miary.py)
- Trzy rodzaje rat: `rowne`, `malejace`, `malejace_met2`
- Decimal precision dla kwot (grosze = Decimal(".01"))
- KredytSuwak - iteracyjna symulacja z nadpłatami do poziomu raty porównawczej
- Walidacja: data startu >= 1900, rata nie może być w dniu startu

### Krzywa stóp (stopy.py)
- Interpolacja cubic spline na timestampach
- Dzielenie na okresy (dni, miesiące)
- Mnożenie przez Inflacja daje wartości realne

### System księgowy (konto.py)
- Podwójna księgowość: Ma/Winien
- Klucz złożony: (t_symulacji, tr_rzeczywisty) - czas dyskretny symulacji + czas ciągły rzeczywisty
- Agent posiada wiele Kont z różnymi jednostkami (PLN, tony, szt)
- Wymiana wewnętrzna, transfer między agentami, wymiana dwustronna
- SiecAgentow - zarządzanie wieloma agentami i śledzenie globalnego stanu
- Cache sald z invalidacją

## Konwencje kodu

- Język: Nazewnictwo polskie (zmienne, klasy, metody), docstringi polskie
- Typy: Decimal dla kwot pieniężnych, float dla stóp i wartości interpolowanych
- Type annotations w większości modułów
- Daty: datetime obiekty, formatowanie "%Y-%m-%d" w stringach
- Dataclasses z logiką w `__post_init__`
- Manager pakietu: Poetry
- Formatowanie: black (88 znaków), isort (profil black), flake8

## Zależności

- scipy (interpolacja, newton solver dla XIRR)
- pandas (operacje na seriach czasowych, WIBOR)
- numpy (obliczenia numeryczne)
- pendulum (dni odsetkowe w miary.py)
- python-dateutil (relativedelta)
- loguru (logowanie)
- pyyaml (zadeklarowane, ale nieużywane w kodzie źródłowym)
- sqlalchemy (opcjonalna, lazy import w generate_model.py)
- networkx (tylko w przyklady/zasoby.py, niezadeklarowane)

## Testy

- `tests/test_2.py` - 2 testy (kredyt + RRSO vs XIRR)
- `tests/test_miary.py` - 2 testy LiczbaDni
- `tests/test_kredyt.py` - 24 testy (raty równe/malejące, nadpłaty, transze, zmiana oprocentowania, walidacja, KredytSuwak, KredytPorownanie)
- `tests/test_inwestycja.py` - 17 testów (Lokata, XIRR, XNPV, NPV, RRSO, MPKK, Inwestycja)
- `tests/test_konto.py` - 30 testów (Zapis, Konto, Agent, SiecAgentow, wymiana, transfer)
- `tests/test_inflacja_stopy.py` - 13 testów (Krzywa, Inflacja, urealnianie)
- `tests/test_utils.py` - 37 testów (liczba_dni_w_roku, diff_month, LiczbaDni, Zloty, create_kredyt)

Łącznie: 125 testów

## Jak uruchomić

```bash
poetry install
poetry run pytest tests/ -v
poetry run python przyklady/kredyt1.py
```

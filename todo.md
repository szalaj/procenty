# Ocena projektu Procenty + Plan zmian

## Ocena ogolna

| Kategoria | Ocena (1-10) | Komentarz |
|-----------|:---:|-----------|
| Logika | 7 | Solidna architektura event-driven, dobry model ksiegowy. Kilka bugow i martwego kodu |
| Software Engineering | 5 | Niska pokrycia testami (~10%), brak CI/CD, `except BaseException`, mieszanie float/Decimal |
| Potencjal | 8 | Unikalna kombinacja: kredyty + ksiegowosc agentowa + makroekonomia. Duze mozliwosci ABM |
| Poprawnosc finansowa | 7 | Decimal z ROUND_HALF_UP, act/act day counting, poprawny XIRR. Ale malejace_met2 uzywa regresji liniowej zamiast wzoru analitycznego |
| Cyberbezpieczenstwo | 6 | Brak wrażliwych danych, ale `except BaseException` maskuje bledy, brak walidacji inputow w inwestycja.py |

---

## BUGI - Priorytet krytyczny

### [DONE] BUG-1: generate_model.py - `except BaseException` (6 wystapien)
- **Fix**: Zamieniono na `except (KeyError, IndexError)` i `except ValueError`

### [DONE] BUG-2: kredyt.py - `raise Exception` zamiast `ValueError`
- **Fix**: Zamieniono na `raise ValueError(...)` w walidacji i `oblicz_rate()`

### [DONE] BUG-3: generate_model.py - type hint mismatch
- **Fix**: Poprawiono type hint z `str` na `dt.datetime`

---

## LOGIKA

### [DONE] LOG-1: Zdarzenie.__lt__ - sortowanie przez string concatenation
- **Fix**: Zamieniono na porownanie krotek `(self.data, self.rodzaj.value)`

### LOG-2: malejace_met2 - regresja liniowa zamiast wzoru
- **Lokalizacja**: `src/procenty/kredyt.py:112-129`
- **Problem**: Po symulacji przelicza odsetki regresja liniowa (`__przelicz_odsetki_mal2`). To przybliżenie, nie dokladny wzor
- **Fix**: Zaimplementowac analityczny wzor dla metody 2 bezposrednio w symulacji

### [DONE] LOG-3: IRR w inwestycja.py - naiwna implementacja
- **Fix**: Zamieniono naiwna iteracje na `scipy.optimize.brentq`

---

## SOFTWARE ENGINEERING

### SE-1: Zwiekszyc pokrycie testami do >80%
- **Priorytet**: Wysoki
- **Brakujace testy**:
  - [ ] Kredyt z wieloma nadplatami + zmiana oprocentowania jednoczesnie
  - [ ] Transze kredytowe (edge cases)
  - [ ] WAKACJE (typ zdarzenia istnieje ale nie testowany)
  - [ ] Inflacja z brakujacymi miesiącami (interpolacja)
  - [ ] SiecAgentow - wymiana miedzy agentami
  - [ ] mpkk() - rozne przypadki (wieloletnie)
  - [ ] Edge case: kredyt na 1 rate, kredyt na 360 rat
  - [ ] Edge case: oprocentowanie 0%

### SE-2: Dodac CI/CD (GitHub Actions)
- [ ] Uruchamianie testow przy kazdym PR
- [ ] black + isort check
- [ ] flake8 check
- [ ] Coverage report (pytest-cov)

### [DONE] SE-3: Usunac martwy kod
- [x] `tests/test_1.py` - usuniety pusty plik
- [x] Zakomentowane printy i stary kod w generate_model.py - wyczyszczone
- [ ] `przyklady/zasoby.py` - prototyp z niezadeklarowana zaleznoscia networkx

### [DONE] SE-4: Usunięto generate_model.py z biblioteki
- **Fix**: Usunięto plik z zależnością od SQLAlchemy i bazy danych

### SE-5: Mieszanie float i Decimal w stopach procentowych
- **Problem**: `stopy.py` (Krzywa) uzywa float, `kredyt.py` uzywa Decimal dla `r` i `marza`
- **Fix**: Ujednolicic - albo konsekwentnie Decimal w calym flow, albo jasno udokumentowac granice konwersji

### SE-6: Brak pyproject.toml dependency: networkx
- **Lokalizacja**: `przyklady/zasoby.py` uzywa networkx
- **Fix**: Dodac do optional dependencies lub usunac przyklad

---

## POPRAWNOSC FINANSOWA

### [DONE] FIN-1: Walidacja inputow w inwestycja.py
- **Fix**: Dodano walidacje w Lokata (kwota, czas, kapitalizacja), irr (pusta lista), mpkk (K, N)

### FIN-2: RRSO - metoda bisekcji vs standard UE
- **Problem**: Implementacja RRSO uzywa prostej bisekcji. Standard UE (Dyrektywa 2008/48/WE) wymaga wlaczenia wszystkich kosztow (prowizja, ubezpieczenie)
- **Fix**: Rozszerzyc RRSO o liste dodatkowych kosztow; zweryfikowac z kalkulatorem UOKiK

### [DONE] FIN-3: mpkk() - brak walidacji ujemnych kwot
- **Fix**: Dodano walidacje K > 0 i N > 0

### FIN-4: Brak obslugi walut obcych
- **Problem**: Tylko PLN (implicit). Brak przewalutowania, brak kursow
- **Sugestia**: Na przyszlosc - dodac pole waluta do Kredyt i Lokata

---

## CYBERBEZPIECZENSTWO

### [DONE] SEC-1: `except BaseException` - maskowanie bledow
- **Fix**: Zamieniono wszystkie 6 wystapien na konkretne typy wyjatkow

### [DONE] SEC-2: SQL Injection w generate_model.py
- **Fix**: Zamieniono string formatting w zapytaniach SQL na parametryzowane queries (`:rodzaj` + `params={}`)

### [DONE] SEC-3: Brak limitu na N (liczba rat)
- **Fix**: Dodano walidacje N w zakresie 1-600 w Kredyt.__post_init__

### SEC-4: Brak limitu na wielkosc sieci agentow
- **Problem**: SiecAgentow nie ma limitu liczby agentow/kont - potencjalny DoS
- **Fix**: Dodac konfigurowalny limit

### SEC-5: Loguru - dane finansowe w logach
- **Problem**: `loguru` moze logowac kwoty i parametry kredytu do plikow
- **Fix**: Upewnic sie ze logi nie trafiaja do plikow produkcyjnych z danymi wrazliwymi

---

## POTENCJAL - Sugestie rozwoju

### POT-1: Web API (FastAPI)
- Exposing kalkulatora kredytowego jako REST API
- Endpoint: POST /kredyt/symulacja, POST /inwestycja/lokata
- Swagger docs z przykladami

### POT-2: Interaktywny dashboard (Streamlit/Gradio)
- Wizualizacja harmonogramu splat
- Porownywarka kredytow (KredytPorownanie)
- Slider do nadplat (KredytSuwak)

### POT-3: Agent-Based Modeling (ABM)
- konto.py to solidna baza - rozwinac do pelnej symulacji gospodarki
- Dodac: rynek pracy, bank centralny, rynek nieruchomosci
- Integracja z bibliotekami ABM (Mesa)

### POT-4: Import danych z NBP API
- Automatyczne pobieranie stop procentowych, inflacji, kursow walut
- Zastapi reczne dane w generate_model.py

### POT-5: Export do Excel/PDF
- Harmonogram splat w formacie bankowym
- Porownanie ofert kredytowych

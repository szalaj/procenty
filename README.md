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
| `bank_centralny` | Ogólny bank centralny dla symulacji krokowych: emisja pieniądza, stopa referencyjna, inflacja z równania wymiany (MV=PY), reguła Taylora |
| `mmt` | Państwo w duchu MMT dla symulacji krokowych: wydatek tworzy pieniądz, podatek umarza, inflacja z presji fiskalnej na realne moce, salda sektorowe |

## Szybki start

```python
from procenty.kredyt import Kredyt
from decimal import Decimal
from datetime import datetime

# Kredyt 400k PLN, 35 lat, raty równe
k = Kredyt(
    K=Decimal(400000), N=420,
    r=Decimal("0.076"), marza=Decimal("0.04"),
    start=datetime(2021, 10, 13), rodzajRat='rowne'
)
print(f"XIRR: {k.xirr:.4f}")
print(f"Suma odsetek: {k.podsumowanie['info']['suma_odsetek']} PLN")
```

## Przykłady

Katalog `przyklady/` zawiera skrypty demonstracyjne:
- `kredyt1.py` - kredyty z nadpłatami i porównania
- `inflacja_przyklad.py` - urealnianie wartości
- `gospodarka.py` - model IS-LM + kredyt
- `zasoby.py` - grafy zasobów (prototyp)

## Rozwój

Ocena stanu projektu i kierunki rozwoju: [ROADMAP.md](ROADMAP.md).

## Zastrzeżenie

**Użytkowanie na własną odpowiedzialność.** Ta biblioteka jest narzędziem edukacyjnym i symulacyjnym. Wyniki obliczeń mogą zawierać błędy i nie powinny stanowić podstawy do podejmowania decyzji finansowych. Autor nie ponosi odpowiedzialności za jakiekolwiek straty wynikające z użycia tego oprogramowania. Przed podjęciem decyzji finansowych skonsultuj się z wykwalifikowanym doradcą.

## Licencja

MIT - patrz [LICENSE](LICENSE).

## Autor

szalaj (mszalajski@gmail.com)

"""Testy regresyjne importów create_kredyt.

Historia: w 0.3.x definicja create_kredyt przeniosła się do utils, a
kredyt.py zachował alias kompatybilności. Zachłanny import aliasu na końcu
modułu tworzył cykl, przez co bezpośredni import
procenty.utils.create_kredyt wywalał się na wpół zainicjalizowanym module
(kolejność importów decydowała o awarii). Testy odpalają świeży interpreter,
bo w bieżącym procesie cache modułów maskuje problem.
"""

import subprocess
import sys

import pytest

PRZYPADKI = [
    # (opis, kod importu)
    ("bezpośrednio utils", "from procenty.utils.create_kredyt import create_kredyt"),
    ("alias w kredyt", "from procenty.kredyt import create_kredyt"),
    (
        "utils, potem alias",
        "from procenty.utils.create_kredyt import create_kredyt; "
        "from procenty.kredyt import create_kredyt as ck2; "
        "assert ck2 is create_kredyt",
    ),
    (
        "alias, potem utils",
        "from procenty.kredyt import create_kredyt; "
        "from procenty.utils.create_kredyt import create_kredyt as ck2; "
        "assert ck2 is create_kredyt",
    ),
]


@pytest.mark.parametrize("opis,kod", PRZYPADKI, ids=[p[0] for p in PRZYPADKI])
def test_import_create_kredyt(opis, kod):
    wynik = subprocess.run(
        [sys.executable, "-c", kod], capture_output=True, text=True
    )
    assert wynik.returncode == 0, f"{opis}: {wynik.stderr}"

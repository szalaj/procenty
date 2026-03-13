import datetime as dt
from decimal import ROUND_HALF_UP, Decimal

import pytest

import procenty.inwestycja
import procenty.kredyt


@pytest.fixture
def kredyt1():
    return procenty.kredyt.Kredyt(
        Decimal(4000), 30, Decimal(0.1), Decimal(0.1), dt.datetime(2021, 1, 1), "rowne"
    )


@pytest.fixture
def kredyt2():
    return procenty.kredyt.Kredyt(
        Decimal(40000),
        320,
        Decimal(0.1),
        Decimal(0.1),
        dt.datetime(2021, 1, 1),
        "rowne",
    )


def test_check_raty(kredyt1):
    print(len(kredyt1.raty))
    assert len(kredyt1.raty) == 30


def test_porownaj_rrso(kredyt2):
    rrso = procenty.inwestycja.RRSO(
        float(kredyt2.Kstart), kredyt2.raty, 10
    ).oblicz_rrso()
    assert abs(rrso - kredyt2.xirr) < 0.0001

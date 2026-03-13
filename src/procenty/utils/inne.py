import datetime


def liczba_dni_w_roku(rok: int) -> int:
    """Zwraca liczbę dni w roku zgodnie z regułą kalendarza gregoriańskiego.

    Rok jest przestępny, gdy:
    - jest podzielny przez 4, ALE
    - nie jest podzielny przez 100, CHYBA ŻE
    - jest podzielny przez 400.
    """
    if (rok % 4 == 0 and rok % 100 != 0) or rok % 400 == 0:
        return 366
    return 365


def diff_month(d1: datetime.datetime, d2: datetime.datetime) -> int:
    """Zwraca różnicę w miesiącach między dwoma datami."""
    return (d1.year - d2.year) * 12 + d1.month - d2.month

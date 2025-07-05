def liczba_dni_w_roku(rok):
    if rok % 4 == 0:
        dni_rok = 366
    else:
        dni_rok = 365

    return dni_rok


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

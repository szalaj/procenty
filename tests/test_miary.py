from procenty.miary import LiczbaDni


def test_dni1():
    dni = LiczbaDni("2024-01-01", "2024-01-02")
    assert dni.dni_odsetkowe == 1


def test_dni2():
    dni = LiczbaDni("2019-01-01", "2025-07-05")
    assert dni.dni_odsetkowe == 2377

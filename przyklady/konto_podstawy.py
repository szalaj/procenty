"""
Przykład 1: Podstawy systemu księgowego - Zapis i Konto.

Pokazuje tworzenie kont, dodawanie zapisów księgowych,
obliczanie sald i przeglądanie historii.
"""

from datetime import datetime
from procenty.konto import Zapis, Konto

if __name__ == "__main__":
    teraz = datetime(2025, 1, 1)

    # --- Tworzenie konta i dodawanie zapisów ---
    kasa = Konto("Kasa", "PLN")

    # Wpłata początkowa (Ma = przychód)
    kasa.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=10000.0, opis="Wpłata początkowa"))

    # Przychód ze sprzedaży w kolejnych miesiącach
    kasa.dodaj_zapis(Zapis(t_symulacji=2, tr_rzeczywisty=teraz, ma=3000.0, opis="Sprzedaż - styczeń"))
    kasa.dodaj_zapis(Zapis(t_symulacji=3, tr_rzeczywisty=teraz, ma=4500.0, opis="Sprzedaż - luty"))
    kasa.dodaj_zapis(Zapis(t_symulacji=4, tr_rzeczywisty=teraz, ma=2800.0, opis="Sprzedaż - marzec"))

    # Wydatki (Winien = rozchód)
    kasa.dodaj_zapis(Zapis(t_symulacji=2, tr_rzeczywisty=teraz, winien=1500.0, opis="Czynsz"))
    kasa.dodaj_zapis(Zapis(t_symulacji=3, tr_rzeczywisty=teraz, winien=2000.0, opis="Wynagrodzenia"))
    kasa.dodaj_zapis(Zapis(t_symulacji=4, tr_rzeczywisty=teraz, winien=800.0, opis="Media"))

    print(kasa)

    # --- Saldo na koniec każdego okresu ---
    for t in range(1, 5):
        ma, winien = kasa.rachunek_biezacy(t)
        saldo = kasa.saldo(t)
        print(f"  Okres {t}: Ma={ma:>10.2f}, Winien={winien:>10.2f}, Saldo={saldo:>10.2f}")

    # --- Historia sald ---
    print("\nHistoria sald:")
    historia = kasa.historia_sald([1, 2, 3, 4])
    for okres, saldo in historia.items():
        print(f"  Okres {okres}: {saldo:>10.2f} PLN")

    # --- Zapisy w okresie ---
    print("\nZapisy w okresie 2-3:")
    for z in kasa.zapisy_w_okresie(2, 3):
        strona = f"Ma={z.ma}" if z.ma > 0 else f"Winien={z.winien}"
        print(f"  t={z.t_symulacji}: {strona:>15} | {z.opis}")

    # --- Transakcja między kontami ---
    print("\n--- Transakcja między kontami ---")
    konto_firmowe = Konto("Firmowe", "PLN")
    konto_firmowe.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=50000.0))

    konto_podatkowe = Konto("Podatki", "PLN")

    # Zapłata podatku: pieniądze z konta firmowego -> konto podatkowe
    Konto.transakcja(
        konto_ma=konto_podatkowe,
        konto_winien=konto_firmowe,
        kwota=5000.0,
        t_symulacji=2,
        tr_rzeczywisty=teraz,
        opis="Zapłata VAT",
    )

    print(f"  Konto firmowe, saldo po podatku: {konto_firmowe.saldo(2):.2f} PLN")
    print(f"  Konto podatkowe, saldo: {konto_podatkowe.saldo(2):.2f} PLN")

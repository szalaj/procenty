"""
Przykład 3: Sieć agentów - symulacja prostej gospodarki.

Trzy firmy (Kopalnia, Huta, Fabryka) tworzą łańcuch dostaw:
  Kopalnia -> rudy -> Huta -> stal -> Fabryka -> maszyny

Każda firma płaci dostawcy i sprzedaje dalej.
Na końcu podsumowanie sald całej gospodarki.
"""

from datetime import datetime

from procenty.konto import Agent, Konto, SiecAgentow, Zapis

if __name__ == "__main__":
    teraz = datetime(2025, 1, 1)

    # === Budowa sieci agentów ===
    gospodarka = SiecAgentow("Łańcuch dostaw")

    # Kopalnia: wydobywa rudę, posiada pieniądze
    kopalnia = Agent("Kopalnia")
    k_ruda = Konto("ruda", "tony")
    k_ruda.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=1000.0, opis="Wydobycie")
    )
    kopalnia.dodaj_konto(k_ruda)
    k_pln_kop = Konto("PLN", "PLN")
    k_pln_kop.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=50000.0))
    kopalnia.dodaj_konto(k_pln_kop)
    gospodarka.dodaj_agenta(kopalnia)

    # Huta: przetwarza rudę na stal
    huta = Agent("Huta")
    huta.dodaj_konto(Konto("ruda", "tony"))
    k_stal = Konto("stal", "tony")
    k_stal.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=200.0, opis="Zapas stali")
    )
    huta.dodaj_konto(k_stal)
    k_pln_huta = Konto("PLN", "PLN")
    k_pln_huta.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=100000.0))
    huta.dodaj_konto(k_pln_huta)
    gospodarka.dodaj_agenta(huta)

    # Fabryka: produkuje maszyny ze stali
    fabryka = Agent("Fabryka")
    fabryka.dodaj_konto(Konto("stal", "tony"))
    k_maszyny = Konto("maszyny", "szt")
    k_maszyny.dodaj_zapis(
        Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=50.0, opis="Zapas maszyn")
    )
    fabryka.dodaj_konto(k_maszyny)
    k_pln_fab = Konto("PLN", "PLN")
    k_pln_fab.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=200000.0))
    fabryka.dodaj_konto(k_pln_fab)
    gospodarka.dodaj_agenta(fabryka)

    print(f"{gospodarka}")
    print(f"Agenci: {gospodarka.lista_agentow()}")

    # === Stan początkowy ===
    print("\n=== Stan początkowy (t=1) ===")
    salda = gospodarka.wszystkie_salda(1)
    for agent_nazwa, konta in salda.items():
        print(f"  {agent_nazwa}:")
        for konto_nazwa, saldo in konta.items():
            if saldo != 0:
                print(f"    {konto_nazwa}: {saldo}")

    # === Runda 1 (t=2): Kopalnia sprzedaje rudę Hucie ===
    # Wymiana: Kopalnia daje 100t rudy, Huta płaci 20000 PLN
    print("\n--- t=2: Kopalnia sprzedaje 100t rudy Hucie za 20000 PLN ---")
    gospodarka.wymiana(
        nazwa_agenta_oddajacego="Kopalnia",
        nazwa_produktu_oddawanego="ruda",
        ilosc_oddawana=100.0,
        nazwa_agenta_otrzymujacego="Huta",
        nazwa_produktu_otrzymywanego="PLN",
        ilosc_otrzymywana=20000.0,
        t_symulacji=2,
        tr_rzeczywisty=teraz,
    )

    # === Runda 2 (t=3): Huta przetwarza rudę na stal (wymiana wewnętrzna) ===
    print("--- t=3: Huta przetwarza 100t rudy na 50t stali ---")
    huta.wymiana(
        nazwa_konta_oddawanego="ruda",
        ilosc_oddawana=100.0,
        nazwa_konta_otrzymywanego="stal",
        ilosc_otrzymywana=50.0,
        t_symulacji=3,
        tr_rzeczywisty=teraz,
        opis="Przetop rudy na stal",
    )

    # === Runda 3 (t=4): Huta sprzedaje stal Fabryce ===
    print("--- t=4: Huta sprzedaje 50t stali Fabryce za 40000 PLN ---")
    gospodarka.wymiana(
        nazwa_agenta_oddajacego="Huta",
        nazwa_produktu_oddawanego="stal",
        ilosc_oddawana=50.0,
        nazwa_agenta_otrzymujacego="Fabryka",
        nazwa_produktu_otrzymywanego="PLN",
        ilosc_otrzymywana=40000.0,
        t_symulacji=4,
        tr_rzeczywisty=teraz,
    )

    # === Runda 4 (t=5): Fabryka produkuje maszyny ze stali ===
    print("--- t=5: Fabryka zamienia 50t stali na 25 maszyn ---")
    fabryka.wymiana(
        nazwa_konta_oddawanego="stal",
        ilosc_oddawana=50.0,
        nazwa_konta_otrzymywanego="maszyny",
        ilosc_otrzymywana=25.0,
        t_symulacji=5,
        tr_rzeczywisty=teraz,
        opis="Produkcja maszyn",
    )

    # === Stan końcowy ===
    print("\n=== Stan końcowy (t=10) ===")
    salda = gospodarka.wszystkie_salda(10)
    for agent_nazwa, konta in salda.items():
        print(f"  {agent_nazwa}:")
        for konto_nazwa, saldo in konta.items():
            if saldo != 0:
                print(f"    {konto_nazwa}: {saldo}")

    # === Śledzenie historii sald ===
    print("\n=== Historia salda PLN Kopalni ===")
    historia = kopalnia.pobierz_konto("PLN").historia_sald([1, 2, 3, 4, 5])
    for okres, saldo in historia.items():
        print(f"  t={okres}: {saldo:>10.2f} PLN")

    print("\n=== Historia salda PLN Huty ===")
    historia = huta.pobierz_konto("PLN").historia_sald([1, 2, 3, 4, 5])
    for okres, saldo in historia.items():
        print(f"  t={okres}: {saldo:>10.2f} PLN")

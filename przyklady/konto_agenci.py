"""
Przykład 2: Agenci ekonomiczni - wymiana, transfer, handel.

Symulacja prostej gospodarki: rolnik, piekarz i sklep
wymieniają się towarami i pieniędzmi.
"""

from datetime import datetime
from procenty.konto import Zapis, Konto, Agent

if __name__ == "__main__":
    teraz = datetime(2025, 1, 1)

    # === Tworzenie agentów z kontami ===

    # Rolnik: ma zboże i pieniądze
    rolnik = Agent("Rolnik")
    k_zboze = Konto("zboze", "tony")
    k_zboze.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=100.0, opis="Zbiory"))
    rolnik.dodaj_konto(k_zboze)

    k_pln_rolnik = Konto("PLN", "PLN")
    k_pln_rolnik.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=5000.0, opis="Oszczędności"))
    rolnik.dodaj_konto(k_pln_rolnik)

    # Rolnik potrzebuje też konta na mąkę (żeby mógł ją otrzymać w wymianie)
    rolnik.dodaj_konto(Konto("maka", "tony"))

    # Piekarz: ma mąkę, chleb i pieniądze
    piekarz = Agent("Piekarz")
    k_maka = Konto("maka", "tony")
    k_maka.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=20.0, opis="Zapas mąki"))
    piekarz.dodaj_konto(k_maka)

    k_chleb = Konto("chleb", "szt")
    k_chleb.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=500.0, opis="Wypiek"))
    piekarz.dodaj_konto(k_chleb)

    k_pln_piekarz = Konto("PLN", "PLN")
    k_pln_piekarz.dodaj_zapis(Zapis(t_symulacji=1, tr_rzeczywisty=teraz, ma=10000.0))
    piekarz.dodaj_konto(k_pln_piekarz)

    # Piekarz potrzebuje konta na zboże
    piekarz.dodaj_konto(Konto("zboze", "tony"))

    print("=== Stan początkowy ===")
    for agent in [rolnik, piekarz]:
        print(f"\n{agent}")
        for nazwa in agent.lista_nazw_kont():
            s = agent.saldo_konta(nazwa, 1)
            if s != 0:
                print(f"  {nazwa}: {s}")

    # === Wymiana między agentami ===
    # Rolnik sprzedaje 10 ton zboża piekarzowi za 5 ton mąki
    print("\n=== Wymiana: Rolnik daje 10t zboża, Piekarz daje 5t mąki ===")
    Agent.wymiana_miedzy_agentami(
        agent_oddajacy=rolnik,
        nazwa_produktu_oddawanego="zboze",
        ilosc_oddawana=10.0,
        agent_otrzymujacy=piekarz,
        nazwa_produktu_otrzymywanego="maka",
        ilosc_otrzymywana=5.0,
        t_symulacji=2,
        tr_rzeczywisty=teraz,
    )

    print(f"  Rolnik - zboże: {rolnik.saldo_konta('zboze', 3)}")  # 100 - 10 = 90
    print(f"  Rolnik - mąka:  {rolnik.saldo_konta('maka', 3)}")   # 0 + 5 = 5
    print(f"  Piekarz - zboże: {piekarz.saldo_konta('zboze', 3)}") # 0 + 10 = 10
    print(f"  Piekarz - mąka:  {piekarz.saldo_konta('maka', 3)}")  # 20 - 5 = 15

    # === Transfer (jednostronny) ===
    # Piekarz przekazuje 2000 PLN rolnikowi (zapłata za dostawę)
    print("\n=== Transfer: Piekarz płaci Rolnikowi 2000 PLN ===")
    piekarz.transfer(
        nazwa_konta_oddawanego="PLN",
        ilosc=2000.0,
        agent_otrzymujacy=rolnik,
        nazwa_konta_otrzymywanego="PLN",
        t_symulacji=3,
        tr_rzeczywisty=teraz,
        opis="Zapłata za zboże",
    )

    print(f"  Rolnik - PLN:  {rolnik.saldo_konta('PLN', 4)}")   # 5000 + 2000 = 7000
    print(f"  Piekarz - PLN: {piekarz.saldo_konta('PLN', 4)}")   # 10000 - 2000 = 8000

    # === Wymiana wewnętrzna agenta ===
    # Piekarz wymienia 5 ton mąki na 200 sztuk chleba (produkcja)
    print("\n=== Produkcja: Piekarz zamienia 5t mąki -> 200 szt chleba ===")
    piekarz.wymiana(
        nazwa_konta_oddawanego="maka",
        ilosc_oddawana=5.0,
        nazwa_konta_otrzymywanego="chleb",
        ilosc_otrzymywana=200.0,
        t_symulacji=4,
        tr_rzeczywisty=teraz,
        opis="Wypiek chleba",
    )

    print(f"  Piekarz - mąka:  {piekarz.saldo_konta('maka', 5)}")   # 15 - 5 = 10
    print(f"  Piekarz - chleb: {piekarz.saldo_konta('chleb', 5)}")   # 500 + 200 = 700

    # === Podsumowanie końcowe ===
    print("\n=== Stan końcowy ===")
    for agent in [rolnik, piekarz]:
        salda = agent.wszystkie_salda(10)
        print(f"\n{agent.nazwa}:")
        for nazwa_konta, saldo in salda[agent.nazwa].items():
            if saldo != 0:
                print(f"  {nazwa_konta}: {saldo}")

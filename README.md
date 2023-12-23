# procenty

- symulacja kredytu mieszkaniowego
- symulacja wymiany handlowej
- symulacja kreacji pieniądza

# procenty

obliczenia kredytu z ratą malejącą przy zmiennym oprocentowaniu i nadpłatach.

Dodatkowo
 - realna wartosc nieruchomości w czasie
 - lokaty, obligacje
 - porównanie strategii, np. czy lokata czy nadpłata

 # Kredyt

 Wybierz model kredytu
    - K
    - N
    - data uruchomienia
    - daty spłaty
    - rodzaj rata (stała/malejąca)
    - oprocentowanie
    - nadplaty
    - sposob rozliczania nadplat


    Wszystkie dane powinny być zapisane do modelu

    1. ModelKredyt
    2. Kredyt : Obliczenia danych kredytu podstawowych (ModelKredyt) 

  ![alt text](docs/rys1.png)

Celem program jest obliczenie sald kredytu $$S = (s_0, s_1, s_2, ..., s_i, ..., s_N)$$  w czasach $$T = (t_0, t_1, ..., t_i, ..., t_N)$$ kiedy płacone są raty $$R = (r_1, r_2, ..., r_i, ..., r_N)$$
Czasy $T$ tworzą ciąg niemalejący, niekoniecznie o równych odstępach czasowych (kredytobiorca może zmieniać datę spłaty).
W czasie $t_0$ następuje wypłata kredytu, i zaczynają być naliczanie odsetki (dzień po dniu). W czasach $t_i$, $t_2$, ... $t_i$, $t_N$ płacone są raty. Ponieważ warunki kredytu mogą się zmieniać (oprocentowanie, nadpłaty, kary), po każdej płatności raty ponownie obliczany jest ciąg rat $R$. Po ostatniej racie $r_N$ saldo kredytu powinno wynieść $0$.


# Model

Istnieje zbiór konsumentów C. Konsumenci wymieniają się dobrami. Jednym z dobrem jest pieniądz. Oprócz konsumentów istnieje również Rząd - G oraz Bank - B.

## Zasoby

W gospodarce istnieją zasoby początkowe. Ich struktura określa możliwe ścieżki rozwoju.

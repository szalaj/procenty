# procenty

- obliczanie raty równej i malejącej kredytu hipotecznego

# założenia

Kwota udzielona K w czasie Ts.
Spłata w N ratach miesięcznych.
Oprocentowanie zmienne.

Dodatkowo
 - realna wartosc nieruchomości w czasie
 - lokaty, obligacje
 - porównanie strategii, np. czy lokata czy nadpłata

 # Model Kredytu

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

  ![alt text](docs_img/rys1.png)

Celem program jest obliczenie sald kredytu $$S = (s_0, s_1, s_2, ..., s_i, ..., s_N)$$  w czasach $T = (t_0, t_1, ..., t_i, ..., t_N)$ kiedy płacone są raty $$R = (r_1, r_2, ..., r_i, ..., r_N)
Czasy $T$ tworzą ciąg niemalejący, niekoniecznie o równych odstępach czasowych (kredytobiorca może zmieniać datę spłaty).
W czasie $t_0$ następuje wypłata kredytu, i zaczynają być naliczanie odsetki (dzień po dniu). W czasach $t_i$, $t_2$, ... $t_i$, $t_N$ płacone są raty. Ponieważ warunki kredytu mogą się zmieniać (oprocentowanie, nadpłaty, kary), po każdej płatności raty ponownie obliczany jest ciąg rat $R$. Po ostatniej racie $r_N$ saldo kredytu powinno wynieść $0$.


# Model Lokaty

    3. Opcjonalnie : Obliczenie Lokat (ModelLokata)
    4. Opcjonalnie, bbliczenia danych rzeczywistych

# Model Nieruchomości

    Jak zmienia się wartość nieruchomości w czasie

# Portfel

Podsumowanie powyższych. Na tej podstawie można wybrać najlepszy sposób postępowania dla kredytobiorcy.
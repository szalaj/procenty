# procenty
symulacja kredytu mieszkaniowego

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

## Uruchomienie modelu

```
$ python proc.py -m nazwa_modelu
```

`nazwa_modelu` to plik `.yaml` znajdujący się w katalogu `./models`.
 
 składa się z następujących części:

 1. `K` - kapitał kredytu
 2. `start` - data uruchomienia kredytu (start naliczania odsetek)
 3. `p` - początkowa stopa procentowa kredytu
 4. lista `daty_splaty` - dni w których następuję płatność raty. Ich suma tworzy `N` - liczbę rat.
 5. opcjanalna lista zmian oprocentowania `oprocentowanie`. Każdy element listy zawiera dwie pozycje:
  - `dzien` zmiany oprocenotowania
  - `proc` nowa stopa procentowa
 6. opcjonalna lista nadpłat `nadplaty`. Każdy element listy zawiera dwie pozycje:
  - `dzien` nadpłaty
  - `kwota` nadpłaty

Przykład:
```
---
K: 460000
start: '2022-11-04'
p: 4.9

daty_splaty:
  - '2022-12-04'
  - '2023-01-04'
  - '2023-02-04'
  - '2023-03-04'
  - '2023-04-04'
...

oprocentowanie:
  - dzien: '2023-12-14'
    proc: 10.46
  - dzien: '2026-09-13'
    proc: 12

nadplaty:
  - dzien: '2023-11-03'
    kwota: 20000
  - dzien: '2025-07-01'
    kwota: 20000
    ```
## generacja modelu

p:k:r:o:s:',  ["plik=", "kapital=", "oprocentowanie=", "okresy=", "startdate="])

python generate_model.py -p nowy_model.yml -k 450000 -r 10 -o 352 -s 2022-12-28

python proc.py -m nowy_model



Jest ustalany i publikowany przez GWP Benchmark.

Dostęp do danych jest utrudniony.

Miał być ustalany na podstawie rzeczywistych transakcji a tych nie ma.

Definiuje go rozporządzenie unijne.

Wysoki Wibor sprzyja rządowi w walce z inflacją.

1. Jak to działa w innych państwach?

https://stooq.pl/q/d/l/?s=plopln6m&i=d


@ to do

- wykres rat
- wykres wiboru

dla dwóch scenariuszy.

-----------------------


5.1. Administrator wyznacza Stawki Referencyjne zgodnie z Metodą Ustalania Stawek
Referencyjnych, w oparciu o Kwotowania przekazywane Administratorowi przez Uczestników
Fixingu w ramach Fixingu.

wyznaczony pracownik Uczestnika Fixingu odpowiedzialny za
przekazanie Kwotowania Wiążącego lub Kwotowania
Modelowego

Kwotowania Wiążące a Kwotowania Modelowe

Dni fixingowe

Fixing = proces ustalenia Stawek Referencyjnych przez Administratora

Kwotowanie=Kwotowanie Modelowe i Kwotowanie Wiążące stanowiące dla
Administratora Dane Wejściowe, na podstawie których Administrator zgodnie z Metodą Ustalania Stawek
Referencyjnych przeprowadza Fixing Stawek Referencyjnych dla
poszczególnych Terminów Fixingowych


Kwotowanie Modelowe=stopa procentowa, po jakiej Uczestnik Fixingu mógłby przyjąć
(Kwotowanie Modelowe stawki bid) lub złożyć (Kwotowanie
Modelowe stawki offer) Depozyt na Rynku Bazowym na każdy z
Terminów Fixingowych, ustalana przez Uczestnika Fixingu
zgodnie z warunkami określonymi w Kodeksie Postępowania na
podstawie Danych Transakcyjnych zgodnie z Metodą Kaskady
Danych, stanowiąca wynik działania poziomu 1,2 lub 3 Metody
Kaskady Danych

Kwotowanie Podejrzane=Kwotowanie, w stosunku do którego istnieje podejrzenie
manipulacji w rozumieniu MAR

Kwotowanie Wiążące=Kwotowanie określające stopę procentową, po jakiej Uczestnik
Fixingu jest, zgodnie z warunkami określonymi w Kodeksie
Postępowania, w wiążący sposób gotowy złożyć (Kwotowanie
Wiążące stawki offer) lub przyjąć Depozyt (Kwotowanie Wiążące
stawki bid) od innego Uczestnika Fixingu na każdy z Terminów
Fixingowych, stanowiące jednocześnie wynik działania poziomu
4 Kaskady Danych

Kwotowanie Podejrzane=Kwotowanie, w stosunku do którego istnieje podejrzenie
manipulacji w rozumieniu MAR 

MAR=Rozporządzenie Parlamentu Europejskiego i Rady (UE)
nr 596/2014 z dnia 16 kwietnia 2014 r. w sprawie nadużyć na
rynku (rozporządzenie w sprawie nadużyć na rynku) oraz
uchylające dyrektywę 2003/6/WE Parlamentu Europejskiego
i Rady i dyrektywy Komisji 2003/124/WE, 2003/125/WE
i 2004/72/WE


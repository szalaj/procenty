
wymagania dotyczące zasoby.py

Zasady rozgrywki "Zasoby"

1. Istnieją zony, czyli obszary geograficzne, z1, z2, ..., zi, ..zn.
2. Istnieją zasoby podstawowe (resources), r1, r2, .., ri, .., rn.
3. Zasoby są przydzielane do zon losowo na początku rozgrywki.
4. Zasób r1 jest energią.
5. Zasoby mogą być przetwarzane na zasoby złożone. np. r2 i r3 mogą stworzyć zasób r2r3.
6. Każde stworzenie zasobu złożonego wymaga energii (r1).
7. Możliwe zasoby złożone oraz ilość energii potrzebnej do stworzenia zasobu złożonego jest przedstawione w tabeli T1.
8. Każdy zasób ma odpowiednią wartość. Wartość jest podawana w liczbach. Jednostką wartości jest V (value). Wartość każdego zasobu jest przedstawiona w tabeli T1.
9. Celem rozgrywki jest dla każdej zony zmaksymalizować wartość posiadanych zasobów.


:T1
|   zasób   | kompotenty | koszt stworzenia w r1 | wartość |
| --------- | ---------- | --------------------- | ------- |
| r1        |            | 0                     | 10      |
| r2        |            | 0                     | 5       |
| r3        |            | 0                     | 7       |
| r1r2      | r1,r2      | 1                     | 20      |
| r1r3      | r1,r3      | 12                    | 30      |
| r1r2.r1r3 | r1r2, r1r3 | 40                    | 140     |



# TO DO 

1. stworzenie Obszaru
a. utworzenie Zon
b. określenie połączeń między nimi (długość, trudność transportu, itp.)

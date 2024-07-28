
# 1. Przydziel zasoby
# 2 (pętla decyzyjna). Wyprodukuj zasoby, wymień zasoby
# 3. Skonsumuj zasoby
# 4. Jeśli zostałem zabity lub jestem jedynym żywym, zakończ. Jeśli nie, wróć do 2.


from procenty.symulacja import Panstwo


if __name__ == '__main__':
    polska = Panstwo(28, 100,200,300)
    niemcy = Panstwo(80, 200,300,100)
    polska.polacz(niemcy)

    if polska.sila > niemcy.sila:
        print("Polska wygrała")
    else:
        print("Niemcy wygrały")

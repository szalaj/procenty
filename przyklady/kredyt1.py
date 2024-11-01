from procenty.kredyt import Kredyt, Zdarzenie, Rodzaj
from datetime import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import networkx as nx
from procenty.podmioty import Podmiot, Menadzer


k = Kredyt(Decimal(400000), 420, Decimal(0.076), Decimal(0.04), datetime(2021, 10, 1), 'rowne')

datetimes = [datetime(2021, 11, 1) + relativedelta(months=i) for i in range(420)]
for dzien_splaty in datetimes:
    k.zdarzenia.append(Zdarzenie(dzien_splaty, Rodzaj.SPLATA, 0))

wynik = k.symuluj()


headers = wynik['raty'][0].keys()
rows = [list(item.values()) for item in wynik['raty']]


mg = Menadzer('2022-10')

p1 = Podmiot('2022-10','A', mg)
p2 = Podmiot('2022-10','B', mg)


mg.dodaj_przeplyw(p2, p1, typ='przeplyw', czas='2022-10', kwota=1112050)

for r in rows:
    rata=r[6]
    kiedy=r[0]

    mg.dodaj_przeplyw(p1, p2, typ='przeplyw', czas=kiedy, kwota=rata)

mg.sim()

print(p1.konto)
print(p2.konto)
from procenty.proc import Kredyt, Zdarzenie, Rodzaj
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from tabulate import tabulate



k = Kredyt(Decimal(10000), 12, Decimal(0.03), Decimal(0.01), datetime(2020, 12, 11), 'rowne')



datetimes = [datetime(2021, 1, 1) + relativedelta(months=i) for i in range(20)]
for dzien_splaty in datetimes:
    k.zdarzenia.append(Zdarzenie(dzien_splaty, Rodzaj.SPLATA, 0))

wynik = k.symuluj()
# print(wynik['raty'][0].keys())

headers = wynik['raty'][0].keys()
rows = [list(item.values()) for item in wynik['raty']]

# Print the table
print(tabulate(rows, headers=headers, tablefmt="grid"))
# R = []
# for r in wynik['raty']:
#     R.append(r['rata'])
# print(R)
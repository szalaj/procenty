import procenty.proc
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP

k = procenty.proc.Kredyt(Decimal(1000), 12, Decimal(0.01), Decimal(0.01), dt.datetime(2020, 12, 11), 'rowne')
wynik = k.symuluj()
print(wynik)
R = []
for r in wynik['raty']:
    R.append(r['rata'])
print(R)
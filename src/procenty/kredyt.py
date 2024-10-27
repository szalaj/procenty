import datetime as dt
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


class Zloty:
    '''Klasa do obsługi kwot w złotówkach.
    
    Argumenty:
    
    kwota -- kwota w złotówkach
    '''
    def __init__(self, kwota: float):
        self.kwota = kwota

    def __add__(self, other):
        return Zloty(self.kwota + other.kwota)

    def __sub__(self, other):
        return Zloty(self.kwota - other.kwota)

    def __mul__(self, other):
        return Zloty(self.kwota * other)

    def __truediv__(self, other):
        return Zloty(self.kwota / other)

    def __str__(self):
        return f'{self.kwota} zł'

    def __repr__(self):
        return f'{self.kwota} zł'

    def __eq__(self, other):
        return self.kwota == other.kwota

    def __lt__(self, other):
        return self.kwota < other.kwota

    def __le__(self, other):
        return self.kwota <= other.kwota

    def __gt__(self, other):
        return self.kwota > other.kwota

    def __ge__(self, other):
        return self.kwota >= other.kwota

    def __ne__(self, other):
        return self.kwota != other.kwota

@dataclass
class KredytSuwak:

    kwota: Zloty
    okres: int

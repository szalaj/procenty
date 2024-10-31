"""\
Moduł z klasami miar finansowych.



"""
import pendulum
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Odleglosc:
    """Liczy dni do np. wyliczania odsetek.

    Bierze pod uwagę liczbę dni w latach przestępnych.

    Argumenty:
    start -- data w formacie YYYY-MM-DD
    koniec -- data w formacie YYYY-MM-DD
    """
    start : str
    koniec : str
    flaga : str

    def __post_init__(self):
        dt_start = pendulum.from_format(self.start, 'YYYY-MM-DD')
        dt_koniec = pendulum.from_format(self.koniec, 'YYYY-MM-DD')

        if dt_start > dt_koniec:
            raise Exception('Dzien start > Dzien koniec')

      
        self._dni_odsetkowe = dt_koniec.diff(dt_start).in_days()

        mnoznik = 0

        if dt_start.year==dt_koniec.year:
            mnoznik = self._dni_odsetkowe / liczba_dni(dt_start.year)
        else:
            for rok in range(dt_start.year, dt_koniec.year+1):
                if rok==dt_start.year:
                    mnoznik += pendulum.datetime(dt_start.year+1, 1, 1).diff(dt_start).in_days()/liczba_dni(dt_start.year)
                elif rok==dt_koniec.year:
                    mnoznik += dt_koniec.diff(pendulum.datetime(dt_koniec.year, 1, 1)).in_days()/liczba_dni(dt_koniec.year)
                else:
                    mnoznik += 1

        self._mnoznik = mnoznik
                 
            

    @property
    def dni_odsetkowe(self):
	    return self._dni_odsetkowe
    

    @property
    def mnoznik(self)->Decimal:
        return Decimal(self._mnoznik)
    
def liczba_dni(rok):
    if rok%4==0:
        liczba_dni = 366
    else:
        liczba_dni = 365
    return liczba_dni


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
"""\
Moduł z klasami miar finansowych.



"""
import pendulum
from dataclasses import dataclass

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

      
        self._dni_odsetkowe = dt_koniec.diff(dt_start).in_days()

    @property
    def dni_odsetkowe(self):
	    return self._dni_odsetkowe
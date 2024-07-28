
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Panstwo:
    ludnosc: int
    zasob_a: int
    zasob_b: int
    zasob_c: int
    polaczenia: Optional[list] = field(default_factory=list)
    _sila: Optional[float] = 0

    def polacz(self, pan):
        self.polaczenia.append(pan)
        pan.polaczenia.append(self)

    @property  
    def sila(self):
        self._sila = (self.zasob_a + self.zasob_b*2 + self.zasob_c*3)*self.ludnosc
        return self._sila



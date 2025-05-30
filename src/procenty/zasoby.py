import numpy as np
import random
from dataclasses import dataclass

# tutaj będą klasy związane z obsługą podstawywych obszarów gospodarczych - zon


class Zona:
    pass

class HexZona(Zona):
    pass

@dataclass
class GPol:
    name: str
    value: int = 0


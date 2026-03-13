"""
1. krzywa typu splajn posiada punkt startowy, końcowy, oraz punkty pośrednie
2. do każdego punktu przypisany jest timestamp oraz wartość
3. krzywą można interpolować
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Tuple, Union

import numpy as np
from dateutil.relativedelta import relativedelta
from scipy.interpolate import CubicSpline, interp1d

from procenty.utils import diff_month


@dataclass
class Krzywa:

    punkty: List[Tuple[datetime, float]]

    def __post_init__(self) -> None:

        self.punkty.sort(key=lambda x: x[0])

        self.start: datetime = self.punkty[0][0]
        self.end: datetime = self.punkty[-1][0]

        self.timestamps: np.ndarray = np.array(
            [dt.timestamp() for dt, _ in self.punkty]
        )
        self.values: np.ndarray = np.array([val for _, val in self.punkty])

        spline: CubicSpline = CubicSpline(self.timestamps, self.values)

        # Generate points for smooth plot
        self.timestamps_smooth: np.ndarray = np.linspace(
            self.timestamps.min(), self.timestamps.max(), 500
        )
        self.values_smooth: np.ndarray = spline(self.timestamps_smooth)

        self.interpolation_function: interp1d = interp1d(
            self.timestamps_smooth, self.values_smooth
        )

    def __repr__(self) -> str:
        return f"Krzywa({self.start}, {self.end}, {self.punkty})"

    def __mul__(self, inflator: Any) -> Union[List[Tuple[datetime, float]], Any]:
        from procenty.inflacja import Inflacja

        if isinstance(inflator, Inflacja):

            wynik: List[Tuple[datetime, float]] = []
            punkty_miesiac: List[Tuple[datetime, float]] = self.podzial_miesiac()

            for punkt in punkty_miesiac:
                wartosc_inflator: float = inflator.urealnij(punkt[0], punkt[1])
                wynik.append((punkt[0], wartosc_inflator))

            return wynik
        return NotImplemented

    @property
    def splajn(self) -> List[Tuple[float, float]]:
        return list(zip(self.timestamps_smooth, self.values_smooth))

    @property
    def punkty_zip(self) -> List[Tuple[float, float]]:
        return list(zip(self.timestamps, self.values))

    def podzial(self, okres_dni: int) -> List[Tuple[datetime, float]]:
        """
        Dzieli krzywą na okresy o długości okres_dni
        """

        dajs: List[datetime] = [
            self.start + relativedelta(days=(i + 1) * okres_dni)
            for i in range(int((self.end - self.start).days / okres_dni))
        ]
        opr: List[Tuple[datetime, float]] = [
            (d, self.interpolation_function(d.timestamp()).item()) for d in dajs
        ]

        return opr

    def podzial_miesiac(self) -> List[Tuple[datetime, float]]:
        """
        Na razie dzieli na miesace biorac konkretny dzień.
        Trzeba zrobić uśrednienie z całego miesiąca.
        """
        dajs: List[datetime] = [self.start]
        dajs.extend(
            [
                self.start + relativedelta(months=(i + 1))
                for i in range(diff_month(self.end, self.start))
            ]
        )
        opr: List[Tuple[datetime, float]] = [
            (d, self.interpolation_function(d.timestamp()).item()) for d in dajs
        ]

        return opr

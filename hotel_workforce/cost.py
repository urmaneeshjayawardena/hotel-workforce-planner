"""Section 1: daily cost of housekeepers and overtime, minimised by calculus.

C(x, y) = 2x^2 + 3y^2 - 2xy - a*x - b*y + c   (thousand LKR per day)
x = regular housekeepers, y = overtime hours.
"""

import math
from dataclasses import dataclass

from .params import HotelParams

C_XX = 4
C_YY = 6
C_XY = -2


@dataclass(frozen=True)
class CostOptimum:
    x: float
    y: float
    cost: float
    discriminant: float
    kind: str


@dataclass(frozen=True)
class StaffPlan:
    housekeepers: int
    overtime_hours: int
    cost: float
    penalty: float


def daily_cost(params: HotelParams, x: float, y: float) -> float:
    return 2 * x**2 + 3 * y**2 - 2 * x * y - params.a * x - params.b * y + params.c


def gradient(params: HotelParams, x: float, y: float) -> tuple[float, float]:
    """Partial derivatives (C_x, C_y)."""
    return 4 * x - 2 * y - params.a, 6 * y - 2 * x - params.b


def discriminant() -> float:
    return C_XX * C_YY - C_XY**2


def classify(d: float, c_xx: float) -> str:
    if d > 0:
        return "minimum" if c_xx > 0 else "maximum"
    if d < 0:
        return "saddle"
    return "inconclusive"


def critical_point(params: HotelParams) -> tuple[float, float]:
    """Solve C_x = 0 and C_y = 0 in closed form."""
    x = (3 * params.a + params.b) / 10
    y = (params.a + 2 * params.b) / 10
    return x, y


def optimise(params: HotelParams) -> CostOptimum:
    x, y = critical_point(params)
    d = discriminant()
    return CostOptimum(
        x=x,
        y=y,
        cost=daily_cost(params, x, y),
        discriminant=d,
        kind=classify(d, C_XX),
    )


def best_whole_plan(params: HotelParams) -> StaffPlan:
    """Pick the cheapest whole-number plan next to the continuous optimum.

    Ties are broken by distance to the optimum, so a plain rounding wins
    when it is just as cheap.
    """
    optimum = optimise(params)
    candidates = [
        (x, y)
        for x in {math.floor(optimum.x), math.ceil(optimum.x)}
        for y in {math.floor(optimum.y), math.ceil(optimum.y)}
    ]

    def rank(point):
        x, y = point
        distance = (x - optimum.x) ** 2 + (y - optimum.y) ** 2
        return round(daily_cost(params, x, y), 9), distance

    x, y = min(candidates, key=rank)
    cost = daily_cost(params, x, y)
    return StaffPlan(
        housekeepers=x,
        overtime_hours=y,
        cost=cost,
        penalty=cost - optimum.cost,
    )

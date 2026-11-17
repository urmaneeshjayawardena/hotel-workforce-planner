"""Section 2A: waiters needed through a 12-hour restaurant day.

w(t) = w0 + A*t(12 - t)/36   (waiters, t = hours since opening, 0 <= t <= 12)

t(12 - t)/36 is 0 at opening and closing and reaches 1 at t = 6, so w0 is the
base demand and w0 + A is the peak.
"""

from dataclasses import dataclass

from .params import HotelParams

OPEN_HOURS = 12


@dataclass(frozen=True)
class DemandPeak:
    hour: float
    waiters: float
    curvature: float
    kind: str


def base_demand(params: HotelParams) -> float:
    """w0: waiters needed at opening and closing."""
    return params.base_waiters


def amplitude(params: HotelParams) -> float:
    """A: extra waiters needed at the peak on top of the base."""
    return params.peak_waiters - params.base_waiters


def demand(params: HotelParams, t: float) -> float:
    """w(t): waiters needed t hours after opening."""
    _check_hour(t)
    return base_demand(params) + amplitude(params) * t * (OPEN_HOURS - t) / 36


def demand_rate(params: HotelParams, t: float) -> float:
    """w'(t) = A(12 - 2t)/36: change in waiters needed per hour."""
    _check_hour(t)
    return amplitude(params) * (OPEN_HOURS - 2 * t) / 36


def demand_curvature(params: HotelParams) -> float:
    """w''(t) = -A/18: the same at every hour because w is a parabola."""
    return -amplitude(params) / 18


def critical_hour() -> float:
    """Solve w'(t) = 0: A(12 - 2t)/36 = 0 gives t = 6.

    When A = 0 the curve is flat and every hour is critical; t = 6 is still
    returned so the peak report stays defined.
    """
    return OPEN_HOURS / 2


def classify(curvature: float) -> str:
    if curvature < 0:
        return "maximum"
    if curvature > 0:
        return "minimum"
    return "inconclusive"


def peak(params: HotelParams) -> DemandPeak:
    hour = critical_hour()
    curvature = demand_curvature(params)
    return DemandPeak(
        hour=hour,
        waiters=demand(params, hour),
        curvature=curvature,
        kind=classify(curvature),
    )


def total_staff_hours(params: HotelParams) -> float:
    """Area under w(t) over the day: 12*w0 + 8A.

    The base contributes w0 for all 12 hours. The bump integrates to
    A/36 * [6t^2 - t^3/3] from 0 to 12 = A/36 * (864 - 576) = 8A.
    """
    return OPEN_HOURS * base_demand(params) + 8 * amplitude(params)


def daily_wage_cost(params: HotelParams) -> float:
    """Total staff-hours paid at the hourly wage, in LKR."""
    return total_staff_hours(params) * params.wage_lkr


def _check_hour(t: float) -> None:
    if not 0 <= t <= OPEN_HOURS:
        raise ValueError(f"t must be between 0 and {OPEN_HOURS} hours")

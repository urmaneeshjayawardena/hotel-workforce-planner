"""Section 2A: waiters needed through a 12-hour restaurant day.

w(t) = w0 + A*t(12 - t)/36   (waiters, t = hours since opening, 0 <= t <= 12)

t(12 - t)/36 is 0 at opening and closing and reaches 1 at t = 6, so w0 is the
base demand and w0 + A is the peak.
"""

from .params import HotelParams

OPEN_HOURS = 12


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


def _check_hour(t: float) -> None:
    if not 0 <= t <= OPEN_HOURS:
        raise ValueError(f"t must be between 0 and {OPEN_HOURS} hours")

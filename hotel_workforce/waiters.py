"""Section 2A: waiters needed through a 12-hour restaurant day.

w(t) = w0 + A*t(12 - t)/36   (waiters, t = hours since opening, 0 <= t <= 12)

t(12 - t)/36 is 0 at opening and closing and reaches 1 at t = 6, so w0 is the
base demand and w0 + A is the peak.
"""

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from scipy.integrate import quad

from .params import HotelParams

OPEN_HOURS = 12


@dataclass(frozen=True)
class DemandPeak:
    hour: float
    waiters: float
    curvature: float
    kind: str


@dataclass(frozen=True)
class ShortfallWindow:
    """Hours when demand is above the roster, from start to end."""

    start: float
    end: float

    @property
    def hours(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class TrapezoidStep:
    """One row of the trapezoid convergence table."""

    strips: int
    estimate: float
    error: float


@dataclass(frozen=True)
class QuadEstimate:
    """A numerical integral from quad, with its own error bound and the true error."""

    estimate: float
    error_bound: float
    error: float


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


def trapezoid(f: Callable[[float], float], lo: float, hi: float, strips: int) -> float:
    """Integrate f from lo to hi with the trapezoid rule on equal strips.

    h * (f(t0)/2 + f(t1) + ... + f(t_{n-1}) + f(tn)/2), with h = (hi - lo)/n.
    """
    if strips < 1:
        raise ValueError("strips must be a positive integer")
    width = (hi - lo) / strips
    inner = sum(f(lo + i * width) for i in range(1, strips))
    return width * ((f(lo) + f(hi)) / 2 + inner)


def trapezoid_staff_hours(params: HotelParams, strips: int) -> float:
    """Total staff-hours estimated by the trapezoid rule over the day."""
    return trapezoid(lambda t: demand(params, t), 0, OPEN_HOURS, strips)


def trapezoid_error(params: HotelParams, strips: int) -> float:
    """Exact total minus the trapezoid estimate.

    For a parabola the trapezoid error is exactly -(12^3 / 12n^2) * w'' =
    8A/n^2: positive because the chords sit under a curve that bends down,
    and divided by four each time the strips double.
    """
    return total_staff_hours(params) - trapezoid_staff_hours(params, strips)


def trapezoid_convergence(
    params: HotelParams, strip_counts: Iterable[int] = (1, 2, 4, 8, 16, 32)
) -> list[TrapezoidStep]:
    """Trapezoid estimate and error for each strip count, to show the error shrinking."""
    exact = total_staff_hours(params)
    steps = []
    for n in strip_counts:
        estimate = trapezoid_staff_hours(params, n)
        steps.append(TrapezoidStep(strips=n, estimate=estimate, error=exact - estimate))
    return steps


def quad_staff_hours(params: HotelParams) -> QuadEstimate:
    """Total staff-hours from scipy.integrate.quad, checked against 12*w0 + 8A."""
    estimate, error_bound = quad(lambda t: demand(params, t), 0, OPEN_HOURS)
    return QuadEstimate(
        estimate=estimate,
        error_bound=error_bound,
        error=total_staff_hours(params) - estimate,
    )


def shortfall_window(params: HotelParams, roster: int | None = None) -> ShortfallWindow | None:
    """When a fixed roster of n waiters is not enough, or None if it always is.

    Solving w(t) = n gives t(12 - t) = 36(P - n)/A, so t = 6 +/- h with
    h = 6*sqrt((P - n)/A). Demand only exceeds n between those two times.
    """
    n = _roster(params, roster)
    w0 = base_demand(params)
    peak_waiters = w0 + amplitude(params)

    # Touching the peak exactly is enough, so the roster has to be below it.
    if n >= peak_waiters:
        return None
    # Below the base there is no crossing: demand is above n all day.
    if n < w0:
        return ShortfallWindow(0.0, float(OPEN_HOURS))

    h = 6 * math.sqrt((peak_waiters - n) / amplitude(params))
    return ShortfallWindow(6 - h, 6 + h)


def understaffed_hours(params: HotelParams, roster: int | None = None) -> float:
    """Staff-hours of demand the roster cannot cover: the area where w(t) > n.

    Writing w - n = (P - n) - A(t - 6)^2/36 and integrating over 6 +/- k gives
    2k(P - n) - A*k^3/54. With k = h this is the problem's (4/3)*h*(P - n); using
    the window's own half-width also covers rosters that are short all day.
    """
    n = _roster(params, roster)
    k = _shortfall_half_width(params, n)
    peak_waiters = base_demand(params) + amplitude(params)
    return 2 * k * (peak_waiters - n) - amplitude(params) * k**3 / 54


def idle_hours(params: HotelParams, roster: int | None = None) -> float:
    """Staff-hours the roster is paid for but not needed: the area where n > w(t).

    This is the integral of n - w over the two tails [0, 6 - k] and [6 + k, 12].
    Each tail gives (n - P)(6 - k) + A(216 - k^3)/108, and the curve is
    symmetric about t = 6, so the day is twice that.
    """
    n = _roster(params, roster)
    k = _shortfall_half_width(params, n)
    peak_waiters = base_demand(params) + amplitude(params)
    one_tail = (n - peak_waiters) * (6 - k) + amplitude(params) * (216 - k**3) / 108
    return 2 * one_tail


def staff_hours_balance(params: HotelParams, roster: int | None = None) -> bool:
    """Self-check: total - understaffed + idle must equal the 12n hours rostered."""
    n = _roster(params, roster)
    balance = (
        total_staff_hours(params)
        - understaffed_hours(params, n)
        + idle_hours(params, n)
    )
    return math.isclose(balance, OPEN_HOURS * n, abs_tol=1e-9)


def _shortfall_half_width(params: HotelParams, roster: int) -> float:
    """k such that the roster falls short between 6 - k and 6 + k (0 if never)."""
    window = shortfall_window(params, roster)
    return 0.0 if window is None else window.hours / 2


def _roster(params: HotelParams, roster: int | None) -> int:
    return params.roster if roster is None else roster


def _check_hour(t: float) -> None:
    if not 0 <= t <= OPEN_HOURS:
        raise ValueError(f"t must be between 0 and {OPEN_HOURS} hours")

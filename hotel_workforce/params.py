"""Model parameters derived from a single input: the number of rooms R."""

from dataclasses import dataclass

DEFAULT_OCCUPANCY = (78, 82, 70, 65, 52, 48, 60, 68, 55, 58, 66, 90)
DEFAULT_WAGE_LKR = 450


@dataclass(frozen=True)
class HotelParams:
    rooms: int
    a: float
    b: float
    c: float
    peak_waiters: int
    base_waiters: int
    roster: int
    wage_lkr: int = DEFAULT_WAGE_LKR
    occupancy: tuple = DEFAULT_OCCUPANCY


def from_rooms(rooms: int) -> HotelParams:
    """Build every model parameter from the room count."""
    if rooms <= 0:
        raise ValueError("rooms must be a positive integer")

    peak = round(rooms / 4)
    return HotelParams(
        rooms=rooms,
        a=2 * rooms / 3,
        b=2 * rooms / 5,
        c=8 * rooms**2 / 45,
        peak_waiters=peak,
        base_waiters=round(peak / 4),
        roster=round(0.8 * peak),
    )

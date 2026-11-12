import pytest

from hotel_workforce.params import from_rooms


@pytest.mark.parametrize(
    "rooms, a, b, c, peak, base, roster",
    [
        (15, 10, 6, 40, 4, 1, 3),
        (60, 40, 24, 640, 15, 4, 12),
        (150, 100, 60, 4000, 38, 10, 30),
    ],
)
def test_parameters_match_problem_table(rooms, a, b, c, peak, base, roster):
    params = from_rooms(rooms)

    assert params.a == pytest.approx(a)
    assert params.b == pytest.approx(b)
    assert params.c == pytest.approx(c)
    assert params.peak_waiters == peak
    assert params.base_waiters == base
    assert params.roster == roster


def test_default_occupancy_averages_66_percent():
    occupancy = from_rooms(60).occupancy

    assert len(occupancy) == 12
    assert sum(occupancy) / 12 == 66


@pytest.mark.parametrize("rooms", [0, -5])
def test_rejects_non_positive_rooms(rooms):
    with pytest.raises(ValueError):
        from_rooms(rooms)

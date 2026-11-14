import pytest

from hotel_workforce import waiters
from hotel_workforce.params import from_rooms


@pytest.mark.parametrize(
    "rooms, w0, amplitude",
    [(15, 1, 3), (60, 4, 11), (150, 10, 28)],
)
def test_curve_constants_match_problem_table(rooms, w0, amplitude):
    params = from_rooms(rooms)

    assert waiters.base_demand(params) == w0
    assert waiters.amplitude(params) == amplitude


@pytest.mark.parametrize("rooms, base, peak", [(15, 1, 4), (60, 4, 15), (150, 10, 38)])
def test_demand_runs_from_base_to_peak_and_back(rooms, base, peak):
    params = from_rooms(rooms)

    assert waiters.demand(params, 0) == pytest.approx(base)
    assert waiters.demand(params, 6) == pytest.approx(peak)
    assert waiters.demand(params, 12) == pytest.approx(base)


def test_demand_at_intermediate_hours():
    params = from_rooms(60)

    assert waiters.demand(params, 3) == pytest.approx(4 + 11 * 27 / 36)
    assert waiters.demand(params, 9) == pytest.approx(waiters.demand(params, 3))


@pytest.mark.parametrize("rooms", [15, 60, 150])
def test_rate_matches_finite_difference(rooms):
    params = from_rooms(rooms)
    h = 1e-6

    for t in (1, 2.5, 6, 8, 11):
        slope = (waiters.demand(params, t + h) - waiters.demand(params, t - h)) / (2 * h)
        assert waiters.demand_rate(params, t) == pytest.approx(slope, abs=1e-6)


def test_rate_is_positive_before_peak_zero_at_peak_negative_after():
    params = from_rooms(60)

    assert waiters.demand_rate(params, 0) == pytest.approx(11 / 3)
    assert waiters.demand_rate(params, 6) == 0
    assert waiters.demand_rate(params, 12) == pytest.approx(-11 / 3)


@pytest.mark.parametrize("rooms", [15, 60, 150])
def test_rate_is_zero_at_critical_hour(rooms):
    params = from_rooms(rooms)

    assert waiters.critical_hour() == 6
    assert waiters.demand_rate(params, waiters.critical_hour()) == 0


@pytest.mark.parametrize("rooms", [15, 60, 150])
def test_curvature_matches_finite_difference_of_rate(rooms):
    params = from_rooms(rooms)
    h = 1e-4

    for t in (1, 6, 11):
        slope = (waiters.demand_rate(params, t + h) - waiters.demand_rate(params, t - h)) / (2 * h)
        assert waiters.demand_curvature(params) == pytest.approx(slope)


@pytest.mark.parametrize(
    "rooms, peak_waiters, curvature",
    [(15, 4, -3 / 18), (60, 15, -11 / 18), (150, 38, -28 / 18)],
)
def test_peak_matches_problem_table_and_is_a_maximum(rooms, peak_waiters, curvature):
    peak = waiters.peak(from_rooms(rooms))

    assert peak.hour == 6
    assert peak.waiters == pytest.approx(peak_waiters)
    assert peak.curvature == pytest.approx(curvature)
    assert peak.kind == "maximum"


def test_flat_curve_peak_is_inconclusive():
    # One room gives P = w0 = 0, so A = 0 and w''(t) = 0.
    peak = waiters.peak(from_rooms(1))

    assert peak.curvature == 0
    assert peak.kind == "inconclusive"


@pytest.mark.parametrize(
    "curvature, expected",
    [(-0.5, "maximum"), (0.5, "minimum"), (0, "inconclusive")],
)
def test_classify(curvature, expected):
    assert waiters.classify(curvature) == expected


@pytest.mark.parametrize("t", [-0.5, 12.5])
def test_rejects_hours_outside_opening_time(t):
    params = from_rooms(60)

    with pytest.raises(ValueError):
        waiters.demand(params, t)
    with pytest.raises(ValueError):
        waiters.demand_rate(params, t)

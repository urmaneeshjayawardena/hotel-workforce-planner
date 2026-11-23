from dataclasses import replace

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


@pytest.mark.parametrize(
    "rooms, staff_hours, wage_cost",
    [(15, 36, 16_200), (60, 136, 61_200), (150, 344, 154_800)],
)
def test_staff_hours_and_wage_cost_match_problem_table(rooms, staff_hours, wage_cost):
    params = from_rooms(rooms)

    assert waiters.total_staff_hours(params) == staff_hours
    assert waiters.daily_wage_cost(params) == wage_cost


@pytest.mark.parametrize("rooms", [15, 60, 150, 300])
def test_staff_hours_match_simpsons_rule(rooms):
    # Simpson's rule is exact for a parabola, so one pair of strips is enough.
    params = from_rooms(rooms)
    simpson = 12 / 6 * (
        waiters.demand(params, 0) + 4 * waiters.demand(params, 6) + waiters.demand(params, 12)
    )

    assert waiters.total_staff_hours(params) == pytest.approx(simpson)


def test_wage_cost_follows_the_wage():
    params = replace(from_rooms(60), wage_lkr=500)

    assert waiters.daily_wage_cost(params) == 136 * 500


@pytest.mark.parametrize(
    "rooms, start, end",
    [(15, 2.54, 9.46), (60, 2.87, 9.13), (150, 2.79, 9.21)],
)
def test_shortfall_window_matches_problem_table(rooms, start, end):
    window = waiters.shortfall_window(from_rooms(rooms))

    assert window.start == pytest.approx(start, abs=0.005)
    assert window.end == pytest.approx(end, abs=0.005)


@pytest.mark.parametrize("rooms", [15, 60, 150, 300])
def test_demand_equals_roster_at_both_ends_of_the_window(rooms):
    params = from_rooms(rooms)
    window = waiters.shortfall_window(params)

    assert waiters.demand(params, window.start) == pytest.approx(params.roster)
    assert waiters.demand(params, window.end) == pytest.approx(params.roster)
    assert waiters.demand(params, 6) > params.roster


def test_window_is_centred_on_the_peak():
    window = waiters.shortfall_window(from_rooms(60))

    assert (window.start + window.end) / 2 == pytest.approx(6)
    assert window.hours == pytest.approx(2 * 6 * (3 / 11) ** 0.5)


def test_a_bigger_roster_shrinks_the_window():
    params = from_rooms(60)
    widths = [waiters.shortfall_window(params, roster=n).hours for n in (5, 8, 12, 14)]

    assert widths == sorted(widths, reverse=True)


@pytest.mark.parametrize("roster", [15, 20])
def test_roster_at_or_above_peak_is_always_enough(roster):
    assert waiters.shortfall_window(from_rooms(60), roster=roster) is None


@pytest.mark.parametrize("roster", [4, 2])
def test_roster_at_or_below_base_is_short_all_day(roster):
    window = waiters.shortfall_window(from_rooms(60), roster=roster)

    assert (window.start, window.end) == pytest.approx((0, 12))


@pytest.mark.parametrize(
    "rooms, understaffed, idle",
    [(15, 4.62, 4.62), (60, 12.53, 20.53), (150, 34.21, 50.21)],
)
def test_understaffed_and_idle_hours_match_problem_table(rooms, understaffed, idle):
    params = from_rooms(rooms)

    assert waiters.understaffed_hours(params) == pytest.approx(understaffed, abs=0.005)
    assert waiters.idle_hours(params) == pytest.approx(idle, abs=0.005)


@pytest.mark.parametrize("rooms", [15, 60, 150])
def test_understaffed_hours_match_closed_form(rooms):
    # The problem statement's (4/3)*h*(P - n), valid when the window is inside the day.
    params = from_rooms(rooms)
    h = waiters.shortfall_window(params).hours / 2

    assert waiters.understaffed_hours(params) == pytest.approx(
        4 / 3 * h * (params.peak_waiters - params.roster)
    )


@pytest.mark.parametrize("rooms", [15, 60, 150, 300])
@pytest.mark.parametrize("roster_offset", [-20, -5, 0, 3, 20])
def test_understaffed_and_idle_match_simpsons_rule(rooms, roster_offset):
    # Simpson's rule is exact on each piece where w - n keeps its sign.
    params = from_rooms(rooms)
    n = max(params.roster + roster_offset, 0)
    window = waiters.shortfall_window(params, roster=n)
    cuts = [0.0, 12.0] if window is None else [0.0, window.start, window.end, 12.0]

    under = idle = 0.0
    for lo, hi in zip(cuts, cuts[1:]):
        area = (hi - lo) / 6 * sum(
            weight * (waiters.demand(params, t) - n)
            for weight, t in ((1, lo), (4, (lo + hi) / 2), (1, hi))
        )
        if area > 0:
            under += area
        else:
            idle -= area

    assert waiters.understaffed_hours(params, roster=n) == pytest.approx(under, abs=1e-9)
    assert waiters.idle_hours(params, roster=n) == pytest.approx(idle, abs=1e-9)


@pytest.mark.parametrize("rooms", [1, 15, 60, 150, 300])
@pytest.mark.parametrize("roster", [None, 0, 2, 8, 12, 15, 40])
def test_staff_hours_balance_holds(rooms, roster):
    assert waiters.staff_hours_balance(from_rooms(rooms), roster=roster)


def test_staff_hours_balance_for_r60_matches_problem_statement():
    params = from_rooms(60)
    balance = (
        waiters.total_staff_hours(params)
        - waiters.understaffed_hours(params)
        + waiters.idle_hours(params)
    )

    assert balance == pytest.approx(144)


@pytest.mark.parametrize("roster", [15, 20])
def test_roster_at_or_above_peak_is_never_understaffed(roster):
    params = from_rooms(60)

    assert waiters.understaffed_hours(params, roster=roster) == 0
    assert waiters.idle_hours(params, roster=roster) == pytest.approx(12 * roster - 136)


@pytest.mark.parametrize("roster", [4, 2])
def test_roster_at_or_below_base_is_never_idle(roster):
    params = from_rooms(60)

    assert waiters.idle_hours(params, roster=roster) == pytest.approx(0, abs=1e-9)
    assert waiters.understaffed_hours(params, roster=roster) == pytest.approx(136 - 12 * roster)

import pytest

from hotel_workforce import cost
from hotel_workforce.params import from_rooms


@pytest.mark.parametrize("rooms", [10, 15, 60, 150, 300])
def test_gradient_is_zero_at_critical_point(rooms):
    params = from_rooms(rooms)
    x, y = cost.critical_point(params)

    cx, cy = cost.gradient(params, x, y)

    assert cx == pytest.approx(0, abs=1e-9)
    assert cy == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize("rooms", [10, 60, 300])
def test_critical_point_scales_with_rooms(rooms):
    x, y = cost.critical_point(from_rooms(rooms))

    assert x == pytest.approx(0.24 * rooms)
    assert y == pytest.approx(0.88 * rooms / 6)


def test_discriminant_classifies_a_minimum():
    optimum = cost.optimise(from_rooms(60))

    assert optimum.discriminant == 20
    assert optimum.kind == "minimum"


@pytest.mark.parametrize(
    "d, c_xx, expected",
    [(20, 4, "minimum"), (20, -4, "maximum"), (-5, 4, "saddle"), (0, 4, "inconclusive")],
)
def test_classify(d, c_xx, expected):
    assert cost.classify(d, c_xx) == expected


@pytest.mark.parametrize(
    "rooms, x, y, c_min, plan_x, plan_y, plan_cost, penalty",
    [
        (15, 3.6, 2.2, 15.4, 4, 2, 16.0, 0.6),
        (60, 14.4, 8.8, 246.4, 14, 9, 247.0, 0.6),
        (150, 36, 22, 1540, 36, 22, 1540, 0),
    ],
)
def test_matches_problem_table(rooms, x, y, c_min, plan_x, plan_y, plan_cost, penalty):
    params = from_rooms(rooms)
    optimum = cost.optimise(params)
    plan = cost.best_whole_plan(params)

    assert (optimum.x, optimum.y) == (pytest.approx(x), pytest.approx(y))
    assert optimum.cost == pytest.approx(c_min)
    assert (plan.housekeepers, plan.overtime_hours) == (plan_x, plan_y)
    assert plan.cost == pytest.approx(plan_cost)
    assert plan.penalty == pytest.approx(penalty, abs=1e-9)


@pytest.mark.parametrize("rooms", [15, 60, 150])
def test_minimum_cost_formula(rooms):
    params = from_rooms(rooms)
    optimum = cost.optimise(params)

    expected = params.c - (params.a * optimum.x + params.b * optimum.y) / 2

    assert optimum.cost == pytest.approx(expected)
    assert optimum.cost > 0

"""Command-line report: python -m hotel_workforce --rooms 60"""

import argparse

from . import cost
from .params import from_rooms


def build_report(rooms: int) -> str:
    params = from_rooms(rooms)
    optimum = cost.optimise(params)
    plan = cost.best_whole_plan(params)

    lines = [
        f"Hotel with {rooms} rooms",
        f"  a = {params.a:.2f}, b = {params.b:.2f}, c = {params.c:.2f}",
        f"  peak waiters = {params.peak_waiters}, base = {params.base_waiters}, "
        f"roster = {params.roster}",
        "",
        "Housekeepers and overtime (thousand LKR per day)",
        f"  optimum: x* = {optimum.x:.2f}, y* = {optimum.y:.2f}, "
        f"C = {optimum.cost:.2f} ({optimum.kind}, D = {optimum.discriminant:g})",
        f"  whole plan: {plan.housekeepers} housekeepers, "
        f"{plan.overtime_hours} overtime hours, C = {plan.cost:.2f}, "
        f"penalty = {plan.penalty:.2f}",
    ]
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Hotel workforce planner")
    parser.add_argument("--rooms", type=int, default=60, help="number of rooms R")
    args = parser.parse_args(argv)
    print(build_report(args.rooms))


if __name__ == "__main__":
    main()

# Hotel Workforce Planner

Staffing a hotel is a set of connected guesses. How many housekeepers should be on the
payroll, and how much overtime should cover the rest? How many waiters does the restaurant
need at 7 PM compared with opening time? How often will people leave, and what does
replacing them cost? Which months are busy enough to need temporary staff?

Small hotels usually answer these by habit, and large ones answer them with spreadsheets
that break when the hotel grows. This project answers all four with one model driven by a
single number, **R = the number of rooms**. Change R and every result updates, so the same
code works for a 10-room guesthouse or a 300-room resort.

The full problem statement is in [`docs/Hotel_Problem.pdf`](docs/Hotel_Problem.pdf).

## What it answers

| Question | Maths | Status |
| --- | --- | --- |
| Cheapest mix of regular housekeepers and overtime hours | Differentiation (critical points, discriminant) | Done |
| Waiters needed at each hour, and whether a fixed roster works | Integration | Planned |
| How long staff stay and what turnover costs | Geometric series | Planned |
| Months that need temporary staff | DFT, Fourier series, DCT | Planned |

See [`BACKLOG.md`](BACKLOG.md) for the full roadmap.

## How the cost model works

Daily cost in thousand LKR, with `x` regular housekeepers and `y` overtime hours:

```
C(x, y) = 2x² + 3y² − 2xy − a·x − b·y + c
a = 2R/3,  b = 2R/5,  c = 8R²/45
```

Setting both partial derivatives to zero gives `x* = (3a + b)/10` and `y* = (a + 2b)/10`.
The discriminant `D = 4·6 − (−2)² = 20` is positive with `Cₓₓ > 0`, so this is a minimum for
every R. Staff come in whole numbers, so the planner then checks the neighbouring whole-number
plans and reports the extra cost of rounding.

## Usage

Requires Python 3.12 or newer.

```bash
python -m pip install -r requirements.txt
python -m hotel_workforce --rooms 60
```

```
Hotel with 60 rooms
  a = 40.00, b = 24.00, c = 640.00
  peak waiters = 15, base = 4, roster = 12

Housekeepers and overtime (thousand LKR per day)
  optimum: x* = 14.40, y* = 8.80, C = 246.40 (minimum, D = 20)
  whole plan: 14 housekeepers, 9 overtime hours, C = 247.00, penalty = 0.60
```

## Tests

```bash
python -m pytest
```

The tests check the code against the worked tables in the problem statement for
R = 15, 60 and 150.

## Project layout

```
hotel_workforce/
  params.py   parameters derived from R
  cost.py     Section 1: housekeeper and overtime optimisation
  cli.py      command-line report
tests/        pytest suite
docs/         original problem statement
```

# Backlog

Work top to bottom. Each item is one small, tested change. Tick the box in the same
commit that delivers the item.

## Section 2A: Integration (waiter demand)

- [x] Add a `waiters` module with the demand curve `w(t) = w0 + A·t(12 − t)/36` and its derivative
- [ ] Find the demand peak from `w'(t) = 0` and confirm it is a maximum with `w''(t)`
- [ ] Compute total staff-hours in closed form (`12·w0 + 8A`) and the daily wage cost
- [ ] Find the hours when a fixed roster is not enough (`t = 6 ± h`)
- [ ] Compute understaffed and idle staff-hours, with the self-check `total − under + idle = 12n`
- [ ] Add a hand-written trapezoid rule and show its error shrinking as strips increase
- [ ] Verify the staff-hour integral numerically with `scipy.integrate.quad`
- [ ] Verify the staff-hour integral exactly with SymPy
- [ ] Add the waiter section to the command-line report

## Section 2B: Sequences and series (turnover)

- [ ] Add a `turnover` module with expected tenure `1/(1 − r)` and a convergence check
- [ ] Compute partial sums `Sn` and the number of terms needed for 99% (`r^n ≤ 0.01`)
- [ ] Add default department retention rates (kitchen, front desk, housekeeping)
- [ ] Estimate yearly hires and turnover cost from `x*` and a configurable cost per hire
- [ ] Add the turnover section to the command-line report

## Section 3: Transforms (seasonality)

- [ ] Add a `seasonality` module with rooms sold per night from monthly occupancy
- [ ] Compute the DFT with NumPy and report the dominant non-zero frequency as a cycle length in months
- [ ] Compute Fourier series coefficients `a0`, `an`, `bn` from the monthly data
- [ ] Rebuild the occupancy curve from the first 1, 2 and 3 harmonics and report the fit error
- [ ] Compress occupancy with an orthonormal DCT, keeping the largest k coefficients
- [ ] Report reconstruction error against compression ratio `12/k`
- [ ] Scale monthly housekeepers and peak waiters by occupancy relative to the average
- [ ] Flag the months that need temporary staff using the smoothed curve
- [ ] Add the seasonality section to the command-line report

## Plots

- [ ] Plot the cost surface in 3D with the optimum marked
- [ ] Plot cost contours with the optimum marked
- [ ] Plot the waiter curve with the roster line and shaded under- and over-staffed areas
- [ ] Plot partial sums of the tenure series against their limits
- [ ] Plot occupancy with the 1, 2 and 3 harmonic fits
- [ ] Plot DCT error against compression ratio

## Packaging

- [ ] Add a `--save-plots DIR` option to write every figure to disk
- [ ] Add a `--json` option that prints the full report as JSON
- [ ] Load occupancy and wage overrides from a TOML config file
- [ ] Add a Jupyter notebook that walks through all sections with a single `R` cell
- [ ] Add a GitHub Actions workflow that runs the tests on every push

# Current results and discussion

## Synthetic validation (complete)

All 33 unit tests pass (13 analytic anchors plus 20 input-contract and
regression anchors). The model behaves exactly as theory demands. The
deviations below are the ones measured by running the suite and the
measurement script on this repository, not tolerances alone:

- **Closed evolution**: Rabi limit p1(t) = sin^2(omega t/2) matched to 3.2e-9
  over t in [0, 3] (test tolerance 2e-3); purity conserved to 1.6e-13 (test
  tolerance 1e-8).
- **Dephasing**: off-diagonal coherence decays as e^{-2 gamma t} to 6.3e-12
  (test tolerance 1e-3); populations untouched (no drift at all, test
  tolerance 1e-10); oscillation damps toward p1 = 1/2 (|p1(12) - 0.5| < 0.05
  at T = 12 with gamma = 1.5).
- **Amplitude damping**: relaxation into the committed state, p1 = 0.99967
  after 8 time units at gamma = 1 (test threshold > 0.999).
- **Baselines**: Laplace-smoothed Markov estimator recovers planted
  transition matrices to 0.0047 (test tolerance 0.03) and is row-stochastic
  to machine precision; likelihood ordering prefers true models; BIC
  penalises parameters exactly as k ln n (212.429216 for k = 2, n = 500,
  ln L = -100).

## Numerical contract corrections (2026-10-21)

The contract suite added on 2026-10-21 exposed two defects that the analytic
anchors could not see, because every anchor used a uniform time grid. Both
were *silent*: the package returned a well-formed number for an input it did
not support, so nothing pointed at the wrong answer.

### 1. The trajectory reported the wrong times

`choice_probability_trajectory` integrated the master equation on a uniform
grid of step `dt = min(diff(times))` and read the answer off with
`idx = round(times / dt)`. On a non-uniform request grid that index is not
the requested time.

Measured on this repository (omega = 2, gamma = 0, grid `[0, 0.2, 0.5]`):

| requested t | reported before | reported now | true sin^2(omega t / 2) |
|---|---|---|---|
| 0.2 | 0.039467 | 0.039467 | 0.039470 |
| 0.5 | 0.151608 | 0.229668 | 0.229849 |

The value reported for t = 0.5 was the value at t = 0.4. The maximum error
over that grid was 7.8e-2 and is now 1.8e-4. On the grid `[0, 0.3, 0.5]` the
old rounding mapped t = 0.3 and t = 0.5 onto the same integration point and
reported one number twice; the two values are now distinct to three decimal
places.

`twolevel_log_likelihood` inherited the fault one level up: an observation
time was snapped to the nearest grid point, so an observation at t = 99 on a
grid covering [0, 2] was scored at the grid endpoint with no warning.
Out-of-grid observation times and outcomes outside {0, 1} (including NaN) are
now rejected with a `ValueError`.

For uniform grids the trajectory is unchanged: comparing the pre- and
post-correction implementations on three uniform grids (dt = 0.01 and 0.005,
gamma = 0, 0.3 and 1.5) the largest difference is 1.5e-13, i.e. floating-point
noise. The dt = 10 ms grid of the fitting pipeline is therefore unaffected.

### 2. The Markov estimator mis-attributed states and could return NaN

- A negative state label indexed the *last* row of the count matrix, so the
  transitions of an unknown state were attributed silently to a real one.
- A fractional label was silently truncated to an integer.
- With `alpha = 0`, a state that never occurs as a source produced an
  all-zero row, so the normalisation returned `0 / 0` and the whole row was
  NaN. The NaN then spread into `markov_log_likelihood` and `bic`, where it
  silently failed to compare; the only trace was a `RuntimeWarning` on
  stderr.

Labels outside `[0, n_states)` and unestimable rows are now rejected with a
`ValueError` that names the offending state, and `bic` rejects a NaN
log-likelihood instead of returning a NaN score.

### What this section does not cover

This is a result about the software, not about the science. No MetaRDK trial
table exists yet (Issue #1), so H1, H2 and H3 are untested, the falsifier in
the README has not been evaluated, and the model-comparison pipeline
(Issues #3-#5 of the plan) has not been run on any data. The corrections
above change the values returned for non-uniform time grids and turn silent
inputs into loud errors; they are not evidence for or against the
quantum-like account.

## Design lessons baked into the plan

1. **Identifiability first**: omega and gamma both affect the oscillation
   envelope (frequency vs damping), so recovery checks (simulate → refit)
   are a mandatory pipeline stage, not an afterthought (plan milestone 5,
   model comparison).
2. **The classical regime must be reachable**: at high coherence the model
   should fit large gamma/omega (overdamped). If it does not, the model is
   wrong in an instructive way — H3 tests this explicitly.
3. **Two noise channels are distinct**: dephasing (corridor closing) and
   damping (one-way population flow) have different signatures; the primary
   model uses dephasing only, with the damping arm as sensitivity analysis,
   to keep the comparison honest and parsimonious.
4. **A test suite that only walks the happy path is decoration**: the two
   defects above sat next to thirteen green anchors, because every anchor
   used a uniform grid and every state label was valid.

## Interpretation sketch

Under uncertainty (low coherence), a coherent-accumulation account predicts
non-monotone commitment probability — "wavering" — before dephasing locks
the decision in. If human choice curves waver in the way the model requires
and BIC prefers it out of sample, that is evidence for quantum-like
*dynamics* (as a description of cognition); if not, the penalised classical
baselines win and we have a sharp, pre-registered negative result.

## Risks

- **Choice-curve granularity**: empirical curves may be too coarsely binned
  in time to see oscillation; mitigation: use RT distributions (dense
  timing) and fixed-duration sites of MetaRDK.
- **Overfitting the envelope**: damped sinusoids can mimic many shapes;
  mitigation: held-out CV and the recovery suite.
- **Mechanistic overreach**: any positive result is about *dynamics of
  choice probabilities*, not brain hardware; all docs repeat this.
- **Grid arithmetic**: the trajectory now integrates onto the requested
  times, so a caller who asks for a coarse grid gets the coarse-grid
  accuracy, not the accuracy of a finer internal grid. The integration step
  never exceeds the finest spacing requested; this is documented rather than
  silently corrected.

## Open questions

- Does fitted gamma relate to confidence reports (metacognition), as the
  dephasing interpretation suggests?
- Can the same (omega, gamma) fit generalise across RDK sites (a transport
  test), or are parameters site-specific?

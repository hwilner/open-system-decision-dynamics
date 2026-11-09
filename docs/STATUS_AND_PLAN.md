# Status and plan

## Done

- [x] Scaffold, license, requirements.
- [x] `open_decision` package: GKSL master equation (RK4, Hermiticity
      hygiene), Rabi drive, dephasing and amplitude-damping channels;
      choice-probability trajectories; Markov estimator and likelihoods;
      BIC.
- [x] 33-test suite with analytic anchors (sin^2 Rabi limit, coherence
      decay at exactly 2 gamma, damping relaxation to > 0.999, trace and
      purity conservation, Markov recovery, BIC algebra) and input-contract
      regressions (non-uniform time grids, out-of-grid observations,
      non-binary outcomes, invalid state labels, unestimable transition
      rows, NaN scores).
- [x] Publication-quality INTRODUCTION and high-school EXTENDED_INTRODUCTION.
- [x] Continuous integration on Python 3.11–3.13, plus a packaging check
      that installs the distribution and imports it (Issue #5).
- [x] Packaging metadata (`pyproject.toml`), so the suite runs without a
      hand-set `PYTHONPATH` (Issue #5).

## In progress

- [ ] MetaRDK access + loader (Issue #1).
- [ ] Behavioural targets: choice curves and commitment proxy (Issue #2).

## Planned

The milestones below are the plan; the issue column gives the GitHub issue
that tracks each one.

| Milestone | Issue | Depends on |
|---|---|---|
| 1. MetaRDK downloader + trial table | #1 | — |
| 2. Behavioural targets (choice curves, RT distributions) | #2 | 1 |
| 3. Open-system fitting pipeline (per-subject, per-coherence) | #6 | 2 |
| 4. Baselines: Markov + reference DDM likelihoods | #7 | 2 |
| 5. Model comparison: BIC + held-out CV + recovery checks | #8 | 6, 7 |
| 6. H2/H3: gamma as a trait; coherence-dependent regime | #9 | 6 |
| 7. Figures (incl. PaperBanana-style schematic) + write-up | #10 | 8, 9 |

Software issues filed alongside the sweep of 2026-10-21:

| Issue | Subject | State |
|---|---|---|
| #3 | The choice-probability trajectory reports the wrong times on a non-uniform grid | closed |
| #4 | The Markov estimator silently mis-attributes states and can return NaN rows | closed |
| #5 | Add CI and align the declared environment with the code | closed |

## Next quarter target

H1 decided per coherence band with full recovery checks; negative-result
branch prepared in parallel (per the falsifier).

# Status and plan

## Done

- [x] Scaffold, license, requirements.
- [x] `open_decision` package: GKSL master equation (RK4, Hermiticity
      hygiene), Rabi drive, dephasing and amplitude-damping channels;
      choice-probability trajectories; Markov estimator and likelihoods;
      BIC.
- [x] 13-test suite with analytic anchors (sin^2 Rabi limit, coherence
      decay at exactly 2 gamma, damping relaxation to > 0.999, trace and
      purity conservation, Markov recovery, BIC algebra).
- [x] Publication-quality INTRODUCTION and high-school EXTENDED_INTRODUCTION.

## In progress

- [ ] MetaRDK access + loader (Issue #1).
- [ ] Behavioural targets: choice curves and commitment proxy (Issue #2).

## Planned (Issues #1–#7)

| # | Milestone | Depends on |
|---|---|---|
| 1 | MetaRDK downloader + trial table | — |
| 2 | Behavioural targets (choice curves, RT distributions) | 1 |
| 3 | Open-system fitting pipeline (per-subject, per-coherence) | 2 |
| 4 | Baselines: Markov + reference DDM likelihoods | 2 |
| 5 | Model comparison: BIC + held-out CV + recovery checks | 3, 4 |
| 6 | H2/H3: gamma as a trait; coherence-dependent regime | 3 |
| 7 | Figures (incl. PaperBanana-style schematic) + write-up | 5, 6 |

## Next quarter target

H1 decided per coherence band with full recovery checks; negative-result
branch prepared in parallel (per the falsifier).

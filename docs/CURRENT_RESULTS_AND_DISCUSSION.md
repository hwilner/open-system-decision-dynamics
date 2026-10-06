# Current results and discussion

## Synthetic validation (complete)

All 13 anchors pass. The model behaves exactly as theory demands:

- **Closed evolution**: Rabi limit p1(t) = sin^2(omega t/2) matched to
  2e-3 over t in [0, 3]; purity conserved to 1e-8.
- **Dephasing**: off-diagonal coherence decays as e^{-2 gamma t} to 1e-3;
  populations untouched to 1e-10; oscillation damps toward p1 = 1/2
  (|p1(T) - 0.5| < 0.05 at T = 12 with gamma = 1.5).
- **Amplitude damping**: relaxation into the committed state, p1 > 0.999
  after 8 time units at gamma = 1.
- **Baselines**: Laplace-smoothed Markov estimator recovers planted
  transition matrices to 0.03; likelihood ordering prefers true models;
  BIC penalises parameters exactly as k ln n.

## Design lessons baked into the plan

1. **Identifiability first**: omega and gamma both affect the oscillation
   envelope (frequency vs damping), so recovery checks (simulate → refit)
   are a mandatory pipeline stage, not an afterthought (Issue #5).
2. **The classical regime must be reachable**: at high coherence the model
   should fit large gamma/omega (overdamped). If it does not, the model is
   wrong in an instructive way — H3 tests this explicitly.
3. **Two noise channels are distinct**: dephasing (corridor closing) and
   damping (one-way population flow) have different signatures; the primary
   model uses dephasing only, with the damping arm as sensitivity analysis,
   to keep the comparison honest and parsimonious.

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

## Open questions

- Does fitted gamma relate to confidence reports (metacognition), as the
  dephasing interpretation suggests?
- Can the same (omega, gamma) fit generalise across RDK sites (a transport
  test), or are parameters site-specific?

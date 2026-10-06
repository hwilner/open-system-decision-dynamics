# Materials and methods

## Data

**MetaRDK** — a multi-site random-dot-kinematogram dataset of perceptual
decisions with confidence ratings (public via OpenNeuro; see
https://openneuro.org/ and the dataset accession recorded in
`data/README.md` once Issue #1 lands). Trials vary motion coherence
(evidence strength) and, in several sites, viewing duration. We use:
choice (left/right), coherence level, viewing/response times, confidence,
site, subject id.

Exclusions: trials with RT < 150 ms or > 3 SD above subject median; subjects
with < 200 usable trials after exclusions.

## Behavioural targets

- **Choice curves**: P(choose right) as a function of signed coherence and
  viewing time (psychometric chronometric surface).
- **Commitment proxy**: for fixed-duration paradigms, the time-resolved
  fraction of committed responses; for RT paradigms, the RT distribution as
  the commitment-time read-out.
- **Confidence**: secondary read-out for the dephasing interpretation.

## Models

1. **Two-level open-system model** (`src/open_decision/`): drive
   H = (omega/2) sigma_x, dephasing sqrt(gamma) sigma_z, optional amplitude
   damping sqrt(kappa) sigma_-. Parameters per coherence level c:
   omega = omega0 * c (evidence scaling), gamma free; kappa = 0 in the
   primary model (damping arm is a sensitivity analysis).
2. **First-order Markov baseline**: 2-state chain fitted by
   `estimate_markov_matrix` on binned latent-state sequences (undecided /
   committed) with Laplace smoothing alpha = 0.5.
3. **Reference DDM**: drift proportional to coherence, fitted with a
   standard HDDM-style likelihood (documented in `analysis/` when Issue #4
   lands); used as the field-standard comparator, not as a packaged
   dependency.

## Fitting

- Log-likelihood of observed (time, outcome) pairs under
  `twolevel_log_likelihood`; grid search over (omega0, gamma) followed by
  Nelder–Mead polish; per-subject fits, and hierarchical partial pooling
  across subjects as a sensitivity arm.
- Integration grid: dt = 10 ms (convergence checked at 5 ms), RK4
  (`integrate_lindblad`).

## Model comparison

- **BIC** per subject: k ln n − 2 ln L; primary endpoint is the per-subject
  BIC difference (open-system minus Markov), sign-tested across subjects.
- **Held-out validation**: 5-fold CV over trials within subject; mean
  held-out log-likelihood per trial.
- **Recovery checks**: simulate from fitted parameters, refit, and require
  parameter recovery (correlation > 0.9) and model-identifiability (the
  correct model wins BIC on its own simulations > 80%).

## Hypothesis tests

- **H1**: sign test / Wilcoxon over per-subject BIC differences, separately
  per coherence band; prediction: open-system wins at low coherence.
- **H2**: Spearman correlation between fitted gamma and within-subject RT
  coefficient of variation; permutation p-value (5 000 shuffles).
- **H3**: LMM gamma/omega ~ coherence + (1|subject); prediction: positive
  slope (damped/classical regime at high coherence).
- **Falsifier** (pre-registered in README): if the open-system model wins
  nowhere (all coherence bands, BIC and CV), report the negative result.

## Reproducibility

- 13 unit tests green before merge; fixed seeds; one `analysis/run_all.py`;
  figures via `figures/make_all.py`.

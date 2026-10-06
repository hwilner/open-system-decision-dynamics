# open-system-decision-dynamics

**Quantum-like open-system dynamics (Lindblad master equation) as a model of
perceptual decision-making — tested against classical Markov and
drift-diffusion baselines on the MetaRDK random-dot-kinematogram dataset.**

## Core idea

A decision under uncertainty can be written as the dynamics of a two-level
"decision state" governed by the **GKSL (Lindblad) master equation**:

```
d rho / dt = -i [H, rho] + sum_k ( L_k rho L_k^dag - 0.5 {L_k^dag L_k, rho} )
```

- **H = (omega/2) sigma_x** — coherent evidence accumulation with
  *interference* (the quantum-like part: undecided states are superpositions,
  so probability can oscillate before committing).
- **Dephasing L = sqrt(gamma) sigma_z** — noise/commitment that kills
  off-diagonal coherences at rate 2 gamma while leaving populations fixed.
- **Amplitude damping L = sqrt(gamma) sigma_-** — irreversible relaxation
  into the committed state.

This follows the *quantum cognition* programme (Busemeyer & Bruza, 2012): the
formalism is used as a probabilistic dynamical system. **No physical quantum
brain is claimed.**

## Hypotheses

- **H1 (dynamics).** Choice probabilities over viewing time in MetaRDK show
  damped-oscillation structure better fit by the two-level open-system model
  than by a first-order Markov chain (BIC, held-out).
- **H2 (parameters).** The fitted dephasing rate gamma indexes individual
  "commitment speed" and correlates with response-time variability.
- **H3 (classical limit).** For high-coherence motion the model reduces to
  the classical (strongly damped) regime — quantum-like structure should
  appear mainly under *uncertainty*.

**Falsifier:** if the quantum-like model never beats the penalised classical
baselines out of sample (BIC), the framework is falsified for this task.

## Quickstart

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest tests/ -q        # 13 analytic anchors, all pass
```

```python
import numpy as np
from open_decision import choice_probability_trajectory

times = np.linspace(0, 4.0, 401)
p = choice_probability_trajectory(omega=2.0, gamma=0.3, times=times)
# gamma = 0 gives exactly sin^2(omega t / 2); gamma > 0 damps toward 1/2
```

## Repository map

| Path | Contents |
|---|---|
| `src/open_decision/lindblad.py` | Pauli operators, commutators, dissipators, RK4 master-equation integrator, Rabi Hamiltonian, dephasing/damping channels |
| `src/open_decision/models.py` | Choice-probability trajectories, Markov estimator + likelihood, two-level likelihood, BIC |
| `tests/` | 13 unit tests (Rabi sin² limit, dephasing rate 2γ, amplitude-damping relaxation, Markov recovery, BIC algebra) |
| `docs/INTRODUCTION.md` | publication-quality introduction with derivations |
| `docs/EXTENDED_INTRODUCTION.md` | high-school-level version with analogies and links |
| `docs/METHODS.md` | MetaRDK data, preprocessing, fitting, model comparison |
| `docs/STATUS_AND_PLAN.md` | milestone map (mirrors GitHub Issues #1–#7) |
| `docs/CURRENT_RESULTS_AND_DISCUSSION.md` | synthetic validation results, risks, open questions |

## Empirical target

MetaRDK: multi-site random-dot-kinematogram perceptual-decision dataset with
confidence ratings (OpenNeuro). See `docs/METHODS.md`.

## License

MIT.

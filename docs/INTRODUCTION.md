# Quantum-like open-system dynamics of perceptual decision-making

**Do choice dynamics under uncertainty carry the signature of *coherent*
processing — interference and damped oscillation — that classical Markov and
diffusion models cannot produce, and can the Lindblad master equation
capture it with two interpretable parameters?**

## Background

### The quantum-cognition programme

"Quantum cognition" (Busemeyer & Bruza, 2012) uses the *probability calculus
of quantum mechanics* — superposition, interference, incompatibility — as a
modelling language for human judgement and decision, without any claim of
physical quantum processes in the brain. Its empirical track record includes
order effects in surveys, conjunction/disjunction fallacies, and
categorisation–decision interactions that classical probability struggles to
fit. This project pushes the programme one level deeper: from static
judgements to the **time course** of a decision, modelled as an **open
quantum system**.

### The GKSL (Lindblad) master equation

The most general Markovian (memoryless) evolution of a density matrix rho
that preserves trace and positivity is the
Gorini–Kossakowski–Sudarshan–Lindblad equation:

```
d rho / dt = -i [H, rho]  +  sum_k D[L_k] rho,
D[L] rho = L rho L^dag - (1/2) {L^dag L, rho}.
```

- The **commutator** term −i[H, rho] is the coherent (Schroedinger-like)
  part: unitary rotation, capable of interference.
- The **dissipators** D[L_k] describe irreversible exchange with an
  "environment": noise, measurement, commitment — anything that destroys
  coherence or moves population one way.
- **Trace preservation** follows because tr[H, rho] = 0 (cyclic property of
  the trace) and tr D[L] rho = tr(L rho L^dag) − tr(L^dag L rho) = 0, again
  by cyclicity. Positivity is guaranteed by the GKSL theorem (Lindblad,
  1976). These two properties make the equation a safe *probabilistic*
  dynamical system: every trajectory is a valid density matrix, so every
  read-out is a valid probability.

### The two-level decision state

We model a binary perceptual decision (e.g. "dots move left" vs "right")
with a qubit-like state:

```
|0> = "undecided / accumulating",   |1> = "committed".
rho(t) = [ p0(t)   c(t)    ]
         [ c*(t)   p1(t)   ],        p0 + p1 = 1.
```

The **populations** p0, p1 are the probabilities of being undecided vs
committed; the **coherence** c(t) is the genuinely quantum-like degree of
freedom — a complex amplitude encoding *superposition between undecided and
committed*, which lets probability flow back and forth before it settles.

### Model components and their exact solutions

**Drive Hamiltonian (evidence accumulation with interference).**

```
H = (omega / 2) sigma_x,      sigma_x = [ 0 1 ; 1 0 ].
```

Starting from rho(0) = |0><0|, unitary evolution gives the **Rabi
oscillation**

```
p1(t) = sin^2(omega t / 2),
```

Derivation: U(t) = exp(−i H t) = cos(omega t/2) I − i sin(omega t/2) sigma_x
(because sigma_x^2 = I and the exponential of a Pauli matrix splits by Euler's
formula); applying U to |0> yields amplitude −i sin(omega t/2) on |1>, whose
modulus squared is the result. **omega** is the evidence-accumulation rate:
stronger evidence → faster oscillation toward commitment.

**Dephasing (noise/commitment pressure).** With jump operator

```
L = sqrt(gamma) sigma_z,
```

one finds d c / dt = −2 gamma c while populations are untouched (our tests
verify c(t) = c(0) e^{−2 gamma t} to 1e-3). Physically: the environment
"watches" the decision axis, washing out the superposition. Under drive +
dephasing the Rabi oscillation is **damped**: p1(t) oscillates with decaying
amplitude toward 1/2 — a signature no monotone classical accumulator shows.

**Amplitude damping (irreversible commitment).** L = sqrt(gamma) sigma_-
moves population from |0> to |1> at rate gamma; p1(t) → 1 exponentially
(verified in tests). This models absorbing commitment — the point of no
return.

### Why not just a drift-diffusion model (DDM)?

The DDM — a noisy integrator hitting a threshold — is the gold-standard
classical model of two-choice decisions. Its predicted commitment
probability is *monotone* in time for fixed evidence. The open-system model
differs in three testable ways:

1. **Oscillation**: coherent exchange between undecided and committed
   produces non-monotone choice curves under uncertainty.
2. **Two-channel noise**: dephasing (coherence loss) and damping (population
   relaxation) are distinct knobs; classical models conflate them.
3. **Parameter parsimony**: (omega, gamma) generate the full time course;
   the question is empirical — penalised model comparison (BIC) decides.

## Hypotheses

- **H1 (dynamics).** Held-out choice-vs-viewing-time curves in MetaRDK are
  better fit (BIC) by the two-level open-system model than by first-order
  Markov dynamics, especially at low motion coherence.
- **H2 (individual differences).** Fitted gamma (dephasing rate) correlates
  across subjects with RT variability — a "commitment speed" trait.
- **H3 (classical limit).** At high coherence the fitted gamma/omega ratio
  grows (strong damping) — the model self-selects the classical regime when
  evidence is strong, reserving quantum-like structure for uncertainty.
- **Falsifier.** If the open-system model never wins penalised out-of-sample
  comparisons, the framework is falsified for this task and we report the
  negative result.

## What is in this repository

`src/open_decision/lindblad.py` — Pauli matrices, commutator/anticommutator,
the dissipator D[L], the master-equation right-hand side, a 4th-order
Runge–Kutta integrator with Hermiticity hygiene, and constructors for the
Rabi drive, dephasing, and amplitude damping. `src/open_decision/models.py` —
the two-level choice-probability trajectory (analytic sin² limit when
gamma = 0), a Laplace-smoothed Markov estimator with log-likelihood, the
two-level log-likelihood for (time, outcome) observations, and BIC.
`tests/` — 13 analytic anchors: the [sigma_x, sigma_z] = −2i sigma_y
algebra, trace preservation, purity conservation under closed evolution,
coherence decay at exactly 2 gamma, amplitude-damping relaxation, the Rabi
sin² limit, damping toward 1/2, Markov-matrix recovery, likelihood ordering,
and BIC arithmetic.

## Key terms

- **Density matrix rho**: PSD, unit-trace matrix encoding the state;
  diagonal = probabilities, off-diagonal = coherences. *Why*: it is the
  unique state notion allowing both classical uncertainty and superposition.
- **GKSL / Lindblad equation**: the most general trace- and
  positivity-preserving Markovian dynamics. *When to use*: whenever a
  coherent system interacts with memoryless noise — here, a decision exposed
  to commitment pressure.
- **Hamiltonian H**: generator of coherent evolution; our H = (omega/2)
  sigma_x rotates undecided ↔ committed.
- **Jump operator L_k**: channel of irreversible dynamics; dephasing
  (sigma_z) kills coherence, damping (sigma_-) moves population.
- **Coherence c(t)**: off-diagonal of rho; the superposition amplitude.
  Its decay rate 2 gamma is a direct observable of the model.
- **Rabi oscillation**: sin²(omega t/2) probability sloshing between two
  levels under coherent drive; the interference signature.
- **Dephasing rate gamma**: how fast superpositions wash out; our H2
  "commitment speed" trait.
- **Markov chain baseline**: classical model with transition matrix W;
  P(next | current) only. The penalised competitor.
- **DDM (drift-diffusion model)**: gold-standard classical accumulator;
  included as a reference point in model comparison (via HDDM or custom).
- **BIC (Bayesian information criterion)**: k ln n − 2 ln L; lower is
  better; penalises the open-system model's extra flexibility — our
  referee.
- **MetaRDK**: multi-site random-dot-kinematogram dataset (motion-direction
  decisions at several coherence levels, with confidence); our test bed.
- **Coherence (motion)**: fraction of dots moving consistently; the task's
  evidence-strength dial.

## References

- Lindblad, G. (1976). On the generators of quantum dynamical semigroups.
  *Communications in Mathematical Physics*, 48, 119.
- Gorini, V., Kossakowski, A., & Sudarshan, E. C. G. (1976). Completely
  positive dynamical semigroups of N-level systems. *Journal of Mathematical
  Physics*, 17, 821.
- Breuer, H.-P., & Petruccione, F. (2002). *The Theory of Open Quantum
  Systems*. Oxford University Press.
- Busemeyer, J. R., & Bruza, P. D. (2012). *Quantum Models of Cognition and
  Decision*. Cambridge University Press.
- Broekaert, J. B., Basieva, I., Blasiak, P., & Pothos, E. M. (2020).
  Quantum-like dynamics applied to cognition. *Phil. Trans. R. Soc. A*.
- Ratcliff, R. (1978). A theory of memory retrieval. *Psychological Review*,
  85, 59. (The DDM.)
- Ruff, D. A., et al. / MetaRDK consortium — multi-site RDK dataset
  (OpenNeuro). See METHODS for the accession.

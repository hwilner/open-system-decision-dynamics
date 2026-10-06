# Extended introduction — decisions as a swinging pendulum that slowly stills

*For high-school readers and curious non-specialists. One sine wave, one
decaying exponential — that is all the math we need.*

## The one-paragraph story

When you watch a cloud of dots on a screen and must decide "left or right?",
your brain does not instantly flip a switch. Evidence builds up — and this
project models that build-up as a **pendulum**: probability swings from
"undecided" toward "committed" and can swing *back* before it settles, like a
pendulum swinging in honey. The swinging is the quantum-like part
(physicists call it a **Rabi oscillation**); the honey is noise and
commitment pressure (called **dephasing**). Two numbers — swing speed
(omega) and honey thickness (gamma) — generate the entire time course of a
decision. We then ask the only honest question: *does this two-number model
beat the classical alternatives on real data?* If not, we publish that too.

## The experiment we model (random-dot kinematograms)

The dataset is called **MetaRDK**. Volunteers watch a field of moving dots:
a hidden fraction (the **coherence**) moves consistently left or right; the
rest jump randomly. Easy trials (high coherence) are decided fast and
accurately; hard trials (low coherence) take long and waver. We have each
person's choices, reaction times, and confidence — thousands of trials from
multiple labs, freely downloadable (link in the table below).

## The model, piece by piece

**A decision with two addresses.** Imagine the decision lives in a house with
two rooms: room 0 = "still thinking", room 1 = "decided". At every moment the
decision has a *probability* of being found in each room — call them p0 and
p1 (they add to 1). Classical models only track these two probabilities.

**The secret corridor (coherence).** The quantum-like twist: there is also a
"corridor" between the rooms — an extra degree of freedom c, the
**coherence** of the state. While probability travels through the corridor,
it can *interfere* with itself — like two water waves meeting can cancel or
reinforce. This is what allows p1 to *overshoot and come back* instead of
creeping up monotonically. The full state is written as a little 2×2 table
called a **density matrix**: probabilities on the diagonal, the corridor on
the off-diagonal.

**The pendulum (drive, omega).** A force swings probability between the
rooms at speed omega. With no honey, the math is exact and beautiful:

  p1(t) = sin²(omega · t / 2)

— a perfect sine-squared wave: decided, undecided again, decided... Our
code reproduces this wave to 2 decimal places (it is one of the 13 tests).

**The honey (dephasing, gamma).** Real brains are noisy and real decisions
"lock in" gradually: the corridor slowly closes. The math says the corridor
shrinks as e^(−2·gamma·t) — and our tests verify the *exact* rate 2·gamma.
With honey, the pendulum stills: p1 oscillates with fading swings toward ½
(maximum wavering) until commitment finishes the job.

**The trapdoor (damping).** A second noise channel just moves probability
one way, room 0 → room 1, never back: irreversible commitment. p1 then
climbs to 1 exponentially — the classical-looking limit.

**The rulebook (Lindblad equation).** One equation assembles all of this —
the **GKSL master equation**. It is famous in physics because it is the most
general rule that (a) keeps probabilities adding to 1 and (b) never produces
a negative probability. Think of it as a safety certificate: whatever we
simulate, the answer is always a legal probability.

## What we will actually test

1. **H1 — shape of choice curves.** Does "probability of choosing right"
vs viewing time show damped swings (two-number model wins) or a monotone
rise (classical models win)? The judge is **BIC**, a score that rewards fit
but *fines* extra parameters — so our model only wins if the swing is real.
2. **H2 — people differ.** Is your personal gamma (honey thickness) stable
across sessions, and does it predict how variable your reaction times are?
3. **H3 — uncertainty is where it shows.** On easy trials the model should
choose thick honey (classical regime); quantum-like swing should survive
mainly on hard, uncertain trials.

## Every keyword, explained

| Term | Plain meaning | Why here | Link |
|---|---|---|---|
| RDK / coherence | Moving-dot display; fraction of signal dots | The experiment | https://en.wikipedia.org/wiki/Random-dot_kinematogram |
| MetaRDK | Public multi-lab RDK dataset | Our data | https://openneuro.org/ |
| Density matrix | 2×2 table: room probabilities + corridor | The state we simulate | https://en.wikipedia.org/wiki/Density_matrix |
| Superposition | Being "between rooms" with wave-like amplitude | Allows interference/overshoot | https://en.wikipedia.org/wiki/Quantum_superposition |
| Interference | Waves reinforcing/cancelling | The non-classical signature | https://en.wikipedia.org/wiki/Wave_interference |
| Hamiltonian | The pendulum's push rule | Evidence accumulation | https://en.wikipedia.org/wiki/Hamiltonian_(quantum_mechanics) |
| Rabi oscillation | sin² probability sloshing between two states | H1's predicted swing | https://en.wikipedia.org/wiki/Rabi_cycle |
| Dephasing | Corridor closing; wave→coin-flip | The honey, rate 2γ | https://en.wikipedia.org/wiki/Quantum_decoherence |
| Lindblad (GKSL) equation | Safety-certified rule for noisy quantum dynamics | Keeps all probabilities legal | https://en.wikipedia.org/wiki/Lindbladian |
| Jump operator | One noise channel in the rulebook | Dephasing / damping knobs | https://en.wikipedia.org/wiki/Lindbladian#Diagonalization |
| Markov chain | Classical "next room depends only on current room" model | The competitor to beat | https://en.wikipedia.org/wiki/Markov_chain |
| Drift-diffusion model | Classical evidence-accumulator with threshold | Gold-standard competitor | https://en.wikipedia.org/wiki/Two-alternative_forced_choice#Drift-diffusion_model |
| BIC | Fit score with a parameter fine | The referee | https://en.wikipedia.org/wiki/Bayesian_information_criterion |
| Reaction time (RT) | Time from dots appear to button press | H2's behavioural correlate | https://en.wikipedia.org/wiki/Mental_chronometry |

## Try it yourself

```python
import numpy as np
from open_decision import choice_probability_trajectory

t = np.linspace(0, 8, 801)
for gamma in [0.0, 0.2, 0.8]:
    p = choice_probability_trajectory(omega=2.0, gamma=gamma, times=t)
    print(gamma, "->", "first peak p1 =", round(p[:200].max(), 3))
# gamma = 0: pure sin^2 wave (peaks at 1.0)
# bigger gamma: the swings die out and p1 relaxes toward 0.5
```

## Common confusions, pre-empted

- *"Do you think the brain is a quantum computer?"* No. We use the math of
  quantum probability because it handles "between two minds" better than
  classical probability. Same math, borrowed — like using accountants'
  spreadsheets to track your football team's scores.
- *"Isn't this just more parameters?"* Two (omega, gamma) — fewer than most
  classical fits — and BIC fines us for every parameter anyway.
- *"What if the classical model wins?"* Then that is the result, and the
  falsifier built into the README makes it a clean, publishable negative.

## Friendly resources

- The double-slit experiment (interference intuition), 3Blue1Brown-style
  video: https://www.youtube.com/watch?v=Iuv6hY6zsd0
- Markov chains (Khan Academy):
  https://www.khanacademy.org/math/statistics-probability
- OpenNeuro (free brain/behaviour datasets): https://openneuro.org/
- Busemeyer & Bruza's book (the field's map):
  https://www.cambridge.org/core/books/quantum-models-of-cognition-and-decision/

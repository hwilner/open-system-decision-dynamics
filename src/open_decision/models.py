"""Decision models: quantum-like open-system vs classical Markov.

Both model families assign a likelihood to an observed sequence of
latent/behavioural states.  The quantum-like model evolves a two-level
density matrix under a drive Hamiltonian (evidence accumulation with
interference) plus dephasing (noise/commitment); the classical baseline
is a first-order Markov chain.  Model comparison uses the Bayesian
information criterion so that the extra flexibility of the quantum-like
model is penalised -- the falsifier of this repository is precisely that
it never wins out of sample.
"""

from __future__ import annotations

import numpy as np

from open_decision.lindblad import (
    dephasing_operators,
    integrate_lindblad,
    rabi_hamiltonian,
)


def ground_state() -> np.ndarray:
    """Density matrix ``|0><0|`` of the two-level decision state."""
    return np.array([[1, 0], [0, 0]], dtype=complex)


def choice_probability_trajectory(omega: float, gamma: float,
                                  times: np.ndarray) -> np.ndarray:
    """Probability of the "commit" state over time for the two-level model.

    Integrates the master equation for ``H = (omega/2) sigma_x`` with
    pure dephasing ``gamma`` starting from ``|0>`` and returns
    ``P_1(t) = rho_11(t)``.  For ``gamma = 0`` this is exactly
    ``sin^2(omega t / 2)``; dephasing damps the oscillation toward 1/2.

    Args:
        omega: Drive frequency (evidence-accumulation rate).
        gamma: Dephasing rate.
        times: Monotone array of times.

    Returns:
        Commit probability at each time.
    """
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or times.size < 2 or times[0] != 0:
        raise ValueError("times must be 1-D, start at 0, len >= 2")
    dt = float(np.min(np.diff(times)))
    if dt <= 0:
        raise ValueError("times must be increasing")
    n_steps = int(round(times[-1] / dt))
    traj = integrate_lindblad(ground_state(), rabi_hamiltonian(omega),
                              dephasing_operators(gamma), dt, n_steps)
    idx = np.round(times / dt).astype(int)
    return np.real(traj[idx, 1, 1])


def estimate_markov_matrix(sequences: list[np.ndarray], n_states: int,
                           alpha: float = 1.0) -> np.ndarray:
    """Laplace-smoothed maximum-likelihood Markov transition matrix.

    Args:
        sequences: Observed state sequences (integer labels).
        n_states: Number of states.
        alpha: Additive smoothing constant (>= 0).

    Returns:
        Row-stochastic matrix ``W[i, j] = P(next = j | current = i)``.
    """
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    counts = np.full((n_states, n_states), float(alpha))
    for seq in sequences:
        s = np.asarray(seq, dtype=int)
        for a, b in zip(s[:-1], s[1:]):
            counts[a, b] += 1.0
    return counts / counts.sum(axis=1, keepdims=True)


def markov_log_likelihood(sequences: list[np.ndarray], w: np.ndarray) -> float:
    """Log-likelihood of state sequences under a Markov matrix.

    Initial states contribute a uniform ``1 / n_states`` factor so that
    models with different transition structure are compared fairly.

    Args:
        sequences: Observed state sequences.
        w: Row-stochastic transition matrix.

    Returns:
        Total log-likelihood.
    """
    w = np.asarray(w, dtype=float)
    n = w.shape[0]
    ll = 0.0
    for seq in sequences:
        s = np.asarray(seq, dtype=int)
        ll += np.log(1.0 / n)
        ll += float(np.sum(np.log(w[s[:-1], s[1:]])))
    return ll


def twolevel_log_likelihood(observations: np.ndarray, omega: float,
                            gamma: float, times: np.ndarray) -> float:
    """Log-likelihood of binary commit/undecided observations.

    Each observation ``(t_k, y_k)`` with ``y_k in {0, 1}`` contributes
    ``log P(y_k | t_k)`` under the two-level open-system model.

    Args:
        observations: Array of shape ``(n, 2)`` with columns (time,
            binary outcome).
        omega: Drive frequency.
        gamma: Dephasing rate.
        times: Integration grid starting at 0 covering all observation
            times.

    Returns:
        Total log-likelihood.
    """
    obs = np.asarray(observations, dtype=float)
    p = np.clip(choice_probability_trajectory(omega, gamma, times), 1e-12,
                1 - 1e-12)
    grid = np.asarray(times, dtype=float)
    ll = 0.0
    for t, y in obs:
        pk = float(p[int(np.argmin(np.abs(grid - t)))])
        ll += np.log(pk if y == 1 else 1.0 - pk)
    return float(ll)


def bic(log_likelihood: float, n_params: int, n_obs: int) -> float:
    """Bayesian information criterion ``k log(n) - 2 log L``.

    Args:
        log_likelihood: Maximised log-likelihood.
        n_params: Number of fitted parameters.
        n_obs: Number of observations.

    Returns:
        BIC value (lower is better).
    """
    if n_obs < 1:
        raise ValueError("n_obs must be positive")
    return float(n_params * np.log(n_obs) - 2.0 * log_likelihood)

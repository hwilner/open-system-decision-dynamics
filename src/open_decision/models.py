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
    integrate_lindblad_on_grid,
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

    The master equation is integrated onto the requested times themselves,
    so a non-uniform grid is answered at the times it asks for rather than
    at the nearest point of a uniform integration grid.  The integration
    step never exceeds the finest spacing requested, so a fine grid buys the
    corresponding accuracy.

    Args:
        omega: Drive frequency (evidence-accumulation rate).
        gamma: Dephasing rate.
        times: Strictly increasing array of times starting at 0.

    Returns:
        Commit probability at each time.

    Raises:
        ValueError: If ``times`` is not one-dimensional, starts at 0, holds
            at least two entries, or is not strictly increasing.
    """
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or times.size < 2 or times[0] != 0:
        raise ValueError("times must be 1-D, start at 0, len >= 2")
    spacings = np.diff(times)
    if np.any(spacings <= 0):
        raise ValueError("times must be increasing")
    max_dt = float(np.min(spacings))
    traj = integrate_lindblad_on_grid(ground_state(), rabi_hamiltonian(omega),
                                      dephasing_operators(gamma), times,
                                      max_dt)
    return np.real(traj[:, 1, 1])


def _validated_labels(seq: np.ndarray, n_states: int) -> np.ndarray:
    """Return the integer state labels of one sequence after validation.

    Args:
        seq: Observed state sequence.
        n_states: Number of states the labels must fall inside.

    Returns:
        The labels as integers.

    Raises:
        ValueError: If the sequence is not one-dimensional, holds a
            non-integer label, or holds a label outside ``[0, n_states)``.
    """
    labels = np.asarray(seq, dtype=float)
    if labels.ndim != 1:
        raise ValueError("each sequence must be a 1-D array of state labels")
    if labels.size == 0:
        return np.empty(0, dtype=int)
    if not np.all(labels == np.round(labels)):
        raise ValueError("state labels must be integers")
    if labels.min() < 0 or labels.max() >= n_states:
        raise ValueError("state labels must lie in [0, n_states)")
    return labels.astype(int)


def estimate_markov_matrix(sequences: list[np.ndarray], n_states: int,
                           alpha: float = 1.0) -> np.ndarray:
    """Laplace-smoothed maximum-likelihood Markov transition matrix.

    Args:
        sequences: Observed state sequences (integer labels).
        n_states: Number of states.
        alpha: Additive smoothing constant (>= 0).

    Returns:
        Row-stochastic matrix ``W[i, j] = P(next = j | current = i)``.

    Raises:
        ValueError: If ``alpha`` is negative, ``n_states`` is not positive, a
            state label is not an integer in ``[0, n_states)``, or a state has
            no observed outgoing transition while ``alpha`` is zero (its row
            would be undefined).
    """
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    if n_states < 1:
        raise ValueError("n_states must be positive")
    counts = np.full((n_states, n_states), float(alpha))
    for seq in sequences:
        s = _validated_labels(seq, n_states)
        for a, b in zip(s[:-1], s[1:]):
            counts[a, b] += 1.0
    totals = counts.sum(axis=1, keepdims=True)
    if np.any(totals == 0):
        unobserved = np.flatnonzero(totals.ravel() == 0).tolist()
        raise ValueError(
            f"no observed transitions out of state(s) {unobserved}; use a "
            "positive alpha or drop those states")
    return counts / totals


def markov_log_likelihood(sequences: list[np.ndarray], w: np.ndarray) -> float:
    """Log-likelihood of state sequences under a Markov matrix.

    Initial states contribute a uniform ``1 / n_states`` factor so that
    models with different transition structure are compared fairly.

    Args:
        sequences: Observed state sequences.
        w: Row-stochastic transition matrix.

    Returns:
        Total log-likelihood, which is ``-inf`` when a sequence contains a
        transition the matrix gives probability zero.

    Raises:
        ValueError: If a state label is not an integer in
            ``[0, n_states)``.
    """
    w = np.asarray(w, dtype=float)
    n = w.shape[0]
    ll = 0.0
    for seq in sequences:
        s = _validated_labels(seq, n)
        ll += np.log(1.0 / n)
        # A zero transition probability makes the sequence impossible under
        # W, which is a log-likelihood of -inf rather than an error.
        with np.errstate(divide="ignore"):
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

    Raises:
        ValueError: If the observations are not an ``(n, 2)`` array, an
            outcome is not 0 or 1, or an observation time falls outside the
            integration grid.
    """
    obs = np.asarray(observations, dtype=float)
    grid = np.asarray(times, dtype=float)
    p = choice_probability_trajectory(omega, gamma, grid)
    if obs.ndim != 2 or obs.shape[1] != 2:
        raise ValueError("observations must have shape (n, 2)")
    outcomes = obs[:, 1]
    if not np.all(np.isin(outcomes, (0.0, 1.0))):
        raise ValueError("observation outcomes must be 0 or 1")
    obs_times = obs[:, 0]
    if np.any(obs_times < grid[0]) or np.any(obs_times > grid[-1]):
        raise ValueError(
            "observation times must lie inside the integration grid")
    # Off-grid observation times are read off the trajectory by linear
    # interpolation; snapping them to the nearest grid point would score the
    # likelihood at a different time than the one observed.
    p_obs = np.clip(np.interp(obs_times, grid, p), 1e-12, 1.0 - 1e-12)
    return float(np.sum(np.log(np.where(outcomes == 1.0, p_obs,
                                       1.0 - p_obs))))


def bic(log_likelihood: float, n_params: int, n_obs: int) -> float:
    """Bayesian information criterion ``k log(n) - 2 log L``.

    Args:
        log_likelihood: Maximised log-likelihood.
        n_params: Number of fitted parameters.
        n_obs: Number of observations.

    Returns:
        BIC value (lower is better).

    Raises:
        ValueError: If ``n_obs`` is not positive or the log-likelihood is
            NaN (a missing score, which would silently never compare).
    """
    if n_obs < 1:
        raise ValueError("n_obs must be positive")
    if np.isnan(log_likelihood):
        raise ValueError("log_likelihood must not be NaN")
    return float(n_params * np.log(n_obs) - 2.0 * log_likelihood)

"""Unit tests for the open_decision package."""

import unittest

import numpy as np

from open_decision.lindblad import (
    SIGMA_MINUS,
    SIGMA_X,
    SIGMA_Z,
    amplitude_damping_operators,
    commutator,
    dephasing_operators,
    dissipator,
    integrate_lindblad,
    rabi_hamiltonian,
)
from open_decision.models import (
    bic,
    choice_probability_trajectory,
    estimate_markov_matrix,
    ground_state,
    markov_log_likelihood,
    twolevel_log_likelihood,
)


def purity(rho):
    """tr(rho^2) helper."""
    return np.real(np.trace(rho @ rho))


class TestLindbladCore(unittest.TestCase):
    """Master-equation mechanics."""

    def test_commutator_anticommutator(self):
        # [sigma_x, sigma_z] = -2i sigma_y
        np.testing.assert_allclose(
            commutator(SIGMA_X, SIGMA_Z),
            -2j * np.array([[0, -1j], [1j, 0]]), atol=1e-12)

    def test_trace_preserved_under_dephasing(self):
        rho0 = 0.5 * (np.eye(2) + 0.3 * SIGMA_X + 0.2 * SIGMA_Z)
        traj = integrate_lindblad(rho0, np.zeros((2, 2)),
                                  dephasing_operators(0.7), 0.01, 200)
        np.testing.assert_allclose(
            np.real(np.trace(traj, axis1=-2, axis2=-1)), 1.0, atol=1e-10)

    def test_purity_preserved_without_dissipation(self):
        traj = integrate_lindblad(ground_state(), rabi_hamiltonian(1.3),
                                  [], 0.005, 300)
        np.testing.assert_allclose([purity(r) for r in traj[::50]], 1.0,
                                   atol=1e-8)

    def test_purity_decreases_with_dephasing(self):
        traj = integrate_lindblad(ground_state(), rabi_hamiltonian(1.0),
                                  dephasing_operators(0.5), 0.01, 200)
        self.assertLess(purity(traj[-1]), purity(traj[0]))

    def test_dephasing_leaves_populations_fixed(self):
        rho0 = np.diag([0.7, 0.3]).astype(complex)
        traj = integrate_lindblad(rho0, np.zeros((2, 2)),
                                  dephasing_operators(1.0), 0.01, 100)
        np.testing.assert_allclose(np.real(traj[-1].diagonal()),
                                   [0.7, 0.3], atol=1e-10)

    def test_dephasing_kills_coherence_at_rate_2gamma(self):
        gamma = 0.8
        rho0 = 0.5 * np.ones((2, 2), dtype=complex)  # |+><+|
        times, coh = [], []
        dt, n = 0.005, 300
        traj = integrate_lindblad(rho0, np.zeros((2, 2)),
                                  dephasing_operators(gamma), dt, n)
        ts = np.arange(n + 1) * dt
        measured = np.real(traj[:, 0, 1])
        expected = 0.5 * np.exp(-2 * gamma * ts)
        np.testing.assert_allclose(measured, expected, atol=1e-3)

    def test_amplitude_damping_relaxes_to_ground(self):
        traj = integrate_lindblad(ground_state(), np.zeros((2, 2)),
                                  amplitude_damping_operators(1.0), 0.01,
                                  800)
        self.assertGreater(np.real(traj[-1][1, 1]), 0.999)


class TestDecisionModels(unittest.TestCase):
    """Two-level decision model and classical baselines."""

    def test_rabi_limit_matches_sin_squared(self):
        omega = 2.0
        times = np.linspace(0, 3.0, 301)
        p = choice_probability_trajectory(omega, 0.0, times)
        expected = np.sin(omega * times / 2) ** 2
        np.testing.assert_allclose(p, expected, atol=2e-3)

    def test_dephasing_damps_oscillation_toward_half(self):
        times = np.linspace(0, 12.0, 1201)
        p = choice_probability_trajectory(2.0, 1.5, times)
        self.assertLess(np.abs(p[-1] - 0.5), 0.05)

    def test_markov_estimator_recovers_matrix(self):
        rng = np.random.default_rng(0)
        w_true = np.array([[0.9, 0.1], [0.2, 0.8]])
        seqs = []
        for _ in range(60):
            s = [0]
            for _ in range(200):
                stay = rng.random() < w_true[s[-1], s[-1]]
                s.append(s[-1] if stay else 1 - s[-1])
            seqs.append(np.array(s))
        w_est = estimate_markov_matrix(seqs, 2, alpha=0.5)
        np.testing.assert_allclose(w_est, w_true, atol=0.03)
        np.testing.assert_allclose(w_est.sum(axis=1), 1.0, atol=1e-12)

    def test_markov_loglik_prefers_true_model(self):
        rng = np.random.default_rng(1)
        w_true = np.array([[0.85, 0.15], [0.15, 0.85]])
        seqs = []
        for _ in range(30):
            s = [0]
            for _ in range(150):
                stay = rng.random() < w_true[s[-1], s[-1]]
                s.append(s[-1] if stay else 1 - s[-1])
            seqs.append(np.array(s))
        ll_true = markov_log_likelihood(seqs, w_true)
        ll_flat = markov_log_likelihood(seqs, np.full((2, 2), 0.5))
        self.assertGreater(ll_true, ll_flat)

    def test_twolevel_loglik_sensible(self):
        times = np.linspace(0, 2.0, 401)
        p = choice_probability_trajectory(1.0, 0.0, times)
        obs = np.stack([times, (p > 0.5).astype(float)], axis=1)
        ll = twolevel_log_likelihood(obs, 1.0, 0.0, times)
        self.assertGreater(ll, -len(obs) * np.log(2))

    def test_bic_penalises_parameters(self):
        ll, n = -100.0, 500
        self.assertLess(bic(ll, 2, n), bic(ll, 10, n))
        self.assertAlmostEqual(bic(ll, 2, n),
                               2 * np.log(500) + 200.0, places=10)


if __name__ == "__main__":
    unittest.main()

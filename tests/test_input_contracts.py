"""Contract tests for the public model API.

Every test in this module pins down an input contract that the package must
either honour exactly or reject loudly.  The defects guarded against here
were silent: the package returned a well-formed number for an input it did
not actually support, so a caller could not tell a wrong answer from a right
one.
"""

import unittest

import numpy as np

from open_decision.models import (
    bic,
    choice_probability_trajectory,
    estimate_markov_matrix,
    markov_log_likelihood,
    twolevel_log_likelihood,
)


class TestChoiceProbabilityGrid(unittest.TestCase):
    """The trajectory must describe the requested times, not nearby ones."""

    def test_nonuniform_grid_reports_requested_times(self):
        """A non-uniform grid must be answered at the times it asks for.

        The trajectory used to be rounded to the nearest point of a uniform
        integration grid, so the value returned for t = 0.5 was really the
        value at t = 0.4.
        """
        omega = 2.0
        times = np.array([0.0, 0.2, 0.5])
        p = choice_probability_trajectory(omega, 0.0, times)
        expected = np.sin(omega * times / 2) ** 2
        np.testing.assert_allclose(p, expected, atol=2e-3)

    def test_nonuniform_grid_keeps_neighbouring_values_distinct(self):
        """Two distinct requested times must not collapse onto one value.

        With a 0.3 and a 0.5 second request the old rounding mapped both
        onto the same integration point, reporting one number twice.
        """
        times = np.array([0.0, 0.3, 0.5])
        p = choice_probability_trajectory(2.0, 0.0, times)
        self.assertNotAlmostEqual(p[1], p[2], places=3)

    def test_uniform_grid_keeps_the_analytic_anchor(self):
        """The uniform-grid anchor must not drift with the correction."""
        times = np.linspace(0.0, 3.0, 301)
        p = choice_probability_trajectory(2.0, 0.0, times)
        np.testing.assert_allclose(p, np.sin(times) ** 2, atol=2e-3)

    def test_decreasing_grid_is_rejected(self):
        """A grid that runs backwards is an error, not a reordering."""
        with self.assertRaises(ValueError):
            choice_probability_trajectory(2.0, 0.0, np.array([0.0, 1.0, 0.5]))

    def test_repeated_time_is_rejected(self):
        """A repeated time has zero spacing and cannot define a step."""
        with self.assertRaises(ValueError):
            choice_probability_trajectory(2.0, 0.0, np.array([0.0, 0.2, 0.2]))

    def test_grid_must_start_at_zero(self):
        """The trajectory is defined relative to the initial state at t = 0."""
        with self.assertRaises(ValueError):
            choice_probability_trajectory(2.0, 0.0, np.array([0.1, 0.2, 0.3]))


class TestTwoLevelLogLikelihoodContract(unittest.TestCase):
    """Observations must match the grid and the binary outcome coding."""

    def setUp(self):
        """Use a regular integration grid shared by the cases below."""
        self.grid = np.linspace(0.0, 2.0, 401)

    def test_observation_after_the_grid_is_rejected(self):
        """A time outside the grid used to be snapped to the last grid point."""
        obs = np.array([[0.5, 1.0], [99.0, 1.0]])
        with self.assertRaises(ValueError):
            twolevel_log_likelihood(obs, 1.0, 0.0, self.grid)

    def test_observation_before_the_grid_is_rejected(self):
        """A negative time is outside the grid and must not be snapped."""
        obs = np.array([[-0.5, 1.0]])
        with self.assertRaises(ValueError):
            twolevel_log_likelihood(obs, 1.0, 0.0, self.grid)

    def test_non_binary_outcome_is_rejected(self):
        """An outcome of 7 used to be scored as "not committed"."""
        obs = np.array([[0.5, 7.0]])
        with self.assertRaises(ValueError):
            twolevel_log_likelihood(obs, 1.0, 0.0, self.grid)

    def test_missing_outcome_is_rejected(self):
        """A NaN outcome is missing data, not a zero."""
        obs = np.array([[0.5, np.nan]])
        with self.assertRaises(ValueError):
            twolevel_log_likelihood(obs, 1.0, 0.0, self.grid)

    def test_malformed_observations_are_rejected(self):
        """Observations must be an (n, 2) array of (time, outcome) pairs."""
        with self.assertRaises(ValueError):
            twolevel_log_likelihood(np.array([0.5, 1.0]), 1.0, 0.0, self.grid)

    def test_on_grid_observation_keeps_its_value(self):
        """An observation on a grid point keeps the same likelihood."""
        obs = np.array([[0.5, 1.0], [1.0, 0.0]])
        ll = twolevel_log_likelihood(obs, 1.0, 0.0, self.grid)
        p = choice_probability_trajectory(1.0, 0.0, self.grid)
        # The grid runs from 0 to 2 in steps of 0.005, so t = 0.5 is index
        # 100 and t = 1.0 is index 200.
        expected = np.log(p[100]) + np.log(1.0 - p[200])
        self.assertAlmostEqual(ll, expected, places=10)


class TestMarkovEstimatorContract(unittest.TestCase):
    """The Markov estimator must not invent states or undefined rows."""

    def test_negative_state_label_is_rejected(self):
        """A label of -1 indexed the last row of the count matrix.

        The transitions of an unobserved state were therefore attributed
        silently to a real one.
        """
        with self.assertRaises(ValueError):
            estimate_markov_matrix([np.array([-1, -1, 0])], 2, alpha=0.0)

    def test_out_of_range_state_label_is_rejected(self):
        """A label beyond the state count is a data error, not an error."""
        with self.assertRaises(ValueError):
            estimate_markov_matrix([np.array([0, 1, 2])], 2, alpha=0.0)

    def test_non_integer_state_label_is_rejected(self):
        """A fractional label used to be truncated to the next integer."""
        with self.assertRaises(ValueError):
            estimate_markov_matrix([np.array([0.0, 0.5, 1.0])], 2, alpha=0.0)

    def test_unidentifiable_row_is_rejected(self):
        """A state with no observed outgoing transition has no row.

        Without smoothing the row was all NaN, and the NaN spread into the
        likelihood and the BIC of every model compared with it.
        """
        with self.assertRaises(ValueError):
            estimate_markov_matrix([np.array([0, 0, 1])], 3, alpha=0.0)

    def test_smoothing_defines_every_row(self):
        """With smoothing the same data is estimable and stays finite."""
        w = estimate_markov_matrix([np.array([0, 0, 1])], 3, alpha=0.5)
        self.assertFalse(np.isnan(w).any())
        np.testing.assert_allclose(w.sum(axis=1), 1.0, atol=1e-12)

    def test_markov_loglik_rejects_out_of_range_labels(self):
        """A negative label in the likelihood used to wrap to the last row."""
        w = np.array([[0.5, 0.5], [0.5, 0.5]])
        with self.assertRaises(ValueError):
            markov_log_likelihood([np.array([0, -1])], w)

    def test_impossible_transition_gives_minus_infinity(self):
        """A zero transition probability means the sequence cannot occur.

        The log-likelihood is -inf, which is a meaningful score, not an
        exception and not a NaN.
        """
        w = np.array([[1.0, 0.0], [0.0, 1.0]])
        ll = markov_log_likelihood([np.array([0, 1])], w)
        self.assertEqual(ll, -np.inf)

    def test_bic_rejects_a_missing_log_likelihood(self):
        """A NaN likelihood used to yield a NaN score that never compares."""
        with self.assertRaises(ValueError):
            bic(float("nan"), 2, 100)


if __name__ == "__main__":
    unittest.main()

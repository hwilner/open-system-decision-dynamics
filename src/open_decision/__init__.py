"""Quantum-like open-system models of decision dynamics.

Public API: Lindblad master-equation machinery
(:mod:`open_decision.lindblad`) and decision models with classical
baselines and model comparison (:mod:`open_decision.models`).
"""

from open_decision.lindblad import (
    IDENTITY,
    SIGMA_MINUS,
    SIGMA_X,
    SIGMA_Y,
    SIGMA_Z,
    amplitude_damping_operators,
    anticommutator,
    commutator,
    dephasing_operators,
    dissipator,
    integrate_lindblad,
    lindblad_rhs,
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

__all__ = [
    "IDENTITY",
    "SIGMA_MINUS",
    "SIGMA_X",
    "SIGMA_Y",
    "SIGMA_Z",
    "amplitude_damping_operators",
    "anticommutator",
    "bic",
    "choice_probability_trajectory",
    "commutator",
    "dephasing_operators",
    "dissipator",
    "estimate_markov_matrix",
    "ground_state",
    "integrate_lindblad",
    "lindblad_rhs",
    "markov_log_likelihood",
    "rabi_hamiltonian",
    "twolevel_log_likelihood",
]

__version__ = "0.1.0"

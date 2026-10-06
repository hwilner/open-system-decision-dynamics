"""Open quantum-system dynamics: Hamiltonian + Lindblad dissipators.

The Gorini-Kossakowski-Sudarshan-Lindblad (GKSL) master equation

    d rho / dt = -i [H, rho] + sum_k ( L_k rho L_k^dag
                                        - 0.5 {L_k^dag L_k, rho} )

is the most general Markovian evolution preserving trace and positivity.
Here it serves as a *quantum-like cognitive model*: a two-level "decision
state" undergoes coherent rotation (evidence accumulation with
interference) plus dissipative dephasing/damping (commitment, noise).
No physical quantum brain is implied -- the equation is used as a
flexible probabilistic dynamical system, following the quantum-cognition
programme (Busemeyer & Bruza 2012; Broekaert et al. 2020).
"""

from __future__ import annotations

import numpy as np

SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)
SIGMA_MINUS = np.array([[0, 0], [1, 0]], dtype=complex)  # |1><0| decay
IDENTITY = np.eye(2, dtype=complex)


def commutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Commutator ``[a, b] = ab - ba``."""
    return a @ b - b @ a


def anticommutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Anticommutator ``{a, b} = ab + ba``."""
    return a @ b + b @ a


def dissipator(rho: np.ndarray, l: np.ndarray) -> np.ndarray:
    """Lindblad dissipator ``D[L] rho`` for a single jump operator.

    ``D[L] rho = L rho L^dag - 0.5 {L^dag L, rho}``.

    Args:
        rho: Density matrix.
        l: Jump (Lindblad) operator of the same dimension.

    Returns:
        The dissipative contribution to ``d rho / dt``.
    """
    ld = l.conj().T
    return l @ rho @ ld - 0.5 * anticommutator(ld @ l, rho)


def lindblad_rhs(rho: np.ndarray, h: np.ndarray,
                 l_ops: list[np.ndarray]) -> np.ndarray:
    """Right-hand side of the GKSL master equation.

    Args:
        rho: Current density matrix.
        h: Hamiltonian (Hermitian).
        l_ops: List of Lindblad jump operators (possibly empty).

    Returns:
        ``d rho / dt``.
    """
    rhs = -1j * commutator(h, rho)
    for l in l_ops:
        rhs = rhs + dissipator(rho, l)
    return rhs


def integrate_lindblad(rho0: np.ndarray, h: np.ndarray,
                       l_ops: list[np.ndarray], dt: float,
                       n_steps: int) -> np.ndarray:
    """Integrate the master equation with fourth-order Runge-Kutta.

    Args:
        rho0: Initial density matrix.
        h: Hamiltonian.
        l_ops: Lindblad jump operators.
        dt: Time step.
        n_steps: Number of steps.

    Returns:
        Array of shape ``(n_steps + 1, d, d)`` with the state trajectory.
    """
    rho = np.array(rho0, dtype=complex, copy=True)
    traj = np.empty((n_steps + 1,) + rho.shape, dtype=complex)
    traj[0] = rho
    for i in range(1, n_steps + 1):
        k1 = lindblad_rhs(rho, h, l_ops)
        k2 = lindblad_rhs(rho + 0.5 * dt * k1, h, l_ops)
        k3 = lindblad_rhs(rho + 0.5 * dt * k2, h, l_ops)
        k4 = lindblad_rhs(rho + dt * k3, h, l_ops)
        rho = rho + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        # numerical hygiene: keep Hermitian
        rho = 0.5 * (rho + rho.conj().T)
        traj[i] = rho
    return traj


def rabi_hamiltonian(omega: float) -> np.ndarray:
    """Two-level drive Hamiltonian ``H = (omega / 2) sigma_x``.

    Without dissipation, a state starting in ``|0>`` oscillates with
    ``P(excited, t) = sin^2(omega t / 2)`` -- the Rabi oscillation.

    Args:
        omega: Angular drive frequency.

    Returns:
        2x2 Hermitian matrix.
    """
    return 0.5 * omega * SIGMA_X


def dephasing_operators(gamma: float) -> list[np.ndarray]:
    """Pure-dephasing jump operator ``L = sqrt(gamma) sigma_z``.

    Damps off-diagonal coherences at rate ``2 gamma`` while leaving
    populations untouched.

    Args:
        gamma: Dephasing rate (non-negative).

    Returns:
        Single-element list of jump operators.
    """
    if gamma < 0:
        raise ValueError("gamma must be non-negative")
    return [np.sqrt(gamma) * SIGMA_Z]


def amplitude_damping_operators(gamma: float) -> list[np.ndarray]:
    """Amplitude-damping jump operator ``L = sqrt(gamma) sigma_-``.

    Relaxes the excited state ``|0>`` to ``|1>`` at rate gamma (energy
    loss / commitment-like irreversibility).

    Args:
        gamma: Damping rate (non-negative).

    Returns:
        Single-element list of jump operators.
    """
    if gamma < 0:
        raise ValueError("gamma must be non-negative")
    return [np.sqrt(gamma) * SIGMA_MINUS]

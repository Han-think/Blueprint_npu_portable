"""
solve_fea.py -- real first-order structural FE (Euler-Bernoulli beam), numpy-only
=================================================================================

This is an ACTUAL numerical solver, not an empirical ratio: the critical
load-path member is discretized into Euler-Bernoulli beam elements, the global
stiffness matrix is assembled, boundary conditions (cantilever root) and loads
(distributed self-weight + carried tip load) are applied, and K u = F is solved
for nodal displacement/rotation. Element bending moments -> stress -> Factor of
Safety are recovered from the solved field.

HONEST LIMIT: 1D beam idealization of the primary member with assumed load
factor and material allowable. It is a genuine FE solve at beam-theory fidelity,
NOT a 3D continuum FEA and NOT a certified structural qualification.

Depends only on numpy (always present with build123d).
"""
from __future__ import annotations

import numpy as np

# Young's modulus E (MPa = N/mm^2). Educational values, not certified.
E_MPA = {
    "pla": 3500, "petg": 2100, "abs": 2000, "asa": 2100, "nylon": 2000,
    "tpu": 60, "aluminum": 69000, "al6061": 69000, "steel": 200000, "titanium": 110000,
}
DEFAULT_E = 2100.0


def _beam_element_k(EI: float, L: float) -> np.ndarray:
    """2-node Euler-Bernoulli planar beam element stiffness (DOF: v1,th1,v2,th2)."""
    L = max(L, 1e-6)
    c = EI / L ** 3
    return c * np.array([
        [12,    6 * L,   -12,    6 * L],
        [6 * L, 4 * L * L, -6 * L, 2 * L * L],
        [-12,  -6 * L,    12,   -6 * L],
        [6 * L, 2 * L * L, -6 * L, 4 * L * L],
    ], dtype=float)


def solve_cantilever(b_mm: float, h_mm: float, L_mm: float, *,
                     E_mpa: float, allowable_mpa: float,
                     w_N_per_mm: float, tip_load_N: float,
                     n_elem: int = 8) -> dict:
    """Cantilever beam FE: depth h (bending), width b. Fixed at root (x=0).
    Distributed load w (N/mm) + tip point load (N). Returns deflection/stress/FoS."""
    h_mm = max(h_mm, 0.5)
    b_mm = max(b_mm, 0.5)
    I = b_mm * h_mm ** 3 / 12.0          # mm^4
    c = h_mm / 2.0                       # extreme fiber
    EI = E_mpa * I                       # N·mm^2
    n_node = n_elem + 1
    ndof = 2 * n_node
    Le = L_mm / n_elem
    K = np.zeros((ndof, ndof))
    F = np.zeros(ndof)
    ke = _beam_element_k(EI, Le)
    # consistent nodal load vector for uniform w over an element
    fe = w_N_per_mm * Le * np.array([0.5, Le / 12.0, 0.5, -Le / 12.0])
    for e in range(n_elem):
        d = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(d, d)] += ke
        F[d] += fe
    F[2 * (n_node - 1)] += tip_load_N    # tip transverse point load
    # BC: clamp root node 0 (v=0, theta=0)
    free = list(range(2, ndof))
    Kff = K[np.ix_(free, free)]
    Ff = F[free]
    u = np.zeros(ndof)
    try:
        u[free] = np.linalg.solve(Kff, Ff)
    except np.linalg.LinAlgError:
        return {"ok": False, "reason": "singular stiffness"}
    tip_defl = float(u[2 * (n_node - 1)])
    # recover max element bending moment -> max stress
    max_M = 0.0
    for e in range(n_elem):
        d = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        ue = u[d]
        # moment at element ends: M = EI * (B u); use end curvatures
        for xi in (0.0, 1.0):
            # second derivative of Hermite shape functions at xi (natural)
            Bp = np.array([
                (12 * xi - 6) / Le ** 2,
                (6 * xi - 4) / Le,
                (-12 * xi + 6) / Le ** 2,
                (6 * xi - 2) / Le,
            ])
            M = EI * float(Bp @ ue)
            max_M = max(max_M, abs(M))
    sigma = max_M * c / I if I > 0 else 9e9     # MPa
    fos = round(allowable_mpa / sigma, 2) if sigma > 1e-9 else 999.0
    return {
        "ok": True,
        "solver": "euler_bernoulli_beam_fe_numpy",
        "elements": n_elem,
        "I_mm4": round(I, 1),
        "EI_Nmm2": round(EI, 1),
        "tip_deflection_mm": round(tip_defl, 4),
        "max_bending_moment_Nmm": round(max_M, 1),
        "max_bending_stress_mpa": round(sigma, 2),
        "fos": fos,
    }

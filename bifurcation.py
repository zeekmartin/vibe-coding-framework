"""
topostability.core.bifurcation
==============================
Analytical computation of edge-level critical coupling thresholds.

THE key result:
    C_crit(e) = 2(A - beta) / [tri(e) * g''(0)]

For tri(e) = 0: C_crit = inf (no stabilization possible).
Monotonicity: dC_crit/d(tri) < 0 (more triangles → lower threshold).
"""

import numpy as np
from typing import Dict, Tuple, Optional


def critical_coupling(
    tri: int,
    A: float = 1.0,
    beta: float = 0.2,
    g2: float = 2.0,
) -> float:
    """
    Compute C_crit for a single edge given its triangle count.

    C_crit(e) = 2(A - beta) / [tri(e) * g''(0)]

    Parameters
    ----------
    tri : int
        Number of triangles containing this edge.
    A : float
        Instability drive parameter. Must be > beta.
    beta : float
        Baseline damping parameter.
    g2 : float
        g''(0), second derivative of stabilization function at origin.
        For g(phi) = phi^2: g2 = 2.
        For g(phi) = phi^2 + 0.25*phi^4: g2 = 2.

    Returns
    -------
    float
        Critical coupling value. inf if tri == 0.
    """
    if not (A > beta > 0):
        raise ValueError(f"Need A > beta > 0, got A={A}, beta={beta}")
    if g2 <= 0:
        raise ValueError(f"Need g''(0) > 0, got {g2}")
    if tri < 0:
        raise ValueError(f"Triangle count cannot be negative, got {tri}")

    if tri == 0:
        return np.inf
    return 2.0 * (A - beta) / (tri * g2)


def critical_coupling_map(
    tri_map: Dict[Tuple[int, int], int],
    A: float = 1.0,
    beta: float = 0.2,
    g2: float = 2.0,
) -> Dict[Tuple[int, int], float]:
    """
    Compute C_crit for all edges given their triangle counts.

    Parameters
    ----------
    tri_map : dict
        Mapping edge -> triangle count (from motifs.triangle_count_per_edge).
    A, beta, g2 : float
        Model parameters.

    Returns
    -------
    ccrit : dict mapping edge -> float
    """
    return {
        e: critical_coupling(t, A, beta, g2)
        for e, t in tri_map.items()
    }


def stability_classification(
    tri_map: Dict[Tuple[int, int], int],
    C: float,
    A: float = 1.0,
    beta: float = 0.2,
    g2: float = 2.0,
) -> Dict[Tuple[int, int], str]:
    """
    Classify each edge as 'stable' or 'unstable' at a given coupling C.

    - stable: C >= C_crit(e), phi=0 is a local minimum
    - unstable: C < C_crit(e), phi=0 is a local maximum

    Parameters
    ----------
    tri_map : dict
        Edge -> triangle count.
    C : float
        Global coupling parameter.
    A, beta, g2 : float
        Model parameters.

    Returns
    -------
    classification : dict mapping edge -> 'stable' | 'unstable' | 'always_unstable'
    """
    ccrit_map = critical_coupling_map(tri_map, A, beta, g2)
    result = {}
    for e, ccrit in ccrit_map.items():
        if np.isinf(ccrit):
            result[e] = "always_unstable"
        elif C >= ccrit:
            result[e] = "stable"
        else:
            result[e] = "unstable"
    return result

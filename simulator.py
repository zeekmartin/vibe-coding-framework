"""
topostability.dynamics.simulator
================================
Gradient descent dynamics on edge potentials and threshold verification.

The verify_threshold function is THE scientific validation instrument:
it checks empirically that the analytical C_crit(e) predicts the
actual bifurcation point for each edge.

Convention (fixed, do not change):
    Low C  → phi=0 is unstable (instability drive dominates)
    High C → phi=0 is stable for tri(e)>0 (triangle stabilization wins)
    C_crit(e) is the stabilization threshold, strictly decreasing in tri(e).
"""

import numpy as np
import networkx as nx
from typing import Dict, Tuple, List, Optional, Callable, Union
from dataclasses import dataclass, field

from ..core.motifs import triangle_count_per_edge
from ..core.bifurcation import critical_coupling


def _edge_key(e: Tuple[int, int], is_undirected: bool) -> Tuple[int, int]:
    """Normalize edge key for undirected graphs to match tri_map keys."""
    if is_undirected:
        return (min(e), max(e))
    return e


# ── Penalty functions ──────────────────────────────────────────────

def g_quadratic(phi: np.ndarray) -> np.ndarray:
    """g(phi) = phi^2 + 0.25*phi^4. g''(0) = 2."""
    return phi**2 + 0.25 * phi**4


def g_prime_quadratic(phi: np.ndarray) -> np.ndarray:
    """g'(phi) = 2*phi + phi^3."""
    return 2.0 * phi + phi**3


G2_DEFAULT = 2.0  # g''(0) for the default penalty


# ── Core dynamics ──────────────────────────────────────────────────

def run_relaxation(
    G: Union[nx.Graph, nx.DiGraph],
    tri_map: Dict[Tuple[int, int], int],
    C: float,
    A: float = 1.0,
    beta: float = 0.2,
    g_prime: Callable = g_prime_quadratic,
    steps: int = 5000,
    lr: float = 0.02,
    noise0: float = 1e-2,
    anneal: float = 0.999,
    cooldown_frac: float = 0.1,
    W: float = 1.0,
    seed: int = 0,
) -> Dict[Tuple[int, int], float]:
    """
    Run gradient descent on the decoupled edge potential system.

    V_e(phi) = (-A + beta)*phi^2 + C*tri(e)*g(phi)
    grad_e = 2*(-A + beta)*phi_e + C*tri(e)*g'(phi_e)

    The last `cooldown_frac` fraction of steps runs WITHOUT noise,
    allowing truly stable edges to settle exactly to phi=0.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph.
    tri_map : dict
        Edge -> triangle count.
    C : float
        Coupling parameter.
    cooldown_frac : float
        Fraction of steps at the end with noise=0 (default 0.1 = 10%).

    Returns
    -------
    final_phi : dict mapping edge -> |phi_e| (absolute value at convergence)
    """
    rng = np.random.RandomState(seed)
    edges = list(G.edges())
    n_edges = len(edges)
    edge_idx = {e: i for i, e in enumerate(edges)}
    is_undirected = not isinstance(G, nx.DiGraph)

    # Triangle counts as array (aligned with edges list).
    # For undirected Graph, tri_map keys are normalized to (min,max),
    # so we normalize the lookup key to match.
    tri_arr = np.array(
        [tri_map.get(_edge_key(e, is_undirected), 0) for e in edges],
        dtype=np.float64,
    )

    # Initialize with small noise
    phi = rng.normal(0, noise0, size=n_edges)
    phi = np.clip(phi, -W, W)

    noise = noise0
    coeff_instab = 2.0 * (-A + beta)  # negative, drives instability

    cooldown_start = int(steps * (1.0 - cooldown_frac))

    for t in range(steps):
        # Gradient: dV/dphi = 2(-A+beta)*phi + C*tri(e)*g'(phi)
        grad = coeff_instab * phi + C * tri_arr * g_prime(phi)

        # Cooldown: last fraction of steps, no noise
        if t >= cooldown_start:
            phi = phi - lr * grad
        else:
            phi = phi - lr * grad + rng.normal(0, noise, size=n_edges)
            noise *= anneal

        phi = np.clip(phi, -W, W)

    return {e: abs(phi[edge_idx[e]]) for e in edges}


# ── Threshold verification ─────────────────────────────────────────

@dataclass
class EdgeMetrics:
    """Verification metrics for a single edge."""
    edge: Tuple[int, int]
    tri: int
    C_crit: float
    C50_empirical: float  # empirical transition point
    p_low: Optional[float] = None   # P(stable) at C < C_crit
    p_high: Optional[float] = None  # P(stable) at C > C_crit
    accurate: Optional[bool] = None


@dataclass
class TriZeroSanity:
    """Sanity check results for tri=0 edges (should NEVER stabilize)."""
    n_tested: int
    n_always_unstable: int  # unstable at ALL tested C values (P(stable)<0.1)
    max_p_stable: float     # worst case: highest P(stable) seen
    pass_: bool             # True if ALL tested edges are always unstable


@dataclass
class VerificationResult:
    """Full verification result."""
    edge_metrics: List[EdgeMetrics]
    overall_accuracy: float
    n_tested: int
    n_finite: int  # edges with finite C_crit
    tri_zero_sanity: Optional[TriZeroSanity] = None
    params: dict = field(default_factory=dict)


def verify_threshold(
    G: Union[nx.Graph, nx.DiGraph],
    A: float = 1.0,
    beta: float = 0.2,
    g2: float = G2_DEFAULT,
    g_prime: Callable = g_prime_quadratic,
    C_values: Optional[np.ndarray] = None,
    n_restarts: int = 5,
    steps: int = 5000,
    lr: float = 0.02,
    noise0: float = 1e-2,
    anneal: float = 0.999,
    cooldown_frac: float = 0.1,
    W: float = 1.0,
    eps_zero: float = 1e-3,
    sample_edges: Optional[int] = None,
    sample_tri_zero: int = 20,
    delta: float = 0.15,
    seed: int = 0,
    verbose: bool = True,
) -> VerificationResult:
    """
    Verify that the analytical C_crit(e) predicts the actual bifurcation.

    Protocol:
    1. Compute tri(e) and C_crit(e) analytically for all edges
    2. For each C in C_values, run multiple restarts of gradient descent
    3. Record whether each edge ends up stable (|phi| < eps_zero) or polarized
    4. Find empirical transition C50(e): smallest C where P(stable) >= 0.5
    5. Score: at C = (1-delta)*C_crit, edge should be unstable;
             at C = (1+delta)*C_crit, edge should be stable
    6. Sanity check: tri=0 edges should NEVER stabilize at any C

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Input graph.
    A, beta, g2 : float
        Model parameters.
    C_values : array-like, optional
        Grid of coupling values to test. Default: linspace(0.05, 1.5, 30).
    n_restarts : int
        Number of independent runs per C value.
    sample_edges : int, optional
        If set, test only this many randomly sampled edges (with tri>0).
    sample_tri_zero : int
        Number of tri=0 edges to include in sanity check (default 20).
    delta : float
        Fractional margin around C_crit for accuracy scoring.
    cooldown_frac : float
        Fraction of steps at the end without noise (default 0.1).
    verbose : bool
        Print progress.

    Returns
    -------
    VerificationResult
        Contains per-edge metrics, overall accuracy, and tri=0 sanity check.
    """
    rng = np.random.RandomState(seed)

    if C_values is None:
        C_values = np.linspace(0.05, 1.5, 30)
    C_values = np.sort(C_values)

    # 1. Precompute triangles and analytical thresholds
    tri_map = triangle_count_per_edge(G)
    edges = list(G.edges())
    is_undirected = not isinstance(G, nx.DiGraph)

    def _tri(e):
        return tri_map.get(_edge_key(e, is_undirected), 0)

    ccrit_map = {
        e: critical_coupling(_tri(e), A, beta, g2)
        for e in edges
    }

    # Separate finite (tri>0) and zero-triangle edges
    finite_edges = [e for e in edges if np.isfinite(ccrit_map[e])]
    zero_edges = [e for e in edges if _tri(e) == 0]

    # Select edges to test (tri > 0)
    if sample_edges is not None and sample_edges < len(finite_edges):
        test_edges = [finite_edges[i] for i in
                      rng.choice(len(finite_edges), sample_edges, replace=False)]
    else:
        test_edges = finite_edges

    # Select tri=0 edges for sanity check
    if zero_edges and sample_tri_zero > 0:
        n_zero_sample = min(sample_tri_zero, len(zero_edges))
        sanity_edges = [zero_edges[i] for i in
                        rng.choice(len(zero_edges), n_zero_sample, replace=False)]
    else:
        sanity_edges = []

    # Combined set for dynamics (test + sanity)
    all_monitored = set(test_edges) | set(sanity_edges)

    if verbose:
        print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f"Edges with tri>0: {len(finite_edges)}, testing: {len(test_edges)}")
        print(f"Edges with tri=0: {len(zero_edges)}, sanity check: {len(sanity_edges)}")
        if finite_edges:
            tri_vals = [_tri(e) for e in finite_edges]
            print(f"Triangle range: {min(tri_vals)}-{max(tri_vals)}, "
                  f"C_crit range: {min(ccrit_map[e] for e in finite_edges):.4f}-"
                  f"{max(ccrit_map[e] for e in finite_edges):.4f}")

    # 2. Run dynamics for each C value
    # outcomes[e][C_idx] = list of |phi| values across restarts
    outcomes = {e: {i: [] for i in range(len(C_values))} for e in all_monitored}

    for ci, C in enumerate(C_values):
        if verbose and ci % 5 == 0:
            print(f"  C={C:.3f} ({ci+1}/{len(C_values)})")

        for r in range(n_restarts):
            final_phi = run_relaxation(
                G, tri_map, C, A, beta, g_prime,
                steps=steps, lr=lr, noise0=noise0,
                anneal=anneal, cooldown_frac=cooldown_frac,
                W=W, seed=seed + ci * 1000 + r,
            )
            for e in all_monitored:
                outcomes[e][ci].append(final_phi[e])

    # 3. Helper: P(stable | e, C)
    def p_stable(e, ci):
        vals = outcomes[e][ci]
        return sum(1 for v in vals if v < eps_zero) / len(vals)

    # 4. Find empirical C50(e)
    def find_C50(e):
        for ci in range(len(C_values)):
            if p_stable(e, ci) >= 0.5:
                return C_values[ci]
        return np.inf

    # 5. Score accuracy around C_crit (tri > 0 edges)
    def nearest_ci(target):
        return int(np.argmin(np.abs(C_values - target)))

    metrics = []
    n_accurate = 0

    for e in test_edges:
        cc = ccrit_map[e]
        c50 = find_C50(e)
        tri_e = _tri(e)

        if not np.isfinite(cc):
            metrics.append(EdgeMetrics(e, tri_e, cc, c50))
            continue

        ci_low = nearest_ci((1 - delta) * cc)
        ci_high = nearest_ci((1 + delta) * cc)

        pl = p_stable(e, ci_low)
        ph = p_stable(e, ci_high)

        # Correct prediction: low C → unstable (p<0.5), high C → stable (p>0.5)
        acc = (pl < 0.5) and (ph > 0.5)
        if acc:
            n_accurate += 1

        metrics.append(EdgeMetrics(
            edge=e, tri=tri_e, C_crit=cc, C50_empirical=c50,
            p_low=pl, p_high=ph, accurate=acc,
        ))

    overall_acc = n_accurate / max(1, len(test_edges))

    # 6. Sanity check: tri=0 edges should NEVER be stable
    tri_zero_sanity = None
    if sanity_edges:
        n_always_unstable = 0
        max_p = 0.0

        for e in sanity_edges:
            # Check P(stable) at highest C — if even the strongest coupling
            # can't stabilize it, the model is correct
            all_p = [p_stable(e, ci) for ci in range(len(C_values))]
            worst = max(all_p)
            max_p = max(max_p, worst)
            if worst < 0.1:
                n_always_unstable += 1

        tri_zero_sanity = TriZeroSanity(
            n_tested=len(sanity_edges),
            n_always_unstable=n_always_unstable,
            max_p_stable=max_p,
            pass_=(n_always_unstable == len(sanity_edges)),
        )

        if verbose:
            status = "PASS" if tri_zero_sanity.pass_ else "FAIL"
            print(f"\nTri=0 sanity check: {status}")
            print(f"  {n_always_unstable}/{len(sanity_edges)} always unstable "
                  f"(threshold: P(stable)<0.1), "
                  f"max P(stable)={max_p:.3f}")

    if verbose:
        print(f"\n{'='*50}")
        print(f"VERIFICATION RESULT")
        print(f"{'='*50}")
        print(f"Edges tested:      {len(test_edges)}")
        print(f"Accurate:          {n_accurate} / {len(test_edges)}")
        print(f"Overall accuracy:  {overall_acc:.1%}")
        print(f"{'='*50}")

    return VerificationResult(
        edge_metrics=metrics,
        overall_accuracy=overall_acc,
        n_tested=len(test_edges),
        n_finite=len(finite_edges),
        tri_zero_sanity=tri_zero_sanity,
        params={"A": A, "beta": beta, "g2": g2,
                "delta": delta, "eps_zero": eps_zero,
                "n_restarts": n_restarts, "steps": steps,
                "cooldown_frac": cooldown_frac},
    )

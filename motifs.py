"""
topostability.core.motifs
=========================
Edge-level motif counting for bifurcation analysis.

For the bifurcation model, triangles represent local structural closure:
a triangle through edge (u,v) is any node w connected to both u and v.
For directed graphs, we use undirected neighborhoods (any direction counts)
because the stabilization mechanism depends on structural closure,
not edge direction.

Note: MultiGraph / MultiDiGraph are NOT supported. Pass a simple
Graph or DiGraph.
"""

import networkx as nx
from typing import Dict, Tuple, Union


def _normalize_edge(u, v) -> Tuple[int, int]:
    """Canonical edge key for undirected graphs: (min, max)."""
    return (min(u, v), max(u, v))


def triangle_count_per_edge(
    G: Union[nx.Graph, nx.DiGraph],
) -> Dict[Tuple[int, int], int]:
    """
    Count triangles per edge.

    For edge (u, v): tri(u,v) = |{w : w~u AND w~v, w not in {u,v}}|
    where w~u means w is connected to u in any direction.

    For undirected graphs, edge keys are normalized to (min(u,v), max(u,v))
    to avoid duplicate/ambiguous keys. For directed graphs, keys follow
    G.edges() iteration order.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Simple graph (MultiGraph not supported).

    Returns
    -------
    tri : dict mapping (u, v) -> int

    Raises
    ------
    TypeError
        If G is a MultiGraph or MultiDiGraph.
    """
    if isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(
            "MultiGraph/MultiDiGraph not supported. "
            "Convert to simple Graph/DiGraph first."
        )

    # Build undirected neighbor sets
    if isinstance(G, nx.DiGraph):
        neighbors = {}
        for n in G.nodes():
            neighbors[n] = (
                set(G.successors(n)) | set(G.predecessors(n))
            ) - {n}
    else:
        neighbors = {n: set(G.neighbors(n)) - {n} for n in G.nodes()}

    tri = {}
    is_directed = isinstance(G, nx.DiGraph)

    for u, v in G.edges():
        common = neighbors[u] & neighbors[v]
        if is_directed:
            tri[(u, v)] = len(common)
        else:
            # Normalize key to avoid (u,v) vs (v,u) ambiguity
            tri[_normalize_edge(u, v)] = len(common)

    return tri

"""Graphs: the note Tonnetz, the PLR ('chicken-wire') dual graph and Hamiltonian cycles."""
from __future__ import annotations
import networkx as nx
from .core import Triad, all_triads, P, L, R, NOTE_NAMES, transpose, invert

__all__ = ["note_tonnetz_graph", "plr_graph", "hamiltonian_cycles",
           "canonical_cycle", "cycle_word", "symmetry_classes", "plr_distance_table"]


def note_tonnetz_graph(intervals=(3, 4, 7), n=12):
    """Graph on Z_n: x ~ x +/- a for each generating interval a."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for x in range(n):
        for a in intervals:
            G.add_edge(x, (x + a) % n, interval=a)
    return G


def plr_graph():
    """The 24 consonant triads joined by P, L and R (a cubic graph, 36 edges)."""
    G = nx.Graph()
    for t in all_triads():
        for name, op in (("P", P), ("L", L), ("R", R)):
            G.add_edge(t, op(t), op=name)
    return G


def hamiltonian_cycles(G, start=None):
    """Enumerate all Hamiltonian cycles of G (each undirected cycle reported once).

    Simple backtracking; fine for the 24-vertex PLR graph (runs in about a second)."""
    nodes = list(G.nodes)
    start = start if start is not None else min(nodes)
    n = len(nodes)
    out, path, seen = [], [start], {start}

    def rec(v):
        if len(path) == n:
            if G.has_edge(v, start):
                # keep only one of the two directions: compare 2nd and last vertex
                if path[1] < path[-1]:
                    out.append(list(path))
            return
        for w in G.neighbors(v):
            if w not in seen:
                seen.add(w); path.append(w)
                rec(w)
                path.pop(); seen.discard(w)
    rec(start)
    return out


def cycle_word(G, cyc):
    """The sequence of operation labels ('P','L','R') read around a cycle."""
    return "".join(G.edges[cyc[i], cyc[(i + 1) % len(cyc)]]["op"] for i in range(len(cyc)))


def canonical_cycle(word):
    """Canonical representative of a cyclic word up to rotation and reversal."""
    cands = []
    for w in (word, word[::-1]):
        for i in range(len(w)):
            cands.append(w[i:] + w[:i])
    return min(cands)


def symmetry_classes(G, cycles):
    """Group Hamiltonian cycles into orbits under transposition and inversion (the
    dihedral group of order 24 acting on triads). Returns list of orbits (lists of
    frozensets of edges)."""
    def edgeset(c):
        return frozenset(frozenset((c[i], c[(i + 1) % len(c)])) for i in range(len(c)))
    maps = [lambda t, k=k: transpose(t, k) for k in range(12)] + \
           [lambda t, k=k: invert(t, k) for k in range(12)]
    remaining = {edgeset(c) for c in cycles}
    orbits = []
    while remaining:
        e = next(iter(remaining))
        orb = set()
        for f in maps:
            orb.add(frozenset(frozenset(f(x) for x in edge) for edge in e))
        orbits.append(sorted(orb, key=lambda s: sorted(map(str, s))))
        remaining -= orb
    return orbits


def plr_distance_table():
    """All-pairs shortest-path distances in the PLR graph (dict of dicts)."""
    return dict(nx.all_pairs_shortest_path_length(plr_graph()))

"""Edge-labelled Tonnetze: triangles are chords, *edges* are notes.

A face (chord) is a triangle whose three edges carry its three (essential) notes.
Faces are glued edge-to-edge only along equal note labels. Because a note usually
belongs to more than two chords, one must choose *which* pairs of faces to glue and
*how* (two orientations) - different choices give different surfaces. This module
builds and samples such gluings and measures the resulting surfaces."""
from __future__ import annotations
import random
from collections import defaultdict

__all__ = ["EdgeGluing", "random_edge_gluing", "sample_edge_tonnetze"]


class _UF:
    def __init__(self): self.p = {}
    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def u(self, a, b): self.p[self.f(a)] = self.f(b)


class EdgeGluing:
    """faces: list of 3-tuples of notes (edge labels in cyclic order).
    pairs: list of ((f, i), (g, j), s) gluing edge i of face f to edge j of face g,
    s = +1 orientation-compatible, s = -1 with a twist."""

    def __init__(self, faces, pairs):
        self.faces, self.pairs = faces, pairs
        uf = _UF()
        for f in range(len(faces)):
            for v in range(3):
                uf.f((f, v))
        for (f, i), (g, j), s in pairs:
            a, b = (f, i), (f, (i + 1) % 3)
            c, d = (g, j), (g, (j + 1) % 3)
            if s > 0:
                uf.u(a, d); uf.u(b, c)
            else:
                uf.u(a, c); uf.u(b, d)
        self.vclass = {k: uf.f(k) for k in uf.p}

    @property
    def V(self): return len(set(self.vclass.values()))
    @property
    def E(self): return len(self.pairs) + (3 * len(self.faces) - 2 * len(self.pairs))
    @property
    def F(self): return len(self.faces)
    def chi(self): return self.V - self.E + self.F

    def orientable(self):
        """Search for face signs so that every gluing is orientation-compatible."""
        adj = defaultdict(list)
        for (f, _), (g, _), s in self.pairs:
            adj[f].append((g, s)); adj[g].append((f, s))
        sign = {}
        for r in range(self.F):
            if r in sign: continue
            sign[r] = 1; stack = [r]
            while stack:
                x = stack.pop()
                for y, s in adj[x]:
                    need = sign[x] * s  # s=+1: same sign keeps compatibility
                    if y not in sign:
                        sign[y] = need; stack.append(y)
                    elif sign[y] != need:
                        return False
        return True

    def is_connected(self):
        adj = defaultdict(set)
        for (f, _), (g, _), _s in self.pairs:
            adj[f].add(g); adj[g].add(f)
        seen, stack = {0}, [0]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        return len(seen) == self.F

    def surface_name(self):
        """Closed surfaces from pairwise edge gluing are always genuine surfaces;
        classify a connected one by (chi, orientability)."""
        if not self.is_connected():
            return "disconnected"
        chi, o = self.chi(), self.orientable()
        if o:
            return {2: "sphere", 0: "torus"}.get(chi, f"orientable genus {(2 - chi) // 2}")
        return {1: "projective plane", 0: "Klein bottle"}.get(chi, f"non-orientable, {2 - chi} cross-caps")

    def is_closed(self):
        return 2 * len(self.pairs) == 3 * self.F


def random_edge_gluing(faces, rng=random, twist_prob=0.5):
    """Glue every edge: for each note, randomly perfect-match its edge slots.
    Returns None if some note occurs an odd number of times."""
    slots = defaultdict(list)
    for f, tri in enumerate(faces):
        for i, n in enumerate(tri):
            slots[n].append((f, i))
    pairs = []
    for n, sl in slots.items():
        if len(sl) % 2: return None
        sl = sl[:]; rng.shuffle(sl)
        for k in range(0, len(sl), 2):
            s = -1 if rng.random() < twist_prob else 1
            pairs.append((sl[k], sl[k + 1], s))
    return EdgeGluing(faces, pairs)


def sample_edge_tonnetze(faces, n=20000, seed=0, twist_prob=0.5):
    """Monte-Carlo census: Counter of surface names over random closed gluings."""
    from collections import Counter
    rng = random.Random(seed); c = Counter()
    for _ in range(n):
        g = random_edge_gluing(faces, rng, twist_prob)
        if g is not None:
            c[g.surface_name()] += 1
    return c

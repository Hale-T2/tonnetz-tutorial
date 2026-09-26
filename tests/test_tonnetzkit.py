"""Regression tests for every numerical claim made in the report."""
import collections
import pytest
from tonnetzkit import *


def test_plr_involutions_and_examples():
    C = Triad.parse("C")
    assert str(P(C)) == "Cm" and str(R(C)) == "Am" and str(L(C)) == "Em"
    for t in all_triads():
        assert P(P(t)) == t and L(L(t)) == t and R(R(t)) == t


def test_plr_graph_shape():
    G = plr_graph()
    assert G.number_of_nodes() == 24 and G.number_of_edges() == 36
    assert set(dict(G.degree()).values()) == {3}
    import networkx as nx
    assert nx.is_bipartite(G) and nx.diameter(G) == 5


def test_hamiltonian_counts():
    G = plr_graph(); H = hamiltonian_cycles(G)
    assert len(H) == 62                       # 124 directed (Albini & Antonini 2009)
    sizes = sorted(len(o) for o in symmetry_classes(G, H))
    assert sizes == [1, 2, 3, 4, 4, 12, 12, 24]
    assert len({canonical_cycle(cycle_word(G, h)) for h in H}) == 8


def test_classical_tonnetz_is_torus():
    K = generalized_tonnetz(3, 4, 5)
    assert K.f_vector == (12, 36, 24) and K.euler_characteristic() == 0
    assert classify_surface(K) == "torus"


def test_generalized_parity():
    assert classify_surface(generalized_tonnetz(1, 1, 10)) == "annulus (cylinder)"
    assert classify_surface(generalized_tonnetz(1, 1, 9, n=11)) == "Moebius band"


def test_rp2_hexagon():
    pts = [(q, r) for q in range(-2, 3) for r in range(-2, 3) if max(abs(q), abs(r), abs(q + r)) <= 2]
    S = set(pts); tris = set()
    for (q, r) in pts:
        for tri in (((q, r), (q + 1, r), (q, r + 1)), ((q + 1, r), (q + 1, r - 1), (q, r))):
            if all(p in S for p in tri):
                tris.add(tuple(sorted(tri)))
    lab = lambda p: min(p, (-p[0], -p[1])) if max(abs(p[0]), abs(p[1]), abs(p[0] + p[1])) == 2 else p
    K = SimplicialComplex([tuple(lab(p) for p in t) for t in tris])
    assert K.f_vector == (13, 36, 24) and K.euler_characteristic() == 1
    assert K.betti("Q") == (1, 0, 0) and K.betti("Z2") == (1, 1, 1)
    assert classify_surface(K) == "real projective plane"


def test_harte_parser():
    assert harte_to_pcs("A:min7") == frozenset({9, 0, 4, 7})
    assert harte_to_triad("G:7/3") == Triad(7, "M")
    assert harte_to_pcs("N") is None


def test_tonal_centroid_matches_librosa():
    librosa = pytest.importorskip("librosa")
    import numpy as np
    y = np.concatenate([synth_chord(Triad.parse(c).pcs, dur=0.5) for c in ("C", "Am")])
    ch = librosa.feature.chroma_cqt(y=y, sr=22050)
    assert np.allclose(tonal_centroid(ch), librosa.feature.tonnetz(chroma=ch), atol=1e-6)

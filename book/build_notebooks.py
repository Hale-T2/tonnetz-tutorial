"""Builds the notebook 'book of Python sheets' from compact cell specs.
Run from the repository root:  python book/build_notebooks.py"""
import nbformat as nbf, os

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP = """# Setup: make the repository importable whether or not `pip install -e .` was run
import sys, os
sys.path.insert(0, os.path.abspath('..'))
import numpy as np, networkx as nx, matplotlib.pyplot as plt
from tonnetzkit import *
%matplotlib inline"""


def sol(text):
    return f"<details><summary><b>Show solution</b></summary>\n\n{text}\n\n</details>"


def nb(cells):
    n = nbf.v4.new_notebook()
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    out = []
    for kind, src in cells:
        out.append(nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src))
    n.cells = out
    return n


BOOK = {}

BOOK["00_welcome.ipynb"] = [
("md", """# Sheet 0 — Welcome and a five-minute tour

*Companion to* **Euler's Tonnetz, Graph Theory and Geometry: A Tutorial Review** *(H. Tureli, 2026).*

Each sheet mirrors one chapter of the report. Sheets are *executable*: change a number, rerun a cell, and see
what the mathematics does. Exercises end every sheet; solutions are folded away under **Show solution**.

| Sheet | Report chapter | Topic |
|---|---|---|
| 1 | 2 | Pitch classes, intervals, the group $D_{12}$ |
| 2 | 3 | The Tonnetz lattice and why it is a torus |
| 3 | 4 | P, L, R and the dual ("chicken-wire") graph |
| 4 | 5 | Hamiltonian cycles — enumerate, classify, *listen* |
| 5 | 6 | Generalized Tonnetze and their topology |
| 6 | 7 | Seventh chords, edge Tonnetze, non-orientable surfaces |
| 7 | 8 | Real corpora on the Tonnetz (Bach, Beethoven, pop) |
| 8 | 8 | Audio: the tonal-centroid ("tonnetz") feature |
| 9 | 9 | Research sandbox |
"""),
("code", SETUP),
("md", "A thirty-second tour: build the 24 triads, move with P, L, R, and count Hamiltonian cycles."),
("code", """C = Triad.parse('C')
print('P(C) =', P(C), '  L(C) =', L(C), '  R(C) =', R(C))
G = plr_graph()
print('PLR graph:', G.number_of_nodes(), 'triads,', G.number_of_edges(), 'edges')
H = hamiltonian_cycles(G)
print('Hamiltonian cycles (undirected):', len(H), ' directed:', 2*len(H))"""),
("md", "Hear a triad (additive synthesis, no audio files needed):"),
("code", """from IPython.display import Audio
Audio(np.concatenate([synth_chord(t.pcs, sr=11025, dur=0.6) for t in apply_word(C, 'RLRL')]), rate=11025)"""),
]

BOOK["01_pitch_classes.ipynb"] = [
("md", """# Sheet 1 — Pitch classes, intervals and symmetry (Chapter 2)

**Goals.** (i) Treat notes as elements of $\\mathbb{Z}_{12}$; (ii) implement transposition $T_n$ and inversion $I_n$;
(iii) verify that $\\{T_n, I_n\\}$ is a group of order 24 acting on the 24 consonant triads."""),
("code", SETUP),
("code", """for name in ['C', 'F#', 'Bb', 'E', 'Cb']:
    print(f'{name:>3} -> {pc(name)}')
# interval class between two pitch classes
ic = lambda a, b: min((a-b) % 12, (b-a) % 12)
print('interval class C..A =', ic(pc('C'), pc('A')))"""),
("md", "### Transposition and inversion as permutations of the 24 triads"),
("code", """T = all_triads(); idx = {t: i for i, t in enumerate(T)}
perm = lambda f: tuple(idx[f(t)] for t in T)
group = {perm(lambda t, n=n: transpose(t, n)) for n in range(12)} | {perm(lambda t, n=n: invert(t, n)) for n in range(12)}
print('number of distinct T/I permutations:', len(group))
print('I_0(C major) =', invert(Triad.parse('C'), 0), '   (C E G -> C Ab F = F minor)')"""),
("md", "### Set classes of trichords\nEvery 3-note chord in 12-TET is described (up to transposition) by the three gaps around the pitch-class circle, which add to 12."),
("code", """classes = {}
for (a, b, c) in trichord_classes():
    key = min((a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a))  # up to T and I
    classes.setdefault(key, []).append((a, b, c))
print(len(trichord_classes()), 'T-classes;', len(classes), 'T/I set classes')
for k, v in classes.items(): print(k, v)"""),
("md", """## Exercises
1. Show that $I_n \\circ I_m = T_{n-m}$ by checking all $n, m$ in code.
2. Which set class is the major/minor triad? Which is the augmented triad and why is it *alone* in its T-class orbit of size 4?
3. Compute the interval vector of the dominant-seventh chord $\\{0,4,7,10\\}$.
""" + sol("""```python
ok = all(invert(invert(t, m), n) == transpose(t, n - m) for t in all_triads() for n in range(12) for m in range(12))
print(ok)   # True
```
2. Major/minor is (3,4,5): gaps 3,4,5 in some cyclic order; major is (4,3,5), minor (3,4,5) — mirror images, so one T/I class.
The augmented triad (4,4,4) is invariant under $T_4$, so it has only $12/3 = 4$ distinct transpositions.

3.
```python
from itertools import combinations
ch = [0, 4, 7, 10]; v = [0]*6
for a, b in combinations(ch, 2): v[min((a-b)%12, (b-a)%12)-1] += 1
print(v)   # [0, 1, 2, 1, 1, 1]
```""")),
]

BOOK["02_tonnetz_torus.ipynb"] = [
("md", """# Sheet 2 — The Tonnetz lattice and the torus (Chapter 3)

The Tonnetz is the image of the lattice $\\mathbb{Z}^2$ under $\\varphi(i,j) = 7i + 4j \\pmod{12}$:
horizontal steps are perfect fifths, diagonal steps major thirds, and the other diagonal minor thirds."""),
("code", SETUP),
("code", """phi = lambda i, j: (7*i + 4*j) % 12
for j in range(3, -4, -1):
    print('  '*(3-j) + '  '.join(f'{pc_name(phi(i, j)):>2}' for i in range(-4, 5)))"""),
("md", "### The kernel lattice: which lattice moves return to the same note?"),
("code", """ker = [(i, j) for i in range(-6, 7) for j in range(-6, 7) if phi(i, j) == 0 and (i, j) != (0, 0)]
small = sorted(ker, key=lambda v: v[0]**2 + v[1]**2)[:6]
print('shortest kernel vectors:', small)
a, b = (4, -1), (0, 3)
print('det of basis', a, b, '=', a[0]*b[1] - a[1]*b[0], '-> fundamental domain holds 12 notes')"""),
("md", "### Count cells of the quotient and compute the Euler characteristic"),
("code", """K = generalized_tonnetz(3, 4, 5)       # all major and minor triads as triangles
print(K.summary()); print('=>', classify_surface(K))"""),
("md", """## Exercises
1. Change $\\varphi$ to $\\varphi(i,j) = 7i + 3j$ (fifths and *minor* thirds). Is the resulting triangulated quotient still a torus? Which triads are the triangles?
2. In just intonation there is no enharmonic equivalence, so $\\varphi$ is injective on $\\mathbb{Z}^2$. What does that say about the "torus" slide in the original presentation?
3. Verify $V - E + F = 0$ by hand from the fundamental domain picture in Figure 3.2 of the report.
""" + sol("""1. Yes: 7i+3j has kernel spanned by (0,4) and (3,1) (determinant −12, so again 12 notes per domain); triangles are {x, x+7, x+3} and {x+3, x+7, x+10}: again minor and major triads (the same complex!), because the three intervals 3,4,5 are the same set. `generalized_tonnetz(3,4,5)` covers both drawings.
2. The torus needs *pitch-class* equivalence, i.e. octave equivalence **and** 12-tone equal temperament (enharmonic equivalence, F♯ = G♭). Octaves alone leave an infinite plane (or a cylinder if one also identifies the line of fifths, as in Harte et al. 2006).
3. 12 vertices; each vertex has 6 neighbours so E = 12·6/2 = 36; each vertex is in 6 triangles so F = 12·6/3 = 24; 12 − 36 + 24 = 0.""")),
]

BOOK["03_plr_dual.ipynb"] = [
("md", """# Sheet 3 — P, L, R and the dual graph (Chapter 4)

Triads sharing two notes are adjacent. The graph on the 24 triads with P/L/R edges is the
*dual* of the Tonnetz triangulation (Douthett & Steinbach's "chicken-wire torus")."""),
("code", SETUP),
("code", """G = plr_graph()
print('cubic?', set(dict(G.degree()).values()), ' bipartite?', nx.is_bipartite(G), ' diameter:', nx.diameter(G))
import collections
D = plr_distance_table(); Tr = all_triads()
print('distance distribution over ordered pairs:', collections.Counter(D[a][b] for a in Tr for b in Tr if a != b))"""),
("md", "### Famous cycles: hexagons, hexatonic and octatonic systems"),
("code", """C = Triad.parse('C')
print('hexagon around note C  (PLR)^2 :', apply_word(C, 'PLRPLR'))
print('hexatonic cycle        (PL)^3  :', apply_word(C, 'PLPLPL'))
print('octatonic cycle        (PR)^4  :', apply_word(C, 'PRPRPRPR'))
print('all triads containing C:', [t for t in all_triads() if 0 in t.pcs])"""),
("md", """### A correction worth making
The original slide lists "going around a hexagon" as C → Am → F → Dm → G → Em → C. Let us test every step:"""),
("code", """seq = [Triad.parse(s) for s in 'C Am F Dm G Em C'.split()]
for a, b in zip(seq, seq[1:]):
    print(f'{a!s:>3} -> {b!s:<3}', 'adjacent' if G.has_edge(a, b) else f'NOT adjacent (distance {D[a][b]})')"""),
("md", "Dm → G shares only one note, so this is a *diatonic* chain of thirds, not a face of the dual graph. The true hexagon around C is C–Cm–A♭–Fm–F–Am."),
("md", "### The PLR group"),
("code", """idx = {t: i for i, t in enumerate(Tr)}
gens = [tuple(idx[f(t)] for t in Tr) for f in (P, L, R)]
grp = {tuple(range(24))}; frontier = list(grp)
while frontier:
    nxt = []
    for g in frontier:
        for h in gens:
            c = tuple(h[g[i]] for i in range(24))
            if c not in grp: grp.add(c); nxt.append(c)
    frontier = nxt
print('order of <P,L,R> =', len(grp), ' (dihedral of order 24)')
print('P commutes with transposition:', all(P(transpose(t, 5)) == transpose(P(t), 5) for t in Tr))"""),
("md", """## Exercises
1. Show that the voice-leading cost (total semitones moved) is 1 for P and L and 2 for R.
2. Find a shortest path from C major to F♯ major. Is it unique?
3. Prove (or check) that the PLR graph is bipartite. Musically, what are the two parts?
""" + sol("""```python
for op in (P, L, R): print(op.__name__, {voice_leading_distance(t, op(t)) for t in Tr})
paths = list(nx.all_shortest_paths(G, Triad.parse('C'), Triad.parse('F#')))
print(len(paths), 'shortest paths of length', len(paths[0])-1); print(paths[0])
```
3. Every P, L, R swaps major and minor, so {majors} and {minors} are the two parts — `nx.is_bipartite(G)` is True.""")),
]

BOOK["04_hamiltonian.ipynb"] = [
("md", """# Sheet 4 — Hamiltonian cycles: enumerate, classify, listen (Chapter 5)

A Hamiltonian cycle visits all 24 triads once, moving only by P, L or R."""),
("code", SETUP + "\nimport collections\nfrom IPython.display import Audio"),
("code", """G = plr_graph()
%time H = hamiltonian_cycles(G)
print(len(H), 'undirected cycles =', 2*len(H), 'directed cycles (Albini & Antonini 2009 report 124)')"""),
("md", "### Classify by their P/L/R word and by the symmetry group"),
("code", """by_word = collections.defaultdict(list)
for h in H: by_word[canonical_cycle(cycle_word(G, h))].append(h)
orbits = symmetry_classes(G, H)
print('classes by word:', len(by_word), '   orbits under T/I:', len(orbits))
rows = []
for w, cyc in sorted(by_word.items(), key=lambda kv: len(kv[1])):
    c = collections.Counter(w); vl = c['P'] + c['L'] + 2*c['R']
    rows.append((len(cyc), c['P'], c['L'], c['R'], vl))
    print(f'size {len(cyc):2d}  P={c["P"]:2d} L={c["L"]:2d} R={c["R"]:2d}  voice-leading cost={vl} semitones')"""),
("md", "### Listen to two of them (0.35 s per chord)"),
("code", """def play(cycle, dur=0.35, sr=11025):
    k = cycle.index(Triad.parse('C')); cycle = cycle[k:] + cycle[:k] + [cycle[k]]
    return Audio(np.concatenate([synth_chord(t.pcs, sr=sr, dur=dur) for t in cycle]), rate=sr)
smooth = min(H, key=lambda h: collections.Counter(cycle_word(G, h))['R'])
print(' '.join(map(str, smooth)))
play(smooth)"""),
("code", """lr = next(h for h in H if set(cycle_word(G, h)) == {'L', 'R'})
print(' '.join(map(str, lr)))
play(lr)"""),
("md", """## Exercises
1. How many Hamiltonian *paths* (not cycles) start at C major? (Hint: modify the backtracking to skip the closing check.)
2. There is exactly one Hamiltonian cycle using only L and R. Explain why.
3. Design a listening experiment to test the slide's question "do they sound better?". What would be your control condition?
""" + sol("""1. Remove the `G.has_edge(v, start)` test and the direction filter. There are exactly **470** directed Hamiltonian paths starting at C major; **124** of them end at a neighbour of C and close up — these are precisely the 124 directed Hamiltonian cycles.
2. L and R are involutions, so a walk using only L and R must alternate them (LL = RR = identity would revisit a triad). Starting from C the alternating walk C, Em, G, Bm, D, … moves the root of the majors by a fifth every two steps; the composite RL has order 12 on the majors, so the walk closes only after visiting all 12 majors and 12 minors. The two alternating walks from C (starting with L or with R) are the same cycle traversed in opposite directions, hence uniqueness.
3. E.g. rate pleasantness/coherence of 24-chord sequences: Hamiltonian cycles vs (a) random walks on the PLR graph of equal length with repeats, (b) random permutations of the 24 triads, matched for duration, register and voicing; randomise order, use within-subject design, and pre-register the hypothesis.""")),
]

BOOK["05_generalized_tonnetze.ipynb"] = [
("md", """# Sheet 5 — Generalized Tonnetze and their topology (Chapter 6)

Catanzaro (2011) builds, for any trichord type $(n_1,n_2,n_3)$ with $n_1+n_2+n_3=N$, the complex of all its transpositions
and inversions in $\\mathbb{Z}_N$. We compute $\\chi$, Betti numbers over $\\mathbb{Q}$ and $\\mathbb{Z}_2$, and orientability."""),
("code", SETUP + "\nimport pandas as pd"),
("code", """seen, rows = set(), []
for (a, b, c) in trichord_classes(12):
    key = min((a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a))
    if key in seen: continue
    seen.add(key)
    K = generalized_tonnetz(*key); s = K.summary()
    rows.append(dict(trichord=key, V=s['V'], E=s['E'], F=s['F'], chi=s['chi'],
                     betti_Q=s['betti_Q'], betti_Z2=s['betti_Z2'], surface=classify_surface(K)))
pd.DataFrame(rows)"""),
("md", "### Parity matters: the chromatic cluster (1,1,N−2)"),
("code", """for N in range(7, 16):
    print(N, classify_surface(generalized_tonnetz(1, 1, N-2, n=N)))"""),
("md", """## Exercises
1. For the (2,2,8) and (3,3,6) cases, describe each component musically.
2. Extend the table to $N = 19$ (19-tone equal temperament). Which trichords give tori?
3. Why do Betti numbers over $\\mathbb{Q}$ and $\\mathbb{Z}_2$ agree for every row of the $N=12$ table?
""" + sol("""1. (2,2,8) splits into the two whole-tone scales; (3,3,6) — diminished triads — gives three components, one per diminished-seventh collection, each the boundary of a tetrahedron (a sphere).
2. Loop `trichord_classes(19)` with `generalized_tonnetz(a,b,c,n=19)`; most classes give tori, consistent with Catanzaro's remark that the torus becomes generic as N grows.
3. They differ only when there is 2-torsion in homology, i.e. a non-orientable piece; the N = 12 complexes contain no Möbius band (the (1,1,10) strip is a cylinder because N is even).""")),
]

BOOK["06_edge_tonnetz.ipynb"] = [
("md", """# Sheet 6 — Seventh chords, edge Tonnetze and non-orientable surfaces (Chapter 7)

We (a) reproduce the slide "V − E + F = 1" from the hexagonal diagram, (b) test orientability,
(c) build the actual pitch-class complex of whole-tone shell chords, and (d) explore the space of edge-labelled gluings."""),
("code", SETUP + "\nimport collections"),
("md", "### (a) The hexagon with antipodal boundary identification"),
("code", """pts = [(q, r) for q in range(-2, 3) for r in range(-2, 3) if max(abs(q), abs(r), abs(q+r)) <= 2]
S = set(pts); tris = set()
for (q, r) in pts:
    for tri in (((q,r),(q+1,r),(q,r+1)), ((q+1,r),(q+1,r-1),(q,r))):
        if all(p in S for p in tri): tris.add(tuple(sorted(tri)))
on_bdry = lambda p: max(abs(p[0]), abs(p[1]), abs(p[0]+p[1])) == 2
label = lambda p: min(p, (-p[0], -p[1])) if on_bdry(p) else p
K = SimplicialComplex([tuple(label(p) for p in t) for t in tris])
print(K.summary()); print('=>', classify_surface(K))"""),
("md", "Betti numbers differ between $\\mathbb{Q}$ and $\\mathbb{Z}_2$ — the fingerprint of the projective plane ($H_1 = \\mathbb{Z}_2$)."),
("md", "### (b) The honest pitch-class complex of shell chords"),
("code", """wt = [0, 2, 4, 6, 8, 10]
dom = [essential_notes(r, 'dom7') for r in wt]; m9 = [essential_notes(r, 'maj9') for r in wt]
for name, ch in [('dom7 shells', dom), ('maj9 shells', m9), ('both', dom + m9)]:
    Kc = chord_complex(ch); print(f'{name:12s}', Kc.summary(), '->', classify_surface(Kc))"""),
("md", "### (c) Edge-labelled gluings: a census"),
("code", """odd = [1, 3, 5, 7, 9, 11]
faces = [tuple(sorted(essential_notes(r, 'dom7'))) for r in odd] + [tuple(sorted(essential_notes(r, 'maj9'))) for r in odd]
census = sample_edge_tonnetze(faces, n=20000, seed=1)
tot = sum(census.values())
for k, v in sorted(census.items(), key=lambda kv: -kv[1]): print(f'{k:32s} {100*v/tot:6.2f}%')"""),
("md", """## Exercises
1. Find (by search) an edge gluing of the 12 shell chords that is a **sphere**. How many vertices does it have?
2. Use `essential_notes(r, 'maj9_jazz')` (3rd, 7th, 9th) instead. Does the census change?
3. Prove that a closed surface with $\\chi = 1$ cannot be orientable.
""" + sol("""```python
import random
rng = random.Random(0)
while True:
    g = random_edge_gluing(faces, rng)
    if g.surface_name() == 'sphere': print(g.V, g.E, g.F); break   # V = 8, E = 18, F = 12
```
2. The jazz shells {3,7,9} = {r+4, r+11, r+2} lie in *both* whole-tone scales, so the faces must be rebuilt over all 12 roots; rerun and compare.
3. Orientable closed surfaces have χ = 2 − 2g, which is even; 1 is odd.""")),
]

BOOK["07_corpus_analysis.ipynb"] = [
("md", """# Sheet 7 — Real music on the Tonnetz (Chapter 8)

**Data.** Run `bash scripts/fetch_data.sh` once from the repository root. It downloads
* the Annotated Beethoven Corpus (DCMLab/ABC, CC BY-NC-SA 4.0),
* NYU MARL chord labels for RWC-Pop (100 songs) and a USPop2002 subset (195 songs),

and uses the Bach chorales that ship with `music21`. Data are *not* redistributed in this repository."""),
("code", SETUP + "\nimport json, collections, pandas as pd"),
("code", """DATA = os.path.abspath('../data/external')
print('available:', os.listdir(DATA) if os.path.isdir(DATA) else 'run scripts/fetch_data.sh first')"""),
("md", "### Parsing chord syntaxes"),
("code", """for lab in ['C:maj', 'A:min7', 'G:7/3', 'Bb:maj9', 'F#:hdim7', 'D:(1,b3,5)', 'N']:
    print(f'{lab:12s} pcs={sorted(harte_to_pcs(lab)) if harte_to_pcs(lab) else None}  triad={harte_to_triad(lab)}')"""),
("md", "### Run the full study (same code as `scripts/corpus_analysis.py`)"),
("code", """import importlib.util
spec = importlib.util.spec_from_file_location('ca', '../scripts/corpus_analysis.py'); ca = importlib.util.module_from_spec(spec); spec.loader.exec_module(ca)
G, D = plr_graph(), plr_distance_table()
corpora = {
  'Bach chorales': list(ca.bach_sequences(cache=os.path.join(DATA, 'bach_triads.json')).values()),
  'Beethoven (ABC)': [ca.dedupe([dcml_to_triad(t) for t in v]) for v in load_dcml_corpus(os.path.join(DATA, 'ABC', 'harmonies')).values()],
  'RWC Pop': [sequence_to_triads(v) for v in load_lab_corpus(os.path.join(DATA, 'Chord-Annotations', 'RWC_Pop_Chords')).values()],
  'USPop': [sequence_to_triads(v) for v in load_lab_corpus(os.path.join(DATA, 'Chord-Annotations', 'uspopLabels')).values()],
}
res = [ca.analyse(k, v, D, G, n_shuffles=10) for k, v in corpora.items()]
pd.DataFrame([{k: r[k] for k in ('corpus', 'pieces', 'transitions', 'mean_plr', 'null_mean_plr')} | {'P(d=1)': r['dist'].get(1, 0), 'P(d=4)': r['dist'].get(4, 0)} for r in res]).round(3)"""),
("md", "### What are the distance-4 moves in pop?"),
("code", """cnt = collections.Counter(); n = 0
for s in corpora['USPop']:
    for a, b in zip(s, s[1:]):
        if D[a][b] == 4: cnt[((b.root - a.root) % 12, a.quality + b.quality)] += 1; n += 1
[(k, round(v/n, 3)) for k, v in cnt.most_common(5)]"""),
("md", """Root motion by a whole step between two major triads (e.g. IV→V, ♭VII→I) accounts for most of them. In the PLR metric
F→G costs 4 steps, although it is idiomatic in rock (Biamonte 2010; de Clercq & Temperley 2011). The metric is a *model*, not a verdict.

## Exercises
1. Replace the PLR distance with `voice_leading_distance`. Do the corpus rankings change?
2. Restrict the pop corpora to songs whose chords are ≥ 90 % triad-reducible. Does the result persist?
3. Compute, per piece, the fraction of the 24 triads visited. Which corpus is most "Hamiltonian"?
""" + sol("""Sketches:
```python
vl = {k: np.mean([voice_leading_distance(a, b) for s in v for a, b in zip(s, s[1:])]) for k, v in corpora.items()}
cover = {k: np.mean([len(set(s))/24 for s in v if s]) for k, v in corpora.items()}
```
The ranking persists: mean voice-leading cost is about 3.1 semitones for Bach and Beethoven and about 3.6 for the pop corpora, because a whole step between major triads (F→G) moves all three voices by 2 semitones (cost 6), while R-type moves cost 2. Coverage is well below 1 for all corpora: real pieces sit in small regions of the torus.""")),
]

BOOK["08_audio_centroid.ipynb"] = [
("md", """# Sheet 8 — Audio: the tonal-centroid ("tonnetz") feature (Chapter 8)

Harte, Sandler & Gasser (2006) map a 12-bin chroma vector to 6-D: two coordinates each for the circle of fifths,
the minor-third circle and the major-third circle. `librosa.feature.tonnetz` implements it; so does `tonnetzkit.tonal_centroid`."""),
("code", SETUP + "\nimport librosa, librosa.display\nfrom IPython.display import Audio"),
("code", """sr = 22050
prog = [Triad.parse(s) for s in 'C Am F G C E Am'.split()]
y = np.concatenate([synth_chord(t.pcs, sr=sr, dur=0.8) for t in prog])
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
ours, lib = tonal_centroid(chroma), librosa.feature.tonnetz(chroma=chroma)
print('max difference ours vs librosa:', np.abs(ours - lib).max())
fig, ax = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
librosa.display.specshow(chroma, y_axis='chroma', x_axis='time', ax=ax[0], sr=sr)
librosa.display.specshow(lib, y_axis='tonnetz', x_axis='time', ax=ax[1], sr=sr); plt.tight_layout()
Audio(y, rate=sr)"""),
("md", "### Harmonic change detection: distance between successive centroids"),
("code", """hcdf = np.r_[0, np.linalg.norm(np.diff(lib, axis=1), axis=0)]
t = librosa.times_like(hcdf, sr=sr)
plt.figure(figsize=(8, 2)); plt.plot(t, hcdf); plt.xlabel('s'); plt.title('HCDF — peaks at chord changes'); plt.show()"""),
("md", """## Exercises
1. Which pairs of triads are closest in tonal-centroid space? Compare with the PLR distance.
2. Change the circle radii `r=(1,1,0.5)` and observe how the HCDF peaks change for L versus R moves.
""" + sol("""```python
import itertools
T = all_triads()
vec = {t: tonal_centroid(np.isin(np.arange(12), list(t.pcs)).astype(float)) for t in T}
pairs = sorted(itertools.combinations(T, 2), key=lambda ab: np.linalg.norm(vec[ab[0]] - vec[ab[1]]))
D = plr_distance_table(); print([(a, b, D[a][b]) for a, b in pairs[:6]])
```
The nearest pairs are exactly R-related (relative major/minor), then L and P pairs: two shared tones dominate the centroid.""")),
]

BOOK["09_research_sandbox.ipynb"] = [
("md", """# Sheet 9 — Research sandbox (Chapter 9)

Open-ended starting points. None has a known complete answer in the literature surveyed in the report."""),
("code", SETUP + "\nimport collections, random"),
("md", """### Project A — Minimal edge Tonnetz
Among all closed edge gluings of the 12 whole-tone shell chords, which surfaces occur, and with what exact counts?
Random sampling (Sheet 6) is a start; an exact enumeration needs symmetry reduction."""),
("code", """odd = [1, 3, 5, 7, 9, 11]
faces = [tuple(sorted(essential_notes(r, 'dom7'))) for r in odd] + [tuple(sorted(essential_notes(r, 'maj9'))) for r in odd]
# number of gluing choices: each note labels 6 edge-slots -> 15 perfect matchings x 2^3 orientations
print('size of the search space: (15 * 8)^6 =', (15*8)**6)"""),
("md", """### Project B — Hamiltonian cycles for seventh chords
Build a graph on seventh chords whose edges are single-semitone or whole-tone moves (cf. Cannas & Andreatta 2018) and
count Hamiltonian cycles. Warning: the backtracking in `hamiltonian_cycles` is exponential; add pruning (e.g. degree-2 forcing)."""),
("code", """SEV = {'dom7': (0,4,7,10), 'min7': (0,3,7,10), 'hdim7': (0,3,6,10), 'maj7': (0,4,7,11)}
chords = [frozenset((r+i) % 12 for i in iv) for r in range(12) for iv in SEV.values()]
chords = list(dict.fromkeys(chords))
G7 = nx.Graph()
for a in chords:
    for b in chords:
        if a != b and len(a & b) == 3:   # share three of four notes
            G7.add_edge(a, b)
print(G7.number_of_nodes(), 'chords;', G7.number_of_edges(), 'edges; degrees', collections.Counter(dict(G7.degree()).values()))"""),
("md", """### Project C — Perceptual test
Generate stimuli for a listening test comparing Hamiltonian cycles with matched random walks; export WAV files."""),
("code", """G = plr_graph(); H = hamiltonian_cycles(G)
def random_walk(n=24, seed=0):
    rng = random.Random(seed); t = Triad.parse('C'); out = [t]
    for _ in range(n-1):
        t = rng.choice(list(G.neighbors(t))); out.append(t)
    return out
print('Hamiltonian :', ' '.join(map(str, H[0][:10])), '...')
print('random walk :', ' '.join(map(str, random_walk()[:10])), '...')"""),
]

TOC = """format: jb-book
root: 00_welcome
chapters:
""" + "".join(f"  - file: {k[:-6]}\n" for k in list(BOOK)[1:])

CONFIG = """title: "Tonnetz, Graphs and Geometry — Python Sheets"
author: Hale Tureli
copyright: "2026"
execute:
  execute_notebooks: cache
  timeout: 900
repository:
  url: https://github.com/<your-user>/tonnetz-tutorial
  path_to_book: book
  branch: main
html:
  use_repository_button: true
"""

if __name__ == "__main__":
    for name, cells in BOOK.items():
        nbf.write(nb(cells), os.path.join(HERE, name))
    open(os.path.join(HERE, "_toc.yml"), "w").write(TOC)
    open(os.path.join(HERE, "_config.yml"), "w").write(CONFIG)
    print("wrote", len(BOOK), "notebooks")

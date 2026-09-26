# Euler's Tonnetz, Graph Theory and Geometry — a tutorial review with Python sheets

**Author:** Hale Tureli · **Report:** [`report/tonnetz_report.pdf`](report/tonnetz_report.pdf) (37 pp.) ·
**Python sheets:** [`book/`](book/) (Jupyter Book)

Developed from the DREAMS 2025 project presentation *Euler's Tonnetz, Graph Theory, and Geometry*
by S. Doran, K. Tsang and H. Tureli (advisor: J. Jones).

The Tonnetz arranges the twelve pitch classes so that major and minor triads become triangles of a lattice.
This repository contains a tutorial technical report for students and researchers, a small Python package
(`tonnetzkit`), ten executable notebooks (one per chapter, with exercises and solutions), a reproducible
corpus study, and regression tests that pin every number quoted in the report.

## Highlights (all reproduced by `pytest`)

| Result | Value |
|---|---|
| Classical Tonnetz | torus, V=12, E=36, F=24, χ=0, Betti (1,2,1) |
| PLR (dual) graph | cubic, bipartite, 24 vertices, 36 edges, diameter 5 |
| Hamiltonian cycles of the PLR graph | **62 undirected / 124 directed**, 8 orbits under T/I (sizes 1,2,3,4,4,12,12,24) |
| Smoothest Hamiltonian cycles | 28 semitones of total voice leading (4 R-moves) |
| Generalized Tonnetze in 12-TET | 6 of 12 trichord types give tori; chromatic strip is a cylinder (N even) or Möbius band (N odd) |
| Slide's whole-tone "edge Tonnetz" | glued hexagon: V=13, E=36, F=24, χ=1 → real projective plane |
| Random edge gluings of 12 shell chords | ℝP² in 0.041 %, sphere in 0.003 %, mostly 5–7 cross-caps |
| Corpus study (mean PLR distance, observed vs shuffled) | Beethoven 2.39 vs 2.58 · Bach 2.33 vs 2.36 · RWC-Pop 2.62 vs 2.47 · USPop 2.49 vs 2.44 |

## Quick start

```bash
git clone https://github.com/Hale-T2/tonnetz-tutorial.git && cd tonnetz-tutorial
pip install -e ".[dev,audio,corpora]"
pytest -q                               # 8 tests
jupyter lab book/00_welcome.ipynb       # start the Python sheets
```

```python
from tonnetzkit import *
C = Triad.parse("C"); print(P(C), L(C), R(C))          # Cm Em Am
print(len(hamiltonian_cycles(plr_graph())))             # 62
print(classify_surface(generalized_tonnetz(3, 4, 5)))  # torus
```

Corpus study and figures:

```bash
bash scripts/fetch_data.sh              # DCMLab/ABC + NYU MARL chord labels (not redistributed)
python scripts/corpus_analysis.py       # -> results/corpus_stats.json
python scripts/make_figures.py          # -> report/figures/
cd report && latexmk -pdf main.tex      # rebuild the report
jupyter-book build book/                # build the sheets as a website
```

## Repository layout

```
tonnetzkit/   core (triads, P/L/R) · graphs (dual graph, Hamiltonian cycles) · topology (complexes,
              homology, orientability) · edge_tonnetz (edge gluings) · chords (parsers, loaders, tonal centroid)
book/         00_welcome … 09_research_sandbox.ipynb, _toc.yml, _config.yml, build_notebooks.py
report/       LaTeX source, bibliography, figures, compiled PDF
scripts/      fetch_data.sh, corpus_analysis.py, make_figures.py
results/      corpus_stats.json
tests/        test_tonnetzkit.py
```

## Data

No third-party data are stored here. `scripts/fetch_data.sh` downloads the
[Annotated Beethoven Corpus](https://github.com/DCMLab/ABC) (CC BY-NC-SA 4.0) and the
[NYU MARL chord annotations](https://github.com/tmc323/Chord-Annotations) for RWC-Pop and USPop2002;
Bach chorales come with [music21](https://github.com/cuthbertLab/music21). For larger studies see
[ChoCo](https://github.com/smashub/choco) and [Chordonomicon](https://github.com/spyroskantarelis/chordonomicon).

## Licence and citation

Code: MIT (`LICENSE`). Report text and figures: CC BY 4.0 (`LICENSE-docs`). Please cite via `CITATION.cff`.

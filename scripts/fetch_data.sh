#!/usr/bin/env bash
# Download the public corpora used in Chapter 8 into data/external/ (not redistributed here).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/external && cd data/external
# Annotated Beethoven Corpus (Neuwirth et al. 2018), DCML standard, CC BY-NC-SA 4.0 — harmonies only
if [ ! -d ABC ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/DCMLab/ABC.git
  (cd ABC && git sparse-checkout set harmonies)
fi
# NYU MARL chord annotations for RWC-Pop (100) and a USPop2002 subset (195), Harte syntax
[ -d Chord-Annotations ] || git clone --depth 1 https://github.com/tmc323/Chord-Annotations.git
echo "Done. Bach chorales come with music21 (pip install music21)."

"""Reproduce the corpus study of Chapter 8. Usage:
    python scripts/corpus_analysis.py --data data/external --out results/corpus_stats.json
Requires the datasets fetched by scripts/fetch_data.sh (and music21 for Bach)."""
import argparse, json, os, random, collections
from tonnetzkit import (plr_graph, plr_distance_table, Triad, load_dcml_corpus, dcml_to_triad,
                        load_lab_corpus, sequence_to_triads, voice_leading_distance)


def bach_sequences(limit=400, cache=None):
    if cache and os.path.exists(cache):
        return {k: [Triad.parse(s) for s in v] for k, v in json.load(open(cache)).items()}
    import music21 as m21
    paths = [p for p in m21.corpus.getComposer("bach") if "bwv" in str(p).lower()][:limit]
    out = {}
    for p in paths:
        try:
            ch = m21.converter.parse(p).chordify()
        except Exception:
            continue
        seq = []
        for c in ch.recurse().getElementsByClass("Chord"):
            try:
                t = Triad.from_pcs({n.pitch.pitchClass for n in c.notes})
            except ValueError:
                continue  # non-triadic slice (passing tones, sevenths, ...)
            if not seq or seq[-1] != t:
                seq.append(t)
        out[os.path.basename(str(p))] = seq
    if cache:
        json.dump({k: [str(t) for t in v] for k, v in out.items()}, open(cache, "w"))
    return out


def dedupe(seq):
    out = []
    for t in seq:
        if t is not None and (not out or out[-1] != t):
            out.append(t)
    return out


def analyse(name, seqs, D, G, n_shuffles=20, seed=0):
    rng = random.Random(seed)
    dist, ops, vl = collections.Counter(), collections.Counter(), collections.Counter()
    n = songs = 0
    for s in seqs:
        if len(s) < 2:
            continue
        songs += 1
        for a, b in zip(s, s[1:]):
            d = D[a][b]; dist[d] += 1; n += 1
            vl[voice_leading_distance(a, b)] += 1
            if d == 1:
                ops[G.edges[a, b]["op"]] += 1
    # null model: shuffle chord order within each piece (keeps vocabulary), re-dedupe
    null = []
    for _ in range(n_shuffles):
        tot = cnt = 0
        for s in seqs:
            if len(s) < 2:
                continue
            sh = s[:]; rng.shuffle(sh); sh = dedupe(sh)
            for a, b in zip(sh, sh[1:]):
                tot += D[a][b]; cnt += 1
        null.append(tot / cnt)
    mean = sum(k * v for k, v in dist.items()) / n
    return dict(corpus=name, pieces=songs, transitions=n, mean_plr=mean,
                null_mean_plr=sum(null) / len(null),
                dist={int(k): v / n for k, v in sorted(dist.items())},
                single_ops={k: v / n for k, v in sorted(ops.items())},
                voice_leading={int(k): v / n for k, v in sorted(vl.items())})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/external")
    ap.add_argument("--out", default="results/corpus_stats.json")
    a = ap.parse_args()
    G, D = plr_graph(), plr_distance_table()
    corpora = {}
    corpora["Bach chorales"] = list(bach_sequences(cache=os.path.join(a.data, "bach_triads.json")).values())
    abc = load_dcml_corpus(os.path.join(a.data, "ABC", "harmonies"))
    corpora["Beethoven quartets (ABC)"] = [dedupe([dcml_to_triad(t) for t in v]) for v in abc.values()]
    ca = os.path.join(a.data, "Chord-Annotations")
    corpora["RWC Pop"] = [sequence_to_triads(v) for v in load_lab_corpus(os.path.join(ca, "RWC_Pop_Chords")).values()]
    corpora["USPop2002 (MARL subset)"] = [sequence_to_triads(v) for v in load_lab_corpus(os.path.join(ca, "uspopLabels")).values()]
    res = [analyse(k, v, D, G) for k, v in corpora.items()]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    for r in res:
        print(f"{r['corpus']:28s} pieces={r['pieces']:4d} n={r['transitions']:6d} "
              f"mean={r['mean_plr']:.3f} shuffled={r['null_mean_plr']:.3f} "
              f"P(d=1)={r['dist'].get(1,0):.3f} P(d=4)={r['dist'].get(4,0):.3f}")


if __name__ == "__main__":
    main()

"""Chord symbols, corpus loaders and Tonnetz-based features."""
from __future__ import annotations
import os, re, glob
import numpy as np
from .core import Triad, pc

__all__ = ["harte_to_pcs", "harte_to_triad", "load_lab", "load_lab_corpus",
           "dcml_chord_pcs", "dcml_to_triad", "load_dcml_corpus", "tonal_centroid", "synth_chord",
           "sequence_to_triads", "essential_notes", "SHORTHANDS"]

# Harte et al. (2005) shorthand -> intervals in semitones above the root
SHORTHANDS = {
    "maj": (0, 4, 7), "min": (0, 3, 7), "dim": (0, 3, 6), "aug": (0, 4, 8),
    "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "7": (0, 4, 7, 10),
    "dim7": (0, 3, 6, 9), "hdim7": (0, 3, 6, 10), "minmaj7": (0, 3, 7, 11),
    "maj6": (0, 4, 7, 9), "min6": (0, 3, 7, 9), "9": (0, 4, 7, 10, 14),
    "maj9": (0, 4, 7, 11, 14), "min9": (0, 3, 7, 10, 14), "sus4": (0, 5, 7),
    "sus2": (0, 2, 7), "5": (0, 7), "1": (0,),
}
_DEG = {"1": 0, "2": 2, "3": 4, "4": 5, "5": 7, "6": 9, "7": 11, "9": 14, "11": 17, "13": 21}


def _degree(s):
    m = re.fullmatch(r"([b#]*)(\d+)", s)
    acc, d = m.groups()
    return _DEG[d] + acc.count("#") - acc.count("b")


def harte_to_pcs(label: str):
    """Pitch-class set of a Harte-syntax label, e.g. 'A:min7/b3', 'C:(3,5,b7)'.
    Returns None for 'N' / 'X' (no chord)."""
    label = label.strip()
    if label in ("N", "X", ""):
        return None
    root, _, rest = label.partition(":")
    rest = rest.split("/")[0]
    r = pc(root)
    quality, extra = rest, ""
    if "(" in rest:
        quality, extra = rest.split("(", 1)
        extra = extra.rstrip(")")
    quality = quality or ("" if extra else "maj")
    ivs = set(SHORTHANDS.get(quality, (0, 4, 7)) if quality else {0})
    for tok in filter(None, (t.strip() for t in extra.split(","))):
        if tok.startswith("*"):
            ivs.discard(_degree(tok[1:]))
        else:
            ivs.add(_degree(tok))
    return frozenset((r + i) % 12 for i in ivs)


def harte_to_triad(label: str):
    """Reduce a Harte label to its underlying major/minor triad (root + third + fifth)
    when it has one; otherwise return None. This is the standard 'majmin' reduction
    used in chord-recognition evaluation (cf. mir_eval)."""
    label = label.strip()
    if label in ("N", "X", ""):
        return None
    root, _, rest = label.partition(":")
    q = rest.split("/")[0].split("(")[0] or "maj"
    if q in ("maj", "maj7", "7", "maj6", "9", "maj9"):
        return Triad(pc(root), "M")
    if q in ("min", "min7", "min6", "minmaj7", "min9"):
        return Triad(pc(root), "m")
    return None


def load_lab(path):
    """Read a .lab annotation: list of (start, end, label)."""
    out = []
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) >= 3:
                out.append((float(parts[0]), float(parts[1]), parts[2]))
    return out


def load_lab_corpus(root):
    """{song_id: [labels]} for every .lab file under root."""
    songs = {}
    for f in sorted(glob.glob(os.path.join(root, "**", "*.lab"), recursive=True)):
        songs[os.path.relpath(f, root)] = [lab for _, _, lab in load_lab(f)]
    return songs


def sequence_to_triads(labels, merge_repeats=True):
    """Map labels to Triads, dropping non-reducible chords and (optionally) repeats."""
    seq = []
    for lab in labels:
        t = harte_to_triad(lab) if isinstance(lab, str) else lab
        if t is None:
            continue
        if merge_repeats and seq and seq[-1] == t:
            continue
        seq.append(t)
    return seq


# ---- DCML standard (Annotated Beethoven Corpus, Distant Listening Corpus) --------
_MAJ = {"I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11}
_MIN = {"I": 0, "II": 2, "III": 3, "IV": 5, "V": 7, "VI": 8, "VII": 10}


def _key_tonic(key: str) -> tuple:
    """'F' -> (5, False); 'c#' -> (1, True)"""
    return pc(key[0].upper() + key[1:]), key[0].islower()


def _numeral_offset(num: str, minor_context: bool):
    m = re.fullmatch(r"([b#]*)([ivIV]+)", num)
    acc, rn = m.groups()
    base = (_MIN if minor_context else _MAJ)[rn.upper()]
    return base + acc.count("#") - acc.count("b"), rn.islower()


def _local_tonic(globalkey: str, localkey: str) -> int:
    g, gmin = _key_tonic(globalkey)
    lk = localkey.split("/")  # secondary local keys like 'V/V' are rare; apply right-to-left
    t, is_min = g, gmin
    for part in reversed(lk):
        off, mn = _numeral_offset(part, is_min)
        t, is_min = (t + off) % 12, mn
    return t


def dcml_chord_pcs(row) -> tuple:
    """Ordered pitch classes of a DCML harmony row (root, third, fifth, seventh...).
    `chord_tones` are given on the line of fifths relative to the local tonic, so
    pc = tonic + 7*k (mod 12)."""
    tonic = _local_tonic(row["globalkey"], row["localkey"])
    ks = [int(x) for x in str(row["chord_tones"]).replace("(", "").replace(")", "").split(",") if x.strip()]
    return tuple((tonic + 7 * k) % 12 for k in ks)


def dcml_to_triad(tones):
    """Underlying major/minor triad of an ordered DCML chord (first three tones)."""
    try:
        return Triad.from_pcs(tones[:3]) if len(tones) >= 3 else None
    except ValueError:
        return None


def load_dcml_corpus(harmonies_dir):
    """{piece: [ordered pitch-class tuples]} from DCML *.harmonies.tsv files."""
    import pandas as pd
    out = {}
    for f in sorted(glob.glob(os.path.join(harmonies_dir, "*.harmonies.tsv"))):
        df = pd.read_csv(f, sep="\t", dtype=str)
        df = df.dropna(subset=["chord_tones", "globalkey", "localkey"])
        seq = []
        for _, row in df.iterrows():
            try:
                seq.append(dcml_chord_pcs(row))
            except Exception:
                continue
        out[os.path.basename(f).split(".")[0]] = seq
    return out


# ---- Features --------------------------------------------------------------------
def tonal_centroid(chroma, r=(1.0, 1.0, 0.5)):
    """Harte-Sandler-Gasser (2006) 6-D tonal centroid of a 12-bin chroma vector
    (or a 12 x T matrix). Rows: fifths (x,y), minor thirds (x,y), major thirds (x,y)."""
    chroma = np.asarray(chroma, dtype=float)
    l = np.arange(12)
    phi = np.array([r[0] * np.sin(l * 7 * np.pi / 6), r[0] * np.cos(l * 7 * np.pi / 6),
                    r[1] * np.sin(l * 3 * np.pi / 2), r[1] * np.cos(l * 3 * np.pi / 2),
                    r[2] * np.sin(l * 2 * np.pi / 3), r[2] * np.cos(l * 2 * np.pi / 3)])
    norm = np.abs(chroma).sum(axis=0, keepdims=True)
    norm[norm == 0] = 1
    return phi @ (chroma / norm)


def synth_chord(pcs, sr=22050, dur=1.0, octave=4):
    """Additive-synthesis tone cluster for a set of pitch classes (3 harmonics each)."""
    t = np.arange(int(sr * dur)) / sr
    y = np.zeros_like(t)
    for p in pcs:
        f0 = 440.0 * 2 ** ((p - 9) / 12 + (octave - 4))
        for h, a in ((1, 1.0), (2, 0.4), (3, 0.2)):
            y += a * np.sin(2 * np.pi * f0 * h * t)
    env = np.minimum(1, np.minimum(t / 0.02, (dur - t) / 0.05))
    return (y * env / max(1, len(pcs))).astype(np.float32)


def essential_notes(root: int, kind: str):
    """'Shell' reductions used in the presentation's Edge-Tonnetz slide.
    dom7 -> root, 3rd, b7 ; maj9 -> root, 3rd, 9th (as on the slide);
    maj9_jazz -> 3rd, 7th, 9th (a common jazz-pianist rootless voicing)."""
    table = {"dom7": (0, 4, 10), "maj9": (0, 4, 2), "maj9_jazz": (4, 11, 2),
             "min7": (0, 3, 10), "maj7": (0, 4, 11)}
    return frozenset((root + i) % 12 for i in table[kind])

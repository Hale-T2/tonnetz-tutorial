"""Pitch classes, triads and the neo-Riemannian P, L, R operations."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

__all__ = ["NOTE_NAMES", "pc", "pc_name", "Triad", "all_triads", "P", "L", "R",
           "apply_word", "transpose", "invert", "voice_leading_distance"]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLAT = {"Cb": 11, "Db": 1, "Eb": 3, "Fb": 4, "Gb": 6, "Ab": 8, "Bb": 10}


def pc(name: str) -> int:
    """Pitch-class integer (C=0 ... B=11) of a note name such as 'F#', 'Bb', 'E'."""
    name = name.strip()
    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[name[0].upper()]
    for acc in name[1:]:
        base += {"#": 1, "b": -1, "s": 1}.get(acc, 0)
    return base % 12


def pc_name(p: int) -> str:
    return NOTE_NAMES[p % 12]


@dataclass(frozen=True, order=True)
class Triad:
    """A consonant triad: root pitch class and quality ('M' major or 'm' minor)."""
    root: int
    quality: str  # 'M' or 'm'

    def __post_init__(self):
        object.__setattr__(self, "root", self.root % 12)
        if self.quality not in ("M", "m"):
            raise ValueError("quality must be 'M' or 'm'")

    @property
    def third(self) -> int:
        return (self.root + (4 if self.quality == "M" else 3)) % 12

    @property
    def fifth(self) -> int:
        return (self.root + 7) % 12

    @property
    def pcs(self) -> frozenset:
        return frozenset({self.root, self.third, self.fifth})

    @classmethod
    def from_pcs(cls, pcs) -> "Triad":
        s = frozenset(p % 12 for p in pcs)
        for r, q in product(range(12), "Mm"):
            t = cls(r, q)
            if t.pcs == s:
                return t
        raise ValueError(f"{sorted(s)} is not a major or minor triad")

    @classmethod
    def parse(cls, s: str) -> "Triad":
        """Parse 'C', 'Am', 'F#m', 'Bb' ..."""
        s = s.strip()
        if s.endswith("m"):
            return cls(pc(s[:-1]), "m")
        return cls(pc(s), "M")

    def __str__(self):
        return pc_name(self.root) + ("" if self.quality == "M" else "m")

    __repr__ = __str__


def all_triads():
    """The 24 major and minor triads, majors first."""
    return [Triad(r, "M") for r in range(12)] + [Triad(r, "m") for r in range(12)]


def _flip(t: Triad, keep: tuple) -> Triad:
    # the unique other consonant triad sharing the two pitch classes in `keep`
    a, b = keep
    for r, q in product(range(12), "Mm"):
        u = Triad(r, q)
        if u != t and {a, b} <= u.pcs:
            return u
    raise RuntimeError


def P(t: Triad) -> Triad:
    """Parallel: keep root and fifth (C <-> Cm)."""
    return _flip(t, (t.root, t.fifth))


def R(t: Triad) -> Triad:
    """Relative: keep root and third of a major triad (C <-> Am)."""
    return _flip(t, (t.root, t.third) if t.quality == "M" else (t.third, t.fifth))


def L(t: Triad) -> Triad:
    """Leading-tone exchange: keep third and fifth of a major triad (C <-> Em)."""
    return _flip(t, (t.third, t.fifth) if t.quality == "M" else (t.root, t.third))


_OPS = {"P": P, "L": L, "R": R}


def apply_word(t: Triad, word: str) -> list:
    """Apply a word such as 'RLRL' left-to-right; return the whole orbit path."""
    path = [t]
    for ch in word:
        path.append(_OPS[ch](path[-1]))
    return path


def transpose(t: Triad, n: int) -> Triad:
    return Triad(t.root + n, t.quality)


def invert(t: Triad, axis: int = 0) -> Triad:
    """Pitch-class inversion I_axis: x -> axis - x (maps majors to minors)."""
    return Triad.from_pcs({(axis - p) % 12 for p in t.pcs})


def voice_leading_distance(a: Triad, b: Triad) -> int:
    """Minimal total semitone motion (taxicab, pitch-class circle) between two triads,
    minimised over the 6 bijections of their notes."""
    from itertools import permutations
    A = sorted(a.pcs)
    best = 99
    for perm in permutations(sorted(b.pcs)):
        d = sum(min((x - y) % 12, (y - x) % 12) for x, y in zip(A, perm))
        best = min(best, d)
    return best

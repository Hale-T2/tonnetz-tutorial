"""Generate every figure used in the report (report/figures/*.pdf)."""
import os, json, math, collections, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
import networkx as nx
from tonnetzkit import *

OUT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.bbox": "tight"})
C_MAJ, C_MIN = "#d9534f", "#337ab7"
OPC = {"P": "#2ca02c", "L": "#9467bd", "R": "#ff7f0e"}
E1, E2 = np.array([1.0, 0.0]), np.array([0.5, math.sqrt(3) / 2])   # P5, M3


def xy(i, j):
    return i * E1 + j * E2


def lattice_pc(i, j):
    return (7 * i + 4 * j) % 12


def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig)


# 1. Note Tonnetz with highlighted triads ------------------------------------------
def fig_tonnetz():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    I, J = range(-4, 5), range(-3, 4)
    for i in I:
        for j in J:
            p = xy(i, j)
            for (di, dj), col in (((1, 0), "#bbb"), ((0, 1), "#bbb"), ((-1, 1), "#bbb")):
                if i + di in I and j + dj in J:
                    q = xy(i + di, j + dj); ax.plot(*zip(p, q), color=col, lw=0.8, zorder=1)
    def tri(pts, col):
        ax.add_patch(Polygon([xy(*p) for p in pts], closed=True, fc=col, alpha=0.35, ec=col, lw=1.5, zorder=2))
    tri([(0, 0), (1, 0), (0, 1)], C_MAJ)            # C E G
    tri([(1, 0), (0, 1), (1, 1)], C_MIN)            # E G B = Em  (L of C)
    tri([(0, 0), (0, 1), (-1, 1)], C_MIN)           # C E A = Am  (R of C)
    tri([(0, 0), (1, 0), (1, -1)], C_MIN)           # C G Eb = Cm (P of C)
    for i in I:
        for j in J:
            p = xy(i, j)
            ax.scatter(*p, s=330, c="white", edgecolors="#555", zorder=3)
            ax.text(*p, pc_name(lattice_pc(i, j)), ha="center", va="center", fontsize=8.5, zorder=4)
    ax.annotate("", xy=xy(-2, -2) + E1, xytext=xy(-2, -2), arrowprops=dict(arrowstyle="->", color="green", lw=2))
    ax.text(*(xy(-2, -2) + 0.5 * E1 + [0, -0.28]), "P5 (+7)", color="green", ha="center", fontsize=8)
    ax.annotate("", xy=xy(-3, -2) + E2, xytext=xy(-3, -2), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(*(xy(-3, -2) + 0.5 * E2 + [-0.45, 0]), "M3 (+4)", color="red", fontsize=8)
    ax.annotate("", xy=xy(2, -1) + E1 - E2, xytext=xy(2, -1), arrowprops=dict(arrowstyle="->", color="blue", lw=2))
    ax.text(*(xy(2, -1) + 0.5 * (E1 - E2) + [0.15, 0.05]), "m3 (+3)", color="blue", fontsize=8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("The neo-Riemannian Tonnetz: C major (red) and its P, L, R neighbours (blue)")
    save(fig, "tonnetz_lattice.pdf")


# 2. Torus fundamental domain --------------------------------------------------------
def fig_torus_domain():
    fig = plt.figure(figsize=(8.4, 3.6))
    ax = fig.add_subplot(1, 2, 1)
    # kernel of (i,j) -> 7i+4j mod 12 is spanned by (4,-1) and (0,3): a 12-vertex domain
    A, B = xy(4, -1), xy(0, 3)
    for i in range(-1, 6):
        for j in range(-2, 4):
            p = xy(i, j)
            if -0.8 < p[0] < 5.6 and -1.5 < p[1] < 2.9:
                ax.scatter(*p, s=170, c="white", edgecolors="#999", zorder=3)
                ax.text(*p, pc_name(lattice_pc(i, j)), ha="center", va="center", fontsize=6.5, zorder=4)
    o = xy(0, 0)
    ax.add_patch(Polygon([o, o + A, o + A + B, o + B], closed=True, fc="#f5deb3", alpha=0.6,
                         ec="k", lw=1.5, zorder=1))
    for (p, q, lab) in ((o, o + A, "a"), (o + B, o + A + B, "a"), (o, o + B, "b"), (o + A, o + A + B, "b")):
        m = (p + q) / 2
        ax.annotate("", xy=m + 0.1 * (q - p), xytext=m - 0.1 * (q - p),
                    arrowprops=dict(arrowstyle="-|>", lw=1.8, color="k"), zorder=5)
        ax.text(*(m + [0.12, 0.18]), lab, fontsize=11, weight="bold", zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Fundamental domain: 12 notes, 36 edges, 24 triangles", fontsize=9)
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    th, ph = np.meshgrid(np.linspace(0, 2 * np.pi, 60), np.linspace(0, 2 * np.pi, 30))
    R_, r_ = 2.0, 0.8
    X = (R_ + r_ * np.cos(ph)) * np.cos(th); Y = (R_ + r_ * np.cos(ph)) * np.sin(th); Z = r_ * np.sin(ph)
    ax.plot_surface(X, Y, Z, color="#f5deb3", alpha=0.6, linewidth=0.2, edgecolor="#999")
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot((R_ + r_) * np.cos(t), (R_ + r_) * np.sin(t), 0 * t, color="red", lw=1.8)
    ax.plot(R_ + r_ * np.cos(t), 0 * t, r_ * np.sin(t), color="blue", lw=1.8)
    ax.set_box_aspect((1, 1, 0.4)); ax.axis("off")
    ax.set_title("Glue a to a and b to b: a torus\n(red and blue: the images of a and b)", fontsize=9)
    save(fig, "torus_domain.pdf")


# 3. Chicken-wire dual graph -------------------------------------------------------
def dual_positions(I=range(-3, 4), J=range(-2, 3)):
    pos, trs = {}, []
    for i in I:
        for j in J:
            up = [(i, j), (i + 1, j), (i, j + 1)]
            dn = [(i + 1, j), (i, j + 1), (i + 1, j + 1)]
            for pts in (up, dn):
                t = Triad.from_pcs({lattice_pc(*p) for p in pts})
                c = sum(xy(*p) for p in pts) / 3
                trs.append((t, c))
    return trs


def fig_dual():
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    trs = dual_positions()
    for a, ca in trs:
        for b, cb in trs:
            if np.linalg.norm(ca - cb) < 0.6 and str(a) < str(b):
                op = plr_graph().edges[a, b]["op"] if plr_graph().has_edge(a, b) else None
                ax.plot(*zip(ca, cb), color=OPC.get(op, "#ccc"), lw=2, zorder=1)
    # highlight hexagon around C (all triads containing C)
    hexC = [c for t, c in trs if 0 in t.pcs and np.linalg.norm(c - xy(0, 0)) < 0.7]
    for t, c in trs:
        ax.scatter(*c, s=260, c=C_MAJ if t.quality == "M" else C_MIN, edgecolors="k", zorder=3, alpha=0.9)
        ax.text(*c, str(t), ha="center", va="center", fontsize=6.5, color="white", zorder=4, weight="bold")
    ax.text(*xy(0, 0), "C", fontsize=16, ha="center", va="center", color="#444", alpha=0.6)
    for k, v in OPC.items():
        ax.plot([], [], color=v, lw=3, label=k)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 0.9), frameon=False, title="edge = operation")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Dual ('chicken-wire') graph: triads as vertices, P/L/R as edges.\nThe hexagon around note C lists every triad containing C.")
    save(fig, "dual_graph.pdf")


# 4. Hamiltonian cycle classes ---------------------------------------------------------
def fig_hamiltonian():
    G = plr_graph(); H = hamiltonian_cycles(G)
    by = collections.defaultdict(list)
    for h in H:
        by[canonical_cycle(cycle_word(G, h))].append(h)
    classes = sorted(by.items(), key=lambda kv: len(kv[1]))
    order = [Triad(7 * k % 12, "M") for k in range(12)]
    # circular layout: majors on outer ring by fifths, minors (relative) inner ring
    pos = {}
    for k, t in enumerate(order):
        ang = math.pi / 2 - 2 * math.pi * k / 12
        pos[t] = (math.cos(ang), math.sin(ang))
        pos[R(t)] = (0.62 * math.cos(ang - 0.26), 0.62 * math.sin(ang - 0.26))
    fig, axs = plt.subplots(2, 4, figsize=(9, 5))
    for ax, (w, cyc) in zip(axs.flat, classes):
        h = cyc[0]
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#ddd", width=0.6)
        ed = [(h[i], h[(i + 1) % 24]) for i in range(24)]
        nx.draw_networkx_edges(G, pos, edgelist=ed, ax=ax, width=1.8,
                               edge_color=[OPC[G.edges[e]["op"]] for e in ed])
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=28,
                               node_color=[C_MAJ if t.quality == "M" else C_MIN for t in G.nodes])
        cnt = collections.Counter(w)
        ax.set_title(f"orbit size {len(cyc)}\nP{cnt['P']} L{cnt['L']} R{cnt['R']}", fontsize=8)
        ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("The 62 Hamiltonian cycles of the PLR graph fall into 8 classes under transposition/inversion", fontsize=10)
    save(fig, "hamiltonian_classes.pdf")
    return classes


# 5. RP^2 hexagon ------------------------------------------------------------------
def fig_rp2():
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    pts = [(q, r) for q in range(-2, 3) for r in range(-2, 3) if max(abs(q), abs(r), abs(q + r)) <= 2]
    S = set(pts)
    for (q, r) in pts:
        for tri in (((q, r), (q + 1, r), (q, r + 1)), ((q + 1, r), (q + 1, r - 1), (q, r))):
            if all(p in S for p in tri):
                ax.add_patch(Polygon([xy(*p) for p in tri], closed=True, fc="#e8e0f5", ec="#6a51a3", lw=1))
    bnd = [p for p in pts if max(abs(p[0]), abs(p[1]), abs(p[0] + p[1])) == 2]
    lab = {}; k = 0
    for p in sorted(bnd):
        key = min(p, (-p[0], -p[1]))
        if key not in lab:
            lab[key] = "abcdef"[k]; k += 1
    for p in pts:
        key = min(p, (-p[0], -p[1])) if p in bnd else None
        ax.scatter(*xy(*p), s=90 if key else 40, c="#d62728" if key else "#6a51a3", zorder=3)
        if key:
            ax.text(*(xy(*p) * 1.14), lab[key], ha="center", va="center", fontsize=10, weight="bold")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("24 triangles; boundary points glued to their\nantipodes (same letter): V=13, E=36, F=24, $\\chi$=1", fontsize=9)
    save(fig, "rp2_hexagon.pdf")


# 6. Edge-Tonnetz census ---------------------------------------------------------------
def fig_edge_census():
    odd = [1, 3, 5, 7, 9, 11]
    faces = [tuple(sorted(essential_notes(r, "dom7"))) for r in odd] + \
            [tuple(sorted(essential_notes(r, "maj9"))) for r in odd]
    c = sample_edge_tonnetze(faces, n=200000, seed=1)
    tot = sum(c.values())
    items = sorted(c.items(), key=lambda kv: -kv[1])
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.barh([k for k, _ in items][::-1], [100 * v / tot for _, v in items][::-1], color="#6a51a3")
    ax.set_xscale("log"); ax.set_xlabel("% of 200 000 random closed gluings (log scale)")
    ax.set_title("Surfaces obtained by gluing the 12 whole-tone 'shell' chords edge-to-edge")
    save(fig, "edge_census.pdf")
    return {k: v / tot for k, v in c.items()}


# 7. Corpus distributions -----------------------------------------------------------
def fig_corpus(stats_path):
    res = json.load(open(stats_path))
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.2))
    w = 0.2
    cols = ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"]
    for k, r in enumerate(res):
        xs = np.arange(1, 6) + (k - 1.5) * w
        axs[0].bar(xs, [r["dist"].get(str(d), 0) for d in range(1, 6)], w, label=r["corpus"], color=cols[k])
    D = plr_distance_table(); T = all_triads()
    u = collections.Counter(D[a][b] for a in T for b in T if a != b); n = sum(u.values())
    axs[0].plot(range(1, 6), [u[d] / n for d in range(1, 6)], "k--o", ms=3, label="uniform random")
    axs[0].set_xlabel("PLR distance between successive triads"); axs[0].set_ylabel("fraction")
    axs[0].legend(fontsize=7, frameon=False)
    names = [r["corpus"].split(" (")[0] for r in res]
    axs[1].bar(np.arange(4) - 0.18, [r["mean_plr"] for r in res], 0.36, color=cols, label="observed")
    axs[1].bar(np.arange(4) + 0.18, [r["null_mean_plr"] for r in res], 0.36, color="#bbb", label="shuffled")
    axs[1].set_xticks(range(4)); axs[1].set_xticklabels(names, rotation=20, fontsize=8)
    axs[1].set_ylim(2, 2.75); axs[1].set_ylabel("mean PLR distance"); axs[1].legend(frameon=False, fontsize=8)
    save(fig, "corpus_plr.pdf")


# 8. Tonal centroid --------------------------------------------------------------------
def fig_centroid():
    import librosa
    fig, axs = plt.subplots(1, 3, figsize=(8.5, 2.9))
    names = ["fifths", "minor thirds", "major thirds"]
    chords = {"C": Triad.parse("C"), "Am": Triad.parse("Am"), "Em": Triad.parse("Em"), "F#": Triad.parse("F#")}
    cols = dict(zip(chords, ["#d62728", "#1f77b4", "#9467bd", "#2ca02c"]))
    for k, ax in enumerate(axs):
        rad = [1, 1, 0.5][k]
        t = np.linspace(0, 2 * np.pi, 200); ax.plot(rad * np.sin(t), rad * np.cos(t), color="#ccc")
        spots = collections.defaultdict(list)
        for p in range(12):
            v = tonal_centroid(np.eye(12)[p])[2 * k:2 * k + 2]
            spots[(round(v[0], 3), round(v[1], 3))].append(pc_name(p))
        for v, labs in spots.items():
            v = np.array(v); ax.scatter(*v, s=8, c="#999")
            ax.text(*(v * (1.18 if len(labs) == 1 else 1.32)), "/".join(labs), fontsize=5.5,
                    ha="center", va="center", color="#555")
        for nm, tr in chords.items():
            ch = np.zeros(12); ch[list(tr.pcs)] = 1
            v = tonal_centroid(ch)[2 * k:2 * k + 2]
            ax.scatter(*v, color=cols[nm], s=30, label=nm if k == 0 else None)
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(names[k], fontsize=9)
    axs[0].legend(fontsize=7, frameon=False, loc="lower left", bbox_to_anchor=(-0.2, -0.15))
    fig.suptitle("Harte-Sandler-Gasser tonal centroid: each triad is a point in 6-D (three circles)", fontsize=9)
    save(fig, "tonal_centroid.pdf")
    # check against librosa on synthetic audio
    sr = 22050
    y = np.concatenate([synth_chord(chords[c].pcs, sr=sr, dur=1.0) for c in chords])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    ours = tonal_centroid(chroma); lib = librosa.feature.tonnetz(chroma=chroma)
    return float(np.max(np.abs(ours - lib)))


if __name__ == "__main__":
    fig_tonnetz(); fig_torus_domain(); fig_dual(); cl = fig_hamiltonian(); fig_rp2()
    census = fig_edge_census()
    stats = os.path.join(os.path.dirname(__file__), "..", "results", "corpus_stats.json")
    if os.path.exists(stats):
        fig_corpus(stats)
    err = fig_centroid()
    print("hamiltonian classes:", [(len(v), w) for w, v in cl])
    print("max |ours - librosa| tonnetz:", err)
    print("census:", {k: round(v, 5) for k, v in census.items()})

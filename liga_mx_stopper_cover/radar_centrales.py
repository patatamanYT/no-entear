"""Radares de Choque y Cobertura para comparar centrales (percentil por metrica).

Uso:
    python radar_centrales.py stopper_vs_cover_apertura2026_scores.csv \
        --players "Joaquim" "Federico Pereira" --tag "Apertura 26"

Genera DOS imagenes, una por rol (sufijos _choque.png y _cobertura.png):
radar sobre fondo blanco, y debajo una franja entre dos lineas con la leyenda
(punto de color, nombre y etiqueta gris).

Lee el CSV de puntajes de stopper_vs_cover.py (columnas pct_<metrica>, percentil
0-100 dentro del grupo, ya invertido donde menos es mejor). Solo dibuja como
ejes las metricas que realmente se usaron; no rellena ejes que no existen.
"""
import argparse
import re
import sys
import unicodedata

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from stopper_vs_cover import COVER, STOPPER, load_crests

COLORS = ["#b98cf5", "#5ab9ef", "#f5b14c"]  # morado, azul, ambar
EDGES = ["#a26cf0", "#3fa9e8", "#e59a2a"]
INK, LABEL, MUTED, GRID, RULE = "#1f2233", "#3b3f52", "#7c8296", "#c4c4c9", "#c9c9d2"
FONT = ["Inter", "DejaVu Sans"]
LABELS = {
    "tackles_won": "Entradas\nganadas", "aerials_won": "Duelos\naéreos",
    "clearances": "Despejes", "interceptions": "Intercepciones",
    "duels_won": "Duelos\nganados", "dribbled_past": "Evita\nregates",
    "pass_completion_pct": "Retención\nde balón", "recoveries": "Recuperaciones",
    "errors": "Evita\nerrores",
}


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def draw(cols, rows, tag, out, crests=None, note=""):
    n = len(cols)
    ang = np.pi / 2 - np.arange(n) * 2 * np.pi / n  # primer eje arriba, sentido horario
    fig = plt.figure(figsize=(6.8, 7.2), facecolor="white")
    ax = fig.add_axes([0.0, 0.3, 1.0, 0.68])
    ax.set_aspect("equal")
    ax.axis("off")

    # rejilla: 4 anillos poligonales + radios, gris claro, sin relleno
    for lvl in (0.25, 0.5, 0.75, 1.0):
        xs, ys = lvl * np.cos(ang), lvl * np.sin(ang)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=GRID, lw=1.0, zorder=1)
    for a in ang:
        ax.plot([0, np.cos(a)], [0, np.sin(a)], color=GRID, lw=1.0, zorder=1)

    # series (el primer jugador encima)
    for r, fc, ec in reversed(list(zip(rows, COLORS, EDGES))):
        v = np.clip(np.array([r[f"pct_{c}"] for c in cols], float) / 100, 0.04, 1)
        xs, ys = v * np.cos(ang), v * np.sin(ang)
        ax.fill(xs, ys, color=fc, alpha=0.38, lw=0, zorder=2)
        ax.plot(np.r_[xs, xs[0]], np.r_[ys, ys[0]], color=ec, lw=2.0, zorder=3)
        ax.scatter(xs, ys, s=22, color=ec, zorder=4, linewidths=0)

    for a, c in zip(ang, cols):
        cx, cy = np.cos(a), np.sin(a)
        ha = "center" if abs(cx) < 0.2 else ("left" if cx > 0 else "right")
        va = "center" if abs(cy) < 0.2 else ("bottom" if cy > 0 else "top")
        ax.text(1.17 * cx, 1.17 * cy, LABELS.get(c, c), ha=ha, va=va, fontsize=10.5,
                color=LABEL, family=FONT, fontweight=500, linespacing=1.25)
    ax.set_xlim(-1.95, 1.95)
    ax.set_ylim(-1.35, 1.45)

    # franja vacia entre dos lineas y leyenda debajo
    for y in (0.255, 0.14):
        fig.add_artist(plt.Line2D([0, 1], [y, y], color=RULE, lw=1.2))
    from matplotlib.patches import Ellipse
    fw, fh = fig.get_size_inches()
    inv = fig.transFigure.inverted()
    items = []  # medir ancho total para centrar
    for r in rows:
        items.append((r, f"{r['player']}", f" · {tag}"))
    x = 0.0
    widths = []
    for r, name, t in items:
        tn = fig.text(0, -1, name, fontsize=15.5, family=FONT, fontweight=300)
        tt = fig.text(0, -1, t, fontsize=11.5, family=FONT)
        fig.canvas.draw()
        w = (tn.get_window_extent().width + tt.get_window_extent().width) / (fw * fig.dpi)
        widths.append(w)
        tn.remove()
        tt.remove()
    has_crest = [bool(crests) and r.get("team", "") in crests for r, _, _ in items]
    total = sum(widths) + 0.045 * len(items) + 0.05 * (len(items) - 1) + 0.035 * sum(has_crest)
    x = 0.5 - total / 2
    y = 0.075
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    for (r, name, t), fc, crest in zip(items, COLORS, has_crest):
        fig.add_artist(Ellipse((x + 0.011, y), 0.024, 0.024 * fw / fh,
                               transform=fig.transFigure, color=fc))
        x += 0.045
        if crest:
            fig.add_artist(AnnotationBbox(OffsetImage(crests[r["team"]], zoom=0.13),
                                          (x + 0.012, y), xycoords="figure fraction",
                                          frameon=False))
            x += 0.035
        tn = fig.text(x, y, name, fontsize=15.5, color=INK, family=FONT, fontweight=300,
                      va="center")
        fig.canvas.draw()
        x = tn.get_window_extent().transformed(inv).x1
        tt = fig.text(x, y - 0.002, t, fontsize=11.5, color=MUTED, family=FONT, va="center")
        fig.canvas.draw()
        x = tt.get_window_extent().transformed(inv).x1 + 0.05
    if note:
        fig.text(0.5, 0.015, note, fontsize=7, color=MUTED, family=FONT, ha="center")
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"Guardado: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scores")
    ap.add_argument("--players", nargs="+", required=True, help="2 o 3 nombres exactos")
    ap.add_argument("--tag", default="Apertura 26", help="texto gris junto a cada nombre")
    ap.add_argument("--out-prefix", default=None,
                    help="prefijo de salida (default: radar_<jugador1>_vs_<jugador2>)")
    ap.add_argument("--crests", action="store_true",
                    help="agrega el escudo del club en la leyenda (de --crests-dir)")
    ap.add_argument("--crests-dir", default="escudos")
    ap.add_argument("--note", default="", help="nota al pie opcional (fuente, etc.)")
    a = ap.parse_args()
    if not 2 <= len(a.players) <= 3:
        ap.error("compara 2 o 3 jugadores")

    df = pd.read_csv(a.scores)
    missing = [p for p in a.players if p not in set(df["player"])]
    if missing:
        raise SystemExit(f"No estan en {a.scores}: {', '.join(missing)}")
    rows = [df[df["player"] == p].iloc[0] for p in a.players]
    crests = load_crests([r.get("team", "") for r in rows], a.crests_dir, px=120) if a.crests else {}
    prefix = a.out_prefix or "radar_" + "_vs_".join(slug(p) for p in a.players)

    for metrics, role in ((STOPPER, "choque"), (COVER, "cobertura")):
        cols = [c for c, _, _ in metrics if f"pct_{c}" in df.columns]
        if len(cols) < 3:
            print(f"[aviso] {role}: solo {len(cols)} metricas; un radar necesita 3 o mas")
            continue
        for r in rows:
            print(f"{role:10s} {r['player']:20s} "
                  + "  ".join(f"{c}={r[f'pct_{c}']:.0f}" for c in cols))
        draw(cols, rows, a.tag, f"{prefix}_{role}.png", crests, a.note)


if __name__ == "__main__":
    sys.exit(main())

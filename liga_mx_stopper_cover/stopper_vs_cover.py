"""Stopper CB vs Cover CB (Liga MX, fase regular).

Uso:
    python stopper_vs_cover.py datos.csv --min-minutes 450 --out grafica.png
    python stopper_vs_cover.py --write-template plantilla_centrales.csv

CSV esperado (una fila por jugador, acumulado de la fase regular):
    player, team, position, minutes, <metricas...>
Opcional: columna `phase` si el CSV mezcla fase regular y liguilla
(usa --phase-col phase --phase-value Regular).

Pesos: iguales por defecto; se cambian con --weights, p. ej.
    --weights tackles_won=2,errors=0.5
Una metrica que falte en el CSV (columna ausente o vacia) se omite y se
reporta en consola, en la nota al pie de la grafica y en el CSV de salida.
"""
import argparse
import sys

import matplotlib.pyplot as plt
import pandas as pd

# Metrica -> (columna, tipo, invertir)
#   tipo "count": se divide entre minutos/90
#   tipo "rate":  ya es porcentaje/tasa, se usa tal cual
#   invertir=True: menos es mejor
STOPPER = [
    ("tackles_won", "count", False),
    ("aerials_won", "count", False),
    ("clearances", "count", False),
    ("interceptions", "count", False),
    ("duels_won", "count", False),
]
COVER = [
    ("dribbled_past", "count", True),
    ("pass_completion_pct", "rate", False),  # retencion del balon
    ("recoveries", "count", False),
    ("errors", "count", True),
]
ID_COLS = ["player", "team", "position", "minutes"]
OPTIONAL_COLS = ["phase"]


def pct_rank(s: pd.Series) -> pd.Series:
    return s.rank(pct=True) * 100


def parse_weights(text):
    """'tackles_won=2,errors=0.5' -> {'tackles_won': 2.0, 'errors': 0.5}"""
    weights = {}
    if not text:
        return weights
    known = {c for c, _, _ in STOPPER + COVER}
    for item in text.split(","):
        name, sep, value = item.partition("=")
        name = name.strip()
        if not sep or name not in known:
            raise SystemExit(f"Peso invalido '{item}'. Metricas validas: "
                             f"{', '.join(sorted(known))}")
        try:
            w = float(value)
        except ValueError:
            raise SystemExit(f"Peso no numerico en '{item}'")
        if w < 0:
            raise SystemExit(f"El peso de '{name}' no puede ser negativo")
        weights[name] = w
    return weights


def omit_reason(df, col, w, min_coverage):
    """Motivo para omitir una metrica, o None si se usa."""
    if col not in df.columns:
        return "columna ausente"
    cov = df[col].notna().mean()
    if cov == 0:
        return "columna vacia"
    if cov < min_coverage:
        return f"cobertura {cov:.0%} < {min_coverage:.0%}"
    if w == 0:
        return "peso 0"
    return None


def role_score(df: pd.DataFrame, metrics, weights, role, min_coverage=0.0):
    """Devuelve (percentil final del rol, metricas usadas, metricas omitidas).

    Tambien agrega a df una columna pct_<metrica> por cada metrica usada.
    """
    pcts, ws, used, omitted = [], [], [], []
    for col, kind, invert in metrics:
        w = weights.get(col, 1.0)
        why = omit_reason(df, col, w, min_coverage)
        if why:
            omitted.append((col, why))
            continue
        v = df[col] / (df["minutes"] / 90) if kind == "count" else df[col]
        p = pct_rank(v)
        p = 100 - p if invert else p
        df[f"pct_{col}"] = p
        pcts.append(p)
        ws.append(w)
        used.append((col, w, invert))
    for col, why in omitted:
        print(f"[aviso] {role}: se omite '{col}' ({why})")
    if not pcts:
        raise SystemExit(f"No hay metricas disponibles para el rol {role}")
    mat = pd.concat(pcts, axis=1)
    wser = pd.Series(ws, index=mat.columns)
    # Promedio ponderado; si un jugador tiene NaN en una metrica, se
    # promedia con las que si tiene (se renormalizan los pesos).
    raw = mat.mul(wser, axis=1).sum(axis=1) / mat.notna().mul(wser, axis=1).sum(axis=1)
    return pct_rank(raw), used, omitted  # percentil final dentro del grupo


def describe(used, omitted):
    parts = []
    for col, w, inv in used:
        s = col + (" (inv.)" if inv else "")
        if w != 1:
            s += f" x{w:g}"
        parts.append(s)
    txt = ", ".join(parts)
    if omitted:
        txt += " | omitidas: " + ", ".join(c for c, _ in omitted)
    return txt


def write_template(path):
    cols = ID_COLS + [c for c, _, _ in STOPPER + COVER] + OPTIONAL_COLS
    pd.DataFrame(columns=cols).to_csv(path, index=False)
    print(f"Plantilla guardada: {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--min-minutes", type=int, default=450)
    ap.add_argument("--position-col", default="position")
    ap.add_argument("--position-value", default="CB",
                    help="valor(es) de posicion separados por coma, p. ej. CB,DFC")
    ap.add_argument("--phase-col", default=None)
    ap.add_argument("--phase-value", default="Regular")
    ap.add_argument("--weights", default="",
                    help="pesos por metrica, p. ej. tackles_won=2,errors=0.5")
    ap.add_argument("--threshold", type=float, default=70,
                    help="umbral (0-100) de los recuadros resaltados")
    ap.add_argument("--title", default="Stopper CB vs Cover CB · Liga MX (fase regular)")
    ap.add_argument("--source", default="",
                    help="texto de fuente/fecha para la nota al pie")
    ap.add_argument("--top", type=int, default=10,
                    help="cuantos jugadores mostrar por rol en consola")
    ap.add_argument("--out", default="stopper_vs_cover.png")
    ap.add_argument("--scores-out", default=None,
                    help="CSV de puntajes (default: <out>_scores.csv)")
    ap.add_argument("--min-coverage", type=float, default=0.8,
                    help="fraccion minima (0-1) de centrales con dato para usar una metrica")
    ap.add_argument("--max-missing", type=int, default=0,
                    help="huecos permitidos por jugador en las metricas usadas; "
                         "con mas, el jugador se excluye (con 1+ se promedia lo que tenga)")
    ap.add_argument("--write-template", metavar="RUTA",
                    help="solo escribe una plantilla CSV vacia y termina")
    a = ap.parse_args()

    if a.write_template:
        write_template(a.write_template)
        return
    if not a.csv:
        ap.error("falta el CSV de entrada (o usa --write-template)")
    if not 50 <= a.threshold <= 100:
        ap.error("--threshold debe estar entre 50 y 100")
    weights = parse_weights(a.weights)

    df = pd.read_csv(a.csv)
    missing_id = [c for c in ID_COLS if c not in df.columns and c != "team"]
    if a.position_col not in df.columns:
        missing_id.append(a.position_col)
    if missing_id:
        raise SystemExit(f"Faltan columnas obligatorias: {', '.join(sorted(set(missing_id)))}")
    if a.phase_col:
        if a.phase_col not in df.columns:
            raise SystemExit(f"No existe la columna de fase '{a.phase_col}'")
        df = df[df[a.phase_col].astype(str).str.strip() == a.phase_value]
    positions = [p.strip() for p in a.position_value.split(",")]
    df = df[df[a.position_col].astype(str).str.strip().isin(positions)]
    df = df[pd.to_numeric(df["minutes"], errors="coerce") >= a.min_minutes].copy()
    df["player"] = df["player"].astype(str).str.strip()
    print(f"Centrales en el grupo: {len(df)}")
    if len(df) < 2:
        raise SystemExit("Se necesitan al menos 2 centrales para calcular percentiles")
    dup = df["player"].duplicated(keep=False)
    if dup.any():
        print("[aviso] jugadores repetidos (¿cambio de equipo? suma sus filas antes): "
              + ", ".join(sorted(df.loc[dup, "player"].unique())))

    # Metricas utilizables (cobertura medida en el grupo filtrado) y
    # exclusion de jugadores con huecos en ellas, antes de los percentiles.
    usable = [c for c, _, _ in STOPPER + COVER
              if not omit_reason(df, c, weights.get(c, 1.0), a.min_coverage)]
    n_missing = df[usable].isna().sum(axis=1)
    excl = df[n_missing > a.max_missing]
    if len(excl):
        print(f"[aviso] se excluyen {len(excl)} centrales con mas de {a.max_missing} "
              f"hueco(s) en las metricas usadas:")
        for r in excl.itertuples():
            gaps = [c for c in usable if pd.isna(getattr(r, c))]
            print(f"    {r.player} ({getattr(r, 'team', '')}, {r.minutes}'): falta {', '.join(gaps)}")
        df = df[n_missing <= a.max_missing].copy()
        print(f"Centrales evaluados: {len(df)}")
    n_excl = len(excl)

    df["stopper"], s_used, s_omit = role_score(df, STOPPER, weights, "Stopper", a.min_coverage)
    df["cover"], c_used, c_omit = role_score(df, COVER, weights, "Cover", a.min_coverage)

    # --- grafica ---
    fig, ax = plt.subplots(figsize=(9, 8.6))
    T = a.threshold
    # Las zonas se nombran en una leyenda arriba del area de datos, para
    # que ningun nombre de jugador pueda taparlas.
    zones = [  # (x0, x1, y0, y1, color, texto)
        (T, 100, T, 100, "#7c3aed", "Covers and stops"),
        (0, 100 - T, T, 100, "#16a34a", "Cover, weak stopper"),
        (T, 100, 0, 100 - T, "#ea580c", "Stopper, weak cover"),
    ]
    for x0, x1, y0, y1, color, label in zones:
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color=color,
                                   alpha=0.15, lw=0, zorder=0, label=label))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
              fontsize=9, handlelength=1.2, columnspacing=1.5)
    ax.axhline(50, ls="--", c="gray", lw=1)
    ax.axvline(50, ls="--", c="gray", lw=1)
    ax.scatter(df["stopper"], df["cover"], s=40, color="#1f2937", zorder=3)

    texts = [ax.text(r.stopper + 1, r.cover + 1, r.player, fontsize=8, zorder=5)
             for r in df.itertuples()]
    try:
        from adjustText import adjust_text
        # x/y: los puntos a esquivar; objects: los textos de zona (fijos)
        adjust_text(texts, x=df["stopper"].values, y=df["cover"].values, ax=ax,
                    arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.5))
    except ImportError:
        print("[aviso] adjustText no instalado; las etiquetas pueden encimarse")

    ax.set(xlim=(-3, 103), ylim=(-3, 103),
           xlabel="STOPPER CB (percentil) →", ylabel="COVER CB (percentil) →",
           )
    ax.set_title(a.title, pad=24)
    note = (f"Stopper: {describe(s_used, s_omit)}\n"
            f"Cover: {describe(c_used, c_omit)}\n"
            f"Conteos por 90'; tasas tal cual. Percentiles dentro del grupo "
            f"(n={len(df)}, mín. {a.min_minutes}'"
            + (f"; {n_excl} excluidos por datos incompletos" if n_excl else "")
            + f"). Recuadros: ≥{T:g} / ≤{100 - T:g}.")
    if a.source:
        note += f"\nFuente: {a.source}"
    fig.text(0.01, 0.01, note, fontsize=7, color="#4b5563", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04 + 0.018 * note.count("\n"), 1, 1))
    fig.savefig(a.out, dpi=150)
    print(f"Guardado: {a.out}")

    # --- CSV de puntajes ---
    scores_out = a.scores_out or a.out.rsplit(".", 1)[0] + "_scores.csv"
    front = [c for c in ["player", "team", "minutes", "stopper", "cover"] if c in df.columns]
    pct_cols = [c for c in df.columns if c.startswith("pct_")]
    rest = [c for c in df.columns if c not in front + pct_cols]
    out = df[front + pct_cols + rest].sort_values("cover", ascending=False)
    out.round(2).to_csv(scores_out, index=False)
    print(f"Guardado: {scores_out}")

    show = [c for c in ["player", "team", "minutes"] if c in df.columns]
    for role in ("stopper", "cover"):
        print(f"\nTop {a.top} {role.capitalize()}:")
        print(df.nlargest(a.top, role)[show + ["stopper", "cover"]]
              .round(1).to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())

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


def role_score(df: pd.DataFrame, metrics, weights, role):
    """Devuelve (percentil final del rol, metricas usadas, metricas omitidas).

    Tambien agrega a df una columna pct_<metrica> por cada metrica usada.
    """
    pcts, ws, used, omitted = [], [], [], []
    for col, kind, invert in metrics:
        w = weights.get(col, 1.0)
        if col not in df.columns:
            omitted.append((col, "columna ausente"))
            continue
        if df[col].isna().all():
            omitted.append((col, "columna vacia"))
            continue
        if w == 0:
            omitted.append((col, "peso 0"))
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

    df["stopper"], s_used, s_omit = role_score(df, STOPPER, weights, "Stopper")
    df["cover"], c_used, c_omit = role_score(df, COVER, weights, "Cover")

    # --- grafica ---
    fig, ax = plt.subplots(figsize=(9, 8.6))
    T = a.threshold
    # Los textos de zona van en una franja fuera del area de datos (y>100
    # o y<0) para que nunca se encimen con los nombres de los jugadores.
    zones = [  # (x0, x1, y0, y1, color, texto, y_txt, va)
        (T, 100, T, 100, "#7c3aed", "Covers and stops", 101.5, "bottom"),
        (0, 100 - T, T, 100, "#16a34a", "Cover, weak stopper", 101.5, "bottom"),
        (T, 100, 0, 100 - T, "#ea580c", "Stopper, weak cover", -1.5, "top"),
    ]
    for x0, x1, y0, y1, color, label, ty, va in zones:
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color=color,
                                   alpha=0.10, lw=0, zorder=0))
        ax.text((x0 + x1) / 2, ty, label, ha="center", va=va, fontsize=10,
                fontweight="bold", color=color, zorder=4)
    ax.axhline(50, ls="--", c="gray", lw=1)
    ax.axvline(50, ls="--", c="gray", lw=1)
    ax.scatter(df["stopper"], df["cover"], s=40, color="#1f2937", zorder=3)

    texts = [ax.text(r.stopper + 1, r.cover + 1, r.player, fontsize=8, zorder=5)
             for r in df.itertuples()]
    try:
        from adjustText import adjust_text
        adjust_text(texts, ax=ax)
    except ImportError:
        print("[aviso] adjustText no instalado; las etiquetas pueden encimarse")

    ax.set(xlim=(-3, 103), ylim=(-7, 107),
           yticks=range(0, 101, 20),
           xlabel="STOPPER CB (percentil) →", ylabel="COVER CB (percentil) →",
           title=a.title)
    note = (f"Stopper: {describe(s_used, s_omit)}\n"
            f"Cover: {describe(c_used, c_omit)}\n"
            f"Conteos por 90'; tasas tal cual. Percentiles dentro del grupo "
            f"(n={len(df)}, mín. {a.min_minutes}'). Recuadros: ≥{T:g} / ≤{100 - T:g}.")
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

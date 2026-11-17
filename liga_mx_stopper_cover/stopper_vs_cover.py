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
import unicodedata
from pathlib import Path

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


# Textos visibles de la grafica por idioma (--lang)
TEXTS = {
    "es": {
        "title": "Choque vs Cobertura",
        "header": "Liga MX · Centrales",
        "subtitle": "Percentil en cada rol · fase regular",
        "zones": ("CHOCA Y CUBRE", "CUBRE, POCO CHOQUE", "CHOCA, POCA COBERTURA"),
        "xlabel": "CHOQUE  →", "ylabel": "COBERTURA  →",
        "role_s": "Choque", "role_c": "Cobertura", "inv": "inv.", "omitted": "omitidas",
        "method": "Percentil dentro del grupo · conteos por 90', tasas tal cual · "
                  "{n} centrales, mín. {m}'",
        "excluded": " · {k} excluidos por datos incompletos", "source": "Fuente",
        "metrics": {"tackles_won": "entradas ganadas", "aerials_won": "duelos aéreos ganados",
                    "clearances": "despejes", "interceptions": "intercepciones",
                    "duels_won": "duelos ganados", "dribbled_past": "veces regateado",
                    "pass_completion_pct": "% de pase", "recoveries": "recuperaciones",
                    "errors": "errores"},
    },
    "en": {
        "title": "Stopper CB vs Cover CB",
        "header": "Liga MX · Centre-backs",
        "subtitle": "Percentile in each role · regular season",
        "zones": ("COVERS AND STOPS", "COVER, WEAK STOPPER", "STOPPER, WEAK COVER"),
        "xlabel": "STOPPER CB  →", "ylabel": "COVER CB  →",
        "role_s": "Stopper", "role_c": "Cover", "inv": "inv.", "omitted": "omitted",
        "method": "Percentile within the group · counts per 90, rates as is · "
                  "{n} centre-backs, min. {m}'",
        "excluded": " · {k} excluded for incomplete data", "source": "Source",
        "metrics": {},
    },
}


def describe(used, omitted, L=TEXTS["es"]):
    parts = []
    for col, w, inv in used:
        s = L["metrics"].get(col, col) + (f" ({L['inv']})" if inv else "")
        if w != 1:
            s += f" x{w:g}"
        parts.append(s)
    txt = ", ".join(parts)
    if omitted:
        txt += f" | {L['omitted']}: " + ", ".join(L["metrics"].get(c, c) for c, _ in omitted)
    return txt


def write_template(path):
    cols = ID_COLS + [c for c, _, _ in STOPPER + COVER] + OPTIONAL_COLS
    pd.DataFrame(columns=cols).to_csv(path, index=False)
    print(f"Plantilla guardada: {path}")


# --- Estilo de la grafica -------------------------------------------------
BG, PANEL, EDGE = "#f3f0e8", "#fbfaf6", "#e6e1d6"
INK, MUTED, GRID = "#1a1a1a", "#8b857a", "#bdb6a8"
ZONE_COLORS = {"stops": "#7c3aed", "cover": "#16a34a", "stopper": "#ea580c"}
SANS = ["Inter", "DejaVu Sans"]
MONO = ["JetBrains Mono", "DejaVu Sans Mono"]

# Colores aproximados de cada club (relleno, aro) y abreviatura del marcador.
# Equipos que no esten aqui se dibujan en gris con las 3 primeras letras.
TEAM_STYLE = {
    "América": ("#f6c500", "#0b2a5b", "AME"), "Atlante": ("#0b3a8c", "#d0021b", "ATE"),
    "Atlas": ("#c8102e", "#111111", "ATS"), "Atlético San Luis": ("#d71920", "#13294b", "ASL"),
    "Cruz Azul": ("#0047ab", "#ffffff", "CAZ"), "FC Juárez": ("#d71f26", "#39b54a", "JUA"),
    "Guadalajara": ("#cd1f2d", "#1b3c8f", "GDL"), "León": ("#00703c", "#ffffff", "LEO"),
    "Monterrey": ("#1b2a5a", "#ffffff", "MTY"), "Necaxa": ("#e4002b", "#ffffff", "NEC"),
    "Pachuca": ("#003c71", "#ffffff", "PAC"), "Puebla": ("#ffffff", "#1d3f8f", "PUE"),
    "Querétaro": ("#0b4ea2", "#111111", "QRO"), "Santos Laguna": ("#00843d", "#ffffff", "SAN"),
    "Tijuana": ("#c8102e", "#111111", "TIJ"), "Toluca": ("#d0021b", "#ffffff", "TOL"),
    "UANL": ("#fdb913", "#002d62", "TIG"), "UNAM": ("#0b2a4a", "#c9a227", "PUM"),
}

CREST_EXTS = (".png", ".webp", ".jpg", ".jpeg")


def crest_slug(team):
    """'Atlético San Luis' -> 'atletico_san_luis' (nombre de archivo del escudo)."""
    t = unicodedata.normalize("NFKD", str(team)).encode("ascii", "ignore").decode()
    return "_".join(t.lower().replace(".", " ").split())


def load_crests(teams, crest_dir, px=96):
    """Carga escudos de crest_dir/<slug>.(png|webp|jpg). Devuelve {equipo: array RGBA}."""
    if not crest_dir or not Path(crest_dir).is_dir():
        return {}
    from PIL import Image
    import numpy as np
    out, missing = {}, []
    for team in sorted(set(teams)):
        f = next((Path(crest_dir) / (crest_slug(team) + e) for e in CREST_EXTS
                  if (Path(crest_dir) / (crest_slug(team) + e)).exists()), None)
        if f is None:
            missing.append(f"{team} -> {crest_slug(team)}.png")
            continue
        im = Image.open(f).convert("RGBA")
        bbox = im.getbbox()  # recorta margen transparente
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((px, px), Image.LANCZOS)
        canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))  # centrado en lienzo cuadrado
        canvas.paste(im, ((px - im.width) // 2, (px - im.height) // 2), im)
        out[team] = np.asarray(canvas)
    if missing:
        print(f"[aviso] sin escudo en '{crest_dir}' (se usa circulo de color): "
              + "; ".join(missing))
    return out


def _text_color(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 160 else "white"


def draw_chart(df, a, note_lines, L):
    from matplotlib.patches import FancyBboxPatch

    T = a.threshold
    fig = plt.figure(figsize=(12, 11.4), facecolor=BG)
    ax = fig.add_axes([0.095, 0.2, 0.865, 0.6])
    ax.set_facecolor(PANEL)
    ax.set(xlim=(-6, 106), ylim=(-6, 108))
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Panel redondeado detras del area de datos
    pos = ax.get_position()
    fig.patches.append(FancyBboxPatch(
        (pos.x0, pos.y0), pos.width, pos.height, transform=fig.transFigure,
        boxstyle="round,pad=0.006,rounding_size=0.018", fc=PANEL, ec=EDGE, lw=1.5,
        zorder=-1))

    # Corrige la relacion de aspecto para que las esquinas salgan redondas
    fw, fh = fig.get_size_inches()
    aspect = (pos.width * fw) / (pos.height * fh)

    ax.axhline(50, ls=(0, (4, 4)), c=GRID, lw=1, zorder=1)
    ax.axvline(50, ls=(0, (4, 4)), c=GRID, lw=1, zorder=1)

    zones = [  # (x0, x1, y0, y1, color, texto, x_pildora, y_pildora)
        (T, 100, T, 100, ZONE_COLORS["stops"], L["zones"][0], None, 100),
        (0, 100 - T, T, 100, ZONE_COLORS["cover"], L["zones"][1], "right", 100),
        (T, 100, 0, 100 - T, ZONE_COLORS["stopper"], L["zones"][2], None, 100 - T),
    ]
    pills = []
    P = 3  # margen hacia afuera para que los puntos en 0 o 100 queden dentro
    for x0, x1, y0, y1, color, label, px, py in zones:
        x0, x1 = (x0 - P if x0 == 0 else x0), (x1 + P if x1 == 100 else x1)
        y0, y1 = (y0 - P if y0 == 0 else y0), (y1 + P if y1 == 100 else y1)
        py = y1  # todas las pildoras en el borde superior de su caja
        ax.add_patch(FancyBboxPatch(
            (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=3.5",
            mutation_aspect=aspect, fc=color + "1a", ec=color, lw=2, zorder=0))
        x = x1 - (x1 - x0) * 0.2 if px == "right" else (x0 + x1) / 2
        pills.append(ax.text(
            x, py, label, ha="center", va="center", fontsize=8.5, fontweight="bold",
            color="white", family=SANS, zorder=6,
            bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.85", fc=color, ec="none")))

    # Marcadores: escudo del club si existe en --crests-dir; si no, circulo
    # con colores del club y su abreviatura
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    teams = df["team"] if "team" in df.columns else pd.Series("", index=df.index)
    crests = load_crests(teams, a.crests_dir)
    for r, team in zip(df.itertuples(), teams):
        if team in crests:
            ax.scatter(r.stopper, r.cover, s=330, color="white", edgecolor=EDGE,
                       linewidth=0.8, zorder=3)  # disco blanco detras del escudo
            ax.add_artist(AnnotationBbox(OffsetImage(crests[team], zoom=0.17),
                                         (r.stopper, r.cover), frameon=False, zorder=4))
            continue
        fill, ring, abbr = TEAM_STYLE.get(team, ("#9ca3af", "#ffffff", str(team)[:3].upper()))
        ax.scatter(r.stopper, r.cover, s=210, color=fill, edgecolor=ring, linewidth=1.8,
                   zorder=4)
        ax.scatter(r.stopper, r.cover, s=280, facecolor="none", edgecolor="white",
                   linewidth=1.2, zorder=3)  # halo blanco
        ax.text(r.stopper, r.cover, abbr, ha="center", va="center", fontsize=4.6,
                fontweight="bold", color=_text_color(fill), family=SANS, zorder=5)

    texts = [ax.text(r.stopper + 2.0, r.cover, r.player, fontsize=9.5, fontweight="bold",
                     color=INK, family=SANS, va="center", zorder=5)
             for r in df.itertuples()]
    try:
        from adjustText import adjust_text
        adjust_text(texts, x=df["stopper"].values, y=df["cover"].values, objects=pills,
                    ax=ax, expand=(1.1, 1.5), force_text=(0.3, 0.6),
                    force_static=(0.4, 0.8), time_lim=8,
                    arrowprops=dict(arrowstyle="-", color="#a8a29e", lw=0.6))
    except ImportError:
        print("[aviso] adjustText no instalado; las etiquetas pueden encimarse")

    ax.set_xticks(range(0, 101, 20))
    ax.set_yticks(range(0, 101, 20))
    ax.tick_params(length=0, labelsize=11, labelcolor=MUTED, pad=10)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_family(SANS)
    ax.set_xlabel(L["xlabel"], fontsize=12, fontweight="bold", color=INK,
                  family=SANS, labelpad=8)
    ax.set_ylabel(L["ylabel"], fontsize=12, fontweight="bold", color=INK,
                  family=SANS, labelpad=14)

    # Encabezado: linea superior, titulo con "vs" en gris y subtitulo
    x = 0.045
    if a.brand:
        b = fig.text(x, 0.955, a.brand, fontsize=15, fontweight="bold", color=INK,
                     family=SANS, va="center")
        fig.canvas.draw()
        x = b.get_window_extent().transformed(fig.transFigure.inverted()).x1 + 0.012
        fig.text(x, 0.955, "|", fontsize=14, color=EDGE, va="center")
        x += 0.018
    fig.text(x, 0.955, a.header.upper(), fontsize=10, color=MUTED, family=MONO,
             va="center")

    left, sep, right = a.title.partition(" vs ")
    parts = [(left, INK)] + ([(" vs ", "#a39e93"), (right, INK)] if sep else [])
    x = 0.045
    fig.canvas.draw()
    inv = fig.transFigure.inverted()
    for txt, color in parts:
        t = fig.text(x, 0.895, txt, fontsize=36, fontweight="heavy", color=color,
                     family=SANS, va="center")
        fig.canvas.draw()
        x = t.get_window_extent().transformed(inv).x1
    fig.text(0.045, 0.845, a.subtitle, fontsize=14, color="#6b665c", family=SANS,
             va="center")

    fig.text(0.045, 0.02, "\n".join(note_lines), fontsize=7.6, color=MUTED, family=MONO,
             va="bottom", linespacing=1.6)
    fig.patch.set_edgecolor(EDGE)
    fig.patch.set_linewidth(2)
    fig.savefig(a.out, dpi=200, facecolor=BG)
    plt.close(fig)


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
    ap.add_argument("--lang", choices=sorted(TEXTS), default="es",
                    help="idioma de los textos de la grafica (default: es)")
    ap.add_argument("--title", default=None,
                    help='titulo grande; lo que va despues de " vs " se pinta igual y el "vs" en gris')
    ap.add_argument("--header", default=None,
                    help="linea pequena arriba del titulo")
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--crests-dir", default="escudos",
                    help="carpeta con escudos <equipo>.png (p. ej. cruz_azul.png); "
                         "los equipos sin archivo usan circulo de color")
    ap.add_argument("--brand", default="",
                    help="texto de marca opcional arriba a la izquierda (p. ej. tu usuario)")
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
    L = TEXTS[a.lang]
    a.title = a.title or L["title"]
    a.header = a.header or L["header"]
    a.subtitle = a.subtitle or L["subtitle"]
    note = [f"{L['role_s']}: {describe(s_used, s_omit, L)}",
            f"{L['role_c']}: {describe(c_used, c_omit, L)}",
            L["method"].format(n=len(df), m=a.min_minutes)
            + (L["excluded"].format(k=n_excl) if n_excl else "")]
    if a.source:
        note.append(f"{L['source']}: {a.source}")
    draw_chart(df, a, note, L)
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

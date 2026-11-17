"""Descarga los escudos de los clubes de Liga MX desde Wikipedia (en).

Uso:
    python descargar_escudos.py              # guarda en escudos/<slug>.png
    python descargar_escudos.py --force      # vuelve a descargar los que ya existen

Para cada club lee la ficha (Infobox) de su articulo en en.wikipedia.org,
toma el archivo del campo image/logo y descarga el ORIGINAL desde
upload.wikimedia.org (las miniaturas generadas devuelven 429 a clientes
automatizados). Los SVG se convierten a PNG aqui con cairosvg (pip install
cairosvg). Son 2 llamadas a la API (por lotes) + 1 descarga por escudo, con
pausa entre descargas.

Los escudos son marcas registradas de cada club: uso personal/analitico,
no se suben a git (ver .gitignore).
"""
import argparse
import re
import sys
import time
from pathlib import Path

import requests

from stopper_vs_cover import crest_slug

API = "https://en.wikipedia.org/w/api.php"
UA = "LigaMX-StopperCover/1.0 (personal football analytics script; low volume)"

# Nombre en la columna `team` -> articulo de Wikipedia en ingles
CLUBS = {
    "América": "Club América", "Atlante": "Atlante F.C.", "Atlas": "Atlas F.C.",
    "Atlético San Luis": "Atlético San Luis", "Cruz Azul": "Cruz Azul",
    "FC Juárez": "FC Juárez", "Guadalajara": "C.D. Guadalajara", "León": "Club León",
    "Monterrey": "C.F. Monterrey", "Necaxa": "Club Necaxa", "Pachuca": "C.F. Pachuca",
    "Puebla": "Club Puebla", "Querétaro": "Querétaro F.C.",
    "Santos Laguna": "Club Santos Laguna", "Tijuana": "Club Tijuana",
    "Toluca": "Deportivo Toluca F.C.", "UANL": "Tigres UANL",
    "UNAM": "Club Universidad Nacional",
}
FIELD = re.compile(r"^\s*\|\s*(?:image|logo|crest|badge)\s*=\s*(?:\[\[)?\s*(?:File:|Image:)?"
                   r"([^|\]\n<{]+\.(?:svg|png|jpe?g|gif|webp))", re.I | re.M)


def get(s, url, **kw):
    """GET con reintentos ante 429/5xx, respetando Retry-After."""
    for attempt in range(5):
        r = s.get(url, timeout=30, **kw)
        if r.status_code != 429 and r.status_code < 500:
            return r
        wait = int(r.headers.get("retry-after", 0) or 0) or 30 * (attempt + 1)
        print(f"  [{r.status_code}] espero {wait}s y reintento")
        time.sleep(wait)
    return r


def api(s, **params):
    params.update(format="json", formatversion=2)
    r = get(s, API, params=params)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default="escudos")
    ap.add_argument("--width", type=int, default=300)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    out = Path(a.out_dir)
    out.mkdir(exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA

    # 1) wikitext de todos los articulos en una llamada (sigue redirecciones)
    data = api(s, action="query", prop="revisions", rvprop="content", rvslots="main",
               redirects=1, titles="|".join(CLUBS.values()))["query"]
    alias = {r["from"]: r["to"] for r in data.get("redirects", [])}
    alias.update({n["from"]: n["to"] for n in data.get("normalized", [])})
    text = {p["title"]: p["revisions"][0]["slots"]["main"]["content"]
            for p in data["pages"] if "revisions" in p}

    files, problems = {}, []
    for team, title in CLUBS.items():
        t = alias.get(alias.get(title, title), alias.get(title, title))
        m = FIELD.search(text.get(t, ""))
        if not m:
            problems.append(f"{team}: no encontre el escudo en la ficha de '{title}'")
            continue
        files[team] = "File:" + m.group(1).strip()

    # 2) URL de miniatura PNG para todos los archivos en una llamada
    info = api(s, action="query", prop="imageinfo", iiprop="url",
               titles="|".join(files.values()))["query"]
    norm = {n["from"]: n["to"] for n in info.get("normalized", [])}
    urls = {p["title"]: (p.get("imageinfo") or [{}])[0].get("url") for p in info["pages"]}

    # 3) descargas
    for team, f in files.items():
        dest = out / (crest_slug(team) + ".png")
        url = urls.get(norm.get(f, f))
        if not url:
            problems.append(f"{team}: sin URL para {f}")
            continue
        if dest.exists() and not a.force:
            print(f"  ya existe: {dest.name}")
            continue
        url = url.split("?")[0]  # quita parametros de rastreo (utm_*)
        time.sleep(a.sleep)
        r = get(s, url)
        if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
            problems.append(f"{team}: HTTP {r.status_code} en {url}")
            continue
        if "svg" in r.headers.get("content-type", "") or url.lower().endswith(".svg"):
            import cairosvg
            cairosvg.svg2png(bytestring=r.content, write_to=str(dest), output_width=a.width)
        else:
            from io import BytesIO
            from PIL import Image
            im = Image.open(BytesIO(r.content)).convert("RGBA")
            im.thumbnail((a.width, a.width))
            im.save(dest)
        print(f"  {team:18s} -> {dest.name}  ({f})")

    for p in problems:
        print(f"[aviso] {p}")
    print(f"Escudos en {out}/: {len(list(out.glob('*.png')))} de {len(CLUBS)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

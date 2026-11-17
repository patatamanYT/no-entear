# Stopper CB vs Cover CB · Liga MX (fase regular)

Gráfica de dispersión de centrales: eje X = percentil **Stopper** y eje Y = percentil **Cover**.

## Estado

**Corrida actual (17 nov 2026): datos de FotMob recopilados por un asistente de IA (Grok o Muse) con `prompt_para_llenar.md`.**

- **Fuente:** FotMob, páginas de jugador de la Liga MX 2026/2027. `tackles_won` sale de FootyMetrics, solo donde su total de tackles coincidía con el de FotMob. Eduardo Tercero tiene métricas de playmakerstats/thefishy; queda excluido por tener huecos.
- **Periodo:** Apertura 2026, fase regular, jornadas 1–16, partidos hasta el 14 nov 2026. Daniel Piña, Felipe Sánchez y Jonathan Pérez solo llegan a J15.
- **Fecha de consulta:** 16–17 nov 2026.
- **Sin verificar:** no se comparó ningún número contra la fuente. La red de esta sesión no tiene acceso a FotMob, y su scraping está descartado por términos de uso. Revisa a mano a 3 o 4 jugadores antes de publicar.
- **Datos fuera de git:** el CSV, el PNG y los puntajes no se suben al repositorio (ver `.gitignore`) para no redistribuir datos de FotMob.

Comando usado:

```bash
python stopper_vs_cover.py centrales_apertura2026_j16.csv --phase-col phase \
  --header "Liga MX Apertura 2026 · Centrales" \
  --subtitle "Percentil en cada rol · fase regular, jornadas 1–16" \
  --max-missing 1 \
  --source "FotMob, J1–J16, consultado 16–17 nov 2026; recopilado por un asistente de IA y verificado a mano en 1 jugador" \
  --out stopper_vs_cover_apertura2026.png
```

Resultado:
- **Fórmula (v2, 17 nov 2026; incluye las columnas extra de FotMob):**
  - **Choque:** tackles (entradas totales), interceptions, clearances, aerials_won, duels_won_pct y blocked_shots.
  - **Cobertura:** dribbled_past (invertida), pass_completion_pct, recoveries y fouls_committed (invertida).
  - Respecto a v1: entradas ganadas (`tackles_won`, 50% de cobertura) pasa a tackles totales, y duelos ganados (conteo) pasa a % de duelos ganados. Se agregan bloqueos y faltas.
- **Omitidas:** `errors`, porque FotMob no la publica (0% de cobertura).
- **Por 90' con otros minutos:** tackles, bloqueos y faltas se dividen entre `minutes_fotmob` cuando existe, porque son de J16 en jugadores cuyas otras columnas llegan a J15.
- **Muestra (tercera pasada de datos, 17 nov 2026):** 76 centrales en el CSV; 55 con 450' o más; 53 evaluados con `--max-missing 1`. Quedan fuera Carlos Salcedo y Diego Reyes, a los que les faltan 4 métricas y cuyos datos son de FootyMetrics. Jackson Porozo entra con 1 hueco (`dribbled_past`), y su Cobertura se promedia con 3 métricas.
- **Sensibilidad:** sin Porozo (`--max-missing 0`, 52 centrales), los percentiles de los demás cambian como máximo 3.4 puntos.

**Alternativa preparada:** `descargar_datos.py` (Sportmonks, las 9 métricas). Necesita la variable `SPORTMONKS_API_TOKEN`.

## Descarga (Sportmonks)

```bash
export SPORTMONKS_API_TOKEN=...          # nunca en el código ni en git
python descargar_datos.py --plan         # ~4 peticiones: muestra liga, temporada, fases y partidos
python descargar_datos.py --out centrales_apertura2026.csv
```

- **Fase regular:** se elige la fase de la temporada cuyo nombre contiene `--stage-name` (default `Apertura`) y no contiene palabras de liguilla o repechaje (`--stage-exclude`). Si hay ambigüedad, el script se detiene y pide `--stage-id`. Solo cuenta partidos terminados.
- **Peticiones:** una por partido terminado más unas 4 de metadatos, con pausa `--sleep` (1 s) y reintentos ante 429. Las respuestas se guardan en `.cache_sportmonks/` (ignorada por git), así que repetir la corrida no gasta peticiones.
- **Mapeo a tipos de Sportmonks** (estadísticas por partido en `lineups.details`): tackles_won = TACKLES_WON (27267), aerials_won = AERIALS_WON (107), clearances = CLEARANCES (101), interceptions = INTERCEPTIONS (100), duels_won = DUELS_WON (106), dribbled_past = DRIBBLED_PAST (110), recoveries = BALL_RECOVERY (27271), minutes = MINUTES_PLAYED (119).
- **pass_completion_pct** = Σ ACCURATE_PASSES (116) / Σ PASSES (80) × 100. Si faltan los conteos, usa el promedio de ACCURATE_PASSES_PERCENTAGE (1584) ponderado por minutos.
- **errors** = ERROR_LEAD_TO_SHOT (48997) + ERROR_LEAD_TO_GOAL (571). Supuesto: son conteos separados, sin doble conteo. El CSV guarda ambas columnas por si quieres usar solo una.
- **Posición:** la posición detallada en la que jugó más minutos. "Centre Back" se convierte en `CB`. El CSV también trae `cb_minutes` y `position_detail_main`.
- **Jugadores que cambiaron de equipo:** se suman todas sus filas por `player_id`; `team` queda como "Equipo1 / Equipo2", ordenado por minutos.
- Si un tipo no aparece en ningún partido, la columna queda vacía (NaN) y `stopper_vs_cover.py` la omite y lo anota en la gráfica.

## Uso

```bash
pip install pandas matplotlib adjustText   # adjustText es opcional

# 1) Plantilla vacía con las columnas esperadas
python stopper_vs_cover.py --write-template plantilla_centrales.csv

# 2) Correr con tus datos
python stopper_vs_cover.py centrales.csv \
    --min-minutes 450 \
    --phase-col phase --phase-value Regular \
    --position-value CB \
    --weights tackles_won=1,errors=1 \
    --threshold 70 \
    --source "Sofascore, extraído 2026-11-17" \
    --out stopper_vs_cover.png
```

Salidas:
- `<out>.png`: la gráfica. La nota al pie lista las métricas usadas, sus pesos, las métricas omitidas, n, el mínimo de minutos y la fuente.
- `<out>_scores.csv`: una fila por central, ordenada por Cover. Incluye `stopper`, `cover`, el percentil de cada métrica (`pct_*`) y los datos originales.
- En consola: el top N de cada rol (`--top`, default 10) y avisos de métricas omitidas o jugadores repetidos.

## Diseño de la gráfica

- **Idioma:** en español por defecto (`--lang es`): título "Choque vs Cobertura", ejes CHOQUE / COBERTURA, zonas "CHOCA Y CUBRE", "CUBRE, POCO CHOQUE" y "CHOCA, POCA COBERTURA", y las métricas del pie con nombre en español. Con `--lang en` se usan los textos en inglés ("Stopper CB vs Cover CB"). `--title`, `--header` y `--subtitle` reemplazan los textos por defecto.
- Fondo crema, panel redondeado, título grande con "vs" en gris (`--title`), línea superior en monoespaciada (`--header`), subtítulo (`--subtitle`) y marca opcional arriba a la izquierda (`--brand`).
- Zonas con caja redondeada y etiqueta en píldora. Los lados que tocan 0 o 100 se extienden 3 unidades hacia afuera, para que los puntos del borde queden dentro. El lado del umbral (`--threshold`) es exacto.
- Marcadores: círculo con colores aproximados del club y abreviatura (AME, CAZ, TOL…), definidos en `TEAM_STYLE`. Un equipo que no esté ahí sale en gris con sus 3 primeras letras.
- **Escudos:** `python descargar_escudos.py` los baja de Wikipedia (en). Lee el archivo de la ficha de cada club, descarga el SVG original de upload.wikimedia.org y lo convierte a PNG de 300 px con cairosvg (`pip install cairosvg`). Hace 2 llamadas a la API y 18 descargas espaciadas, con reintentos si el servidor limita. Las miniaturas de Wikimedia devuelven 429 a scripts; por eso se usa el original. Si existe `escudos/<equipo>.png` (también `.webp` o `.jpg`), el punto del jugador es el escudo de su club sobre un disco blanco. Los equipos sin archivo usan el círculo de color, y el script avisa cuáles faltan. Otra carpeta se indica con `--crests-dir`. Conviene PNG con fondo transparente, de 200 px o más; el margen transparente se recorta solo. La carpeta no se sube a git porque son logotipos con marca registrada.
  Nombres esperados: `america`, `atlante`, `atlas`, `atletico_san_luis`, `cruz_azul`, `fc_juarez`, `guadalajara`, `leon`, `monterrey`, `necaxa`, `pachuca`, `puebla`, `queretaro`, `santos_laguna`, `tijuana`, `toluca`, `uanl`, `unam` (sin acentos, en minúsculas y con guion bajo, igual que la columna `team`).
- Tipografías: Inter y JetBrains Mono, con DejaVu como respaldo si no están instaladas.
- PNG a 200 dpi (2400 × 2280 px).

## Radares de comparación

```bash
python radar_centrales.py stopper_vs_cover_apertura2026_scores.csv \
  --players "Joaquim" "Eduardo Bauermann" --tag "Apertura 26"
# -> radar_joaquim_vs_eduardo_bauermann_choque.png y ..._cobertura.png
```

- Genera dos imágenes, una por rol, con el estilo de la referencia: fondo blanco, rejilla de anillos grises, morado y azul semitransparentes, una franja vacía entre dos líneas y la leyenda (punto, nombre en letra delgada y etiqueta gris). Compara 2 o 3 jugadores con los percentiles por métrica (`pct_*`) del CSV de puntajes.
- **Ejes propios del radar**, como en la referencia (en `RADAR` dentro del script):
  - **Choque (6 ejes):** entradas (tackles totales), intercepciones, despejes, duelos aéreos, éxito en duelos (`duels_won_pct`) y bloqueos (`blocked_shots`).
  - **Cobertura (4 ejes con los datos actuales):** evita regates, retención de balón, recuperaciones y evita faltas (`fouls_committed` invertida). "Evita errores" se agrega solo cuando haya datos.
- **Cálculo:** cada eje es el percentil dentro del grupo de centrales evaluados (las filas del CSV de puntajes, hoy 48). Los conteos van por 90'. En tackles, bloqueos y faltas se usa `minutes_fotmob` cuando existe, porque esas columnas pueden ir a otra jornada (por ejemplo, Daniel Piña). Un eje con datos para menos de `--min-coverage` del grupo (80%) se omite.
- **Radar y gráfica usan las mismas métricas:** los ejes son las de `STOPPER` / `COVER` de `stopper_vs_cover.py`, así que lo que muestra el radar es lo que entra en el puntaje.
- Opcional: `--crests` agrega el escudo en la leyenda, `--note` agrega una nota al pie y `--out-prefix` cambia el nombre de los archivos.
- El texto para redes y el comentario con la fórmula están en `post_redes.md`.

## ¿Se complementan los centrales de cada equipo?

```bash
python parejas_centrales.py centrales_apertura2026_j16.csv stopper_vs_cover_apertura2026_scores.csv \
  --out parejas_centrales.png
```

- **Titulares y línea de 2 o de 3:** salen de `formaciones.csv`. Grok lo investigó con las alineaciones J1–J16 de FotMob, FBref y otras fuentes, y en `origen` y `nota` explica el conteo de partidos de cada equipo y los casos dudosos.
  - Línea de 3: Atlante, Atlas, San Luis, Cruz Azul, Chivas, Necaxa y Santos.
  - Línea de 2: los otros 11.
  - Mayorías ajustadas (9-7): Atlas y Necaxa.
- **Puntajes:** usa el mismo CSV de puntajes que la dispersión (`--max-missing 1`), así que los números coinciden con la gráfica principal.
- **Perfil de cada central** (Ch = percentil Choque, Cb = percentil Cobertura): Ambos (Ch y Cb ≥ 60), Choque (Ch ≥ 55 y al menos 15 sobre Cb), Cobertura (al revés), Equilibrado (ambos ≥ 40), Bajo y Sin datos.
- **Veredicto:** Completa (hay un "Ambos"), Se complementan (hay un Choque y un Cobertura), Solo choque, Solo cobertura, Sin complemento y Datos incompletos (falta el puntaje de un titular y lo conocido no alcanza para decidir).
- **Titulares sin puntaje:** Aldo Cruz (San Luis) no está en el CSV porque es lateral de posición; Diego Reyes (Querétaro) y Carlos Salcedo (Monterrey) tienen datos incompletos.
- Sin `formaciones.csv`, el script estima la línea por minutos (`--write-formations` guarda esa estimación).

## Columnas del CSV

| Columna | Tipo | Rol | Notas |
|---|---|---|---|
| player | texto | — | obligatoria |
| team | texto | — | opcional, recomendada |
| position | texto | — | obligatoria; se filtra con `--position-value` (acepta varios: `CB,DFC`) |
| minutes | número | — | obligatoria; minutos totales de la fase |
| tackles_won | conteo | Stopper | |
| aerials_won | conteo | Stopper | duelos aéreos ganados |
| clearances | conteo | Stopper | despejes |
| interceptions | conteo | Stopper | |
| duels_won | conteo | Stopper | duelos totales ganados |
| dribbled_past | conteo | Cover | **invertida** (menos = mejor) |
| pass_completion_pct | tasa | Cover | 0–100; se usa tal cual |
| recoveries | conteo | Cover | recuperaciones de balón |
| errors | conteo | Cover | **invertida**; errores que terminan en tiro o gol |
| phase | texto | — | opcional; p. ej. `Regular` / `Liguilla` / `Repechaje` |

Los conteos son **totales acumulados**, no por 90: el script los convierte.

## Metodología

1. Filtra por fase (si se da `--phase-col`), por posición y por minutos ≥ `--min-minutes`.
2. Los conteos se pasan a por 90 (`valor / (minutes/90)`) y las tasas se usan tal cual.
3. Saca el percentil de cada métrica dentro del grupo (`rank(pct=True)*100`) e invierte las negativas (`100 - p`).
4. Puntaje de rol = promedio ponderado de los percentiles de sus métricas. Los pesos son 1 por defecto (`--weights`).
5. Saca el percentil final del puntaje de rol dentro del grupo, que da los ejes 0–100.
6. Pone líneas punteadas en 50 y recuadros con umbral `--threshold` (default 70):
   - arriba-derecha ≥T/≥T **Covers and stops**
   - arriba-izquierda ≤100−T/≥T **Cover, weak stopper**
   - abajo-derecha ≥T/≤100−T **Stopper, weak cover**

## Supuestos y limitaciones

- **Métricas faltantes:** si una columna no existe, está vacía o su cobertura en el grupo es menor que `--min-coverage` (default 0.8), se omite. Se avisa en consola y aparece como "omitidas" en la nota al pie, y el rol se calcula con las que queden. Peso 0 también omite la métrica.
- **Valores faltantes por jugador:** con `--max-missing 0` (default), se excluye a quien tenga algún hueco en las métricas usadas, y se lista en consola. Con `--max-missing N`, se promedia con las métricas que sí tenga (los pesos se renormalizan).
- **Jugadores repetidos** (por ejemplo, un cambio de equipo a mitad de torneo): el script avisa pero no suma. Hay que consolidar las filas antes.
- **Percentiles relativos al grupo:** cambian si cambia el mínimo de minutos o el conjunto de centrales.
- **Métricas no ajustadas por posesión:** los equipos que defienden más acumulan más tackles y despejes.
- La definición exacta de cada métrica (por ejemplo, qué cuenta como "error" o "recuperación") depende del proveedor. Documéntala aquí cuando se elija la fuente.

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
  --source "FotMob (+ FootyMetrics para entradas), J1–J16, consultado 16–17 nov 2026; recopilado por un asistente de IA, no verificado" \
  --out stopper_vs_cover_apertura2026.png
```

Resultado:
- **Métricas usadas:** Stopper = aerials_won, clearances, interceptions, duels_won. Cover = dribbled_past (invertida), pass_completion_pct, recoveries.
- **Omitidas:** `errors` (FotMob no la publica; 0% de cobertura) y `tackles_won` (50% de cobertura, por debajo del mínimo de 80% de `--min-coverage`).
- **Muestra:** 76 centrales en el CSV; 55 con 450' o más; 48 evaluados. Se excluyeron 7 por huecos (`--max-missing 0`): Eduardo Tercero, Gilberto Sepúlveda, Carlos Salcedo, Diego Reyes, Felipe Sánchez, Efraín Orona y Jackson Porozo.
- **Sensibilidad:** con `--max-missing 2` entran Tercero, F. Sánchez y Porozo, y los percentiles de los demás cambian como máximo unos 5.6 puntos.

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
  --players "Joaquim" "Federico Pereira" --tag "Apertura 2026" \
  --source "FotMob, J1–J16, recopilado por IA, no verificado" --out radar_joaquim_vs_pereira.png
```

- Hace dos radares lado a lado (Choque y Cobertura) con 2 o 3 jugadores. Usa los percentiles por métrica (`pct_*`) del CSV de puntajes.
- Solo aparecen como ejes las métricas que realmente se usaron. Con los datos actuales, Choque tiene 4 ejes y Cobertura 3, porque faltan entradas ganadas y errores; con las 9 métricas serían 5 y 4.
- La leyenda lleva el escudo del club si está en `escudos/`.
- El texto para redes y el comentario con la fórmula están en `post_redes.md`.

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

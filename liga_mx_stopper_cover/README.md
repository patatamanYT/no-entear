# Stopper CB vs Cover CB · Liga MX (fase regular)

Gráfica de dispersión de centrales: eje X = percentil **Stopper** y eje Y = percentil **Cover**.

## Estado

- **Fuente de datos: pendiente.** Todavía no se ha procesado ningún dato real. El script espera un CSV que tú proporcionas (exportado de Sofascore, de un proveedor con licencia, etc.). No hace scraping.
- **Fecha de extracción: pendiente.** Se registra aquí y en la gráfica (`--source`) cuando llegue el CSV.
- Contexto de fuentes (nov 2026): FBref perdió los datos avanzados de Opta el 20 ene 2026. Sofascore no se ha podido verificar desde esta sesión porque la red lo bloquea.

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

- **Métricas faltantes:** si una columna no existe o está vacía, se omite. Se avisa en consola y aparece como "omitidas" en la nota al pie, y el rol se calcula con las que queden. Peso 0 también omite la métrica.
- **Valores faltantes por jugador:** si a un jugador le falta una métrica, su puntaje se calcula con las que sí tiene (los pesos se renormalizan).
- **Jugadores repetidos** (por ejemplo, un cambio de equipo a mitad de torneo): el script avisa pero no suma. Hay que consolidar las filas antes.
- **Percentiles relativos al grupo:** cambian si cambia el mínimo de minutos o el conjunto de centrales.
- **Métricas no ajustadas por posesión:** los equipos que defienden más acumulan más tackles y despejes.
- La definición exacta de cada métrica (por ejemplo, qué cuenta como "error" o "recuperación") depende del proveedor. Documéntala aquí cuando se elija la fuente.

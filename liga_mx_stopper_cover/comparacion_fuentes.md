# Comparación de fuentes de datos · Centrales Liga MX, Apertura 2026 (fase regular)

Revisión: 2026-11-17. Todavía no se ha descargado ningún dato ni se ha gastado ninguna petición.

**Cómo se verificó.** La red de esta sesión bloquea los dominios de todos los proveedores (api-football.com, sportmonks.com, thestatsapi.com, football-data.org), así que no se pudo abrir su documentación ni probar sus endpoints. Todo lo de abajo sale de buscadores que citan la documentación o las páginas oficiales. Nivel de evidencia:
- **✔︎** confirmado en documentación o página oficial (citada por el buscador)
- **~** mencionado solo en material de marketing, blogs o terceros, o con nombre de campo no confirmado
- **✘** no existe, o no se encontró en la documentación
- **?** no se pudo verificar

## 1. Cobertura de métricas

| Métrica | API-Football | Sportmonks | TheStatsAPI | football-data.org | fbplot.com |
|---|---|---|---|---|---|
| player / team / position / minutes | ✔︎ `games.minutes`, `games.position` | ✔︎ minutos (`CUMULATIVE_MINUTES_PLAYED`, minutos por partido) | ✔︎ `minutes_played`, `position` (en el endpoint por partido) | ✘ sin estadísticas por jugador | ? |
| tackles_won | ~ solo `tackles.total` (intentos, **no ganados**) | ✔︎ Tackles (tipo 78); "tackles ganados" no está confirmado | ~ hay categoría "defending"; campo exacto no confirmado | ✘ | ~ tackles |
| aerials_won | ✘ | ✔︎ Aerials Won (tipo 107) | ? | ✘ | ✘ |
| clearances | ✘ | ✔︎ Clearances (tipo 101) | ~ `clearances` aparece en el ejemplo del endpoint por partido | ✘ | ~ |
| interceptions | ✔︎ `tackles.interceptions` | ✔︎ Interceptions | ~ | ✘ | ~ |
| duels_won | ✔︎ `duels.won` | ✔︎ Duels Won (tipo 106) | ~ categoría "duels" | ✘ | ✘ |
| dribbled_past | ✔︎ `dribbles.past` | ✔︎ Dribbled Past (tipo 110) | ? | ✘ | ✘ |
| pass_completion_pct | ~ `passes.accuracy` (en el endpoint de temporada podría ser un conteo y no un %; hay que verificarlo) | ~ "Accurate Passes Percentage" (página del producto); ID no confirmado. Alternativa: calcularlo con Accurate Passes (tipo 116) / Passes | ~ "pass accuracy" (blog) | ✘ | ✘ |
| recoveries | ✘ | ✔︎ `BALL_RECOVERY` | ? | ✘ | ~ |
| errors | ✘ | ✔︎ Error Lead To Goal (tipo 571) y Error Lead To Shot | ? | ✘ | ✘ |
| **Total (de 9)** | **4–5** (falta aerials, clearances, recoveries, errors; tackles_won solo aproximado) | **9** (pass % y tackles *ganados*: confirmar en `/v3/core/types`) | **≥3 confirmadas, resto ?** | **0** | **≤4, sin descarga** |

## 2. Condiciones prácticas

| Criterio | API-Football | Sportmonks | TheStatsAPI | football-data.org | fbplot.com |
|---|---|---|---|---|---|
| ¿Cubre Liga MX? | ? (no se encontró la página de cobertura; se suele usar el ID 262, sin verificar) | ✔︎ tiene página propia de la "Liga MX API" | ✔︎ página de la liga; `competition_id=comp_298265` | ✘ no aparece en el plan gratis (12 competiciones, sobre todo europeas) | ? (según tú, sí) |
| ¿Apertura 2026 (temporada actual)? | ? Se dice que el plan gratis solo da temporadas recientes o pasadas; no confirmado para 2026 | ✔︎ la prueba es del producto completo | ✔︎ dice "todas las temporadas" en todos los planes | — | ? |
| ¿Separa fase regular de liguilla? | ~ `round` del tipo "Regular Season - N" en fixtures (nombre por confirmar) | ~ los fixtures tienen `stage`/`round`; se suma por partido filtrando por stage | ✔︎ `stage=regular` / `stage=playoff` en el endpoint de stats | — | ? |
| ¿Totales por jugador + minutos? | ✔︎ `/players` (temporada, mezcla fases) o `/fixtures/players` (por partido) | ✔︎ estadísticas por partido (lineups.details) y por temporada | ✔︎ `/players/{id}/stats` (temporada, con filtro de stage) | ✘ | ✘ sin CSV ni API |
| Plan gratis / prueba | Gratis: 100 peticiones/día (se reinicia 00:00 UTC), 10–30 por minuto según la fuente | Prueba de 14 días al suscribirse a un plan pagado (una sola prueba por cuenta). **No está claro si pide tarjeta** (su FAQ se contradice). Después: plan Starter (5 ligas) | Prueba de 7 días; después desde ~50 USD/mes | Gratis: 10 peticiones/min; sin estadísticas por jugador | Gratis, solo web |
| Términos de uso | Restricciones de datos de terceros; puede bloquear cuentas por mal uso. No hay cláusula explícita de uso personal o académico | "Personal and non-commercial use" para el material del sitio; la cuenta no se puede compartir | ? (existe /terms; no se pudo leer) | Términos claros, pero no sirve aquí | Sin descarga: copiar a mano no escala |

## 3. Otras fuentes revisadas

| Fuente | Resultado |
|---|---|
| iSports API | El endpoint por partido trae `aerialWon`, `clearances`, `interception`, `playingTime` y `errorLeadToGoal`, pero su doc dice que solo cubre "some top leagues" y partidos de la última semana. Liga MX no confirmada. Descartada. |
| FootyStats API | Prueba gratis solo con la Premier League; Liga MX requiere plan pagado (desde £29.99/mes). Campos defensivos por jugador no confirmados. Descartada. |
| FBref, y scraping de Sofascore, WhoScored o FotMob | Descartadas por instrucción. |

## 4. Decisión

**Elegida: Sportmonks (prueba de 14 días).**

1. (a) Es la única con evidencia documentada de las 9 métricas, incluidas las 4 del rol Cover (dribbled past, recuperaciones, errores, % de pase) que API-Football no tiene.
2. (b) Cubre la Liga MX de la temporada actual. La fase regular se separa sumando estadísticas por partido y filtrando por stage o round.
3. (c) La prueba de 14 días alcanza de sobra para una descarga única (unos 153 partidos de fase regular, decenas de peticiones con paginación). Pero **es una prueba de un plan pagado**: necesita tu autorización y que la canceles antes del día 14.
4. (d) Sus términos hablan de uso personal y no comercial. La cuenta es individual y los datos no se pueden redistribuir.
5. Respaldo si no quieres registrarte en Sportmonks: TheStatsAPI tiene el mejor filtro de fase (`stage=regular`), pero no está confirmado que tenga aerials, recuperaciones ni errores. API-Football (gratis) obliga a la versión reducida: Cover se queda en dribbled past + % de pase, y Stopper sin aerials ni clearances.

## Fuentes

- Sportmonks, tipos de estadística de jugador: https://docs.sportmonks.com/football/definitions/types/statistics/player-statistics
- Sportmonks, estadísticas agregadas (Duels Won 106): https://www.sportmonks.com/glossary/aggregated-stats/
- Sportmonks, Errors leading to goal (571): https://www.sportmonks.com/glossary/errors-leading-to-goal/
- Sportmonks, Liga MX API: https://www.sportmonks.com/football-api/liga-mx-api
- Sportmonks, planes y prueba: https://www.sportmonks.com/football-api/plans-pricing · FAQ: https://www.sportmonks.com/faq/
- Sportmonks, términos: https://www.sportmonks.com/terms-of-service/
- API-Football, precios: https://www.api-football.com/pricing · términos: https://www.api-football.com/terms
- API-Football, estadísticas por partido (curso de Educative): https://www.educative.io/courses/getting-soccer-data-with-api-football-in-javascript/players-statistics
- TheStatsAPI, Liga MX: https://www.thestatsapi.com/football/league/liga-mx
- TheStatsAPI, guía de stats (stage=regular): https://www.thestatsapi.com/docs/guides/player-and-team-stats
- TheStatsAPI, player stats por partido: https://www.thestatsapi.com/docs/api-reference/matches/player-stats
- football-data.org, políticas: https://docs.football-data.org/general/v4/policies.html
- football-data.org, límites del plan gratis (TheStatsAPI, competidor): https://www.thestatsapi.com/blog/football-data-org-free-tier-limits-2026
- iSports API, player stats por partido: https://www.isportsapi.com/docs.html?id=40
- FootyStats API: https://footystats.org/api

# Prompt para Grok · formaciones y datos faltantes

Copia el texto de abajo y adjunta `formaciones.csv` y `centrales_apertura2026_j16.csv`.

---

Te adjunto dos archivos de la **Liga MX, Apertura 2026, fase regular (jornadas 1–16, partidos hasta el 14 nov 2026)**. Necesito dos cosas.

## PARTE 1 · Formación defensiva de cada equipo (`formaciones.csv`)

Para cada uno de los 18 equipos, investiga con qué línea defensiva jugó **la mayoría de los partidos** del torneo: **2 centrales** (línea de 4) o **3 centrales** (línea de 3 o de 5). Fuentes sugeridas: alineaciones de FotMob, ESPN o Sofascore de cada partido, o crónicas de los partidos.

Devuélveme `formaciones.csv` con estas columnas:
- `team`: igual que en el archivo, sin cambiar los nombres.
- `centrales`: 2 o 3.
- `origen`: de dónde lo sacaste. Ejemplo: "FotMob alineaciones J1–J16: 12 de 16 partidos con línea de 3".
- `titulares`: nombres de los 2 o 3 centrales que más partidos jugaron **de inicio como centrales**, separados por " / " y escritos igual que en la columna `player` del otro CSV.
- `nota`: solo si aplica. Por ejemplo, si un jugador del CSV en realidad jugó de mediocampista o de lateral, si hubo cambio de técnico y de esquema, o si un central se lesionó.

Pon atención especial a estos equipos, donde mi estimación por minutos puede ser rotación y no línea de 3: **Atlante, Cruz Azul, Guadalajara, Necaxa y Toluca**. También necesito saber si **Luis Romo** (Guadalajara) jugó de central o de mediocampista.

## PARTE 2 · Llenar celdas vacías en `centrales_apertura2026_j16.csv`

Estos centrales con 450 minutos o más tienen celdas vacías. Llénalas con datos de **FotMob** (página del jugador → Stats, temporada 2026/2027, solo Liga MX, a J16):

| Jugador | Columnas vacías |
|---|---|
| Gilberto Sepúlveda (FC Juárez) | interceptions, clearances, aerials_won, dribbled_past, pass_completion_pct, recoveries |
| Diego Reyes (Querétaro) | tackles, interceptions, clearances, aerials_won, duels_won_pct, blocked_shots, dribbled_past, pass_completion_pct, recoveries, fouls_committed |
| Carlos Salcedo (Monterrey) | lo mismo que Diego Reyes |
| Luis Romo (Guadalajara) | tackles, duels_won_pct, blocked_shots, fouls_committed |
| Bruno Méndez (Toluca) | tackles, duels_won_pct, blocked_shots, fouls_committed |
| Carlos Villanueva (Querétaro) | tackles, duels_won_pct, blocked_shots, fouls_committed |
| Santiago Ramos (América) | duels_won_pct, blocked_shots, fouls_committed |
| Felipe Sánchez (Santos Laguna) | aerials_won, pass_completion_pct |
| Efraín Orona (Santos Laguna) | aerials_won, pass_completion_pct |
| Eduardo Tercero (Atlante) | dribbled_past, recoveries |
| Jackson Porozo (Tijuana) | dribbled_past |
| Gonzalo Piovi (Cruz Azul) | blocked_shots |

En FotMob: tackles = Tackles · interceptions = Interceptions · clearances = Clearances · aerials_won = Aerial duels won · duels_won_pct = Duels won % · blocked_shots = Blocked shots · dribbled_past = Dribbled past · pass_completion_pct = Successful passes % · recoveries = Recoveries · fouls_committed = Fouls committed.

Reglas:
1. **Solo llena celdas vacías.** No cambies ningún valor que ya exista, ni filas ni columnas.
2. **No inventes ni estimes.** Si no lo encuentras, déjalo vacío. No pongas 0 si no lo sabes.
3. Los conteos son totales del torneo; los porcentajes van de 0 a 100, sin el signo %.
4. Si los minutos de FotMob no coinciden con la columna `minutes`, no la cambies: anota el valor en `minutes_fotmob`.
5. Si un dato no es de FotMob, dilo en `fuente_extra`.

## Qué me devuelves

1. `formaciones.csv` completo, con las columnas de la Parte 1.
2. `centrales_apertura2026_j16.csv` completo, con las celdas llenadas.
3. Una nota corta con la fecha de consulta, qué celdas no encontraste y cualquier dato dudoso.

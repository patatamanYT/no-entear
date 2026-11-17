# Prompt para llenar plantilla_centrales.csv con otra IA

Copia el texto de abajo y adjunta `plantilla_centrales.csv`.

---

Llena el CSV adjunto con los **defensas centrales** de la **Liga MX, Apertura 2026, SOLO fase regular** (sin liguilla ni repechaje), con datos acumulados hasta la fecha de hoy.

Reglas:
1. Una fila por jugador. Si cambió de equipo durante el torneo, suma sus números en una sola fila y pon `team` como "Equipo1 / Equipo2".
2. Solo jugadores cuya posición habitual sea defensa central. En `position` escribe exactamente `CB`. En `phase` escribe `Regular`.
3. Los conteos van como **totales del torneo**, no por partido ni por 90:
   - `minutes`: minutos jugados
   - `tackles_won`: entradas ganadas
   - `aerials_won`: duelos aéreos ganados
   - `clearances`: despejes
   - `interceptions`: intercepciones
   - `duels_won`: duelos totales ganados
   - `dribbled_past`: veces que lo regatearon
   - `recoveries`: recuperaciones de balón
   - `errors`: errores que terminaron en tiro o gol
4. `pass_completion_pct`: porcentaje de pases acertados, entre 0 y 100.
5. **No inventes ni estimes.** Si no encuentras un dato verificable, deja la celda vacía. No pongas 0 si no lo sabes.
6. Agrega al final una columna `fuente` con el sitio y la URL de donde sacaste los números de cada jugador. Usa la misma fuente para todos si es posible, para que las métricas sean comparables.
7. Al final dime: qué fuente usaste, hasta qué jornada llegan los datos, la fecha de consulta, y qué métricas no encontraste.

Devuélveme solo el CSV completo (separado por comas, con encabezados) y la nota del punto 7.

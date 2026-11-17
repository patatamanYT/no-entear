# Prompt para agregar columnas extra al CSV (FotMob)

Copia el texto de abajo y adjunta `centrales_apertura2026_j16.csv`, el CSV que ya llenó la otra IA.

---

Te adjunto un CSV con 76 defensas centrales de la **Liga MX, Apertura 2026, fase regular**. Ya tiene minutos y varias métricas defensivas sacadas de **FotMob** (página de cada jugador, pestaña Stats, temporada 2026/2027).

Agrega estas **5 columnas nuevas** al final, con los valores de FotMob de cada jugador:

| Columna | En FotMob se llama | Sección | Tipo |
|---|---|---|---|
| `tackles` | Tackles | Defending | total del torneo (número entero) |
| `blocked_shots` | Blocked shots | Defending | total del torneo (número entero) |
| `fouls_committed` | Fouls committed | Defending | total del torneo (número entero) |
| `duels_won_pct` | Duels won % | Possession | porcentaje 0–100 sin el signo % (ej. 60.9) |
| `aerials_won_pct` | Aerial duels won % | Possession | porcentaje 0–100 sin el signo % (ej. 66.7) |

Reglas:
1. **No cambies ni borres nada de lo que ya está en el CSV**: ni filas, ni columnas, ni valores, ni su orden.
2. Usa **la misma página de FotMob** de la columna `fuente` de cada jugador. Si la URL no funciona, busca al jugador en FotMob y anota la URL correcta en una columna nueva `fuente_extra`.
3. **No inventes ni estimes.** Si no encuentras un dato, deja la celda vacía. No pongas 0 si no lo sabes.
4. Los datos deben ser de **la misma fecha de corte que el resto del CSV** (jornada 16, partidos hasta el 14 nov 2026). Si FotMob ya incluye la jornada 17, dilo en la nota.
5. Comprobación: en cada fila revisa que `minutes` coincida con los minutos que muestra FotMob. Si no coincide, **no cambies `minutes`**; anota el valor de FotMob en una columna nueva `minutes_fotmob`.

Ejemplo de referencia (Joaquim, Tigres): tackles = 15, blocked_shots = 9, fouls_committed = 10, duels_won_pct = 60.9, aerials_won_pct = 66.7.

Al final dame:
- El CSV completo, separado por comas y con encabezados, con todas las columnas originales más las nuevas.
- Una nota corta con: la fecha de consulta, hasta qué jornada llegan los datos nuevos, cuántos jugadores quedaron con alguna celda nueva vacía (y quiénes), y en qué jugadores no coincidieron los minutos.

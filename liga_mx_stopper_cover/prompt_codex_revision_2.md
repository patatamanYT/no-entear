# Correcciones para Codex · Revisión 2 (ordenar equipos por goles recibidos)

Pega el texto de abajo en Codex. Se suma a la revisión 1, no la reemplaza.

---

Un cambio más para la **escena de parejas (escena 6)**: ordenar las 18 tarjetas por **goles recibidos**.

## 1. Busca el dato

- **Qué:** los **goles en contra (GC)** de cada uno de los 18 equipos en la **Liga MX, Apertura 2026, fase regular, jornadas 1 a 16**, hasta los partidos del 14 de noviembre de 2026. La J17 todavía no se juega, así que no la incluyas.
- **Fuentes:** la tabla general de **FotMob** (columna de goles en contra) y **una segunda fuente** para comparar: ESPN, el sitio oficial ligamx.net o la tabla de Fox Sports o Mediotiempo.

**Reglas:**
1. **No inventes ni estimes.** Si no encuentras el número de un equipo, déjalo vacío y avísame.
2. Comprueba que cada equipo tenga **16 partidos jugados (PJ)**. Si alguno tiene 15 o 17 (partido pendiente o adelantado), anótalo y no lo ordenes junto a los demás sin avisar.
3. Si las dos fuentes no coinciden en algún equipo, usa FotMob y anota la diferencia.
4. Usa los nombres de equipo **exactamente como vienen en `datos_animacion.json`** (por ejemplo "UANL", "UNAM", "Atlético San Luis").

## 2. Guarda el dato

- Agrega a cada equipo en `datos_animacion.json` los campos `goles_en_contra` (entero) y `partidos_jugados` (entero).
- Agrega un campo general `fuente_goles_en_contra`, con las dos fuentes y la fecha de consulta.
- Genera también **`goles_en_contra.csv`** con las columnas `team,partidos_jugados,goles_en_contra,fuente_1,valor_1,fuente_2,valor_2,nota`. Lo necesito para actualizar la imagen fija.

## 3. Cambia la escena 6

- **Orden:** de **menos a más goles recibidos**, de izquierda a derecha y de arriba abajo. Si hay empate, desempata por orden alfabético del equipo.
- **Número en la tarjeta:** pon los goles recibidos en grande y en Bold arriba a la derecha (por ejemplo "**14** GC"). Que sea lo que más destaque después del nombre del equipo.
- **Color:** cada tarjeta mantiene el color de su veredicto, para que se vea el patrón.
- **Título:** "¿Los que se complementan reciben menos goles?". Subtítulo: "Ordenados de menos a más goles recibidos · J1–J16".
- **Animación:** las tarjetas aparecen en ese orden, de la que menos recibe a la que más.
- **Si lo partes en dos pantallas de 9:** la primera tiene los 9 que menos reciben y la segunda los 9 que más. Ya no se separan por "firmes" y "en el límite"; el * de los veredictos se queda.
- **Al final, una línea pequeña:** "Correlación, no causa: los goles recibidos dependen de todo el equipo."
- **Fuente:** agrega la de los goles en contra a la línea de fuente de esa escena.

## Entrega

Antes del render completo, mándame:
1. `goles_en_contra.csv`.
2. Captura del último cuadro de la escena 6.

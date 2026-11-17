# Prompt para Codex · Animar "Choque vs Cobertura" (Liga MX Apertura 2026)

Pega el texto de abajo en Codex y súbele todo el contenido de `paquete_codex.zip`.

---

## Objetivo

Haz un **video animado (MP4) y un GIF** del análisis "Choque vs Cobertura" de los centrales de la Liga MX, Apertura 2026, fase regular, jornadas 1–16, para publicarlo en redes. Todo el texto en **español**.

## Archivos que te doy

| Archivo | Qué es |
|---|---|
| `datos_animacion.json` | **Fuente única de datos.** 56 jugadores (`choque`, `cobertura`, zona, perfil, escudo, percentil por métrica), 18 equipos (línea de 2 o 3, titulares, veredicto, `en_el_limite`), el par del radar, la paleta, las tipografías, la fórmula y los avisos. |
| `escudos/*.png` | Escudo de cada club (la ruta viene en el JSON). |
| `referencia/1_choque_vs_cobertura.png` | Cómo debe verse el **cuadro final** de la escena de dispersión. |
| `referencia/2_parejas_por_equipo.png` | Cómo debe verse el cuadro final de la escena de parejas. |
| `referencia/3_*.png`, `referencia/4_*.png` | Cómo deben verse los radares al final. |
| `referencia/5_texto_post_y_formula.md` | El texto del post (para los títulos de cada escena). |
| `scripts_estilo/*.py` | Los scripts que generaron las imágenes. Úsalos **solo como referencia** de colores, tamaños, tipografías y la forma de las cajas y píldoras. **No recalcules** nada con ellos. |

## Reglas (importantes)

1. **No inventes ni recalcules datos.** Usa los valores del JSON tal cual: posiciones, percentiles, zonas, perfiles y veredictos. Si algo no está en el JSON, no lo muestres.
2. Mantén el **estilo de las imágenes de referencia**:
   - fondo crema `#f3f0e8` con panel redondeado;
   - Inter para el texto y JetBrains Mono para las notas;
   - título grande "Choque **vs** Cobertura" con el "vs" en gris;
   - zonas con caja redondeada y etiqueta tipo píldora;
   - escudos sobre un disco blanco;
   - nombres en negrita;
   - si no están Inter o JetBrains Mono, usa DejaVu Sans y DejaVu Sans Mono.
3. Formato vertical para redes: **1080 × 1350 px (4:5), 30 fps**, de 35 a 45 s en total. Exporta también un **GIF** más ligero (≤ 15 MB; puedes bajar a 540 px de ancho y 15 fps).
4. Que los nombres no se encimen ni queden tapados por las píldoras (en la referencia, la píldora naranja va **debajo** de su caja).
5. Pon **siempre visible una línea de fuente** abajo, en letra pequeña y monoespaciada: el campo `fuente` del JSON.
6. Los equipos con `en_el_limite: true` llevan " *" en su veredicto, y al final de esa escena aparece la nota: "* cambia si un titular se mueve ±3 puntos".
7. Respeta los avisos del JSON (Porozo sin "veces regateado").

## Escenas (guion)

**1. Portada (≈3 s).** Fondo crema. Entra la línea superior "LIGA MX APERTURA 2026 · CENTRALES" (efecto máquina de escribir en la monoespaciada). Después aparece el título "Choque vs Cobertura": "Choque" y "Cobertura" se deslizan desde los lados y el "vs" aparece en gris al final. Debajo, el subtítulo.

**2. Qué es cada rol (≈5 s).** Dos tarjetas lado a lado:
- 🛑 **Choque:** "sale a ganar el balón", con la lista `formula.choque`.
- 🧠 **Cobertura:** "casi nunca lo superan y conserva el balón", con la lista `formula.cobertura`.

Cada tarjeta entra con un desvanecido y un desplazamiento hacia arriba. Abajo, la `formula.nota` en monoespaciada.

**3. La dispersión se construye (≈12 s).**
- Se dibuja el panel, los ejes (CHOQUE → / COBERTURA →, de 0 a 100) y las líneas punteadas en 50.
- Las tres cajas de zona aparecen una por una con su píldora.
- Los 56 escudos salen del **centro (50, 50)** y viajan a su posición con *ease-out*, escalonados unos 40 ms.
- Al llegar cada escudo, su nombre aparece con un desvanecido.
- **El cuadro final debe verse como `referencia/1_choque_vs_cobertura.png`.**

**4. Recorrido por las zonas (≈9 s).** Sobre la dispersión, resalta una zona a la vez: la zona activa al 100% y el resto atenuado al 25%. Muestra un texto corto arriba:
- **Choca y cubre:** los jugadores con `zona = choca_y_cubre`. Los escudos de esa zona hacen un pequeño "pulso".
- **Cubre, poco choque:** "Necesitan un central de choque al lado".
- **Choca, poca cobertura:** "Necesitan un central de cobertura al lado".

**5. Radares (≈7 s).** Joaquim (morado) contra Eduardo Bauermann (azul), en el estilo de `referencia/3` y `referencia/4`:
- Primero el radar de **Choque**: los polígonos crecen desde el centro hasta sus percentiles.
- Luego cambia al radar de **Cobertura**, con un barrido o un desvanecido cruzado.
- Abajo va la leyenda: punto de color, nombre en letra delgada y "· Apertura 26".
- Los valores salen de `jugadores[*].percentiles`.

**6. ¿Se complementan? (≈8 s).**
- Rejilla de 18 tarjetas como en `referencia/2_parejas_por_equipo.png`, ordenadas por veredicto como en la imagen.
- Las tarjetas aparecen volteándose (*flip*) en cascada, fila por fila.
- Después aparece la píldora del veredicto de cada una (con " *" si `en_el_limite`).
- Cierra con la nota del asterisco.

**7. Cierre (≈2 s).** "Fórmula en los comentarios 👇" y la línea de fuente.

## Técnica sugerida

- **Python 3 + matplotlib** (`FuncAnimation` o cuadros PNG) con **ffmpeg** para el MP4 (`libx264`, `yuv420p`, `-crf 18`), y GIF con paleta (`palettegen` / `paletteuse`). También vale **Manim** si te es más cómodo, pero el resultado debe verse igual que las referencias.
- Interpolación con *easing* (ease-out cúbico) para movimientos y escalas; nada lineal ni brusco.
- El código debe estar organizado por escenas (una función por escena) y tener la duración de cada escena en constantes al inicio.

## Entregables

1. `animar.py`: genera todo con un solo comando: `python animar.py --json datos_animacion.json --out choque_vs_cobertura.mp4`.
2. `choque_vs_cobertura.mp4` (1080×1350, 30 fps).
3. `choque_vs_cobertura.gif`.
4. Un `README_animacion.md` corto con cómo correrlo, las dependencias y la duración de cada escena.

Antes de entregar, revisa cuadro por cuadro el final de cada escena:
- que ningún nombre esté tapado;
- que los números coincidan con el JSON;
- que el último cuadro de la escena 3 se vea como la imagen de referencia.

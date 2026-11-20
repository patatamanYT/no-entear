# Referencias Opus · qué se puede mejorar en la v2

Fecha: 20 nov 2026. Este documento es una propuesta. No se ha cambiado el video.

## Catálogos usados

No existe un único «Awesome Opus»: hay varios catálogos comunitarios con ese nombre. Se revisaron dos.

- **yihui-dev/awesome-opus5-5-videos** (703 prompts en `data/videos.json`, con autor y enlace a la publicación original). Las imágenes de vista previa están en media.skillry.dev, que la red de esta sesión bloquea. De este catálogo solo se leyeron los prompts.
- **X-RayLuan/awesome-opus-5-5-video-prompts** (84 entradas, 51 con clip local). De aquí se vieron videos y se extrajeron fotogramas.

Se filtraron los 703 prompts por fútbol, datos, cronología y tipografía sobre foto. La mayoría son lanzamientos de producto o 3D y no sirven para este Reel. Ningún prompt trata de fútbol.

Los derechos de cada video, prompt y música son de su creador; la licencia MIT solo cubre la documentación de los catálogos. De aquí no se reutiliza ningún archivo: solo se adaptan principios con el material propio del Reel.

## Referencias útiles

| Referencia | Fuente | Qué se observó o qué dice | Qué se adapta |
|---|---|---|---|
| Historia de China en línea | WY (@akokoi1), [publicación](https://x.com/akokoi1/status/2102583898865873225) | **Observado** en 8 fotogramas: cada época es un plano con su nombre grande arriba a la izquierda, una etiqueta roja con el año y una sola línea de texto abajo. Un mismo personaje se queda siempre sobre la misma línea de suelo. | En la cronología, una fecha grande por momento y una línea de texto. La línea de base no se mueve entre momentos. |
| Historia de la IA en código | Chubby (@kimmonismus), [publicación](https://x.com/kimmonismus/status/2102844654169575547) | **Observado**: la ficha «the» aparece en todos los capítulos como protagonista. Arriba a la izquierda hay un sello de fecha pequeño y abajo un subtítulo de una línea con una sola palabra en el color de acento. | Un elemento que atraviesa varias escenas: el marcador de puntos. Para cuando exista voz: subtítulos con una sola palabra resaltada. |
| Línea de vida en video | @niirajrshah, [publicación](https://x.com/niirajrshah/status/2104551261270163739) | **Solo prompt**: «One scene per moment. Show the year large and the moment in one line, and move between them.» El mismo prompt pide revisar una hoja de contactos antes de renderizar. | Lo mismo que la primera referencia. La revisión por hoja de contactos ya se hace con las tiras de fotogramas. |
| Reel con un punto naranja | @threeaus y @rossaxbt ([1](https://x.com/threeaus/status/2105152377057886343), [2](https://x.com/rossaxbt/status/2107121188027707651)) | **Solo prompt**: «A single orange circle … is the through-line and the cut»; «motion that isn't connected to an element already on screen» está prohibido. | El hilo conductor y el corte que nace de un elemento que ya está en pantalla. No se adapta el naranja ni el estilo de producto. |
| Historia con sonido | @adrianduta96, [publicación](https://x.com/adrianduta96/status/2109187815195992248) | **Solo prompt**: «make every sound match a movement you can see». | Que cada golpe de `marca.wav` caiga sobre una llegada visible. |

**Descartadas:**
- El collage de papel de Ring Hyacinth: choca con la foto documental y la paleta contenida.
- Los lanzamientos de producto con cursor, cristal líquido o bento: es otro género.
- Las piezas 3D: el Reel no usa 3D.

## Propuestas, de más barata a más ambiciosa

### 1. Mover el primer golpe sonoro a 1.53 s

- **Hallazgo en el proyecto** (tira de fotogramas en 0.3, 0.6 y 0.9 s): el golpe de 0.63 s no coincide con ningún cambio en pantalla. Los otros dos sí: el de 4.875 s cae cuando aparece el sexto «G» y el de 20.92 s cuando aparece «14 puntos».
- **Entrada → acción → salida:** la foto de la afición y el «1» → a 1.53 s entran a la vez la foto del festejo y el «18», y ahí suena el golpe → «puntos en 6 victorias».
- **Guion:** «Luego ganó seis partidos seguidos».
- **Costo:** cambiar `CUES[0]` en `reel.py` de 630 a 1530. Es la primera llegada fuerte del gancho.

### 2. Cronología de la escena 8 con un momento por golpe

- **Hoy:** tres filas visibles a la vez, aunque ya con menos texto que en la v1.
- **Propuesta:**
  - **Entrada:** fecha grande en Barlow Condensed Bold (unos 150 px, salvia) con una línea de texto debajo, sobre el filete fijo.
  - **Acción:** la fecha cambia en el mismo lugar, como un marcador: AGO → 13 SEP → NOV. La línea de texto se reemplaza en cada cambio.
  - **Salida:** NOV con «La afición ya la corea.» se queda en pantalla hasta el corte a la tribuna.
- **Guion:** «Tras ganarle a Juárez, el tema sonó en el Corona» corresponde a 13 SEP; «En noviembre, la afición ya lo coreaba» corresponde a NOV. La voz no menciona agosto, así que AGO ocupa el primer segundo, mientras se lee el título.
- **Límites:** los tiempos son provisionales hasta que exista la grabación de voz. Agrega una animación de cambio de texto; no hacen falta material ni datos nuevos.

### 3. El marcador como hilo conductor (escenas 1 → 2 y 5)

- **Hoy:** cada escena dibuja sus cifras desde cero, y los cortes entre la 1 y la 2 son secos.
- **Propuesta (tramo mínimo, solo escenas 1 → 2):**
  - **Entrada:** el «18» salvia de la escena 1.
  - **Acción:** al final de la escena 1, el «18» se encoge y viaja hasta el lugar de «18 de 18 puntos» de la escena 2. Es un corte por coincidencia, no un fundido.
  - **Salida:** la fila de seis «G» se llena.
- **Guion:** «Luego ganó seis partidos seguidos. / Nunca lo había hecho.»
- **Después**, si funciona: el mismo «18» abre el recuento de la escena 5 (18 → 14).
- **Límites:** el «18» tiene que vivir en una capa que cruce el corte entre los grupos 01 y 02. Se hace en `reel.py` con fotogramas clave de posición y escala, sin datos nuevos. Hay que revisarlo en movimiento, no solo en fotogramas.

### 4. Más adelante, con voz: una palabra resaltada en subtítulos

Aplica solo cuando exista la toma de voz y se decida subtitular. Una línea por frase, con una sola palabra en salvia: por ejemplo «esperanza» en el cierre. No se propone ahora: sin voz no hay tiempos reales, y el texto en pantalla ya funciona sin sonido.

## Siguiente acción

Aplicar la propuesta 1, que cuesta una línea. Si apruebas la 2 o la 3, implementar primero solo ese tramo, revisarlo con tira de fotogramas y una exportación corta, y exportar una v3 sin tocar la v2.

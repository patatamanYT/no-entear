---
name: sonido
description: Selecciona efectos de una biblioteca local y ajusta mezcla y sincronía para videos. Úsala para diseñar golpes, transiciones, ambientes o música bajo voz; requiere recursos propios o con permiso de uso.
---

# Sonido con intención

Identifica el video, fps, duración y biblioteca disponible. Esta skill no incluye audios. Usa la biblioteca autorizada del usuario y respeta las reglas del proyecto sobre su origen (por ejemplo, una carpeta o script obligatorio). No inventes rutas ni presupongas que existe un script.

1. Fija primero eventos visuales y narrativos. Elige efectos por causa perceptible o intención narrativa; evita ruido por cada palabra. Un ambiente continuo puede ser intencional.
2. Busca candidatos en el catálogo disponible. Nombres y etiquetas no prueban cómo suenan: preescucha antes de elegir. Si no puedes escuchar, presenta la selección como provisional.
3. Copia solo los recursos usados a la carpeta del proyecto. Conserva la biblioteca original y documenta origen, licencia y cambios. No redistribuyas packs comprados por el hecho de tenerlos localmente.
4. Alinea el ataque o pico del efecto con el impacto, no necesariamente el inicio del archivo. Calcula inicio = cuadro del impacto / fps − tiempo del pico. Si resulta negativo, ajusta el montaje o recorta una copia sin destruir el original. Respeta las colas y evita clics de corte.
5. Mantén inteligible la voz; automatiza música y efectos en remates y pausas. Mide el conjunto, no solo pistas aisladas. En Remotion evita duplicar voz o montar un efecto fuera de su duración.
6. Reproduce y mide el export final. Con FFmpeg, `ffmpeg -i video.mp4 -af ebur128=peak=true -f null -` permite leer LUFS y true peak. Usa el objetivo del proyecto; si falta, propone uno como criterio de trabajo, no regla universal de plataforma. Un pico correcto no garantiza mezcla agradable.

Entrega archivos usados, eventos de sincronía, mediciones y pendientes reales. No afirmes haber escuchado si solo analizaste métricas. Descargar o generar nuevos recursos requiere que esté dentro del encargo; prioriza lo existente.

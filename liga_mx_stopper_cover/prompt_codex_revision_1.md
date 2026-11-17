# Correcciones para Codex · Revisión 1 (Reels, versión "lean")

Pega el texto de abajo en Codex y súbele el `paquete_codex.zip` actualizado: trae el JSON nuevo y la carpeta `fuentes/`.

---

Gracias, va bien encaminado, pero está **demasiado amontonado**. Quiero una versión más **limpia y ligera ("lean")**. Cambios:

## 1. Formato: Reels

- Se queda en **1080 × 1920, 30 fps**, para Reels.
- Respeta las **zonas seguras de Reels**. Nada importante (títulos, nombres, píldoras, ejes, veredictos) en:
  - los **250 px de arriba**;
  - los **420 px de abajo** (ahí van el texto del post y los botones);
  - los **120 px del lado derecho** en la mitad de abajo.
- El área útil es más o menos **x 60–960, y 250–1500**. Dentro de esa área, **usa todo el espacio**: que las gráficas sean más grandes y no se queden encogidas en el centro.
- La línea de fuente puede ir pequeña justo encima de los 420 px de abajo (y ≈ 1480).

## 2. Tipografías

- Ahora el ZIP trae la carpeta `fuentes/` con **Inter** y **JetBrains Mono** (licencia OFL). Regístralas con `matplotlib.font_manager.fontManager.addfont(...)` o el equivalente en tu herramienta.
- Usa Inter para todo el texto (títulos en Bold o ExtraBold) y JetBrains Mono solo para la línea superior y la fuente. **No uses DejaVu.**

## 3. Escena de la dispersión: menos texto

- **Nombres:** solo para los jugadores con `etiqueta_visible: true` en el JSON (los 15 de las tres zonas). Los demás van **solo con su escudo**, sin nombre ni línea guía.
- **Escudos:** un poco más grandes que ahora, unos 44–48 px de diámetro con el disco blanco. Las cajas de zona deben verse cómodas, no saturadas.
- **Escena 4, recorrido por zonas:** en cada paso muestra **solo los nombres de la zona activa**, en tamaño grande. Las otras zonas y los demás escudos quedan atenuados al 25%.
- **Quita** de esta escena la nota de Porozo ("no tiene 'veces regateado'…"). Pásala a la escena final, en letra pequeña junto a la fuente.
- **Ejes:** solo 0, 50 y 100, en gris claro. Quita los números intermedios para que respire.

## 4. Escena de parejas: tarjetas más simples

- **Sin números en las tarjetas.** Quita la línea "Perfil · Ch xx · Cb xx" de cada jugador.
- **Cada titular:** un punto o cuadrito del color de su perfil, más su nombre. Nada más.
- **Perfiles:** usa `perfiles_simplificados` del JSON. "Equilibrado" y "Bajo" se muestran juntos como **"Sin perfil claro"** (gris `#a8a29e`). La leyenda queda en 4 elementos: Choque, Cobertura, Ambos y Sin perfil claro.
- **Cada tarjeta:**
  - escudo y nombre del equipo en Bold;
  - debajo, "Línea de 2" o "Línea de 3" en gris;
  - luego los titulares;
  - abajo, la píldora del veredicto.
- **Espacio:** que el nombre y los titulares nunca se encimen. Deja aire entre líneas (≥ 1.4 de interlineado).
- **Distribución:** 3 columnas × 6 filas que **ocupen toda el área útil** (250–1480 px de alto). Las tarjetas deben ser más altas que ahora.
- **Opcional, si queda mejor:** parte las 18 tarjetas en **dos pantallas de 9** (3×3) con una transición. La primera con los veredictos firmes (sin *) y la segunda con el resto.

## 5. Números en general

- **Solo enteros**, sin decimales. Ya vienen redondeados en el JSON nuevo.
- En los radares no hace falta mostrar números, solo los polígonos.

## 6. Ritmo

- Mantén los 45 s en total.
- Como hay menos texto en pantalla, puedes dar **un poco más de pausa al final de cada escena** (≈ 1 s quieto) para que se alcance a leer.

## Antes del render completo

Mándame **3 capturas**:
1. Último cuadro de la escena 3.
2. Un cuadro de la escena 4 con una zona activa.
3. Último cuadro de la escena 6.

Revisa tú mismo que:
- nada importante caiga en las zonas seguras;
- ningún nombre quede tapado;
- todos los números coincidan con el JSON.

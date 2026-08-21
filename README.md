# Generador Guepardo

Herramienta local para generar **Comunicados** del Proyecto Guepardo en ES
(master) → EN → PT-BR, con preview PNG automático, respetando el sistema de
diseño y las reglas editoriales del proyecto.

Primer entregable: el flujo de **Comunicado** completo, de punta a punta
(formulario → ES → preview → traducción EN/PT → 3 PNG). El flujo de
**Boletín** queda como siguiente paso (la pantalla inicial ya lo deja
marcado como "Próximamente").

## Requisitos

- Node.js 18+
- Una clave de la API de Anthropic (solo necesaria para el paso de
  traducción EN/PT; el ES y su preview funcionan sin ella)

## Instalación

```bash
npm install
npx playwright install chromium   # una sola vez, para renderizar los PNG
cp .env.example .env               # y completa ANTHROPIC_API_KEY
npm start
```

Abre `http://localhost:4173`.

## Flujo

1. Elige **Comunicado** en la pantalla inicial.
2. Llena el formulario (título, bajada, badge, bloques de contenido,
   vigencia, contacto de dudas, nota de cierre). Un bloque sin título ni
   viñetas se omite automáticamente del comunicado — la herramienta nunca
   rellena con texto genérico.
3. **Generar ES** — arma el HTML master en español y su preview PNG. Este
   es el punto de control humano: revisa el preview antes de continuar.
4. **Generar EN + PT** — traduce el ES ya aprobado (nunca antes de que lo
   apruebes) vía la API de Anthropic, aplicando las reglas de estilo por
   idioma, y renderiza los PNG de EN y PT-BR.
5. Descarga el HTML/PNG de cada versión, o el ZIP completo del comunicado.

Cada comunicado queda en `output/{fecha}-{slug}-{id}/` con
`comunicado_{es,en,pt}.html` y `preview_{es,en,pt}.png`.

## Assets

`/assets` trae el logo del guepardo y el wordmark "Lo Mejoramos Juntos"
(ES). Si faltan `we_improve_together_crop.png` o `melhoramos_juntos_crop.png`
(los wordmarks en inglés/portugués), el generador usa el wordmark en
español como respaldo y lo marca como advertencia en el resultado — nunca
falla en silencio. Coloca los archivos reales en `/assets` con esos nombres
para que EN/PT usen su propio wordmark.

## Notas técnicas

- El HTML final es un documento standalone (imágenes embebidas en base64),
  igual al patrón de las plantillas originales del proyecto.
- Antes de llamar a la API de traducción, los `<img>` en base64 (100KB+ y
  sin texto que traducir) se reemplazan por marcadores cortos; se
  restauran después con el asset correcto por idioma. Esto evita mandar
  binarios enormes al modelo y el riesgo de que los corrompa.
- El disclaimer de traducción AI en el footer de EN/PT se agrega de forma
  determinística en el backend (no se le pide al modelo que lo redacte),
  para garantizar texto y estilo consistentes.
- Si `PLAYWRIGHT_CHROMIUM_PATH` no está definida, Playwright usa el
  Chromium que descargó `npx playwright install` — solo hace falta
  definirla en entornos con un Chromium preinstalado en otra ruta.

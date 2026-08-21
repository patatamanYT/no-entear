const Anthropic = require('@anthropic-ai/sdk');
const { logoDataUri, wordmarkDataUri } = require('./assets');
const { escapeHtml } = require('../templates/comunicadoTemplate');

const PLACEHOLDER_LOGO = '__ASSET_LOGO__';
const PLACEHOLDER_WORDMARK = '__ASSET_WORDMARK__';

const DISCLAIMER = {
  en: 'This document was machine-translated from the Spanish original with AI assistance. In case of any discrepancy, the Spanish version prevails.',
  pt: 'Este documento foi traduzido automaticamente do original em espanhol com apoio de IA. Em caso de divergência, prevalece a versão em espanhol.',
};

const LANG_NAME = {
  en: 'inglés (EN corporativo, US-native)',
  pt: 'portugués (PT-BR corporativo)',
};

const SYSTEM_PROMPT = `Eres el traductor corporativo oficial del Proyecto Guepardo (Grupo Lamosa). Tu única tarea es traducir el texto visible de un documento HTML, preservando exactamente su estructura.

REGLAS GENERALES (obligatorias):
- Traduce el HTML completo manteniendo estructura, tags, atributos y estilos inline intactos. Solo cambia el texto que aparece entre tags (y en atributos visibles como "alt" o "title" si corresponde).
- Nunca alteres el significado, alcance, fechas, montos, responsables, condiciones ni el nivel de compromiso del texto fuente.
- No agregues ni omitas información.
- No traduzcas nombres propios de personas, ni las marcas "Proyecto Guepardo" / "Grupo Lamosa".
- Los marcadores literales __ASSET_LOGO__ y __ASSET_WORDMARK__ deben quedar EXACTAMENTE igual, en su misma posición dentro del atributo src. No los traduzcas, no los muevas, no los elimines.
- No agregues comentarios, explicaciones, notas ni bloques de código markdown (nada de \`\`\`). Responde ÚNICAMENTE con el HTML completo, empezando en "<!DOCTYPE html>" y terminando en "</html>".

REGLAS SEGÚN IDIOMA DESTINO:

Inglés (EN corporativo, US-native):
- Usa voz activa y fraseo idiomático, no traducción literal palabra por palabra.
- Evita repetir el mismo término en elementos de interfaz cercanos; varía con sinónimos cuando el inglés lo pide.

Portugués (PT-BR corporativo):
- Usa "estoque" en vez de "inventário".
- Usa travessão (—) para contraste condicional donde el español usa guion o dos puntos de contraste.
- Usa "Em caso de dúvidas" en vez de alternativas literales como "Em caso de perguntas".`;

function stripCodeFence(text) {
  const trimmed = text.trim();
  const fenced = trimmed.match(/^```(?:html)?\s*([\s\S]*?)\s*```$/i);
  return fenced ? fenced[1].trim() : trimmed;
}

// Los base64 de logo/wordmark pesan 100KB+ y no aportan nada a una tarea de
// traduccion de texto: se reemplazan por marcadores cortos antes de llamar
// a la API (menos tokens, cero riesgo de que el modelo corrompa el base64)
// y se restauran despues con el asset correcto por idioma.
function stripAssets(htmlEs) {
  let count = 0;
  return htmlEs.replace(/data:image\/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+/g, () => {
    count += 1;
    return count === 1 ? PLACEHOLDER_LOGO : PLACEHOLDER_WORDMARK;
  });
}

function restoreAssets(html, targetLang) {
  const logo = logoDataUri();
  const { uri: wordmarkUri, fellBack } = wordmarkDataUri(targetLang);
  const restored = html.split(PLACEHOLDER_LOGO).join(logo).split(PLACEHOLDER_WORDMARK).join(wordmarkUri);
  return { html: restored, fellBack };
}

// El disclaimer de traduccion AI se agrega de forma deterministica (no se
// le pide al modelo que lo redacte) para garantizar texto y estilo
// consistentes. Se ancla al style inline de la ultima linea del footer,
// que las reglas de traduccion obligan a dejar intacto.
function insertDisclaimer(html, targetLang) {
  const marker = 'letter-spacing:.3px;">';
  const idx = html.indexOf(marker);
  if (idx === -1) return html;
  const closeIdx = html.indexOf('</div>', idx);
  if (closeIdx === -1) return html;
  const insertAt = closeIdx + '</div>'.length;
  const disclaimerHtml = `\n      <div style="padding-top:6px; font-size:9px; color:#C7D0DA; letter-spacing:.2px; font-style:italic;">${escapeHtml(DISCLAIMER[targetLang])}</div>`;
  return html.slice(0, insertAt) + disclaimerHtml + html.slice(insertAt);
}

/**
 * Traduce un HTML ES (ya aprobado por el usuario) a "en" o "pt".
 * Devuelve { html, warnings }. Lanza si falta la API key o si la respuesta
 * no preservo los marcadores de imagen (mejor fallar visible que devolver
 * un documento roto).
 */
async function translateComunicado(htmlEs, targetLang) {
  if (!LANG_NAME[targetLang]) {
    throw new Error('targetLang debe ser "en" o "pt"');
  }
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('Falta ANTHROPIC_API_KEY en el entorno (.env). No se puede traducir sin la clave de la API de Anthropic.');
  }

  const client = new Anthropic({ apiKey });
  const model = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-5';
  const strippedHtml = stripAssets(htmlEs);

  const response = await client.messages.create({
    model,
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: `Traduce el siguiente documento HTML al ${LANG_NAME[targetLang]}. Responde únicamente con el HTML completo.\n\n${strippedHtml}`,
      },
    ],
  });

  let translated = response.content
    .filter((block) => block.type === 'text')
    .map((block) => block.text)
    .join('');
  translated = stripCodeFence(translated);

  if (!translated.includes(PLACEHOLDER_LOGO) || !translated.includes(PLACEHOLDER_WORDMARK)) {
    throw new Error(
      `La traducción a "${targetLang}" no preservó los marcadores de imagen esperados; revisa manualmente antes de usar este resultado.`
    );
  }

  const warnings = [];
  const { html: withAssets, fellBack } = restoreAssets(translated, targetLang);
  if (fellBack) {
    warnings.push(
      `No se encontró el asset de wordmark para "${targetLang}" en /assets; se usó el logo en español como respaldo.`
    );
  }

  const withDisclaimer = insertDisclaimer(withAssets, targetLang);
  return { html: withDisclaimer, warnings };
}

module.exports = { translateComunicado };

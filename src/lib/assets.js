const fs = require('fs');
const path = require('path');

const ASSETS_DIR = path.join(__dirname, '..', '..', 'assets');

const MIME_BY_EXT = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

const cache = new Map();

/**
 * Reads a file from /assets and returns it as a base64 data URI.
 * Returns null (instead of throwing) when the file is missing, so callers
 * can fall back gracefully and surface a warning instead of crashing.
 */
function assetDataUri(filename) {
  if (cache.has(filename)) return cache.get(filename);
  const full = path.join(ASSETS_DIR, filename);
  if (!fs.existsSync(full)) {
    cache.set(filename, null);
    return null;
  }
  const ext = path.extname(filename).toLowerCase();
  const mime = MIME_BY_EXT[ext] || 'application/octet-stream';
  const b64 = fs.readFileSync(full).toString('base64');
  const uri = `data:${mime};base64,${b64}`;
  cache.set(filename, uri);
  return uri;
}

// Wordmark ("Lo Mejoramos Juntos") swaps per language. Only the ES asset is
// guaranteed to exist (extracted from the original comunicado template);
// EN/PT wordmarks fall back to the ES asset with a warning until someone
// drops the real files in /assets.
const WORDMARK_BY_LANG = {
  es: 'lo_mejoramos_juntos_crop.png',
  en: 'we_improve_together_crop.png',
  pt: 'melhoramos_juntos_crop.png',
};

function logoDataUri() {
  return assetDataUri('guepardo_logo_crop.jpg');
}

function wordmarkDataUri(lang) {
  const filename = WORDMARK_BY_LANG[lang] || WORDMARK_BY_LANG.es;
  const uri = assetDataUri(filename);
  if (uri) return { uri, fellBack: false };
  // Fallback: reuse the ES wordmark so the layout never breaks.
  const fallback = assetDataUri(WORDMARK_BY_LANG.es);
  return { uri: fallback, fellBack: true };
}

module.exports = { assetDataUri, logoDataUri, wordmarkDataUri, ASSETS_DIR };

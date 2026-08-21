require('dotenv').config();

const fs = require('fs');
const path = require('path');
const express = require('express');
const { nanoid } = require('nanoid');

const { buildComunicadoHtml } = require('./src/templates/comunicadoTemplate');
const { translateComunicado } = require('./src/lib/translate');
const { screenshotHtmlFile } = require('./src/lib/screenshot');
const { pipeDirAsZip } = require('./src/lib/zip');
const { iconTypes, colorKeys } = require('./src/templates/icons');
const { flagCodes } = require('./src/templates/flags');

const app = express();
const PORT = process.env.PORT || 4173;
const OUTPUT_DIR = path.join(__dirname, 'output');

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use('/output', express.static(OUTPUT_DIR));

function slugify(str) {
  return (
    String(str || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')
      .slice(0, 40) || 'comunicado'
  );
}

function todayFecha() {
  return new Date().toISOString().slice(0, 10);
}

function jobDir(jobId) {
  const dir = path.join(OUTPUT_DIR, jobId);
  const resolved = path.resolve(dir);
  if (!resolved.startsWith(OUTPUT_DIR)) {
    throw new Error('jobId invalido');
  }
  return resolved;
}

// Config que el frontend necesita para poblar los selects (tipos de icono,
// colores, banderas disponibles) sin duplicar esas listas en el cliente.
app.get('/api/config', (req, res) => {
  res.json({
    iconTypes,
    colorKeys,
    flagCodes,
    hasApiKey: Boolean(process.env.ANTHROPIC_API_KEY),
  });
});

// Paso 1: genera el HTML ES (master) + preview PNG. Este es el punto de
// control humano obligatorio antes de traducir (nunca se traduce sin que
// el ES haya sido aprobado).
app.post('/api/comunicado/preview', async (req, res) => {
  try {
    const data = req.body || {};
    if (!data.titulo || !data.titulo.trim()) {
      return res.status(400).json({ error: 'El título del comunicado es obligatorio.' });
    }
    if (!data.bajada || !data.bajada.trim()) {
      return res.status(400).json({ error: 'La bajada/subtítulo es obligatoria.' });
    }

    let jobId = typeof data.jobId === 'string' ? data.jobId : null;
    if (jobId && !/^[a-z0-9-]+$/.test(jobId)) jobId = null;
    if (!jobId) {
      jobId = `${todayFecha()}-${slugify(data.titulo)}-${nanoid(5)}`;
    }
    const dir = jobDir(jobId);
    fs.mkdirSync(dir, { recursive: true });

    const html = buildComunicadoHtml(data);
    const htmlPath = path.join(dir, 'comunicado_es.html');
    fs.writeFileSync(htmlPath, html, 'utf8');

    const pngPath = path.join(dir, 'preview_es.png');
    await screenshotHtmlFile(htmlPath, pngPath);

    res.json({
      jobId,
      lang: 'es',
      htmlUrl: `/output/${jobId}/comunicado_es.html`,
      previewUrl: `/output/${jobId}/preview_es.png?t=${Date.now()}`,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Error generando el comunicado ES.' });
  }
});

// Paso 2: traduce el ES ya aprobado (guardado en disco) a EN y/o PT, y
// renderiza su preview PNG. Nunca se dispara automaticamente desde el
// paso 1 -- requiere que el usuario lo pida explicitamente.
app.post('/api/comunicado/:jobId/translate', async (req, res) => {
  const { jobId } = req.params;
  let dir;
  try {
    dir = jobDir(jobId);
  } catch {
    return res.status(400).json({ error: 'jobId inválido.' });
  }

  const esPath = path.join(dir, 'comunicado_es.html');
  if (!fs.existsSync(esPath)) {
    return res.status(404).json({ error: 'No existe un ES aprobado para este jobId. Genera el ES primero.' });
  }

  const langs = Array.isArray(req.body?.langs) && req.body.langs.length ? req.body.langs : ['en', 'pt'];
  const validLangs = langs.filter((l) => l === 'en' || l === 'pt');
  const htmlEs = fs.readFileSync(esPath, 'utf8');

  const results = {};
  const errors = {};

  for (const lang of validLangs) {
    try {
      const { html, warnings } = await translateComunicado(htmlEs, lang);
      const htmlPath = path.join(dir, `comunicado_${lang}.html`);
      fs.writeFileSync(htmlPath, html, 'utf8');

      const pngPath = path.join(dir, `preview_${lang}.png`);
      await screenshotHtmlFile(htmlPath, pngPath);

      results[lang] = {
        htmlUrl: `/output/${jobId}/comunicado_${lang}.html`,
        previewUrl: `/output/${jobId}/preview_${lang}.png?t=${Date.now()}`,
        warnings,
      };
    } catch (err) {
      console.error(`Error traduciendo a ${lang}:`, err);
      errors[lang] = err.message || `Error traduciendo a ${lang}.`;
    }
  }

  res.json({ jobId, results, errors });
});

app.get('/api/comunicado/:jobId/zip', (req, res) => {
  const { jobId } = req.params;
  let dir;
  try {
    dir = jobDir(jobId);
  } catch {
    return res.status(400).send('jobId inválido.');
  }
  if (!fs.existsSync(dir)) return res.status(404).send('No encontrado.');
  pipeDirAsZip(dir, res, `${jobId}.zip`);
});

app.listen(PORT, () => {
  console.log(`Generador Guepardo escuchando en http://localhost:${PORT}`);
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('Aviso: ANTHROPIC_API_KEY no está definida (.env) — el paso de traducción EN/PT fallará hasta que la configures.');
  }
});

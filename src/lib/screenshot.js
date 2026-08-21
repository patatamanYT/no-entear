const { chromium } = require('playwright');
const path = require('path');

let browserPromise = null;

function getBrowser() {
  if (!browserPromise) {
    // Solo se usa si el Chromium de Playwright vive en una ruta no estandar
    // (p.ej. un runner con navegadores preinstalados). En una maquina normal
    // se deja sin definir y Playwright usa el que descargo `playwright install`.
    const executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined;
    browserPromise = chromium.launch({ executablePath });
  }
  return browserPromise;
}

/**
 * Renderiza screenshot PNG del ".container" de un HTML ya escrito en disco.
 * viewport 900px / device_scale_factor 3, igual al patron ya usado en el
 * proyecto para las previews de comunicados/boletines.
 */
async function screenshotHtmlFile(htmlPath, pngPath) {
  const browser = await getBrowser();
  const page = await browser.newPage({
    viewport: { width: 900, height: 1000 },
    deviceScaleFactor: 3,
  });
  try {
    await page.goto(`file://${path.resolve(htmlPath)}`);
    await page.waitForTimeout(400);
    const el = await page.$('.container');
    if (!el) {
      throw new Error(`No se encontro ".container" en ${htmlPath}; no se pudo generar el preview PNG.`);
    }
    await el.screenshot({ path: pngPath });
  } finally {
    await page.close();
  }
}

async function closeBrowser() {
  if (browserPromise) {
    const browser = await browserPromise;
    await browser.close();
    browserPromise = null;
  }
}

module.exports = { screenshotHtmlFile, closeBrowser };

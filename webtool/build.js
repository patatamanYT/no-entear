// Ensambla la herramienta HTML standalone: toma shell.html + app.js +
// html2canvas + los assets de /assets y produce un unico archivo .html
// autocontenido, sin dependencias externas ni servidor.
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const shell = fs.readFileSync(path.join(__dirname, 'shell.html'), 'utf8');
const appJs = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
const html2canvas = fs.readFileSync(
  path.join(ROOT, 'node_modules', 'html2canvas', 'dist', 'html2canvas.min.js'),
  'utf8'
);

function dataUri(filename, mime) {
  const b64 = fs.readFileSync(path.join(ROOT, 'assets', filename)).toString('base64');
  return `data:${mime};base64,${b64}`;
}

const logoUri = dataUri('guepardo_logo_crop.jpg', 'image/jpeg');
const wordmarkEsUri = dataUri('lo_mejoramos_juntos_crop.png', 'image/png');
const wordmarkEnUri = dataUri('we_improve_together_crop.png', 'image/png');
const wordmarkPtUri = dataUri('melhoramos_juntos_crop.png', 'image/png');

// Poppins se embebe como @font-face con los .woff2 en base64 (en vez de
// depender de un <link> a fonts.googleapis.com): asi el tipo de letra se ve
// igual siempre, incluso sin internet o detras de un firewall corporativo
// que bloquee Google Fonts. Una sola linea, sin comillas dobles ni saltos de
// linea, para poder inyectarla tal cual dentro de un literal `"...";` de JS
// en shell.html sin romperlo.
//
// Cada peso usa su PROPIO nombre de familia ("Poppins900", "Poppins800"...)
// en vez de compartir "Poppins" + font-weight distinto: se confirmo que
// html2canvas (via foreignObjectRendering) ignora el font-weight cuando hay
// varios pesos de una misma familia embebidos como @font-face -- exportaba
// siempre el mismo grosor sin importar que font-weight se pidiera en el
// CSS. Con un nombre de familia unico por peso no hay nada que confundir.
function fontFace(weight, filename) {
  const b64 = fs.readFileSync(path.join(ROOT, 'assets', 'fonts', filename)).toString('base64');
  return `@font-face{font-family:'Poppins${weight}';font-style:normal;font-weight:${weight};font-display:swap;src:url(data:font/woff2;base64,${b64}) format('woff2');}`;
}
const poppinsFontFaceCss = [600, 700, 800, 900]
  .map((w) => fontFace(w, `poppins-${w}.woff2`))
  .join('');

// Usamos funcion como reemplazo: si se pasa un string literal, "$$", "$&",
// "$1"... se interpretan como patrones especiales de String.replace y
// corrompen el codigo (p.ej. "const $$ = ..." se volvia "const $ = ...").
let out = shell
  .replace('/* __HTML2CANVAS__ */', () => html2canvas)
  .replace('/* __APP_JS__ */', () => appJs);

out = out.split('%%BUILD_LOGO_B64%%').join(logoUri);
out = out.split('%%BUILD_WORDMARK_ES_B64%%').join(wordmarkEsUri);
out = out.split('%%BUILD_WORDMARK_EN_B64%%').join(wordmarkEnUri);
out = out.split('%%BUILD_WORDMARK_PT_B64%%').join(wordmarkPtUri);
out = out.split('%%BUILD_POPPINS_FONTFACE%%').join(poppinsFontFaceCss);

const outPath = process.argv[2] || path.join(ROOT, 'herramienta-guepardo.html');
fs.writeFileSync(outPath, out, 'utf8');
console.log('Escrito:', outPath, `(${(out.length / 1024).toFixed(0)} KB)`);

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
const wordmarkEnUri = dataUri('we_improve_together_crop.jpg', 'image/jpeg');
const wordmarkPtUri = dataUri('melhoramos_juntos_crop.jpg', 'image/jpeg');

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

const outPath = process.argv[2] || path.join(ROOT, 'herramienta-guepardo.html');
fs.writeFileSync(outPath, out, 'utf8');
console.log('Escrito:', outPath, `(${(out.length / 1024).toFixed(0)} KB)`);

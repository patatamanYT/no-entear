// Chips de bandera como SVG inline (circulares, 28px), simplificados a
// franjas de color -- consistente con la regla "SVG inline exclusivamente,
// nunca emojis" del sistema de diseno. No son banderas heraldicamente
// exactas, son chips reconocibles para el header de tarjeta.

function stripes(colors) {
  const n = colors.length;
  const w = 28 / n;
  return colors
    .map((c, i) => `<rect x="${(i * w).toFixed(2)}" y="0" width="${w.toFixed(2)}" height="28" fill="${c}"/>`)
    .join('');
}

const FLAGS = {
  mx: { label: 'México', svg: stripes(['#006341', '#FFFFFF', '#CE1126']) },
  ar: { label: 'Argentina', svg: `${stripes(['#74ACDF', '#FFFFFF', '#74ACDF'])}<circle cx="14" cy="14" r="3" fill="#F6B40E" stroke="#85340A" stroke-width="0.6"/>` },
  br: { label: 'Brasil', svg: `<rect width="28" height="28" fill="#009C3B"/><polygon points="14,5 25,14 14,23 3,14" fill="#FFDF00"/><circle cx="14" cy="14" r="5" fill="#002776"/>` },
  co: { label: 'Colombia', svg: `<rect width="28" height="14" fill="#FCD116"/><rect y="14" width="28" height="7" fill="#003893"/><rect y="21" width="28" height="7" fill="#CE1126"/>` },
  pe: { label: 'Perú', svg: stripes(['#D91023', '#FFFFFF', '#D91023']) },
  es: { label: 'España', svg: `<rect width="28" height="28" fill="#AA151B"/><rect y="7" width="28" height="14" fill="#F1BF00"/>` },
  cl: { label: 'Chile', svg: `<rect width="28" height="14" fill="#FFFFFF"/><rect y="14" width="28" height="14" fill="#D52B1E"/><rect width="12" height="14" fill="#0039A6"/><polygon points="6,4 7,7 10,7 7.5,9 8.5,12 6,10 3.5,12 4.5,9 2,7 5,7" fill="#FFFFFF"/>` },
  us: { label: 'USA', svg: `<rect width="28" height="28" fill="#B22234"/>${Array.from({ length: 6 }).map((_, i) => `<rect y="${(i * 4.3 + 2.15).toFixed(2)}" width="28" height="2.15" fill="#FFFFFF"/>`).join('')}<rect width="13" height="15" fill="#3C3B6E"/>` },
};

function flagChip(code) {
  const flag = FLAGS[code];
  if (!flag) return '';
  return `<span style="display:inline-flex; width:22px; height:22px; border-radius:999px; overflow:hidden; border:1px solid rgba(15,23,42,.12); flex-shrink:0;" title="${flag.label}"><svg viewBox="0 0 28 28" width="22" height="22">${flag.svg}</svg></span>`;
}

module.exports = { FLAGS, flagChip, flagCodes: Object.keys(FLAGS) };

const { logoDataUri, wordmarkDataUri } = require('../lib/assets');
const { BADGE_ICON, BADGE_BG, BADGE_LABEL, ICON_COLORS, renderIcon } = require('./icons');
const { flagChip } = require('./flags');

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Convierte **negrita** (ya escapado) a <b>. Debe correr DESPUES de
// escapeHtml para que el usuario no pueda inyectar markup propio.
function mdBold(str) {
  return escapeHtml(str).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
}

function renderTitulo(titulo, resaltado) {
  const safeTitulo = escapeHtml(titulo);
  const safeResaltado = escapeHtml(resaltado || '');
  if (safeResaltado && safeTitulo.startsWith(safeResaltado)) {
    const resto = safeTitulo.slice(safeResaltado.length);
    return `<span style="color:#F26722;">${safeResaltado}</span>${resto}`;
  }
  return safeTitulo;
}

function renderBadge(badgeType, lang) {
  const type = BADGE_ICON[badgeType] ? badgeType : 'actualizacion';
  const bg = BADGE_BG[type];
  const label = (BADGE_LABEL[lang] || BADGE_LABEL.es)[type];
  return `<span class="badge" style="background:${bg};">${BADGE_ICON[type]}${escapeHtml(label)}</span>`;
}

function renderBloques(bloques) {
  const items = (bloques || []).filter((b) => b && b.titulo && b.viñetas && b.viñetas.some((v) => v && v.trim()));
  if (!items.length) return '';
  const cards = items
    .map((bloque, i) => {
      const { bg, svg } = renderIcon(bloque.icono, bloque.color);
      const vinetas = bloque.viñetas
        .filter((v) => v && v.trim())
        .map((v) => `<span style="color:${(ICON_COLORS[bloque.color] || ICON_COLORS.naranja).stroke};">&#10004;</span> ${mdBold(v)}`)
        .join('<br>\n            ');
      return `      <!-- Tarjeta ${i + 1} -->
      <div class="card">
        <div style="display:flex; align-items:center; gap:9px; margin-bottom:9px;">
          <div class="num">${i + 1}</div>
          <div class="heading" style="font-size:15px; line-height:1.25;">${escapeHtml(bloque.titulo)}</div>
        </div>
        <div style="display:flex; gap:14px; align-items:flex-start;">
          <div style="width:44px; height:44px; background:${bg}; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            ${svg}
          </div>
          <div class="bullets" style="flex:1;">
            ${vinetas}
          </div>
        </div>
      </div>`;
    })
    .join('\n\n');
  return `    <!-- Tarjetas -->
    <div style="padding:12px 30px 4px 30px;">

${cards}

    </div>`;
}

function renderVigenciaCard(vigencia) {
  if (!vigencia || !vigencia.tipo) return '';
  let texto;
  if (vigencia.tipo === 'fecha' && vigencia.fecha) {
    texto = `Entra en vigor el<br><b style="color:#1F2A44; font-weight:700;">${escapeHtml(vigencia.fecha)}.</b>`;
  } else if (vigencia.tipo === 'custom' && vigencia.custom) {
    texto = mdBold(vigencia.custom);
  } else {
    texto = 'Estos cambios ya se encuentran<br><b style="color:#1F2A44; font-weight:700;">vigentes.</b>';
  }
  return `      <div style="flex:1; background:#FFF9F5; border:1px solid #FCE4D2; border-radius:14px; padding:16px; display:flex; gap:12px; align-items:center;">
        <div style="width:44px; height:44px; background:#FEEDE2; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
          <svg viewBox="0 0 24 24" width="24" height="24"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="#F26722" stroke-width="2"/><line x1="3" y1="10" x2="21" y2="10" stroke="#F26722" stroke-width="2"/><line x1="7" y1="3" x2="7" y2="6.5" stroke="#F26722" stroke-width="2" stroke-linecap="round"/><line x1="17" y1="3" x2="17" y2="6.5" stroke="#F26722" stroke-width="2" stroke-linecap="round"/><line x1="6.5" y1="14" x2="9.5" y2="14" stroke="#F26722" stroke-width="2" stroke-linecap="round"/><line x1="11.5" y1="14" x2="14.5" y2="14" stroke="#F26722" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <div style="font-size:13.5px; font-weight:400; color:#475569; line-height:1.6;">${texto}</div>
      </div>`;
}

function renderContactoCard(contacto) {
  if (!contacto) return '';
  return `      <div style="flex:1; background:#F1F8F3; border:1px solid #D6EADD; border-radius:14px; padding:16px; display:flex; gap:12px; align-items:center;">
        <div style="width:44px; height:44px; background:#E1F0E6; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
          <svg viewBox="0 0 24 24" width="24" height="24"><path d="M4 13 V11 A8 8 0 0 1 20 11 V13" fill="none" stroke="#0F7A43" stroke-width="2" stroke-linecap="round"/><rect x="2.5" y="12" width="4.5" height="7" rx="2" fill="none" stroke="#0F7A43" stroke-width="2"/><rect x="17" y="12" width="4.5" height="7" rx="2" fill="none" stroke="#0F7A43" stroke-width="2"/><path d="M19.2 19 V20 A3 3 0 0 1 16.2 23 H13.5" fill="none" stroke="#0F7A43" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <div style="flex:1;">
          <div style="font-size:11.5px; color:#0F7A43; font-weight:900; letter-spacing:.6px; text-transform:uppercase; margin-bottom:5px;">¿TIENES DUDAS?</div>
          <div style="font-size:13px; color:#475569; line-height:1.5;">
            Repórtalas directamente a <b style="color:#1F2A44;">${escapeHtml(contacto)}</b>.
          </div>
        </div>
      </div>`;
}

function renderVigenciaDudasRow(vigencia, contacto) {
  const vigenciaHtml = renderVigenciaCard(vigencia);
  const contactoHtml = renderContactoCard(contacto);
  if (!vigenciaHtml && !contactoHtml) return '';
  return `    <!-- Vigencia + Dudas -->
    <div style="padding:14px 30px 16px 30px; display:flex; gap:14px;">
${[vigenciaHtml, contactoHtml].filter(Boolean).join('\n')}
    </div>`;
}

function renderNotaCierre(nota) {
  if (!nota || !nota.trim()) return '';
  return `    <!-- Nota de cierre -->
    <div style="margin:0 30px 16px 30px; background:#F8FAFC; border:1px solid #E9EEF5; border-radius:12px; padding:12px 16px; font-size:12px; color:#64748B; line-height:1.6;">${mdBold(nota)}</div>`;
}

/**
 * Arma el HTML completo del Comunicado (ES master). El resultado es un
 * documento standalone (imagenes embebidas en base64) listo para preview
 * o para servir de insumo a la traduccion EN/PT.
 */
function buildComunicadoHtml(data) {
  const {
    titulo,
    tituloResaltado,
    bajada,
    badgeType,
    bandera,
    bloques,
    vigencia,
    contacto,
    notaCierre,
  } = data;

  const logo = logoDataUri();
  const wordmark = wordmarkDataUri('es');

  const flagHtml = bandera ? flagChip(bandera) : '';

  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body { margin:0; padding:0; background:#EEF2F6; font-family:'Segoe UI', Arial, sans-serif; }
  .container { width:820px; margin:24px auto; background:#FFFFFF; border-radius:16px; overflow:hidden; box-shadow:0 10px 28px rgba(15,23,42,.12); }
  .heading { font-family:'Poppins','Segoe UI',Arial,sans-serif; font-weight:900; letter-spacing:-.4px; color:#1F2A44; }
  .badge { display:inline-flex; align-items:center; gap:7px; background:#F26722; color:#FFFFFF; font-size:11px; font-weight:800; letter-spacing:1px; text-transform:uppercase; padding:8px 14px; border-radius:999px; }
  .num { width:24px; height:24px; border-radius:999px; background:#0A2540; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-family:'Poppins',sans-serif; font-weight:900; font-size:12px; flex-shrink:0; }
  .card { background:#FFFFFF; border:1px solid #E9EEF5; border-radius:14px; padding:14px 18px; }
  .card + .card { margin-top:10px; }
  .bullets { font-size:13px; color:#475569; line-height:1.75; padding-top:1px; }
  .bullets b { color:#1F2A44; }
</style>
</head>
<body>
  <div class="container">

    <!-- Header -->
    <div style="padding:20px 30px 8px 30px; background:#FFFFFF; display:flex; justify-content:space-between; align-items:center;">
      <div style="display:flex; align-items:center; gap:12px;">
        <img src="${logo}" alt="Guepardo" style="height:64px; width:auto; display:block;">
        <img src="${wordmark.uri}" alt="Lo Mejoramos Juntos" style="height:46px; width:auto; display:block;">
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        ${flagHtml}
        ${renderBadge(badgeType, 'es')}
      </div>
    </div>

    <!-- Título -->
    <div style="padding:6px 30px 4px 30px;">
      <div class="heading" style="font-size:32px; line-height:1.15; margin-bottom:8px;">${renderTitulo(titulo, tituloResaltado)}</div>
      <div style="font-size:13.5px; color:#475569; line-height:1.5; max-width:640px;">${escapeHtml(bajada)}</div>
    </div>

${renderBloques(bloques)}

${renderVigenciaDudasRow(vigencia, contacto)}

${renderNotaCierre(notaCierre)}

    <!-- Footer -->
    <div style="padding:12px 30px 16px 30px; border-top:1px solid #F1E4DA; text-align:center;">
      <div style="font-size:12px; color:#F26722; font-weight:900; letter-spacing:2px; text-transform:uppercase;">Proyecto Guepardo</div>
      <div style="padding-top:3px; font-size:11px; color:#94A3B8;">Disfrutamos el proceso</div>
      <div style="padding-top:6px; font-size:9.5px; color:#B8C2CE; letter-spacing:.3px;">Grupo Lamosa &middot; Información de uso interno</div>
    </div>

  </div>
</body>
</html>`;
}

module.exports = { buildComunicadoHtml, escapeHtml, mdBold };

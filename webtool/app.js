(() => {
  'use strict';

  // ---------------------------------------------------------------------
  // Assets embebidos (inyectados por build.js como constantes globales
  // ASSET_LOGO_URI / ASSET_WORDMARK_ES_URI antes de este script).
  // ---------------------------------------------------------------------
  const LOGO_URI = window.ASSET_LOGO_URI;
  const WORDMARK_ES_URI = window.ASSET_WORDMARK_ES_URI;

  // ---------------------------------------------------------------------
  // Iconos SVG inline (nunca emojis) — mismo set que la version servidor.
  // ---------------------------------------------------------------------
  const ICONS = {
    showroom: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 9 L4 3 H20 L21 9" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><path d="M3 9 V20 H21 V9" fill="none" stroke="${s}" stroke-width="1.8"/><path d="M3 9 A2.2 2.2 0 0 0 7.4 9" stroke="${s}" stroke-width="1.6" fill="none"/><path d="M7.4 9 A2.2 2.2 0 0 0 11.8 9" stroke="${s}" stroke-width="1.6" fill="none"/><path d="M11.8 9 A2.2 2.2 0 0 0 16.2 9" stroke="${s}" stroke-width="1.6" fill="none"/><path d="M16.2 9 A2.2 2.2 0 0 0 20.6 9" stroke="${s}" stroke-width="1.6" fill="none"/><rect x="9.5" y="14" width="5" height="6" fill="none" stroke="${s}" stroke-width="1.6"/></svg>`,
    escudo: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2 L2 7 V11 C2 16.5 6.2 21 12 22 C17.8 21 22 16.5 22 11 V7 Z" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 8 V13" stroke="${s}" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16" r="1.1" fill="${s}"/></svg>`,
    check: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9.2" fill="none" stroke="${s}" stroke-width="1.8"/><path d="M7.5 12.5 L10.5 15.5 L16.5 9" fill="none" stroke="${s}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    documento: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M6 2.5 H14 L18 6.5 V21.5 H6 Z" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><path d="M14 2.5 V6.5 H18" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><line x1="9" y1="12" x2="15" y2="12" stroke="${s}" stroke-width="1.6" stroke-linecap="round"/><line x1="9" y1="16" x2="15" y2="16" stroke="${s}" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    tendencia: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 17 L9.5 10.5 L13.5 14.5 L21 6.5" fill="none" stroke="${s}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 6.5 H21 V12.5" fill="none" stroke="${s}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    alerta: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 3 L22 20 H2 Z" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><line x1="12" y1="9.5" x2="12" y2="14.5" stroke="${s}" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1" fill="${s}"/></svg>`,
    calendario: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="${s}" stroke-width="1.8"/><line x1="3" y1="10" x2="21" y2="10" stroke="${s}" stroke-width="1.8"/><line x1="7" y1="3" x2="7" y2="6.5" stroke="${s}" stroke-width="1.8" stroke-linecap="round"/><line x1="17" y1="3" x2="17" y2="6.5" stroke="${s}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  };

  const ICON_COLORS = {
    naranja: { bg: '#FEEDE2', stroke: '#F26722' },
    verde: { bg: '#E9F5EC', stroke: '#0F7A43' },
    navy: { bg: '#E9EEF5', stroke: '#1F2A44' },
  };

  const BADGE_ICON = {
    actualizacion: `<svg viewBox="0 0 24 24" width="13" height="13"><path d="M12 2 C7.5 2 5 5 5 9 V14 L2.5 18 H21.5 L19 14 V9 C19 5 16.5 2 12 2 Z" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/><path d="M9.5 18 C9.5 20 10.5 21.2 12 21.2 C13.5 21.2 14.5 20 14.5 18" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>`,
    aviso: `<svg viewBox="0 0 24 24" width="13" height="13"><path d="M12 3 L22 20 H2 Z" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/><line x1="12" y1="9.5" x2="12" y2="14.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1" fill="#FFFFFF"/></svg>`,
    recordatorio: `<svg viewBox="0 0 24 24" width="13" height="13"><circle cx="12" cy="13" r="8" fill="none" stroke="#FFFFFF" stroke-width="2"/><path d="M12 9 V13 L15 15.5" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 2.5 H15" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>`,
  };
  const BADGE_BG = { actualizacion: '#F26722', aviso: '#DC5D2E', recordatorio: '#1F2A44' };
  const BADGE_LABEL = {
    es: { actualizacion: 'Actualización', aviso: 'Aviso', recordatorio: 'Recordatorio' },
    en: { actualizacion: 'Update', aviso: 'Notice', recordatorio: 'Reminder' },
    pt: { actualizacion: 'Atualização', aviso: 'Aviso', recordatorio: 'Lembrete' },
  };

  function renderIcon(type, colorKey) {
    const fn = ICONS[type] || ICONS.check;
    const c = ICON_COLORS[colorKey] || ICON_COLORS.naranja;
    return { bg: c.bg, svg: fn(c.stroke) };
  }

  // ---------------------------------------------------------------------
  // Banderas SVG inline (chips circulares, sin emojis).
  // ---------------------------------------------------------------------
  function stripes(colors) {
    const w = 28 / colors.length;
    return colors.map((c, i) => `<rect x="${(i * w).toFixed(2)}" y="0" width="${w.toFixed(2)}" height="28" fill="${c}"/>`).join('');
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
    const f = FLAGS[code];
    if (!f) return '';
    return `<span style="display:inline-flex; width:22px; height:22px; border-radius:999px; overflow:hidden; border:1px solid rgba(15,23,42,.12); flex-shrink:0;" title="${f.label}"><svg viewBox="0 0 28 28" width="22" height="22">${f.svg}</svg></span>`;
  }

  // ---------------------------------------------------------------------
  // Template del Comunicado (idéntico al de la version servidor).
  // ---------------------------------------------------------------------
  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
  function mdBold(str) {
    return escapeHtml(str).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  }
  function renderTitulo(titulo, resaltado) {
    const t = escapeHtml(titulo);
    const r = escapeHtml(resaltado || '');
    if (r && t.startsWith(r)) return `<span style="color:#F26722;">${r}</span>${t.slice(r.length)}`;
    return t;
  }
  function renderBadge(badgeType, lang) {
    const type = BADGE_ICON[badgeType] ? badgeType : 'actualizacion';
    const bg = BADGE_BG[type];
    const label = (BADGE_LABEL[lang] || BADGE_LABEL.es)[type];
    return `<span class="badge" style="background:${bg};">${BADGE_ICON[type]}${escapeHtml(label)}</span>`;
  }
  function renderBloques(bloques) {
    const items = (bloques || []).filter((b) => b && b.titulo && b.vinetas && b.vinetas.some((v) => v && v.trim()));
    if (!items.length) return '';
    const cards = items
      .map((bloque, i) => {
        const { bg, svg } = renderIcon(bloque.icono, bloque.color);
        const stroke = (ICON_COLORS[bloque.color] || ICON_COLORS.naranja).stroke;
        const vinetas = bloque.vinetas
          .filter((v) => v && v.trim())
          .map((v) => `<span style="color:${stroke};">&#10004;</span> ${mdBold(v)}`)
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
    const v = renderVigenciaCard(vigencia);
    const c = renderContactoCard(contacto);
    if (!v && !c) return '';
    return `    <!-- Vigencia + Dudas -->
    <div style="padding:14px 30px 16px 30px; display:flex; gap:14px;">
${[v, c].filter(Boolean).join('\n')}
    </div>`;
  }
  function renderNotaCierre(nota) {
    if (!nota || !nota.trim()) return '';
    return `    <!-- Nota de cierre -->
    <div style="margin:0 30px 16px 30px; background:#F8FAFC; border:1px solid #E9EEF5; border-radius:12px; padding:12px 16px; font-size:12px; color:#64748B; line-height:1.6;">${mdBold(nota)}</div>`;
  }

  function buildComunicadoHtml(data) {
    const { titulo, tituloResaltado, bajada, badgeType, bandera, bloques, vigencia, contacto, notaCierre } = data;
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
        <img src="__ASSET_LOGO__" alt="Guepardo" style="height:64px; width:auto; display:block;">
        <img src="__ASSET_WORDMARK__" alt="Lo Mejoramos Juntos" style="height:46px; width:auto; display:block;">
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

  // ---------------------------------------------------------------------
  // Placeholders de imagen: la plantilla arriba ya sale con
  // __ASSET_LOGO__ / __ASSET_WORDMARK__ en vez de base64 -- se resuelven
  // aqui mismo (nunca se manda un base64 de 100KB+ a Claude al preparar
  // la traduccion).
  // ---------------------------------------------------------------------
  function resolveAssets(html, lang) {
    const wordmark = lang === 'es' ? WORDMARK_ES_URI : (window.customWordmarks && window.customWordmarks[lang]) || WORDMARK_ES_URI;
    const fellBack = lang !== 'es' && !(window.customWordmarks && window.customWordmarks[lang]);
    const resolved = html.split('__ASSET_LOGO__').join(LOGO_URI).split('__ASSET_WORDMARK__').join(wordmark);
    return { html: resolved, fellBack };
  }

  const DISCLAIMER = {
    en: 'This document was machine-translated from the Spanish original with AI assistance. In case of any discrepancy, the Spanish version prevails.',
    pt: 'Este documento foi traduzido automaticamente do original em espanhol com apoio de IA. Em caso de divergência, prevalece a versão em espanhol.',
  };
  function insertDisclaimer(html, lang) {
    const marker = 'letter-spacing:.3px;">';
    const idx = html.indexOf(marker);
    if (idx === -1) return html;
    const closeIdx = html.indexOf('</div>', idx);
    if (closeIdx === -1) return html;
    const insertAt = closeIdx + '</div>'.length;
    const line = `\n      <div style="padding-top:6px; font-size:9px; color:#C7D0DA; letter-spacing:.2px; font-style:italic;">${escapeHtml(DISCLAIMER[lang])}</div>`;
    return html.slice(0, insertAt) + line + html.slice(insertAt);
  }

  const SYSTEM_PROMPT = `Eres el traductor corporativo oficial del Proyecto Guepardo (Grupo Lamosa). Tu única tarea es traducir el texto visible de un documento HTML, preservando exactamente su estructura.

REGLAS GENERALES (obligatorias):
- Traduce el HTML completo manteniendo estructura, tags, atributos y estilos inline intactos. Solo cambia el texto que aparece entre tags (y en atributos visibles como "alt" o "title" si corresponde).
- Nunca alteres el significado, alcance, fechas, montos, responsables, condiciones ni el nivel de compromiso del texto fuente.
- No agregues ni omitas información.
- No traduzcas nombres propios de personas, ni las marcas "Proyecto Guepardo" / "Grupo Lamosa".
- Los marcadores literales __ASSET_LOGO__ y __ASSET_WORDMARK__ deben quedar EXACTAMENTE igual, en su misma posición dentro del atributo src. No los traduzcas, no los muevas, no los elimines.
- No agregues comentarios, explicaciones, notas ni bloques de código markdown (nada de \`\`\`). Responde ÚNICAMENTE con el HTML completo, empezando en "<!DOCTYPE html>" y terminando en "</html>".`;

  const LANG_RULES = {
    en: `Inglés (EN corporativo, US-native):
- Usa voz activa y fraseo idiomático, no traducción literal palabra por palabra.
- Evita repetir el mismo término en elementos de interfaz cercanos; varía con sinónimos cuando el inglés lo pide.`,
    pt: `Portugués (PT-BR corporativo):
- Usa "estoque" en vez de "inventário".
- Usa travessão (—) para contraste condicional donde el español usa guion o dos puntos de contraste.
- Usa "Em caso de dúvidas" en vez de alternativas literales como "Em caso de perguntas".`,
  };
  const LANG_NAME = { en: 'inglés (EN corporativo, US-native)', pt: 'portugués (PT-BR corporativo)' };

  function buildTranslationPrompt(strippedHtml, lang) {
    return `${SYSTEM_PROMPT}

${LANG_RULES[lang]}

---

Traduce el siguiente documento HTML al ${LANG_NAME[lang]}. Responde únicamente con el HTML completo.

${strippedHtml}`;
  }

  // ---------------------------------------------------------------------
  // UI
  // ---------------------------------------------------------------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function showView(id) {
    $$('.view').forEach((v) => (v.style.display = 'none'));
    $(`#${id}`).style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- Selector ---
  $('#card-comunicado').addEventListener('click', () => showView('view-comunicado'));
  $$('.back-link').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); showView('view-selector'); }));

  // --- Bloques dinamicos ---
  const ICON_OPTIONS = [
    ['check', 'Check / aprobación'], ['showroom', 'Showroom / tienda'], ['escudo', 'Escudo / contingencia'],
    ['documento', 'Documento'], ['tendencia', 'Tendencia / inversión'], ['alerta', 'Alerta'], ['calendario', 'Calendario'],
  ];
  const COLOR_OPTIONS = [['naranja', 'Naranja'], ['verde', 'Verde'], ['navy', 'Navy']];
  const bloquesList = $('#bloques-list');

  function optionsHtml(options, selected) {
    return options.map(([v, l]) => `<option value="${v}" ${v === selected ? 'selected' : ''}>${l}</option>`).join('');
  }
  function addBloque() {
    const card = document.createElement('div');
    card.className = 'bloque-card';
    card.innerHTML = `
      <button type="button" class="btn btn-danger-ghost btn-sm bloque-remove">Quitar</button>
      <label>Título del bloque</label>
      <input type="text" class="bloque-titulo" placeholder="Ej. Flujo de Showroom">
      <div class="row">
        <div><label>Icono</label><select class="bloque-icono">${optionsHtml(ICON_OPTIONS, 'check')}</select></div>
        <div><label>Color</label><select class="bloque-color">${optionsHtml(COLOR_OPTIONS, 'naranja')}</select></div>
      </div>
      <label>Viñetas <span class="hint">(una por línea, usa **texto** para negrita)</span></label>
      <textarea class="bloque-vinetas" placeholder="Nuevo flujo dedicado para la creación de **Showrooms**...&#10;Autoriza el **Country Manager**..."></textarea>`;
    card.querySelector('.bloque-remove').addEventListener('click', () => card.remove());
    bloquesList.appendChild(card);
  }
  $('#btn-add-bloque').addEventListener('click', addBloque);
  addBloque();

  $('#titulo').addEventListener('input', (e) => {
    const words = e.target.value.trim().split(/\s+/).filter(Boolean).length;
    const el = $('#titulo-count');
    el.textContent = e.target.value.trim() ? `${words} palabra${words === 1 ? '' : 's'}${words > 10 ? ' — considera acortar' : ''}` : '';
    el.style.color = words > 10 ? '#B23A12' : '#94A3B8';
  });

  $('#vigenciaTipo').addEventListener('change', (e) => {
    $('#vigencia-fecha-wrap').style.display = e.target.value === 'fecha' ? 'block' : 'none';
    $('#vigencia-custom-wrap').style.display = e.target.value === 'custom' ? 'block' : 'none';
  });
  $('#contactoSelect').addEventListener('change', (e) => {
    $('#contacto-custom-wrap').style.display = e.target.value === '__custom__' ? 'block' : 'none';
  });

  function collectBloques() {
    return $$('.bloque-card', bloquesList).map((card) => ({
      titulo: $('.bloque-titulo', card).value.trim(),
      icono: $('.bloque-icono', card).value,
      color: $('.bloque-color', card).value,
      vinetas: $('.bloque-vinetas', card).value.split('\n').map((v) => v.trim()).filter(Boolean),
    }));
  }
  function collectContacto() {
    const sel = $('#contactoSelect').value;
    if (sel === '__custom__') return $('#contactoCustom').value.trim();
    return sel || '';
  }
  function collectData() {
    return {
      titulo: $('#titulo').value.trim(),
      tituloResaltado: $('#tituloResaltado').value.trim(),
      bajada: $('#bajada').value.trim(),
      badgeType: $('#badgeType').value,
      bandera: $('#bandera').value,
      bloques: collectBloques(),
      vigencia: { tipo: $('#vigenciaTipo').value, fecha: $('#vigenciaFecha').value.trim(), custom: $('#vigenciaCustom').value.trim() },
      contacto: collectContacto(),
      notaCierre: $('#notaCierre').value.trim(),
    };
  }

  function showMsg(container, type, text) {
    container.innerHTML = `<div class="status-msg ${type}">${text}</div>`;
  }
  function clearMsg(container) {
    container.innerHTML = '';
  }

  // --- Estado del comunicado en curso ---
  let currentEsHtml = '';
  let currentEsHtmlWithPlaceholders = '';
  let currentSlug = 'comunicado';

  function slugify(str) {
    return (str || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').slice(0, 40) || 'comunicado';
  }

  function downloadBlob(content, filename, mime) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  // El HTML a exportar es un documento completo (<html><head>...) — para
  // que su propio <style>/<link> se apliquen de verdad (y no se pierdan al
  // meterlos como innerHTML de un <div>), se renderiza en un iframe aislado
  // con su propio document, y html2canvas captura el ".container" de ESE
  // document. Con timeout duro: si la fuente de Google Fonts no carga
  // (sin internet, firewall corporativo, etc.) la exportacion no debe
  // quedarse colgada para siempre.
  function withTimeout(promise, ms, message) {
    let timer;
    const timeout = new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(message)), ms);
    });
    return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
  }

  function renderInHiddenIframe(html) {
    // No se usa el evento "load" del iframe: ese evento espera a que
    // terminen TODOS los subrecursos (incluida la fuente de Google Fonts),
    // asi que si no hay internet nunca dispara. En vez de eso, se hace
    // polling de ".container" -- el parseo del DOM (que es lo unico que
    // necesita html2canvas) termina mucho antes que las fuentes externas.
    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.left = '-9999px';
    iframe.style.top = '0';
    iframe.style.width = '900px';
    iframe.style.height = '1400px';
    iframe.style.border = '0';
    iframe.srcdoc = html;
    document.body.appendChild(iframe);

    return new Promise((resolve, reject) => {
      const start = Date.now();
      const poll = () => {
        let doc;
        try {
          doc = iframe.contentDocument;
        } catch {
          doc = null;
        }
        if (doc && doc.querySelector('.container')) {
          resolve(iframe);
          return;
        }
        if (Date.now() - start > 8000) {
          reject(new Error('El documento a exportar tardó demasiado en cargar.'));
          return;
        }
        setTimeout(poll, 50);
      };
      poll();
    });
  }

  // Para la captura PNG se quita el <link> de Google Fonts: html2canvas
  // puede quedarse esperando minutos si esa fuente no carga (sin internet,
  // firewall corporativo, adblock). El HTML descargado normal SI la
  // conserva -- esto solo afecta la copia oculta usada para el PNG.
  function stripGoogleFontsLink(html) {
    return html.replace(/<link[^>]*fonts\.googleapis\.com[^>]*>/i, '');
  }

  async function downloadPng(html, filename, statusEl) {
    let iframe;
    try {
      iframe = await withTimeout(
        renderInHiddenIframe(stripGoogleFontsLink(html)),
        8000,
        'El documento a exportar tardó demasiado en cargar.'
      );
      const target = iframe.contentDocument.querySelector('.container');
      if (!target) throw new Error('No se encontró ".container" en el documento a exportar.');
      const canvas = await withTimeout(
        html2canvas(target, { scale: 3, backgroundColor: '#ffffff', useCORS: true }),
        15000,
        'La generación del PNG tardó demasiado (revisa tu conexión si usas Google Fonts).'
      );
      await new Promise((resolve) => {
        canvas.toBlob((blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          setTimeout(() => URL.revokeObjectURL(url), 2000);
          resolve();
        }, 'image/png');
      });
    } catch (err) {
      if (statusEl) showMsg(statusEl, 'error', 'No se pudo generar el PNG: ' + err.message);
    } finally {
      if (iframe) iframe.remove();
    }
  }

  // --- Generar ES ---
  $('#form-comunicado').addEventListener('submit', (e) => {
    e.preventDefault();
    const statusEl = $('#es-status-msg');
    clearMsg(statusEl);
    const data = collectData();
    if (!data.titulo) return showMsg(statusEl, 'error', 'El título del comunicado es obligatorio.');
    if (!data.bajada) return showMsg(statusEl, 'error', 'La bajada/subtítulo es obligatoria.');

    currentSlug = slugify(data.titulo);
    const rawHtml = buildComunicadoHtml(data);
    currentEsHtmlWithPlaceholders = rawHtml;
    currentEsHtml = resolveAssets(rawHtml, 'es').html;

    $('#es-preview-frame').srcdoc = currentEsHtml;
    $('#es-preview-section').style.display = 'block';
    showMsg(statusEl, 'ok', 'ES generado. Revisa el preview antes de traducir.');
    $('#es-preview-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  $('#btn-download-html-es').addEventListener('click', () => downloadBlob(currentEsHtml, `comunicado_${currentSlug}_es.html`, 'text/html'));
  $('#btn-download-png-es').addEventListener('click', (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    downloadPng(currentEsHtml, `comunicado_${currentSlug}_es.png`, $('#es-status-msg')).finally(() => (btn.disabled = false));
  });

  // --- Preparar traduccion (copy/paste manual, sin API) ---
  function strippedHtmlForPrompt() {
    // el HTML ya sale con __ASSET_LOGO__/__ASSET_WORDMARK__ en vez de
    // base64 -- eso es justo lo que se manda a traducir.
    return currentEsHtmlWithPlaceholders;
  }

  function setupTranslateLang(lang) {
    const btnPrepare = $(`#btn-prepare-${lang}`);
    const promptBox = $(`#prompt-${lang}`);
    const btnCopy = $(`#btn-copy-${lang}`);
    const pasteBox = $(`#paste-${lang}`);
    const btnRender = $(`#btn-render-${lang}`);
    const statusEl = $(`#status-${lang}`);
    const previewSection = $(`#preview-section-${lang}`);
    const frame = $(`#preview-frame-${lang}`);
    let finalHtml = '';

    btnPrepare.addEventListener('click', () => {
      if (!currentEsHtmlWithPlaceholders) {
        showMsg(statusEl, 'error', 'Primero genera el ES en la pestaña de arriba.');
        return;
      }
      const prompt = buildTranslationPrompt(strippedHtmlForPrompt(), lang);
      promptBox.value = prompt;
      promptBox.style.display = 'block';
      btnCopy.style.display = 'inline-flex';
      pasteBox.style.display = 'block';
      btnRender.style.display = 'inline-flex';
      clearMsg(statusEl);
    });

    btnCopy.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(promptBox.value);
        showMsg(statusEl, 'ok', 'Prompt copiado. Pégalo en una conversación nueva con Claude (claude.ai).');
      } catch {
        promptBox.select();
        showMsg(statusEl, 'warn', 'No se pudo copiar automático — el texto ya quedó seleccionado, usa Ctrl/Cmd+C.');
      }
    });

    btnRender.addEventListener('click', () => {
      const pasted = pasteBox.value.trim();
      if (!pasted) return showMsg(statusEl, 'error', 'Pega la respuesta de Claude primero.');
      if (!pasted.includes('__ASSET_LOGO__') || !pasted.includes('__ASSET_WORDMARK__')) {
        showMsg(statusEl, 'error', 'El HTML pegado no conserva los marcadores __ASSET_LOGO__/__ASSET_WORDMARK__ — revisa que hayas copiado la respuesta completa de Claude, sin recortar.');
        return;
      }
      const { html: withAssets, fellBack } = resolveAssets(pasted, lang);
      finalHtml = insertDisclaimer(withAssets, lang);
      frame.srcdoc = finalHtml;
      previewSection.style.display = 'block';
      const warn = fellBack ? ` (aviso: no hay wordmark propio para "${lang}", se usó el de ES como respaldo)` : '';
      showMsg(statusEl, 'ok', 'Preview generado.' + warn);
    });

    $(`#btn-download-html-${lang}`).addEventListener('click', () => {
      if (!finalHtml) return;
      downloadBlob(finalHtml, `comunicado_${currentSlug}_${lang}.html`, 'text/html');
    });
    $(`#btn-download-png-${lang}`).addEventListener('click', (e) => {
      if (!finalHtml) return;
      const btn = e.currentTarget;
      btn.disabled = true;
      downloadPng(finalHtml, `comunicado_${currentSlug}_${lang}.png`, statusEl).finally(() => (btn.disabled = false));
    });
  }
  setupTranslateLang('en');
  setupTranslateLang('pt');

  $('#btn-goto-translate').addEventListener('click', () => showView('view-translate'));
})();

(() => {
  'use strict';

  // ---------------------------------------------------------------------
  // Assets embebidos (inyectados por build.js como constantes globales
  // antes de este script).
  // ---------------------------------------------------------------------
  const LOGO_URI = window.ASSET_LOGO_URI;
  const WORDMARK_URI_BY_LANG = {
    es: window.ASSET_WORDMARK_ES_URI,
    en: window.ASSET_WORDMARK_EN_URI,
    pt: window.ASSET_WORDMARK_PT_URI,
  };

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
    buscar: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="${s}" stroke-width="1.8"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5" stroke="${s}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
    candado: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><rect x="4.5" y="11" width="15" height="10" rx="2" fill="none" stroke="${s}" stroke-width="1.8"/><path d="M7.5 11 V7.5 A4.5 4.5 0 0 1 16.5 7.5 V11" fill="none" stroke="${s}" stroke-width="1.8"/><circle cx="12" cy="15.7" r="1.4" fill="${s}"/></svg>`,
    megafono: (s) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 10 V14 H6.5 L14 18 V6 L6.5 10 Z" fill="none" stroke="${s}" stroke-width="1.8" stroke-linejoin="round"/><path d="M17 9.5 A4 4 0 0 1 17 14.5" fill="none" stroke="${s}" stroke-width="1.8" stroke-linecap="round"/><path d="M6.5 14 V18 A1.5 1.5 0 0 1 3.5 18 V14" fill="none" stroke="${s}" stroke-width="1.8"/></svg>`,
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
    nuevo_reporte: `<svg viewBox="0 0 24 24" width="13" height="13"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="#FFFFFF" stroke-width="2"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>`,
  };
  const BADGE_BG = { actualizacion: '#F26722', aviso: '#DC5D2E', recordatorio: '#1F2A44', nuevo_reporte: '#F26722' };
  const BADGE_LABEL = {
    es: { actualizacion: 'Actualización', aviso: 'Aviso', recordatorio: 'Recordatorio', nuevo_reporte: 'Nuevo Reporte' },
    en: { actualizacion: 'Update', aviso: 'Notice', recordatorio: 'Reminder', nuevo_reporte: 'New Report' },
    pt: { actualizacion: 'Atualização', aviso: 'Aviso', recordatorio: 'Lembrete', nuevo_reporte: 'Novo Relatório' },
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
  // banderas: [{code, label, custom}]. Los codigos con SVG propio (built-in)
  // se muestran como chip circular; los agregados por el usuario (sin SVG
  // real) se muestran como pill de texto -- se degrada bien sin inventar
  // una bandera que no existe.
  function renderFlagsRow(banderas) {
    if (!banderas || !banderas.length) return '';
    const chips = banderas
      .map((b) => {
        if (!b.custom && FLAGS[b.code]) return flagChip(b.code);
        return `<span style="display:inline-flex; align-items:center; padding:3px 10px; border-radius:999px; border:1px solid #E9EEF5; background:#F8FAFC; font-size:10.5px; font-weight:700; color:#475569; white-space:nowrap;">${escapeHtml(b.label)}</span>`;
      })
      .join('');
    return `<div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; justify-content:flex-end;">${chips}</div>`;
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
  // "impacto": callout chico (icono + "Etiqueta: texto") entre el titulo del
  // bloque y sus vinetas -- visto en comunicados reales para resaltar un
  // resultado/impacto puntual sin que se pierda entre las vinetas.
  function renderImpacto(impacto) {
    if (!impacto || !impacto.texto || !impacto.texto.trim()) return '';
    const etiqueta = (impacto.etiqueta || 'Impacto').trim();
    return `        <div style="background:#FFF9F5; border:1px solid #FCE4D2; border-radius:10px; padding:9px 13px; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
          <svg viewBox="0 0 24 24" width="16" height="16" style="flex-shrink:0;"><path d="M3 17 L9.5 10.5 L13.5 14.5 L21 6.5" fill="none" stroke="#F26722" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 6.5 H21 V12.5" fill="none" stroke="#F26722" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span style="font-size:12.5px; color:#475569; line-height:1.4;"><b style="color:#1F2A44;">${escapeHtml(etiqueta)}:</b> ${mdBold(impacto.texto)}</span>
        </div>`;
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
        const numHtml = bloque.sinNumero ? '' : `<div class="num">${i + 1}</div>`;
        return `      <!-- Tarjeta ${i + 1} -->
      <div class="card">
        <div style="display:flex; align-items:center; gap:9px; margin-bottom:9px;">
          ${numHtml}
          <div class="heading" style="font-size:15px; line-height:1.25;">${escapeHtml(bloque.titulo)}</div>
        </div>
${renderImpacto(bloque.impacto)}
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
  // Caja de contexto/alerta debajo de la bajada -- para el aviso corto que
  // explica "por qué" antes de entrar a las tarjetas (ej. la regla de
  // negocio que motiva el cambio).
  function renderNotaContexto(notaContexto) {
    if (!notaContexto || !notaContexto.trim()) return '';
    return `    <!-- Contexto -->
    <div style="margin:10px 30px 4px 30px; background:#FFF9F5; border:1px solid #FCE4D2; border-radius:14px; padding:16px; display:flex; gap:12px; align-items:flex-start;">
      <div style="width:40px; height:40px; background:#FEEDE2; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 2 C7.5 2 5 5 5 9 V14 L2.5 18 H21.5 L19 14 V9 C19 5 16.5 2 12 2 Z" fill="none" stroke="#F26722" stroke-width="1.8" stroke-linejoin="round"/><path d="M9.5 18 C9.5 20 10.5 21.2 12 21.2 C13.5 21.2 14.5 20 14.5 18" fill="none" stroke="#F26722" stroke-width="1.8" stroke-linecap="round"/></svg>
      </div>
      <div style="font-size:13.5px; color:#475569; line-height:1.6; padding-top:2px;">${mdBold(notaContexto)}</div>
    </div>`;
  }
  function renderVigenciaCard(vigencia) {
    if (!vigencia || !vigencia.tipo) return '';
    if (vigencia.tipo === 'acceso') {
      if (!vigencia.custom || !vigencia.custom.trim()) return '';
      return `      <div style="flex:1; background:#FFF9F5; border:1px solid #FCE4D2; border-radius:14px; padding:16px; display:flex; gap:12px; align-items:center;">
        <div style="width:44px; height:44px; background:#FEEDE2; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
          <svg viewBox="0 0 24 24" width="22" height="22"><rect x="4.5" y="11" width="15" height="10" rx="2" fill="none" stroke="#F26722" stroke-width="1.8"/><path d="M7.5 11 V7.5 A4.5 4.5 0 0 1 16.5 7.5 V11" fill="none" stroke="#F26722" stroke-width="1.8"/><circle cx="12" cy="15.7" r="1.4" fill="#F26722"/></svg>
        </div>
        <div style="flex:1;">
          <div style="font-size:11.5px; color:#F26722; font-weight:900; letter-spacing:.6px; text-transform:uppercase; margin-bottom:5px;">${escapeHtml(vigencia.etiqueta || 'Acceso')}</div>
          <div style="font-size:13px; color:#475569; line-height:1.5;">${mdBold(vigencia.custom)}</div>
        </div>
      </div>`;
    }
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
  function renderContactoCard(contacto, contactoHeader) {
    if (!contacto) return '';
    const header = (contactoHeader && contactoHeader.trim()) || '¿TIENES DUDAS?';
    return `      <div style="flex:1; background:#F1F8F3; border:1px solid #D6EADD; border-radius:14px; padding:16px; display:flex; gap:12px; align-items:center;">
        <div style="width:44px; height:44px; background:#E1F0E6; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
          <svg viewBox="0 0 24 24" width="24" height="24"><path d="M4 13 V11 A8 8 0 0 1 20 11 V13" fill="none" stroke="#0F7A43" stroke-width="2" stroke-linecap="round"/><rect x="2.5" y="12" width="4.5" height="7" rx="2" fill="none" stroke="#0F7A43" stroke-width="2"/><rect x="17" y="12" width="4.5" height="7" rx="2" fill="none" stroke="#0F7A43" stroke-width="2"/><path d="M19.2 19 V20 A3 3 0 0 1 16.2 23 H13.5" fill="none" stroke="#0F7A43" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <div style="flex:1;">
          <div style="font-size:11.5px; color:#0F7A43; font-weight:900; letter-spacing:.6px; text-transform:uppercase; margin-bottom:5px;">${escapeHtml(header)}</div>
          <div style="font-size:13px; color:#475569; line-height:1.5;">
            Repórtalas directamente a <b style="color:#1F2A44;">${escapeHtml(contacto)}</b>.
          </div>
        </div>
      </div>`;
  }
  function renderVigenciaDudasRow(vigencia, contacto, contactoHeader) {
    const v = renderVigenciaCard(vigencia);
    const c = renderContactoCard(contacto, contactoHeader);
    if (!v && !c) return '';
    return `    <!-- Vigencia + Dudas -->
    <div style="padding:14px 30px 16px 30px; display:flex; gap:14px;">
${[v, c].filter(Boolean).join('\n')}
    </div>`;
  }
  // notaCierre puede ser un string (nota gris simple, comportamiento
  // original) o { texto, icono: 'megafono'|'' } para la variante con
  // icono en caja -- vista en comunicados reales que cierran invitando a
  // seguir los proximos avisos.
  function renderNotaCierre(nota) {
    const texto = typeof nota === 'string' ? nota : nota && nota.texto;
    const icono = typeof nota === 'object' && nota ? nota.icono : '';
    if (!texto || !texto.trim()) return '';
    if (icono && ICONS[icono]) {
      return `    <!-- Nota de cierre -->
    <div style="margin:0 30px 16px 30px; background:#FFFFFF; border:1px solid #E9EEF5; border-radius:12px; padding:14px 16px; display:flex; gap:12px; align-items:center;">
      <div style="width:40px; height:40px; background:#FEEDE2; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        ${ICONS[icono]('#F26722').replace('width="22" height="22"', 'width="20" height="20"')}
      </div>
      <div style="font-size:12.5px; color:#64748B; line-height:1.6;">${mdBold(texto)}</div>
    </div>`;
    }
    return `    <!-- Nota de cierre -->
    <div style="margin:0 30px 16px 30px; background:#F8FAFC; border:1px solid #E9EEF5; border-radius:12px; padding:12px 16px; font-size:12px; color:#64748B; line-height:1.6;">${mdBold(texto)}</div>`;
  }

  function renderHeaderKicker(kicker) {
    if (!kicker || !kicker.trim()) return '';
    return `<div style="display:flex; align-items:center; gap:12px; padding-left:12px; margin-left:2px; border-left:1px solid #E2E8F0;">
          <div>
            <div style="font-size:10.5px; color:#94A3B8; letter-spacing:1.5px; text-transform:uppercase; font-weight:700;">Comunicado</div>
            <div class="heading" style="font-size:19px; color:#F26722; line-height:1.1;">${escapeHtml(kicker)}</div>
          </div>
        </div>`;
  }

  function buildComunicadoHtml(data) {
    const { titulo, tituloResaltado, bajada, badgeType, banderas, bloques, vigencia, contacto, contactoHeader, notaCierre, notaContexto, headerKicker } = data;
    const flagHtml = renderFlagsRow(banderas);
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
        <img src="[[ASSET_LOGO]]" alt="Guepardo" style="height:64px; width:auto; display:block;">
        [[WORDMARK_ELEMENT]]
        ${renderHeaderKicker(headerKicker)}
      </div>
      <div style="display:flex; align-items:center; gap:10px;">
        ${flagHtml}
        ${renderBadge(badgeType, 'es')}
      </div>
    </div>

    <!-- Título -->
    <div style="padding:6px 30px 4px 30px;">
      <div class="heading" style="font-size:32px; line-height:1.15; margin-bottom:8px;">${renderTitulo(titulo, tituloResaltado)}</div>
      <div style="font-size:13.5px; color:#475569; line-height:1.5; max-width:640px;">${mdBold(bajada)}</div>
    </div>

${renderNotaContexto(notaContexto)}

${renderBloques(bloques)}

${renderVigenciaDudasRow(vigencia, contacto, contactoHeader)}

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
  // Placeholders de imagen: la plantilla arriba ya sale con [[ASSET_LOGO]]
  // y [[WORDMARK_ELEMENT]] en vez de base64 -- se resuelven aqui mismo
  // (nunca se manda un base64 de 100KB+ a Claude al preparar la
  // traduccion). Se usan corchetes dobles y NO guiones bajos dobles
  // porque "__texto__" es sintaxis markdown de negrita: si el marcador
  // pasara por un renderer de markdown (como el chat de claude.ai) los
  // guiones bajos se pierden y el marcador queda roto sin que se note.
  //
  // El wordmark ("Lo Mejoramos Juntos") tiene su propio PNG/JPG real por
  // idioma (ES/EN/PT, en /assets). Si algun dia se agrega un idioma sin
  // asset todavia, se genera un SVG de respaldo con el mismo estilo (dos
  // lineas, segunda linea en naranja bold, swoosh debajo) en vez de
  // reusar el de español o dejarlo en blanco.
  // ---------------------------------------------------------------------
  const WORDMARK_ALT = {
    es: 'Lo Mejoramos Juntos',
    en: 'We Improve Together',
    pt: 'Melhoramos Juntos',
  };
  const WORDMARK_TEXT_FALLBACK = {
    en: ['We Improve', 'Together'],
    pt: ['Melhoramos', 'Juntos'],
  };
  function buildWordmarkSvg(line1, line2) {
    return `<svg viewBox="0 0 340 118" height="46" style="display:block;" xmlns="http://www.w3.org/2000/svg">
          <text x="2" y="34" font-family="'Poppins','Segoe UI',Arial,sans-serif" font-weight="700" font-size="30" fill="#0A2540">${escapeHtml(line1)}</text>
          <text x="0" y="90" font-family="'Poppins','Segoe UI',Arial,sans-serif" font-weight="900" font-size="56" fill="#F26722">${escapeHtml(line2)}</text>
          <path d="M4 101 Q 170 118 336 96" stroke="#F26722" stroke-width="4" fill="none" stroke-linecap="round"/>
        </svg>`;
  }
  function resolveAssets(html, lang) {
    let wordmarkHtml;
    const realUri = WORDMARK_URI_BY_LANG[lang];
    if (realUri) {
      wordmarkHtml = `<img src="${realUri}" alt="${escapeHtml(WORDMARK_ALT[lang] || WORDMARK_ALT.es)}" style="height:46px; width:auto; display:block;">`;
    } else if (WORDMARK_TEXT_FALLBACK[lang]) {
      const [l1, l2] = WORDMARK_TEXT_FALLBACK[lang];
      wordmarkHtml = buildWordmarkSvg(l1, l2);
    } else {
      wordmarkHtml = `<img src="${WORDMARK_URI_BY_LANG.es}" alt="${escapeHtml(WORDMARK_ALT.es)}" style="height:46px; width:auto; display:block;">`;
    }
    const resolved = html.split('[[ASSET_LOGO]]').join(LOGO_URI).split('[[WORDMARK_ELEMENT]]').join(wordmarkHtml);
    return { html: resolved, fellBack: false };
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
- El marcador literal [[ASSET_LOGO]] (dentro de un atributo src) y el marcador [[WORDMARK_ELEMENT]] (solo en su propia línea, reemplaza a una imagen) deben quedar EXACTAMENTE igual, en su misma posición. No los traduzcas, no los muevas, no los elimines, no les quites ni agregues corchetes.
- No agregues comentarios, explicaciones, notas ni bloques de código markdown (nada de \`\`\`). Responde ÚNICAMENTE con el HTML completo, empezando en "<!DOCTYPE html>" y terminando en "</html>", sin nada antes ni después.`;

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
  $('#card-comunicado').addEventListener('click', () => showView('view-templates'));
  $('#back-from-templates').addEventListener('click', (e) => { e.preventDefault(); showView('view-selector'); });
  $('#back-from-comunicado').addEventListener('click', (e) => { e.preventDefault(); showView('view-templates'); });

  // ---------------------------------------------------------------------
  // Listas editables con guardado en localStorage: países y contactos
  // vienen precargados, y lo que se agrega vía "+ Agregar" queda guardado
  // para la próxima vez que se abra esta misma herramienta en este
  // navegador (no hay backend -- el archivo vive solo, así que el
  // guardado es local al navegador que lo abre).
  // ---------------------------------------------------------------------
  const STORAGE_KEYS = { paises: 'guepardo_paises_custom_v1', contactos: 'guepardo_contactos_custom_v1' };

  function loadCustomList(key) {
    try {
      const raw = localStorage.getItem(key);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
  function saveCustomList(key, list) {
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch {
      // localStorage puede fallar (modo privado, storage lleno, etc.) --
      // la opción agregada sigue funcionando en esta sesión, solo no
      // sobrevive a un reload. No es motivo para romper la herramienta.
    }
  }

  // --- Países (multi-select con chips + agregar nuevo) ---
  const BUILTIN_PAISES = Object.keys(FLAGS).map((code) => ({ code, label: FLAGS[code].label, custom: false }));
  function getAllPaises() {
    const custom = loadCustomList(STORAGE_KEYS.paises);
    return [...BUILTIN_PAISES, ...custom.map((p) => ({ ...p, custom: true }))];
  }
  function addCustomPais(rawLabel) {
    const label = (rawLabel || '').trim();
    if (!label) return null;
    const all = getAllPaises();
    const existing = all.find((p) => p.label.toLowerCase() === label.toLowerCase());
    if (existing) return existing;
    const codes = new Set(all.map((p) => p.code));
    let code = slugify(label) || 'pais';
    let n = 1;
    while (codes.has(code)) code = `${slugify(label) || 'pais'}-${++n}`;
    const entry = { code, label };
    const custom = loadCustomList(STORAGE_KEYS.paises);
    custom.push(entry);
    saveCustomList(STORAGE_KEYS.paises, custom);
    return { ...entry, custom: true };
  }

  const paisesListEl = $('#paises-list');
  const selectedPaisCodes = new Set();
  function renderPaisesChecks() {
    const all = getAllPaises();
    paisesListEl.innerHTML = all
      .map(
        (p) => `<label class="chip-check${selectedPaisCodes.has(p.code) ? ' checked' : ''}">
          <input type="checkbox" value="${escapeHtml(p.code)}" ${selectedPaisCodes.has(p.code) ? 'checked' : ''}>
          ${escapeHtml(p.label)}
        </label>`
      )
      .join('');
    $$('input[type="checkbox"]', paisesListEl).forEach((cb) => {
      cb.addEventListener('change', () => {
        if (cb.checked) selectedPaisCodes.add(cb.value);
        else selectedPaisCodes.delete(cb.value);
        cb.closest('.chip-check').classList.toggle('checked', cb.checked);
        refreshPreview();
      });
    });
  }
  $('#btn-add-pais').addEventListener('click', () => {
    const input = $('#paisNuevoInput');
    const entry = addCustomPais(input.value);
    if (!entry) return;
    input.value = '';
    selectedPaisCodes.add(entry.code);
    renderPaisesChecks();
    refreshPreview();
  });
  $('#paisNuevoInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      $('#btn-add-pais').click();
    }
  });
  function collectBanderas() {
    const all = getAllPaises();
    return all.filter((p) => selectedPaisCodes.has(p.code)).map((p) => ({ code: p.code, label: p.label, custom: p.custom }));
  }

  // --- Contacto de dudas (select editable con agregar nuevo) ---
  const BUILTIN_CONTACTOS = ['Reyna Olmeda', 'Aida Treviño'];
  function getAllContactos() {
    return [...BUILTIN_CONTACTOS, ...loadCustomList(STORAGE_KEYS.contactos)];
  }
  function addCustomContacto(rawName) {
    const name = (rawName || '').trim();
    if (!name) return null;
    const all = getAllContactos();
    const existing = all.find((c) => c.toLowerCase() === name.toLowerCase());
    if (existing) return existing;
    const custom = loadCustomList(STORAGE_KEYS.contactos);
    custom.push(name);
    saveCustomList(STORAGE_KEYS.contactos, custom);
    return name;
  }
  const contactoSelectEl = $('#contactoSelect');
  function renderContactoOptions(selectValue) {
    const all = getAllContactos();
    contactoSelectEl.innerHTML = [
      '<option value="">— Omitir esta sección —</option>',
      ...all.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`),
      '<option value="__add__">+ Agregar nuevo...</option>',
    ].join('');
    if (selectValue !== undefined) contactoSelectEl.value = selectValue;
  }
  renderContactoOptions('');
  contactoSelectEl.addEventListener('change', () => {
    if (contactoSelectEl.value === '__add__') {
      $('#contacto-add-wrap').style.display = 'flex';
      $('#contactoNuevoInput').focus();
    } else {
      $('#contacto-add-wrap').style.display = 'none';
      refreshPreview();
    }
  });
  $('#btn-add-contacto').addEventListener('click', () => {
    const input = $('#contactoNuevoInput');
    const name = addCustomContacto(input.value);
    if (!name) return;
    input.value = '';
    $('#contacto-add-wrap').style.display = 'none';
    renderContactoOptions(name);
    refreshPreview();
  });
  $('#contactoNuevoInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      $('#btn-add-contacto').click();
    }
  });
  function collectContacto() {
    const v = contactoSelectEl.value;
    return v === '__add__' ? '' : v;
  }

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
  function addBloque(preset) {
    preset = preset || {};
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
      <textarea class="bloque-vinetas" placeholder="Nuevo flujo dedicado para la creación de **Showrooms**...&#10;Autoriza el **Country Manager**..."></textarea>
      <label>Impacto <span class="hint">(opcional — resultado destacado en su propio recuadro)</span></label>
      <input type="text" class="bloque-impacto" placeholder="Ej. Asignación más equitativa y eficiente.">
      <label class="chip-check" style="margin-top:10px;"><input type="checkbox" class="bloque-sin-numero"> Sin numeración (para bloques únicos)</label>`;
    card.querySelector('.bloque-remove').addEventListener('click', () => {
      card.remove();
      refreshPreview();
    });
    if (preset.titulo) $('.bloque-titulo', card).value = preset.titulo;
    if (preset.icono) $('.bloque-icono', card).value = preset.icono;
    if (preset.color) $('.bloque-color', card).value = preset.color;
    if (preset.vinetas) $('.bloque-vinetas', card).value = preset.vinetas.join('\n');
    if (preset.impacto) $('.bloque-impacto', card).value = preset.impacto;
    if (preset.sinNumero) $('.bloque-sin-numero', card).checked = true;
    $$('input, select, textarea', card).forEach((field) => {
      field.addEventListener('input', refreshPreview);
      field.addEventListener('change', refreshPreview);
    });
    bloquesList.appendChild(card);
  }
  $('#btn-add-bloque').addEventListener('click', () => {
    addBloque();
    refreshPreview();
  });
  addBloque();

  $('#titulo').addEventListener('input', (e) => {
    const words = e.target.value.trim().split(/\s+/).filter(Boolean).length;
    const el = $('#titulo-count');
    el.textContent = e.target.value.trim() ? `${words} palabra${words === 1 ? '' : 's'}${words > 10 ? ' — considera acortar' : ''}` : '';
    el.style.color = words > 10 ? '#B23A12' : '#94A3B8';
  });

  $('#vigenciaTipo').addEventListener('change', (e) => {
    $('#vigencia-fecha-wrap').style.display = e.target.value === 'fecha' ? 'block' : 'none';
    $('#vigencia-custom-wrap').style.display = e.target.value === 'custom' || e.target.value === 'acceso' ? 'block' : 'none';
    $('#vigencia-etiqueta-wrap').style.display = e.target.value === 'acceso' ? 'block' : 'none';
    $('#vigenciaCustom').placeholder = e.target.value === 'acceso'
      ? 'Ej. Asignado a Jefes de Compra y Compradores de Revestimientos.'
      : 'Ej. Vigente **solo** para Revestimientos.';
  });

  [
    'titulo', 'tituloResaltado', 'bajada', 'badgeType', 'headerKicker', 'notaContexto',
    'vigenciaTipo', 'vigenciaFecha', 'vigenciaCustom', 'vigenciaEtiqueta', 'contactoHeader',
    'notaCierre', 'notaCierreIcono',
  ].forEach((id) => {
    const el = $(`#${id}`);
    el.addEventListener('input', refreshPreview);
    el.addEventListener('change', refreshPreview);
  });

  function collectBloques() {
    return $$('.bloque-card', bloquesList).map((card) => ({
      titulo: $('.bloque-titulo', card).value.trim(),
      icono: $('.bloque-icono', card).value,
      color: $('.bloque-color', card).value,
      vinetas: $('.bloque-vinetas', card).value.split('\n').map((v) => v.trim()).filter(Boolean),
      sinNumero: $('.bloque-sin-numero', card).checked,
      impacto: { etiqueta: 'Impacto', texto: $('.bloque-impacto', card).value.trim() },
    }));
  }
  function collectData() {
    return {
      titulo: $('#titulo').value.trim(),
      tituloResaltado: $('#tituloResaltado').value.trim(),
      bajada: $('#bajada').value.trim(),
      badgeType: $('#badgeType').value,
      banderas: collectBanderas(),
      headerKicker: $('#headerKicker').value.trim(),
      notaContexto: $('#notaContexto').value.trim(),
      bloques: collectBloques(),
      vigencia: {
        tipo: $('#vigenciaTipo').value,
        fecha: $('#vigenciaFecha').value.trim(),
        custom: $('#vigenciaCustom').value.trim(),
        etiqueta: $('#vigenciaEtiqueta').value.trim(),
      },
      contacto: collectContacto(),
      contactoHeader: $('#contactoHeader').value.trim(),
      notaCierre: { texto: $('#notaCierre').value.trim(), icono: $('#notaCierreIcono').checked ? 'megafono' : '' },
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

  // El documento real mide 820px de ancho -- para que quepa en una tarjeta
  // angosta (barra lateral del preview en vivo, o la tarjeta de preview de
  // EN/PT) se renderiza a tamaño natural dentro del iframe y se escala
  // hacia abajo con CSS transform, igual que un "zoom to fit". Se hace con
  // polling de ".container" (no con el evento "load") para no depender de
  // que Google Fonts termine de cargar. Encontrar ".container" no basta:
  // en el primer tick puede existir el nodo pero no todo su contenido
  // (bloques/vigencia/footer) todavia insertado/layouteado -- por eso se
  // exige que la altura medida se repita en dos ticks seguidos antes de
  // darla por buena (si no, se mide a mitad de parseo y sale recortada).
  function fitScaledIframe(iframe, wrap, tries, lastHeight) {
    tries = tries || 0;
    let doc;
    try {
      doc = iframe.contentDocument;
    } catch {
      doc = null;
    }
    const el = doc && doc.querySelector('.container');
    const h = el ? Math.ceil(el.getBoundingClientRect().height) : 0;
    if (h > 0 && h === lastHeight) {
      const naturalHeight = h + 48;
      const scale = wrap.clientWidth > 0 ? wrap.clientWidth / 820 : 1;
      iframe.style.width = '820px';
      iframe.style.height = `${naturalHeight}px`;
      iframe.style.transform = `scale(${scale})`;
      wrap.style.height = `${Math.max(120, Math.round(naturalHeight * scale))}px`;
      return;
    }
    if (tries < 80) setTimeout(() => fitScaledIframe(iframe, wrap, tries + 1, h), 40);
  }
  window.addEventListener('resize', () => {
    fitScaledIframe($('#es-preview-frame'), $('#preview-scale-wrap'));
    ['en', 'pt'].forEach((lang) => {
      const wrap = $(`#preview-scale-wrap-${lang}`);
      if (wrap && wrap.offsetParent) fitScaledIframe($(`#preview-frame-${lang}`), wrap);
    });
  });

  // El preview de la derecha se actualiza mientras se escribe (debounced,
  // no en cada tecla) -- así se ve dónde va cada cosa sin tener que
  // generar/regenerar a mano.
  let previewDebounce;
  function refreshPreview() {
    clearTimeout(previewDebounce);
    previewDebounce = setTimeout(() => {
      const data = collectData();
      currentSlug = slugify(data.titulo);
      const rawHtml = buildComunicadoHtml(data);
      currentEsHtmlWithPlaceholders = rawHtml;
      currentEsHtml = resolveAssets(rawHtml, 'es').html;
      const frame = $('#es-preview-frame');
      frame.srcdoc = currentEsHtml;
      fitScaledIframe(frame, $('#preview-scale-wrap'));
    }, 200);
  }

  function validateMinimal() {
    const statusEl = $('#es-status-msg');
    const data = collectData();
    if (!data.titulo) {
      showMsg(statusEl, 'error', 'El título del comunicado es obligatorio.');
      return false;
    }
    if (!data.bajada) {
      showMsg(statusEl, 'error', 'La bajada/subtítulo es obligatoria.');
      return false;
    }
    clearMsg(statusEl);
    return true;
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

  // El <form> ya no se "envía" -- el preview es continuo. Se evita igual
  // el submit nativo (Enter dentro de un input) por si acaso.
  $('#form-comunicado').addEventListener('submit', (e) => e.preventDefault());

  $('#btn-download-html-es').addEventListener('click', () => {
    if (!validateMinimal()) return;
    downloadBlob(currentEsHtml, `comunicado_${currentSlug}_es.html`, 'text/html');
  });
  $('#btn-download-png-es').addEventListener('click', (e) => {
    if (!validateMinimal()) return;
    const btn = e.currentTarget;
    btn.disabled = true;
    downloadPng(currentEsHtml, `comunicado_${currentSlug}_es.png`, $('#es-status-msg')).finally(() => (btn.disabled = false));
  });

  // --- Preparar traduccion (copy/paste manual, sin API) ---
  function strippedHtmlForPrompt() {
    // el HTML ya sale con [[ASSET_LOGO]]/[[WORDMARK_ELEMENT]] en vez de
    // base64 -- eso es justo lo que se manda a traducir.
    return currentEsHtmlWithPlaceholders;
  }

  // Claude casi siempre envuelve el HTML en un bloque ```html ... ``` al
  // responder en el chat (por mas que el prompt pida no hacerlo), y a
  // veces agrega una frase antes o despues ("Aqui esta la traduccion:").
  // Si el usuario pega la respuesta completa tal cual, eso queda pegado
  // antes de "<!DOCTYPE html>" y rompe el documento (el <head>/<style> ya
  // no aplican bien porque el parser HTML los ve despues de texto suelto
  // en el body). Esta funcion limpia todo eso antes de usar el HTML.
  function cleanPastedHtml(text) {
    let t = (text || '').trim();
    const fenced = t.match(/^```[a-z]*\s*([\s\S]*?)\s*```$/i);
    if (fenced) t = fenced[1].trim();
    const startMatch = t.match(/<!doctype\s+html[^>]*>/i) || t.match(/<html[\s>]/i);
    const start = startMatch ? t.indexOf(startMatch[0]) : -1;
    const end = t.toLowerCase().lastIndexOf('</html>');
    if (start !== -1 && end !== -1 && end > start) {
      t = t.slice(start, end + '</html>'.length);
    }
    return t;
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
      const raw = pasteBox.value.trim();
      if (!raw) return showMsg(statusEl, 'error', 'Pega la respuesta de Claude primero.');
      const pasted = cleanPastedHtml(raw);
      if (!pasted.includes('<!DOCTYPE') && !pasted.toLowerCase().includes('<!doctype')) {
        showMsg(statusEl, 'error', 'No se encontró un documento HTML completo en lo que pegaste — revisa que hayas copiado toda la respuesta de Claude de principio a fin, no solo un fragmento.');
        return;
      }
      if (!pasted.includes('[[ASSET_LOGO]]') || !pasted.includes('[[WORDMARK_ELEMENT]]')) {
        showMsg(statusEl, 'error', 'El HTML pegado no conserva los marcadores [[ASSET_LOGO]]/[[WORDMARK_ELEMENT]] — Claude pudo haberlos alterado al traducir. Pídele que responda de nuevo dejando esos marcadores exactamente igual, entre corchetes dobles.');
        return;
      }
      const { html: withAssets } = resolveAssets(pasted, lang);
      finalHtml = insertDisclaimer(withAssets, lang);
      previewSection.style.display = 'block';
      frame.srcdoc = finalHtml;
      fitScaledIframe(frame, $(`#preview-scale-wrap-${lang}`));
      showMsg(statusEl, 'ok', 'Preview generado.');
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

  $('#btn-goto-translate').addEventListener('click', () => {
    if (!validateMinimal()) return;
    showView('view-translate');
  });

  // ---------------------------------------------------------------------
  // Plantillas: puntos de partida basados en comunicados reales -- se
  // eligen antes del formulario y precargan todos los campos (incluidos
  // los nuevos: contexto, impacto, sin numeración, acceso, header kicker,
  // nota de cierre con ícono). El usuario edita todo después.
  // ---------------------------------------------------------------------
  const TEMPLATES = [
    {
      id: 'nuevo-reporte',
      nombre: 'Nuevo reporte / herramienta',
      descripcion: 'Anuncia una herramienta nueva que resuelve una tarea manual, con el motivo (contexto) y quién tiene acceso.',
      data: {
        titulo: 'Proveedor por proveedor, SAP ya lo hizo por ti',
        tituloResaltado: '',
        bajada: 'Un nuevo reporte (**ZMM_BLOQ_PROV**) en **SAP ECC/S4H** identifica en un clic a los proveedores inactivos que deben bloquearse.',
        badgeType: 'nuevo_reporte',
        headerKicker: 'GUEPARDO',
        banderas: [],
        notaContexto: 'La **Matriz de Control Compras** exige bloquear proveedores sin operación durante **18 meses**. Hasta ahora, el Responsable del Maestro de Proveedores debía identificarlos uno por uno, de forma manual.',
        bloques: [
          {
            titulo: 'El reporte hace la búsqueda por ti',
            icono: 'check',
            color: 'verde',
            sinNumero: true,
            impacto: '',
            vinetas: [
              'El reporte sugiere proveedores sin actividad en el periodo de días que tú defines, revisando:',
              'Sin **órdenes de compra vigentes**',
              'Sin **entrada de mercancía pendiente**',
              'Sin **pendiente de registro de factura**',
            ],
          },
        ],
        vigencia: { tipo: 'acceso', etiqueta: 'Acceso', custom: 'Asignado a **Jefes de Compra** y **Compradores de Revestimientos**.' },
        contacto: 'Reyna Olmeda',
        contactoHeader: '',
        notaCierre: { texto: '', icono: '' },
      },
    },
    {
      id: 'actualizacion-dos-bloques',
      nombre: 'Actualización con dos ajustes',
      descripcion: 'Dos cambios relacionados en un mismo comunicado, cada uno con su propio ícono y color.',
      data: {
        titulo: 'Una cosa menos que subir a SAPI',
        tituloResaltado: 'Una cosa menos',
        bajada: 'Ajustes en documentos soporte y herramientas de captura de inversiones.',
        badgeType: 'actualizacion',
        headerKicker: '',
        banderas: [],
        notaContexto: '',
        bloques: [
          {
            titulo: 'Documentos de soporte para inversiones menores',
            icono: 'documento',
            color: 'verde',
            sinNumero: false,
            impacto: '',
            vinetas: [
              '**Plan de Negocio** opcional en inversiones menores a $20,000 USD.',
              'El **Calendario de Pagos** se sustituye: Administración y Finanzas debe notificar a Tesorería Corporativa los desembolsos de inversión con **al menos 3 meses de anticipación**.',
              'Basta **una cotización base** con oferta técnica.',
            ],
          },
          {
            titulo: 'Herramientas de captura',
            icono: 'tendencia',
            color: 'naranja',
            sinNumero: false,
            impacto: '',
            vinetas: [
              'Nuevos formatos de Plan de Negocio por subcategoría y guía del **Modelo Económico**, disponibles en **Ayudas** del Sistema Ebavel.',
            ],
          },
        ],
        vigencia: { tipo: 'vigente' },
        contacto: 'Reyna Olmeda',
        contactoHeader: '',
        notaCierre: { texto: '', icono: '' },
      },
    },
    {
      id: 's4h-cuotas',
      nombre: 'Funcionalidad ya activa (con impacto)',
      descripcion: 'Un solo bloque sin numerar, con un impacto destacado y nota de cierre invitando a los próximos comunicados.',
      data: {
        titulo: 'S4H – Cuotas para Asignación',
        tituloResaltado: '',
        bajada: 'El sistema distribuye automáticamente el inventario disponible, entre las áreas de venta y los clientes que comparten un mismo producto para la clase de documento ZNA2.',
        badgeType: 'actualizacion',
        headerKicker: 'GUEPARDO',
        banderas: [{ code: 'mx', label: 'México' }],
        notaContexto: '',
        bloques: [
          {
            titulo: 'Determinación del Inventario',
            icono: 'check',
            color: 'naranja',
            sinNumero: true,
            impacto: 'asignación más equitativa y eficiente de productos compartidos entre marcas.',
            vinetas: [
              'Se establece una **cuota (% de asignación)** para las áreas de venta que comparten un mismo producto (SKU).',
              'El **pronóstico de cliente** reparte ese inventario entre los clientes de la misma **organización de venta**: si el material tiene cuota, esa cantidad es la base; si no, no hay restricción.',
              'Se definen **prioridades** que establecen la secuencia para confirmar inventario en los pedidos, por área de venta.',
            ],
          },
        ],
        vigencia: { tipo: 'custom', custom: 'Esta funcionalidad ya está **activa en S4H.**' },
        contacto: 'Aida Treviño y Reyna Olmeda',
        contactoHeader: 'SI TIENES DUDAS',
        notaCierre: {
          texto: 'Esta es solo una de las actualizaciones implementadas en nuestros sistemas. Sigue nuestros próximos **comunicados** para conocer las siguientes mejoras.',
          icono: 'megafono',
        },
      },
    },
  ];

  function setVal(id, val) {
    const el = $(`#${id}`);
    if (el) el.value = val || '';
  }

  function loadTemplateData(data) {
    setVal('titulo', data.titulo);
    setVal('tituloResaltado', data.tituloResaltado);
    setVal('bajada', data.bajada);
    setVal('badgeType', data.badgeType || 'actualizacion');
    setVal('headerKicker', data.headerKicker);
    setVal('notaContexto', data.notaContexto);
    setVal('vigenciaFecha', data.vigencia && data.vigencia.fecha);
    setVal('vigenciaCustom', data.vigencia && data.vigencia.custom);
    setVal('vigenciaEtiqueta', data.vigencia && data.vigencia.etiqueta);
    setVal('vigenciaTipo', (data.vigencia && data.vigencia.tipo) || '');
    $('#vigenciaTipo').dispatchEvent(new Event('change'));
    setVal('contactoHeader', data.contactoHeader);
    setVal('notaCierre', (data.notaCierre && data.notaCierre.texto) || '');
    $('#notaCierreIcono').checked = Boolean(data.notaCierre && data.notaCierre.icono);

    selectedPaisCodes.clear();
    (data.banderas || []).forEach((b) => {
      let entry = getAllPaises().find((p) => p.code === b.code || p.label === b.label);
      if (!entry) entry = addCustomPais(b.label);
      if (entry) selectedPaisCodes.add(entry.code);
    });
    renderPaisesChecks();

    if (data.contacto && !getAllContactos().includes(data.contacto)) addCustomContacto(data.contacto);
    renderContactoOptions(data.contacto || '');

    bloquesList.innerHTML = '';
    (data.bloques && data.bloques.length ? data.bloques : [{}]).forEach((b) => addBloque(b));

    $('#titulo').dispatchEvent(new Event('input'));
    refreshPreview();
  }

  const templateGrid = $('#template-grid');
  function renderTemplateGrid() {
    templateGrid.innerHTML = '';

    TEMPLATES.forEach((tpl) => {
      const card = document.createElement('div');
      card.className = 'template-card';
      card.innerHTML = `
        <div class="template-thumb"><div class="preview-scale-wrap" style="height:100%;"><iframe style="pointer-events:none;"></iframe></div></div>
        <div class="template-body">
          <h3>${escapeHtml(tpl.nombre)}</h3>
          <p>${escapeHtml(tpl.descripcion)}</p>
          <button type="button" class="btn btn-primary btn-sm" style="justify-content:center;">Usar esta plantilla</button>
        </div>`;
      const iframe = card.querySelector('iframe');
      const wrap = card.querySelector('.preview-scale-wrap');
      const rawHtml = buildComunicadoHtml(tpl.data);
      iframe.srcdoc = resolveAssets(rawHtml, 'es').html;
      fitScaledIframe(iframe, wrap);
      card.querySelector('button').addEventListener('click', () => {
        showView('view-comunicado');
        loadTemplateData(tpl.data);
      });
      templateGrid.appendChild(card);
    });

    const blank = document.createElement('div');
    blank.className = 'template-card blank';
    blank.innerHTML = `
      <div class="template-thumb">
        <svg viewBox="0 0 24 24" width="40" height="40"><path d="M12 5 V19 M5 12 H19" fill="none" stroke="#CBD5E1" stroke-width="1.8" stroke-linecap="round"/></svg>
      </div>
      <div class="template-body">
        <h3>Empezar en blanco</h3>
        <p>Formulario vacío, sin contenido de ejemplo.</p>
        <button type="button" class="btn btn-ghost btn-sm" style="justify-content:center;">Empezar en blanco</button>
      </div>`;
    blank.querySelector('button').addEventListener('click', () => {
      showView('view-comunicado');
      loadTemplateData({ bloques: [{}] });
    });
    templateGrid.appendChild(blank);
  }
  renderTemplateGrid();

  // --- Arranque: precargar países/contactos guardados y pintar el
  // preview en vivo desde el primer instante (aunque esté vacío, ya se ve
  // la estructura del comunicado). ---
  renderPaisesChecks();
  refreshPreview();
})();

(() => {
  const ICON_OPTIONS = [
    ['check', 'Check / aprobación'],
    ['showroom', 'Showroom / tienda'],
    ['escudo', 'Escudo / contingencia'],
    ['documento', 'Documento'],
    ['tendencia', 'Tendencia / inversión'],
    ['alerta', 'Alerta'],
    ['calendario', 'Calendario'],
  ];
  const COLOR_OPTIONS = [
    ['naranja', 'Naranja'],
    ['verde', 'Verde'],
    ['navy', 'Navy'],
  ];

  const bloquesList = document.getElementById('bloques-list');
  const btnAddBloque = document.getElementById('btn-add-bloque');
  const form = document.getElementById('form-comunicado');
  const tituloInput = document.getElementById('titulo');
  const tituloCount = document.getElementById('titulo-count');

  let bloqueSeq = 0;
  let currentJobId = null;

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'text') node.textContent = v;
      else node.setAttribute(k, v);
    });
    children.forEach((c) => node.appendChild(c));
    return node;
  }

  function optionsHtml(options, selected) {
    return options
      .map(([value, label]) => `<option value="${value}" ${value === selected ? 'selected' : ''}>${label}</option>`)
      .join('');
  }

  function addBloque() {
    bloqueSeq += 1;
    const id = `bloque-${bloqueSeq}`;
    const card = document.createElement('div');
    card.className = 'bloque-card';
    card.dataset.bloqueId = id;
    card.innerHTML = `
      <button type="button" class="btn btn-danger-ghost btn-sm bloque-remove">Quitar</button>
      <label>Título del bloque</label>
      <input type="text" class="bloque-titulo" placeholder="Ej. Flujo de Showroom">
      <div class="row">
        <div>
          <label>Icono</label>
          <select class="bloque-icono">${optionsHtml(ICON_OPTIONS, 'check')}</select>
        </div>
        <div>
          <label>Color</label>
          <select class="bloque-color">${optionsHtml(COLOR_OPTIONS, 'naranja')}</select>
        </div>
      </div>
      <label>Viñetas <span class="hint">(una por línea, usa **texto** para negrita)</span></label>
      <textarea class="bloque-vinetas" placeholder="Nuevo flujo dedicado para la creación de **Showrooms**...&#10;Autoriza el **Country Manager**..."></textarea>
    `;
    card.querySelector('.bloque-remove').addEventListener('click', () => card.remove());
    bloquesList.appendChild(card);
  }

  btnAddBloque.addEventListener('click', addBloque);
  addBloque(); // arranca con un bloque vacío listo para llenar

  tituloInput.addEventListener('input', () => {
    const words = tituloInput.value.trim().split(/\s+/).filter(Boolean).length;
    tituloCount.textContent = tituloInput.value.trim() ? `${words} palabra${words === 1 ? '' : 's'}${words > 10 ? ' — considera acortar' : ''}` : '';
    tituloCount.style.color = words > 10 ? '#B23A12' : '#94A3B8';
  });

  const vigenciaTipo = document.getElementById('vigenciaTipo');
  const vigenciaFechaWrap = document.getElementById('vigencia-fecha-wrap');
  const vigenciaCustomWrap = document.getElementById('vigencia-custom-wrap');
  vigenciaTipo.addEventListener('change', () => {
    vigenciaFechaWrap.style.display = vigenciaTipo.value === 'fecha' ? 'block' : 'none';
    vigenciaCustomWrap.style.display = vigenciaTipo.value === 'custom' ? 'block' : 'none';
  });

  const contactoSelect = document.getElementById('contactoSelect');
  const contactoCustomWrap = document.getElementById('contacto-custom-wrap');
  contactoSelect.addEventListener('change', () => {
    contactoCustomWrap.style.display = contactoSelect.value === '__custom__' ? 'block' : 'none';
  });

  function collectBloques() {
    return Array.from(bloquesList.querySelectorAll('.bloque-card')).map((card) => ({
      titulo: card.querySelector('.bloque-titulo').value.trim(),
      icono: card.querySelector('.bloque-icono').value,
      color: card.querySelector('.bloque-color').value,
      viñetas: card
        .querySelector('.bloque-vinetas')
        .value.split('\n')
        .map((v) => v.trim())
        .filter(Boolean),
    }));
  }

  function collectContacto() {
    if (contactoSelect.value === '__custom__') {
      return document.getElementById('contactoCustom').value.trim();
    }
    return contactoSelect.value || '';
  }

  function showMsg(container, type, text) {
    container.innerHTML = `<div class="status-msg ${type}">${text}</div>`;
  }

  function clearMsg(container) {
    container.innerHTML = '';
  }

  function setLoading(btn, loading, label) {
    btn.disabled = loading;
    btn.innerHTML = loading ? `<span class="spinner"></span> Generando...` : label;
  }

  const esStatusMsg = document.getElementById('es-status-msg');
  const esPreviewSection = document.getElementById('es-preview-section');
  const esPreviewImg = document.getElementById('es-preview-img');
  const esHtmlLink = document.getElementById('es-html-link');
  const esPngLink = document.getElementById('es-png-link');
  const btnGenerateEs = document.getElementById('btn-generate-es');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMsg(esStatusMsg);

    const data = {
      jobId: currentJobId,
      titulo: tituloInput.value.trim(),
      tituloResaltado: document.getElementById('tituloResaltado').value.trim(),
      bajada: document.getElementById('bajada').value.trim(),
      badgeType: document.getElementById('badgeType').value,
      bandera: document.getElementById('bandera').value,
      bloques: collectBloques(),
      vigencia: {
        tipo: vigenciaTipo.value,
        fecha: document.getElementById('vigenciaFecha').value.trim(),
        custom: document.getElementById('vigenciaCustom').value.trim(),
      },
      contacto: collectContacto(),
      notaCierre: document.getElementById('notaCierre').value.trim(),
    };

    setLoading(btnGenerateEs, true, 'Generar ES');
    try {
      const res = await fetch('/api/comunicado/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Error generando el comunicado.');

      currentJobId = json.jobId;
      esPreviewImg.src = json.previewUrl;
      esHtmlLink.href = json.htmlUrl;
      esPngLink.href = json.previewUrl;
      esPreviewSection.style.display = 'block';
      showMsg(esStatusMsg, 'ok', 'ES generado. Revisa el preview antes de traducir.');
      esPreviewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      showMsg(esStatusMsg, 'error', err.message);
    } finally {
      setLoading(btnGenerateEs, false, 'Generar ES');
    }
  });

  const btnTranslate = document.getElementById('btn-translate');
  const translateStatusMsg = document.getElementById('translate-status-msg');
  const translationsSection = document.getElementById('translations-section');
  const translationsGrid = document.getElementById('translations-grid');
  const btnDownloadZip = document.getElementById('btn-download-zip');

  function langLabel(lang) {
    return { en: 'EN', pt: 'PT-BR' }[lang] || lang.toUpperCase();
  }

  btnTranslate.addEventListener('click', async () => {
    if (!currentJobId) return;
    clearMsg(translateStatusMsg);
    setLoading(btnTranslate, true, 'Generar EN + PT');
    try {
      const res = await fetch(`/api/comunicado/${currentJobId}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ langs: ['en', 'pt'] }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Error traduciendo el comunicado.');

      translationsGrid.innerHTML = '';
      Object.entries(json.results || {}).forEach(([lang, r]) => {
        const card = document.createElement('div');
        card.className = 'preview-card';
        card.innerHTML = `
          <div class="preview-head"><span class="lang-tag">${langLabel(lang)}</span></div>
          <img src="${r.previewUrl}" alt="Preview ${lang}">
          <div class="preview-links">
            <a href="${r.htmlUrl}" target="_blank">Ver HTML</a>
            <a href="${r.previewUrl}" target="_blank" download>Descargar PNG</a>
          </div>
          ${r.warnings && r.warnings.length ? `<div class="status-msg warn" style="margin:0 14px 12px 14px;">${r.warnings.join('<br>')}</div>` : ''}
        `;
        translationsGrid.appendChild(card);
      });

      const errorEntries = Object.entries(json.errors || {});
      if (errorEntries.length) {
        const msg = errorEntries.map(([lang, e]) => `<b>${langLabel(lang)}:</b> ${e}`).join('<br>');
        showMsg(translateStatusMsg, 'error', msg);
      } else {
        showMsg(translateStatusMsg, 'ok', 'Traducción completa.');
      }

      if (Object.keys(json.results || {}).length) {
        translationsSection.style.display = 'block';
        btnDownloadZip.href = `/api/comunicado/${currentJobId}/zip`;
        translationsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (err) {
      showMsg(translateStatusMsg, 'error', err.message);
    } finally {
      setLoading(btnTranslate, false, 'Generar EN + PT');
    }
  });

  // Aviso si el servidor no tiene ANTHROPIC_API_KEY configurada.
  fetch('/api/config')
    .then((r) => r.json())
    .then((cfg) => {
      if (!cfg.hasApiKey) {
        document.getElementById('api-key-warning').style.display = 'block';
      }
    })
    .catch(() => {});
})();

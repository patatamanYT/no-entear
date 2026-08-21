// Libreria de icono SVG inline para el sistema Guepardo.
// Regla del sistema de diseno: iconos SVG inline exclusivamente, nunca
// emojis ni librerias genericas. Cada icono es una funcion (stroke) => svg
// para poder reutilizar el mismo trazo con distinto color por bloque.

const ICONS = {
  showroom: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 9 L4 3 H20 L21 9" fill="none" stroke="${stroke}" stroke-width="1.8" stroke-linejoin="round"/><path d="M3 9 V20 H21 V9" fill="none" stroke="${stroke}" stroke-width="1.8"/><path d="M3 9 A2.2 2.2 0 0 0 7.4 9" stroke="${stroke}" stroke-width="1.6" fill="none"/><path d="M7.4 9 A2.2 2.2 0 0 0 11.8 9" stroke="${stroke}" stroke-width="1.6" fill="none"/><path d="M11.8 9 A2.2 2.2 0 0 0 16.2 9" stroke="${stroke}" stroke-width="1.6" fill="none"/><path d="M16.2 9 A2.2 2.2 0 0 0 20.6 9" stroke="${stroke}" stroke-width="1.6" fill="none"/><rect x="9.5" y="14" width="5" height="6" fill="none" stroke="${stroke}" stroke-width="1.6"/></svg>`,
  escudo: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 2 L2 7 V11 C2 16.5 6.2 21 12 22 C17.8 21 22 16.5 22 11 V7 Z" fill="none" stroke="${stroke}" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 8 V13" stroke="${stroke}" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16" r="1.1" fill="${stroke}"/></svg>`,
  check: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9.2" fill="none" stroke="${stroke}" stroke-width="1.8"/><path d="M7.5 12.5 L10.5 15.5 L16.5 9" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  documento: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M6 2.5 H14 L18 6.5 V21.5 H6 Z" fill="none" stroke="${stroke}" stroke-width="1.8" stroke-linejoin="round"/><path d="M14 2.5 V6.5 H18" fill="none" stroke="${stroke}" stroke-width="1.8" stroke-linejoin="round"/><line x1="9" y1="12" x2="15" y2="12" stroke="${stroke}" stroke-width="1.6" stroke-linecap="round"/><line x1="9" y1="16" x2="15" y2="16" stroke="${stroke}" stroke-width="1.6" stroke-linecap="round"/></svg>`,
  tendencia: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 17 L9.5 10.5 L13.5 14.5 L21 6.5" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 6.5 H21 V12.5" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  alerta: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><path d="M12 3 L22 20 H2 Z" fill="none" stroke="${stroke}" stroke-width="1.8" stroke-linejoin="round"/><line x1="12" y1="9.5" x2="12" y2="14.5" stroke="${stroke}" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1" fill="${stroke}"/></svg>`,
  calendario: (stroke) => `<svg viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="${stroke}" stroke-width="1.8"/><line x1="3" y1="10" x2="21" y2="10" stroke="${stroke}" stroke-width="1.8"/><line x1="7" y1="3" x2="7" y2="6.5" stroke="${stroke}" stroke-width="1.8" stroke-linecap="round"/><line x1="17" y1="3" x2="17" y2="6.5" stroke="${stroke}" stroke-width="1.8" stroke-linecap="round"/></svg>`,
};

const ICON_COLORS = {
  naranja: { bg: '#FEEDE2', stroke: '#F26722' },
  verde: { bg: '#E9F5EC', stroke: '#0F7A43' },
  navy: { bg: '#E9EEF5', stroke: '#1F2A44' },
};

// Icono + color fijos por tipo de badge (no editable desde el formulario).
const BADGE_ICON = {
  actualizacion: `<svg viewBox="0 0 24 24" width="13" height="13"><path d="M12 2 C7.5 2 5 5 5 9 V14 L2.5 18 H21.5 L19 14 V9 C19 5 16.5 2 12 2 Z" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/><path d="M9.5 18 C9.5 20 10.5 21.2 12 21.2 C13.5 21.2 14.5 20 14.5 18" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>`,
  aviso: `<svg viewBox="0 0 24 24" width="13" height="13"><path d="M12 3 L22 20 H2 Z" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/><line x1="12" y1="9.5" x2="12" y2="14.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1" fill="#FFFFFF"/></svg>`,
  recordatorio: `<svg viewBox="0 0 24 24" width="13" height="13"><circle cx="12" cy="13" r="8" fill="none" stroke="#FFFFFF" stroke-width="2"/><path d="M12 9 V13 L15 15.5" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 2.5 H15" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>`,
};

const BADGE_BG = {
  actualizacion: '#F26722',
  aviso: '#DC5D2E',
  recordatorio: '#1F2A44',
};

const BADGE_LABEL = {
  es: { actualizacion: 'Actualización', aviso: 'Aviso', recordatorio: 'Recordatorio' },
  en: { actualizacion: 'Update', aviso: 'Notice', recordatorio: 'Reminder' },
  pt: { actualizacion: 'Atualização', aviso: 'Aviso', recordatorio: 'Lembrete' },
};

function renderIcon(type, colorKey) {
  const iconFn = ICONS[type] || ICONS.check;
  const colors = ICON_COLORS[colorKey] || ICON_COLORS.naranja;
  return { bg: colors.bg, svg: iconFn(colors.stroke) };
}

module.exports = {
  ICONS,
  ICON_COLORS,
  BADGE_ICON,
  BADGE_BG,
  BADGE_LABEL,
  renderIcon,
  iconTypes: Object.keys(ICONS),
  colorKeys: Object.keys(ICON_COLORS),
};

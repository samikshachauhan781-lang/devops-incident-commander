/** Theme persistence and DOM application for DevOps Incident Commander */

export const APPEARANCE_STORAGE_KEY = 'dic-appearance';

export type AppearancePrefs = {
  darkMode: boolean;
  primaryColor: string;
};

export const DEFAULT_APPEARANCE: AppearancePrefs = {
  darkMode: false,
  primaryColor: '#4f46e5',
};

export function isValidAccent(hex: string): boolean {
  return /^#[0-9A-Fa-f]{6}$/.test(hex);
}

function normalizeHex(hex: string): string {
  if (!hex.startsWith('#')) return hex;
  return hex.length === 7 ? hex : hex;
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const h = hex.replace('#', '');
  if (h.length !== 6) return null;
  const n = parseInt(h, 16);
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}

function mixWithWhite(hex: string, weight: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  const r = Math.round(rgb.r + (255 - rgb.r) * weight);
  const g = Math.round(rgb.g + (255 - rgb.g) * weight);
  const b = Math.round(rgb.b + (255 - rgb.b) * weight);
  return `rgb(${r}, ${g}, ${b})`;
}

function mixWithBlack(hex: string, weight: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  const r = Math.round(rgb.r * (1 - weight));
  const g = Math.round(rgb.g * (1 - weight));
  const b = Math.round(rgb.b * (1 - weight));
  return `rgb(${r}, ${g}, ${b})`;
}

/** Read saved appearance or system preference when none saved */
export function readAppearance(): AppearancePrefs {
  if (typeof window === 'undefined') return DEFAULT_APPEARANCE;

  try {
    const raw = localStorage.getItem(APPEARANCE_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as AppearancePrefs;
      return {
        darkMode: Boolean(parsed.darkMode),
        primaryColor: isValidAccent(parsed.primaryColor) ? parsed.primaryColor : DEFAULT_APPEARANCE.primaryColor,
      };
    }
  } catch {
    /* fall through */
  }

  try {
    const appRaw = localStorage.getItem('app-settings');
    if (appRaw) {
      const app = JSON.parse(appRaw);
      if (app.appearance) {
        return {
          darkMode: Boolean(app.appearance.darkMode),
          primaryColor: isValidAccent(app.appearance.primaryColor)
            ? app.appearance.primaryColor
            : DEFAULT_APPEARANCE.primaryColor,
        };
      }
    }
  } catch {
    /* fall through */
  }

  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
  return { darkMode: prefersDark, primaryColor: DEFAULT_APPEARANCE.primaryColor };
}

export function persistAppearance(prefs: AppearancePrefs): void {
  const normalized: AppearancePrefs = {
    darkMode: prefs.darkMode,
    primaryColor: normalizeHex(prefs.primaryColor),
  };
  localStorage.setItem(APPEARANCE_STORAGE_KEY, JSON.stringify(normalized));

  try {
    const appRaw = localStorage.getItem('app-settings');
    const app = appRaw ? JSON.parse(appRaw) : {};
    app.appearance = normalized;
    localStorage.setItem('app-settings', JSON.stringify(app));
  } catch {
    /* non-fatal */
  }
}

/** Apply theme tokens to `document.documentElement` */
export function applyAppearanceToDocument(prefs: AppearancePrefs): void {
  if (typeof document === 'undefined') return;

  const accent = normalizeHex(prefs.primaryColor);
  const theme = prefs.darkMode ? 'dark' : 'light';

  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.classList.toggle('dark', prefs.darkMode);
  document.documentElement.style.colorScheme = theme;

  document.documentElement.style.setProperty('--color-accent', accent);
  document.documentElement.style.setProperty('--app-accent', accent);
  document.documentElement.style.setProperty('--color-accent-hover', mixWithBlack(accent, 0.12));
  const rgb = hexToRgb(accent);
  if (rgb) {
    document.documentElement.style.setProperty('--color-accent-rgb', `${rgb.r}, ${rgb.g}, ${rgb.b}`);
    if (prefs.darkMode) {
      document.documentElement.style.setProperty('--color-accent-soft', `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.22)`);
      document.documentElement.style.setProperty('--color-accent-muted', `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.38)`);
    } else {
      document.documentElement.style.setProperty('--color-accent-soft', mixWithWhite(accent, 0.88));
      document.documentElement.style.setProperty('--color-accent-muted', mixWithWhite(accent, 0.75));
    }
  }
}

export const ACCENT_COLOR_OPTIONS = [
  { value: '#3B82F6', label: 'Blue' },
  { value: '#EF4444', label: 'Red' },
  { value: '#10B981', label: 'Emerald' },
  { value: '#F59E0B', label: 'Amber' },
  { value: '#8B5CF6', label: 'Violet' },
  { value: '#EC4899', label: 'Pink' },
] as const;

import React, { createContext, useCallback, useContext, useLayoutEffect, useMemo, useState } from 'react';
import {
  AppearancePrefs,
  applyAppearanceToDocument,
  persistAppearance,
  readAppearance,
} from '../lib/theme';

type ThemeContextValue = {
  darkMode: boolean;
  primaryColor: string;
  setDarkMode: (enabled: boolean) => void;
  setPrimaryColor: (color: string) => void;
  toggleDarkMode: () => void;
};

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [prefs, setPrefs] = useState<AppearancePrefs>(() => readAppearance());

  useLayoutEffect(() => {
    applyAppearanceToDocument(prefs);
  }, [prefs]);

  const commit = useCallback((updater: (prev: AppearancePrefs) => AppearancePrefs) => {
    setPrefs((prev) => {
      const next = updater(prev);
      persistAppearance(next);
      applyAppearanceToDocument(next);
      return next;
    });
  }, []);

  const setDarkMode = useCallback(
    (enabled: boolean) => {
      commit((prev) => ({ ...prev, darkMode: enabled }));
    },
    [commit]
  );

  const setPrimaryColor = useCallback(
    (color: string) => {
      commit((prev) => ({ ...prev, primaryColor: color }));
    },
    [commit]
  );

  const toggleDarkMode = useCallback(() => {
    commit((prev) => ({ ...prev, darkMode: !prev.darkMode }));
  }, [commit]);

  const value = useMemo(
    () => ({
      darkMode: prefs.darkMode,
      primaryColor: prefs.primaryColor,
      setDarkMode,
      setPrimaryColor,
      toggleDarkMode,
    }),
    [prefs.darkMode, prefs.primaryColor, setDarkMode, setPrimaryColor, toggleDarkMode]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return ctx;
}

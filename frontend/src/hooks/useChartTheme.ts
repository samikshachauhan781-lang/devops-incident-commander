import { useMemo } from 'react';
import { useTheme } from '../contexts/ThemeContext';

/** Recharts tooltip / axis styling aligned with app theme */
export function useChartTheme() {
  const { darkMode } = useTheme();

  return useMemo(
    () => ({
      tooltip: {
        backgroundColor: darkMode ? '#1a2230' : '#ffffff',
        border: `1px solid ${darkMode ? '#334155' : '#e2e8f0'}`,
        borderRadius: 10,
        color: darkMode ? '#f1f5f9' : '#0f172a',
        fontSize: 12,
        boxShadow: darkMode
          ? '0 12px 32px -8px rgba(0, 0, 0, 0.65)'
          : '0 4px 14px -4px rgba(15, 23, 42, 0.12)',
      },
      grid: darkMode ? '#2a3548' : '#e2e8f0',
      axis: darkMode ? '#64748b' : '#94a3b8',
      legend: darkMode ? '#cbd5e1' : '#475569',
      pieLabel: darkMode ? '#e2e8f0' : '#334155',
    }),
    [darkMode]
  );
}

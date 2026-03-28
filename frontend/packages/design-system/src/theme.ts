/**
 * Herald Crypto Exchange - Theme Configuration (FE-03)
 */

import { colors } from './tokens';

export type ThemeMode = 'dark' | 'light';

export interface Theme {
  mode: ThemeMode;
  bg: { primary: string; secondary: string; tertiary: string; card: string; hover: string };
  text: { primary: string; secondary: string; tertiary: string };
  border: { default: string; light: string };
  buy: string;
  sell: string;
  accent: string;
  profit: string;
  loss: string;
}

export const darkTheme: Theme = {
  mode: 'dark',
  bg: {
    primary: colors.bgPrimary,
    secondary: colors.bgSecondary,
    tertiary: colors.bgTertiary,
    card: colors.bgCard,
    hover: colors.bgHover,
  },
  text: {
    primary: colors.textPrimary,
    secondary: colors.textSecondary,
    tertiary: colors.textTertiary,
  },
  border: { default: colors.border, light: colors.borderLight },
  buy: colors.buy,
  sell: colors.sell,
  accent: colors.accent,
  profit: colors.profit,
  loss: colors.loss,
};

export const lightTheme: Theme = {
  mode: 'light',
  bg: {
    primary: '#ffffff',
    secondary: '#f8f9fa',
    tertiary: '#e9ecef',
    card: '#ffffff',
    hover: '#f1f3f5',
  },
  text: {
    primary: '#212529',
    secondary: '#6c757d',
    tertiary: '#adb5bd',
  },
  border: { default: '#dee2e6', light: '#e9ecef' },
  buy: '#0ecb81',
  sell: '#f6465d',
  accent: '#f0b90b',
  profit: '#0ecb81',
  loss: '#f6465d',
};

export function getTheme(mode: ThemeMode): Theme {
  return mode === 'dark' ? darkTheme : lightTheme;
}

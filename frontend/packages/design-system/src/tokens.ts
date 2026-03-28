/**
 * Herald Crypto Exchange - Design Tokens (FE-03)
 *
 * Primitive and semantic design tokens for the exchange UI.
 */

export const colors = {
  // Primitives
  gray: {
    50: '#fafafa', 100: '#f5f5f5', 200: '#e5e5e5', 300: '#d4d4d4',
    400: '#a3a3a3', 500: '#737373', 600: '#525252', 700: '#404040',
    800: '#262626', 900: '#171717', 950: '#0a0a0a',
  },
  green: {
    400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d',
  },
  red: {
    400: '#f87171', 500: '#ef4444', 600: '#dc2626', 700: '#b91c1c',
  },
  blue: {
    400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8',
  },
  yellow: {
    400: '#facc15', 500: '#eab308',
  },
  // Semantic
  buy: '#0ecb81',
  sell: '#f6465d',
  profit: '#0ecb81',
  loss: '#f6465d',
  // Surface
  bgPrimary: '#0b0e11',
  bgSecondary: '#1e2329',
  bgTertiary: '#2b3139',
  bgCard: '#181a20',
  bgHover: '#2b3139',
  // Text
  textPrimary: '#eaecef',
  textSecondary: '#848e9c',
  textTertiary: '#5e6673',
  // Border
  border: '#2b3139',
  borderLight: '#3c4451',
  // Accent
  accent: '#f0b90b',
  accentHover: '#d9a60a',
} as const;

export const spacing = {
  xs: '4px', sm: '8px', md: '12px', lg: '16px',
  xl: '20px', xxl: '24px', xxxl: '32px',
} as const;

export const fontSize = {
  xs: '10px', sm: '12px', md: '14px', lg: '16px',
  xl: '18px', xxl: '20px', h3: '24px', h2: '28px', h1: '32px',
} as const;

export const fontWeight = {
  normal: '400', medium: '500', semibold: '600', bold: '700',
} as const;

export const borderRadius = {
  sm: '4px', md: '8px', lg: '12px', xl: '16px', full: '9999px',
} as const;

export const shadow = {
  sm: '0 1px 2px rgba(0,0,0,0.3)',
  md: '0 4px 6px rgba(0,0,0,0.3)',
  lg: '0 10px 15px rgba(0,0,0,0.3)',
  xl: '0 20px 25px rgba(0,0,0,0.3)',
} as const;

export const zIndex = {
  dropdown: 100, modal: 200, toast: 300, tooltip: 400,
} as const;

export const transition = {
  fast: '150ms ease',
  normal: '250ms ease',
  slow: '350ms ease',
} as const;

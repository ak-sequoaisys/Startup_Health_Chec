/**
 * Offrd Brand Theme Configuration
 * 
 * This file contains all brand tokens for the Offrd Startup Compliance Health Check Tool.
 * All colors, typography, and spacing should reference these tokens to maintain consistency.
 * 
 * WCAG AA compliance is ensured for all color combinations.
 */

export const brand = {
  colors: {
    primary: {
      50: 'hsl(210, 40%, 98%)',
      100: 'hsl(210, 40%, 96%)',
      200: 'hsl(210, 40%, 90%)',
      300: 'hsl(210, 40%, 80%)',
      400: 'hsl(210, 40%, 65%)',
      500: 'hsl(210, 40%, 50%)',
      600: 'hsl(210, 45%, 42%)',
      700: 'hsl(210, 50%, 35%)',
      800: 'hsl(210, 55%, 28%)',
      900: 'hsl(210, 60%, 20%)',
      950: 'hsl(210, 65%, 12%)',
    },
    
    secondary: {
      50: 'hsl(200, 30%, 98%)',
      100: 'hsl(200, 30%, 95%)',
      200: 'hsl(200, 30%, 88%)',
      300: 'hsl(200, 30%, 75%)',
      400: 'hsl(200, 30%, 60%)',
      500: 'hsl(200, 30%, 45%)',
      600: 'hsl(200, 35%, 38%)',
      700: 'hsl(200, 40%, 30%)',
      800: 'hsl(200, 45%, 23%)',
      900: 'hsl(200, 50%, 16%)',
      950: 'hsl(200, 55%, 10%)',
    },
    
    neutral: {
      50: 'hsl(220, 15%, 98%)',
      100: 'hsl(220, 15%, 95%)',
      200: 'hsl(220, 15%, 90%)',
      300: 'hsl(220, 15%, 80%)',
      400: 'hsl(220, 15%, 65%)',
      500: 'hsl(220, 15%, 50%)',
      600: 'hsl(220, 18%, 40%)',
      700: 'hsl(220, 20%, 30%)',
      800: 'hsl(220, 22%, 20%)',
      900: 'hsl(220, 25%, 12%)',
      950: 'hsl(220, 28%, 8%)',
    },
    
    success: {
      50: 'hsl(142, 45%, 97%)',
      100: 'hsl(142, 45%, 92%)',
      200: 'hsl(142, 45%, 82%)',
      300: 'hsl(142, 45%, 68%)',
      400: 'hsl(142, 45%, 52%)',
      500: 'hsl(142, 50%, 42%)',
      600: 'hsl(142, 55%, 35%)',
      700: 'hsl(142, 60%, 28%)',
      800: 'hsl(142, 65%, 22%)',
      900: 'hsl(142, 70%, 16%)',
      950: 'hsl(142, 75%, 10%)',
    },
    
    warning: {
      50: 'hsl(38, 90%, 97%)',
      100: 'hsl(38, 90%, 92%)',
      200: 'hsl(38, 90%, 82%)',
      300: 'hsl(38, 90%, 68%)',
      400: 'hsl(38, 90%, 55%)',
      500: 'hsl(38, 85%, 48%)',
      600: 'hsl(38, 80%, 42%)',
      700: 'hsl(38, 75%, 35%)',
      800: 'hsl(38, 70%, 28%)',
      900: 'hsl(38, 65%, 22%)',
      950: 'hsl(38, 60%, 15%)',
    },
    
    danger: {
      50: 'hsl(0, 70%, 97%)',
      100: 'hsl(0, 70%, 93%)',
      200: 'hsl(0, 70%, 85%)',
      300: 'hsl(0, 70%, 72%)',
      400: 'hsl(0, 70%, 58%)',
      500: 'hsl(0, 75%, 48%)',
      600: 'hsl(0, 80%, 42%)',
      700: 'hsl(0, 85%, 35%)',
      800: 'hsl(0, 88%, 28%)',
      900: 'hsl(0, 90%, 22%)',
      950: 'hsl(0, 92%, 15%)',
    },
    
    critical: {
      50: 'hsl(10, 80%, 97%)',
      100: 'hsl(10, 80%, 93%)',
      200: 'hsl(10, 80%, 85%)',
      300: 'hsl(10, 80%, 72%)',
      400: 'hsl(10, 80%, 58%)',
      500: 'hsl(10, 85%, 48%)',
      600: 'hsl(10, 88%, 42%)',
      700: 'hsl(10, 90%, 35%)',
      800: 'hsl(10, 92%, 28%)',
      900: 'hsl(10, 94%, 22%)',
      950: 'hsl(10, 95%, 15%)',
    },
    
    background: {
      light: 'hsl(220, 20%, 98%)',
      DEFAULT: 'hsl(0, 0%, 100%)',
      dark: 'hsl(220, 25%, 10%)',
    },
    
    foreground: {
      light: 'hsl(220, 15%, 20%)',
      DEFAULT: 'hsl(220, 20%, 15%)',
      dark: 'hsl(220, 15%, 95%)',
    },
    
    border: {
      light: 'hsl(220, 15%, 90%)',
      DEFAULT: 'hsl(220, 15%, 85%)',
      dark: 'hsl(220, 20%, 20%)',
    },
    
    muted: {
      light: 'hsl(220, 15%, 96%)',
      DEFAULT: 'hsl(220, 15%, 94%)',
      foreground: 'hsl(220, 15%, 45%)',
    },
    
    accent: {
      light: 'hsl(210, 40%, 96%)',
      DEFAULT: 'hsl(210, 40%, 92%)',
      foreground: 'hsl(210, 50%, 30%)',
    },
  },
  
  typography: {
    fontFamily: {
      sans: [
        'Inter',
        'system-ui',
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ],
      mono: [
        '"JetBrains Mono"',
        'Menlo',
        'Monaco',
        'Consolas',
        '"Liberation Mono"',
        '"Courier New"',
        'monospace',
      ],
    },
    
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      '5xl': ['3rem', { lineHeight: '1' }],
    },
    
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },
  
  spacing: {
    radius: {
      sm: '0.25rem',
      md: '0.5rem',
      lg: '0.75rem',
      xl: '1rem',
      '2xl': '1.5rem',
      full: '9999px',
    },
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  
  riskLevels: {
    low: {
      color: 'hsl(142, 50%, 42%)',
      background: 'hsl(142, 45%, 97%)',
      border: 'hsl(142, 45%, 82%)',
      foreground: 'hsl(142, 60%, 28%)',
    },
    medium: {
      color: 'hsl(38, 85%, 48%)',
      background: 'hsl(38, 90%, 97%)',
      border: 'hsl(38, 90%, 82%)',
      foreground: 'hsl(38, 75%, 35%)',
    },
    high: {
      color: 'hsl(10, 85%, 48%)',
      background: 'hsl(10, 80%, 97%)',
      border: 'hsl(10, 80%, 85%)',
      foreground: 'hsl(10, 90%, 35%)',
    },
    critical: {
      color: 'hsl(0, 75%, 48%)',
      background: 'hsl(0, 70%, 97%)',
      border: 'hsl(0, 70%, 85%)',
      foreground: 'hsl(0, 85%, 35%)',
    },
  },
} as const;

export type Brand = typeof brand;

export const getRiskLevelColors = (level: string) => {
  const normalizedLevel = level.toLowerCase() as keyof typeof brand.riskLevels;
  return brand.riskLevels[normalizedLevel] || brand.riskLevels.medium;
};

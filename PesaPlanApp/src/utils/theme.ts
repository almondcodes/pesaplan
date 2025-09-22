import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

// PesaPlan Brand Colors
const pesaplanColors = {
  primary: '#2E7D32', // Green - representing money/growth
  primaryVariant: '#1B5E20',
  secondary: '#FF6F00', // Orange - representing energy/action
  secondaryVariant: '#E65100',
  background: '#FAFAFA',
  surface: '#FFFFFF',
  error: '#D32F2F',
  onPrimary: '#FFFFFF',
  onSecondary: '#FFFFFF',
  onBackground: '#212121',
  onSurface: '#212121',
  onError: '#FFFFFF',
  outline: '#BDBDBD',
  surfaceVariant: '#F5F5F5',
  onSurfaceVariant: '#424242',
};

// Light Theme
export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    ...pesaplanColors,
  },
  roundness: 12,
};

// Dark Theme
export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#4CAF50',
    primaryVariant: '#2E7D32',
    secondary: '#FF9800',
    secondaryVariant: '#F57C00',
    background: '#121212',
    surface: '#1E1E1E',
    error: '#CF6679',
    onPrimary: '#000000',
    onSecondary: '#000000',
    onBackground: '#FFFFFF',
    onSurface: '#FFFFFF',
    onError: '#000000',
    outline: '#6D6D6D',
    surfaceVariant: '#2C2C2C',
    onSurfaceVariant: '#E0E0E0',
  },
  roundness: 12,
};

// Default theme (light)
export const theme = lightTheme;

// Typography
export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold' as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 28,
    fontWeight: 'bold' as const,
    lineHeight: 36,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32,
  },
  h4: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  h5: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
  h6: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 22,
  },
  body1: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: 'normal' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal' as const,
    lineHeight: 16,
  },
  button: {
    fontSize: 14,
    fontWeight: '600' as const,
    lineHeight: 20,
  },
};

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Border Radius
export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 50,
};

// Shadows
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
};

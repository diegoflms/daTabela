import { Platform } from 'react-native';

export const typography = {
  fontFamily: {
    regular: Platform.select({
      ios: 'System',
      android: 'System',
      default: 'Inter, sans-serif',
    }),
    medium: Platform.select({
      ios: 'System',
      android: 'System',
      default: 'Inter-Medium, sans-serif',
    }),
    bold: Platform.select({
      ios: 'System',
      android: 'System',
      default: 'Inter-Bold, sans-serif',
    }),
  },
  fontSize: {
    xs: 11,
    sm: 13,
    md: 15,
    lg: 18,
    xl: 22,
    xxl: 28,
    huge: 36,
  },
  lineHeight: {
    xs: 14,
    sm: 18,
    md: 22,
    lg: 26,
    xl: 30,
    xxl: 38,
    huge: 46,
  },
};

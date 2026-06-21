import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'info' | 'error';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'primary',
  style,
  textStyle,
}) => {
  const getBadgeColors = () => {
    switch (variant) {
      case 'secondary':
        return { bg: colors.secondaryLight, text: colors.secondaryDark };
      case 'success':
        return { bg: '#E8F8F5', text: colors.success };
      case 'warning':
        return { bg: '#FEF9E7', text: colors.warning };
      case 'error':
        return { bg: '#FDEDEC', text: colors.error };
      case 'info':
        return { bg: '#EBF5FB', text: colors.info };
      case 'primary':
      default:
        return { bg: colors.primaryLight, text: colors.primary };
    }
  };

  const badgeColors = getBadgeColors();

  return (
    <View style={[styles.badge, { backgroundColor: badgeColors.bg }, style]}>
      <Text style={[styles.text, { color: badgeColors.text }, textStyle]}>{label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    borderRadius: 999,
    paddingVertical: spacing.xs / 2,
    paddingHorizontal: spacing.sm,
    alignSelf: 'flex-start',
  },
  text: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.medium,
  },
});
export default Badge;

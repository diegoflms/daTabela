import React from 'react';
import { useRouter, usePathname } from 'expo-router';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../../theme';

interface NavLinkProps {
  href: any; // Aceita caminhos válidos do Expo Router
  label: string;
  onPress?: () => void;
}

export const NavLink: React.FC<NavLinkProps> = ({ href, label, onPress }) => {
  const router = useRouter();
  const pathname = usePathname();
  
  // Verifica se o link é o ativo
  const hrefStr = typeof href === 'string' ? href : href.pathname || '';
  const isActive = hrefStr === '/' 
    ? pathname === '/' 
    : pathname.startsWith(hrefStr);

  const handlePress = () => {
    if (onPress) {
      onPress();
    }
    router.push(href);
  };

  return (
    <TouchableOpacity 
      style={[styles.link, isActive && styles.activeLink]} 
      activeOpacity={0.7}
      onPress={handlePress}
    >
      <Text style={[styles.text, isActive && styles.activeText]}>{label}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  link: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 6,
    marginHorizontal: spacing.xs,
  },
  activeLink: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },
  text: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.medium,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  activeText: {
    color: colors.textLight,
    fontFamily: typography.fontFamily.bold,
  },
});
export default NavLink;

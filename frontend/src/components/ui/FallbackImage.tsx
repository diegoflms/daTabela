import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';

interface FallbackImageProps {
  sourceUrl?: string | null;
  textFallback: string; // Ex: Nome do jogador ou time
  type?: 'player' | 'team';
  size?: number;
  style?: any;
}

export const FallbackImage: React.FC<FallbackImageProps> = ({
  sourceUrl,
  textFallback,
  type = 'player',
  size = 64,
  style,
}) => {
  const [hasError, setHasError] = useState(false);

  // Gera iniciais para o fallback visual (ex: Matheusinho -> MA, Cauê Borges -> CB)
  const getInitials = (name: string) => {
    if (!name) return '?';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const initials = getInitials(textFallback);

  const containerStyle = [
    styles.container,
    type === 'player' ? styles.playerRadius : styles.teamRadius,
    { 
      width: size, 
      height: size, 
      backgroundColor: type === 'player' ? '#E2E8F0' : colors.primaryLight,
      borderColor: colors.border 
    },
    style,
  ];

  const textStyle: TextStyle = {
    fontSize: size * 0.35,
    fontFamily: typography.fontFamily.bold,
    color: type === 'player' ? colors.textSecondary : colors.primary,
  };

  // Se não houver URL ou falhou no load, mostra o fallback textual
  if (!sourceUrl || hasError) {
    return (
      <View style={containerStyle}>
        <Text style={textStyle}>{initials}</Text>
      </View>
    );
  }

  return (
    <Image
      source={{ uri: sourceUrl }}
      onError={() => setHasError(true)}
      style={[
        { width: size, height: size },
        type === 'player' ? styles.playerImage : styles.teamImage,
        style,
      ]}
      resizeMode="contain"
    />
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
  },
  playerRadius: {
    borderRadius: 999, // Redondo
  },
  teamRadius: {
    borderRadius: 10, // Quadrado arredondado
  },
  playerImage: {
    borderRadius: 999,
  },
  teamImage: {
    borderRadius: 10,
  },
});
export default FallbackImage;

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { Player } from '../../types/models';
import { colors, spacing, typography } from '../../theme';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { Link } from 'expo-router';

interface PlayerCardProps {
  player: Player;
}

export const PlayerCard: React.FC<PlayerCardProps> = ({ player }) => {
  const displayName = player.display_name || player.full_name || player.name || 'Jogador';
  return (
    <Link href={`/players/${player.id}` as any} asChild>
      <TouchableOpacity style={styles.card} activeOpacity={0.8}>
        <View style={styles.avatarContainer}>
          <FallbackImage
            sourceUrl={player.photo_url}
            textFallback={displayName}
            type="player"
            size={72}
            style={styles.avatar}
          />
        </View>
        
        <Text style={styles.name} numberOfLines={1}>
          {displayName}
        </Text>
      </TouchableOpacity>
    </Link>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    width: '47%', // Garante 2 colunas no mobile
    minWidth: 140,
    maxWidth: 220,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: spacing.sm,
  },
  avatar: {
    borderWidth: 1.5,
    borderColor: colors.border,
  },
  teamBadgeOverlay: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 6,
    padding: 2,
    borderWidth: 1.5,
    borderColor: colors.border,
  },
  overlayBadge: {
    borderRadius: 4,
  },
  name: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
});
export default PlayerCard;

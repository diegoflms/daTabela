import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { Team } from '../../types/models';
import { colors, spacing, typography } from '../../theme';
import { FallbackImage } from '../../components/ui/FallbackImage';
import { Link } from 'expo-router';

interface TeamCardProps {
  team: Team;
}

export const TeamCard: React.FC<TeamCardProps> = ({ team }) => {
  const teamName = team.canonical_name || team.name || 'Sem nome';
  return (
    <Link href={`/teams/${team.id}` as any} asChild>
      <TouchableOpacity style={styles.card} activeOpacity={0.8}>
        <FallbackImage
          sourceUrl={team.logo_url}
          textFallback={teamName}
          type="team"
          size={80}
          style={styles.logo}
        />
        <Text style={styles.name} numberOfLines={1}>
          {teamName}
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
    padding: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    width: '45%', // Garante duas colunas no mobile
    minWidth: 140,
    maxWidth: 220,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  logo: {
    marginBottom: spacing.md,
  },
  name: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.textLight,
    textAlign: 'center',
  },
});
export default TeamCard;

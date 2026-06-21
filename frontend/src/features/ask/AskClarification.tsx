import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { FallbackImage } from '../../components/ui/FallbackImage';

interface AskClarificationProps {
  candidates: any[];
  onSelectCandidate: (candidateName: string) => void;
}

export const AskClarification: React.FC<AskClarificationProps> = ({
  candidates,
  onSelectCandidate,
}) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🤔 Ambiguidades Encontradas</Text>
      <Text style={styles.subtitle}>
        Encontramos mais de um jogador possível para a sua pesquisa. Por favor, escolha um candidato abaixo:
      </Text>

      <View style={styles.list}>
        {candidates.map((candidate, idx) => {
          const name = candidate.name || candidate.display_name || candidate.player_name || 'Jogador';
          const teamName = candidate.team_name || candidate.entity_team_name || 'Sem time';
          
          return (
            <TouchableOpacity
              key={`candidate-${candidate.id || idx}`}
              style={styles.card}
              onPress={() => onSelectCandidate(name)}
              activeOpacity={0.8}
            >
              <FallbackImage
                textFallback={name}
                type="player"
                size={48}
                style={styles.avatar}
              />
              <View style={styles.info}>
                <Text style={styles.name}>{name}</Text>
                <Text style={styles.team}>{teamName}</Text>
              </View>
              <Text style={styles.actionArrow}>Selecionar ➔</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FEF9E7', // Amarelo suave de clarificação
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.2)',
    borderRadius: 12,
    padding: spacing.lg,
    width: '100%',
    marginVertical: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.warning,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    lineHeight: typography.lineHeight.sm,
  },
  list: {
    width: '100%',
    gap: spacing.sm,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: spacing.sm,
  },
  avatar: {
    marginRight: spacing.md,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: typography.fontSize.md,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
  },
  team: {
    fontSize: typography.fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
  },
  actionArrow: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.primary,
    paddingRight: spacing.xs,
  },
});
export default AskClarification;

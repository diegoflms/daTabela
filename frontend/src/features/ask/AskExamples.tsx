import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useAsync } from '../../hooks/useAsync';
import { getAskExamples } from '../../api/ask';
import { colors, spacing, typography } from '../../theme';

interface AskExamplesProps {
  onSelect: (example: string) => void;
}

export const AskExamples: React.FC<AskExamplesProps> = ({ onSelect }) => {
  const { data, loading, error, execute } = useAsync(getAskExamples);

  useEffect(() => {
    execute().catch(() => {});
  }, [execute]);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator color={colors.primary} size="small" />
        <Text style={styles.loadingText}>Carregando sugestões...</Text>
      </View>
    );
  }

  if (error) return null; // Oculta silenciosamente em caso de erro

  const examples = data?.examples || [
    'matheusinho ultimos 5 jogos',
    'top 3 jogos com mais pontos do matheusinho',
    'matheusinho vs teichmann ultimos 5 jogos',
    'top 10 rebotes',
    'top 10 times com mais vitorias na historia',
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>💡 Sugestões de Perguntas:</Text>
      <View style={styles.chipsContainer}>
        {examples.map((example, idx) => (
          <TouchableOpacity
            key={`example-${idx}`}
            style={styles.chip}
            onPress={() => onSelect(example)}
            activeOpacity={0.7}
          >
            <Text style={styles.chipText}>{example}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    marginVertical: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.sm,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  chip: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingVertical: spacing.sm - 2,
    paddingHorizontal: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.02,
    shadowRadius: 2,
    elevation: 1,
  },
  chipText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontFamily: typography.fontFamily.medium,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  loadingText: {
    marginLeft: spacing.sm,
    fontSize: typography.fontSize.sm,
    color: colors.textMuted,
  },
});
export default AskExamples;

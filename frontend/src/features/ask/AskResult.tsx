import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { DynamicTable } from '../../components/data/DynamicTable';
import { Badge } from '../../components/ui/Badge';
import { AskResponse } from '../../types/ask';

interface AskResultProps {
  result: AskResponse;
}

export const AskResult: React.FC<AskResultProps> = ({ result }) => {
  const { title, columns, rows, source_tables = [], interpreted_as, note, total } = result;

  return (
    <View style={styles.container}>
      {/* Title */}
      <Text style={styles.title}>{title || 'Resultado da Pergunta'}</Text>

      {/* Interpreted context info */}
      {interpreted_as && (
        <View style={styles.interpretationBox}>
          <Text style={styles.interpretationLabel}>Interpretado como:</Text>
          <View style={styles.interpretationBadges}>
            {interpreted_as.intent && (
              <Badge 
                label={`Intenção: ${interpreted_as.intent}`} 
                variant="primary" 
                style={styles.badge} 
              />
            )}
            {interpreted_as.player && (
              <Badge 
                label={`Jogador: ${interpreted_as.player.name}`} 
                variant="success" 
                style={styles.badge} 
              />
            )}
            {interpreted_as.metric && (
              <Badge 
                label={`Métrica: ${interpreted_as.metric.toUpperCase()}`} 
                variant="secondary" 
                style={styles.badge} 
              />
            )}
            {interpreted_as.last_n_games && (
              <Badge 
                label={`Nº Jogos: ${interpreted_as.last_n_games}`} 
                variant="info" 
                style={styles.badge} 
              />
            )}
            {interpreted_as.top_n && (
              <Badge 
                label={`Top ${interpreted_as.top_n}`} 
                variant="warning" 
                style={styles.badge} 
              />
            )}
          </View>
        </View>
      )}

      {/* Table */}
      <DynamicTable columns={columns} rows={rows} />

      {/* Note or Total info */}
      {note && (
        <Text style={styles.noteText}>💡 Nota: {note}</Text>
      )}

      {total !== undefined && total > 0 && (
        <Text style={styles.totalText}>Linhas retornadas: {total}</Text>
      )}

      {/* Sources */}
      {source_tables.length > 0 && (
        <View style={styles.sourcesContainer}>
          <Text style={styles.sourcesTitle}>Fontes do banco SQLite:</Text>
          <View style={styles.sourcesList}>
            {source_tables.map((table) => (
              <Badge 
                key={table} 
                label={table} 
                variant="primary" 
                style={styles.sourceBadge} 
              />
            ))}
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    padding: spacing.lg,
    width: '100%',
    marginVertical: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 6,
    elevation: 2,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontFamily: typography.fontFamily.bold,
    color: colors.text,
    marginBottom: spacing.md,
  },
  interpretationBox: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  interpretationLabel: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  interpretationBadges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  badge: {
    marginBottom: spacing.xs,
  },
  noteText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontStyle: 'italic',
    marginTop: spacing.md,
    lineHeight: typography.lineHeight.sm,
  },
  totalText: {
    fontSize: typography.fontSize.xs,
    color: colors.textMuted,
    fontFamily: typography.fontFamily.medium,
    marginTop: spacing.sm,
  },
  sourcesContainer: {
    marginTop: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
  },
  sourcesTitle: {
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.bold,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  sourcesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  sourceBadge: {
    backgroundColor: '#F1F5F9',
    borderColor: '#E2E8F0',
  },
});
export default AskResult;

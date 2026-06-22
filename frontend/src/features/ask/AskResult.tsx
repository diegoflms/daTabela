import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../../theme';
import { DynamicTable } from '../../components/data/DynamicTable';
import { Badge } from '../../components/ui/Badge';
import { AskResponse } from '../../types/ask';

interface AskResultProps {
  result: AskResponse;
}

const excludedColumns = [
  'id',
  'game_id',
  'season_id',
  'competition',
  'team_id',
  'opponent_team_id',
  'player_id',
  'jersey_number',
  'is_starter',
  'minutes_text',
  'source_url',
  'parse_model',
  'needs_manual_review',
  'entity_player_name',
  'entity_player_slug',
  'entity_team_slug',
  'entity_opponent_team_slug',
  'game_season_id',
  'game_home_team_id',
  'game_away_team_id',
  'game_boxscore_url',
  'game_source_url',
  'game_round',
  'game_arena',
];

export const AskResult: React.FC<AskResultProps> = ({ result }) => {
  const { title, columns, rows, source_tables = [], note, total } = result;

  const filteredColumns = columns.filter(
    (col) => !excludedColumns.includes(col.toLowerCase())
  );

  return (
    <View style={styles.container}>
      {/* Title */}
      <Text style={styles.title}>{title || 'Resultado da Pergunta'}</Text>

      {/* Table */}
      <DynamicTable columns={filteredColumns} rows={rows} />

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
